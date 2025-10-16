import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.lib.pagesizes import letter
from io import BytesIO
from PIL import Image

class PDFEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Builder")
        self.pdf_path = None

        tk.Button(root, text="Open PDF", command=self.open_pdf, width=20).pack(pady=5)
        tk.Button(root, text="Add Text", command=self.add_text, width=20).pack(pady=5)
        tk.Button(root, text="Add Image", command=self.add_image, width=20).pack(pady=5)
        tk.Button(root, text="Add Table", command=self.add_table, width=20).pack(pady=5)
        tk.Button(root, text="Save PDF", command=self.save_pdf, width=20).pack(pady=5)

        self.pdf_writer = PdfWriter()
        self.overlay_pages = []  # Store pages to add

    def open_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.pdf_path = path
            reader = PdfReader(self.pdf_path)
            for page in reader.pages:
                self.pdf_writer.add_page(page)
            messagebox.showinfo("Loaded", f"{len(reader.pages)} pages loaded.")

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
