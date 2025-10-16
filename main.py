import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.lib.pagesizes import letter
from io import BytesIO
from PIL import Image, ImageTk
from pdf2image import convert_from_path

class PDFEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Builder & Viewer")
        self.pdf_path = None
        self.pdf_writer = PdfWriter()
        self.pages = []
        self.current_page = 0

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Open PDF", command=self.open_pdf, width=15).grid(row=0, column=0, padx=3)
        tk.Button(btn_frame, text="Add Text", command=self.add_text, width=15).grid(row=0, column=1, padx=3)
        tk.Button(btn_frame, text="Add Image", command=self.add_image, width=15).grid(row=0, column=2, padx=3)
        tk.Button(btn_frame, text="Add Table", command=self.add_table, width=15).grid(row=0, column=3, padx=3)
        tk.Button(btn_frame, text="Save PDF", command=self.save_pdf, width=15).grid(row=0, column=4, padx=3)

        # Canvas for preview
        self.preview_canvas = tk.Canvas(root, width=600, height=800, bg="#ddd")
        self.preview_canvas.pack(pady=10)

        # Navigation buttons
        nav_frame = tk.Frame(root)
        nav_frame.pack()
        tk.Button(nav_frame, text="◀ Prev", command=self.prev_page).grid(row=0, column=0, padx=10)
        tk.Button(nav_frame, text="Next ▶", command=self.next_page).grid(row=0, column=1, padx=10)

    def open_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not path:
            return

        self.pdf_path = path
        reader = PdfReader(path)
        self.pdf_writer = PdfWriter()
        for page in reader.pages:
            self.pdf_writer.add_page(page)

        self.load_preview()
        messagebox.showinfo("Loaded", f"{len(reader.pages)} pages loaded.")

    def load_preview(self):
        """Render first page as image."""
        self.pages = convert_from_path(self.pdf_path, dpi=100)
        self.current_page = 0
        self.display_page()

    def display_page(self):
        if not self.pages:
            return
        img = self.pages[self.current_page]
        img.thumbnail((600, 800))
        self.tk_img = ImageTk.PhotoImage(img)
        self.preview_canvas.create_image(300, 400, image=self.tk_img)

    def next_page(self):
        if self.pages and self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.display_page()

    def prev_page(self):
        if self.pages and self.current_page > 0:
            self.current_page -= 1
            self.display_page()

    def add_text(self):
        text_window = tk.Toplevel(self.root)
        text_window.title("Add Text")
        tk.Label(text_window, text="Enter Text:").pack()
        text_entry = tk.Text(text_window, width=40, height=5)
        text_entry.pack()

        def add():
            text_content = text_entry.get("1.0", tk.END).strip()
            if not text_content:
                messagebox.showwarning("Empty", "Text cannot be empty.")
                return

            packet = BytesIO()
            c = canvas.Canvas(packet, pagesize=letter)
            c.drawString(100, 500, text_content)
            c.save()
            packet.seek(0)
            new_pdf = PdfReader(packet)
            self.pdf_writer.add_page(new_pdf.pages[0])
            text_window.destroy()
            messagebox.showinfo("Added", "Text added as new page.")

        tk.Button(text_window, text="Add", command=add).pack(pady=5)

    def add_image(self):
        img_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if not img_path:
            return
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)
        c.drawImage(img_path, 100, 300, width=300, height=200)
        c.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        self.pdf_writer.add_page(new_pdf.pages[0])
        messagebox.showinfo("Added", "Image added as new page.")

    def add_table(self):
        table_window = tk.Toplevel(self.root)
        table_window.title("Add Table")

        tk.Label(table_window, text="Enter table as CSV (comma-separated):").pack()
        table_entry = tk.Text(table_window, width=50, height=10)
        table_entry.pack()

        def add():
            raw_text = table_entry.get("1.0", tk.END).strip()
            if not raw_text:
                messagebox.showwarning("Empty", "Table cannot be empty.")
                return
            data = [row.split(",") for row in raw_text.split("\n")]
            packet = BytesIO()
            doc = SimpleDocTemplate(packet, pagesize=letter)
            table = Table(data)
            doc.build([table])
            packet.seek(0)
            new_pdf = PdfReader(packet)
            self.pdf_writer.add_page(new_pdf.pages[0])
            table_window.destroy()
            messagebox.showinfo("Added", "Table added as new page.")

        tk.Button(table_window, text="Add Table", command=add).pack(pady=5)

    def save_pdf(self):
        if not self.pdf_writer.pages:
            messagebox.showwarning("Empty", "No pages to save.")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if save_path:
            with open(save_path, "wb") as f:
                self.pdf_writer.write(f)
            messagebox.showinfo("Saved", f"PDF saved to {save_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFEditor(root)
    root.mainloop()
