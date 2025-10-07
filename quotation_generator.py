"""
Quotation & Invoice Generator
A complete standalone application for generating quotations and invoices
"""

from tkinter import *
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import sqlite3
import os
import uuid

def connect_database():
    """Connect to SQLite database - creates database file if it doesn't exist"""
    # Get the directory where the script is located
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        app_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    db_path = os.path.join(app_dir, 'quotations.db')
    
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        # Create invoices table
        cursor.execute("""CREATE TABLE IF NOT EXISTS invoices (
            invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
            quotation_number TEXT UNIQUE NOT NULL,
            document_type TEXT NOT NULL,
            client_name TEXT NOT NULL,
            client_address TEXT,
            client_phone TEXT,
            client_email TEXT,
            total_amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        # Create invoice_items table
        cursor.execute("""CREATE TABLE IF NOT EXISTS invoice_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            product_name TEXT,
            quantity REAL,
            unit TEXT,
            unit_price REAL,
            total_price REAL,
            FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id) ON DELETE CASCADE
        )""")
        
        connection.commit()
        return connection, cursor
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to connect: {e}")
        return None, None

class QuotationGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("MABIDIS QUOTATIONS")
        self.root.geometry("1200x700")
        self.root.config(bg="#ecf0f1")
        
        # Database connection
        self.connection, self.cursor = connect_database()
        if not self.connection:
            messagebox.showerror("Error", "Failed to connect to database!")
            return
        
        # Items list
        self.items = []
        
        self.create_widgets()
    
    def create_widgets(self):
        # Header
        header = Frame(self.root, bg="#2c3e50", height=80)
        header.pack(fill=X)
        header.pack_propagate(False)
        
        Label(header, text="📄 MABIDIS TECHNOLOGIES", 
              font=("Arial", 24, "bold"), bg="#2c3e50", fg="white").pack(pady=20)
        
        # Main container
        main_frame = Frame(self.root, bg="#ecf0f1")
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Left panel - Document details
        left_panel = LabelFrame(main_frame, text="Document Details", 
                               font=("Arial", 12, "bold"), bg="white", padx=15, pady=15)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Document Type Selection
        Label(left_panel, text="Document Type:", font=("Arial", 10), bg="white").grid(row=0, column=0, sticky=W, pady=5)
        self.doc_type = ttk.Combobox(left_panel, font=("Arial", 10), width=25, state="readonly")
        self.doc_type['values'] = ('Quotation', 'Invoice')
        self.doc_type.current(0)
        self.doc_type.grid(row=0, column=1, pady=5, padx=5)
        
        # Document number
        Label(left_panel, text="Document Number:", font=("Arial", 10), bg="white").grid(row=1, column=0, sticky=W, pady=5)
        self.quotation_number = Entry(left_panel, font=("Arial", 10), width=27)
        
        unique_id = str(uuid.uuid4())[:8].upper()
        self.quotation_number.insert(0, f"QTN-{unique_id}")
        self.quotation_number.config(state="readonly")
        self.quotation_number.grid(row=1, column=1, pady=5, padx=5)
        
        # Client details
        Label(left_panel, text="Client Name:", font=("Arial", 10), bg="white").grid(row=2, column=0, sticky=W, pady=5)
        self.client_name = Entry(left_panel, font=("Arial", 10), width=27)
        self.client_name.grid(row=2, column=1, pady=5, padx=5)
        
        Label(left_panel, text="Client Address:", font=("Arial", 10), bg="white").grid(row=3, column=0, sticky=NW, pady=5)
        self.client_address = Text(left_panel, font=("Arial", 10), width=27, height=3)
        self.client_address.grid(row=3, column=1, pady=5, padx=5)
        
        Label(left_panel, text="Phone:", font=("Arial", 10), bg="white").grid(row=4, column=0, sticky=W, pady=5)
        self.client_phone = Entry(left_panel, font=("Arial", 10), width=27)
        self.client_phone.grid(row=4, column=1, pady=5, padx=5)
        
        Label(left_panel, text="Email:", font=("Arial", 10), bg="white").grid(row=5, column=0, sticky=W, pady=5)
        self.client_email = Entry(left_panel, font=("Arial", 10), width=27)
        self.client_email.grid(row=5, column=1, pady=5, padx=5)
        
        # Item entry section
        item_frame = LabelFrame(left_panel, text="Add Items", font=("Arial", 10, "bold"), bg="white", padx=10, pady=10)
        item_frame.grid(row=6, column=0, columnspan=2, pady=15, sticky="ew")
        
        Label(item_frame, text="Product/Service:", font=("Arial", 9), bg="white").grid(row=0, column=0, sticky=W, pady=3)
        self.product_name = Entry(item_frame, font=("Arial", 9), width=25)
        self.product_name.grid(row=0, column=1, pady=3, padx=5)
        
        Label(item_frame, text="Quantity:", font=("Arial", 9), bg="white").grid(row=1, column=0, sticky=W, pady=3)
        qty_frame = Frame(item_frame, bg="white")
        qty_frame.grid(row=1, column=1, pady=3, padx=5, sticky=W)
        
        self.quantity = Entry(qty_frame, font=("Arial", 9), width=10)
        self.quantity.pack(side=LEFT, padx=(0, 5))
        
        self.quantity_unit = ttk.Combobox(qty_frame, font=("Arial", 9), width=10, state="readonly")
        self.quantity_unit['values'] = ("dzn","set")
        self.quantity_unit.current(0)
        self.quantity_unit.pack(side=LEFT)
        
        Label(item_frame, text="Unit Price (KES):", font=("Arial", 9), bg="white").grid(row=2, column=0, sticky=W, pady=3)
        self.unit_price = Entry(item_frame, font=("Arial", 9), width=25)
        self.unit_price.grid(row=2, column=1, pady=3, padx=5)
        
        Button(item_frame, text="Add Item", font=("Arial", 9, "bold"), 
               bg="#3498db", fg="white", cursor="hand2", command=self.add_item).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Right panel - Items list
        right_panel = LabelFrame(main_frame, text="Items List", 
                                font=("Arial", 12, "bold"), bg="white", padx=15, pady=15)
        right_panel.grid(row=0, column=1, sticky="nsew")
        
        # Treeview for items
        tree_frame = Frame(right_panel, bg="white")
        tree_frame.pack(fill=BOTH, expand=True)
        
        yscrollbar = Scrollbar(tree_frame, orient=VERTICAL)
        yscrollbar.pack(side=RIGHT, fill=Y)
        
        xscrollbar = Scrollbar(tree_frame, orient=HORIZONTAL)
        xscrollbar.pack(side=BOTTOM, fill=X)
        
        self.items_tree = ttk.Treeview(tree_frame, columns=("Product", "Qty", "Unit", "Price", "Total"),
                                       show="headings", height=12, yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)
        yscrollbar.config(command=self.items_tree.yview)
        xscrollbar.config(command=self.items_tree.xview)
        
        self.items_tree.heading("Product", text="Product/Service")
        self.items_tree.heading("Qty", text="Quantity")
        self.items_tree.heading("Unit", text="Unit")
        self.items_tree.heading("Price", text="Unit Price (KES)")
        self.items_tree.heading("Total", text="Total (KES)")
        
        self.items_tree.column("Product", width=200)
        self.items_tree.column("Qty", width=80, anchor=CENTER)
        self.items_tree.column("Unit", width=80, anchor=CENTER)
        self.items_tree.column("Price", width=120, anchor=E)
        self.items_tree.column("Total", width=120, anchor=E)
        
        self.items_tree.pack(fill=BOTH, expand=True)
        
        # Total section
        total_frame = Frame(right_panel, bg="white")
        total_frame.pack(fill=X, pady=10)
        
        Label(total_frame, text="TOTAL AMOUNT:", font=("Arial", 14, "bold"), 
              bg="white", fg="#2c3e50").pack(side=LEFT, padx=10)
        self.total_label = Label(total_frame, text="KES 0.00", font=("Arial", 16, "bold"), 
                                bg="#27ae60", fg="white", padx=20, pady=5)
        self.total_label.pack(side=RIGHT, padx=10)
        
        # Action buttons
        btn_frame = Frame(right_panel, bg="white")
        btn_frame.pack(fill=X, pady=10)
        
        Button(btn_frame, text="Remove Item", font=("Arial", 10, "bold"), 
               bg="#e74c3c", fg="white", cursor="hand2", width=15,
               command=self.remove_item).pack(side=LEFT, padx=5)
        
        Button(btn_frame, text="Clear All", font=("Arial", 10, "bold"), 
               bg="#95a5a6", fg="white", cursor="hand2", width=15,
               command=self.clear_all).pack(side=LEFT, padx=5)
        
        Button(btn_frame, text="Save to DB", font=("Arial", 10, "bold"), 
               bg="#9b59b6", fg="white", cursor="hand2", width=15,
               command=self.save_to_database).pack(side=LEFT, padx=5)
        
        Button(btn_frame, text="Generate PDF", font=("Arial", 10, "bold"), 
               bg="#27ae60", fg="white", cursor="hand2", width=15,
               command=self.generate_pdf).pack(side=LEFT, padx=5)
        
        # Configure grid weights
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=2)
        main_frame.grid_rowconfigure(0, weight=1)
    
    def add_item(self):
        product = self.product_name.get().strip()
        qty = self.quantity.get().strip()
        unit = self.quantity_unit.get()
        price = self.unit_price.get().strip()
        
        if not product or not qty or not price:
            messagebox.showwarning("Warning", "Please fill all item fields!")
            return
        
        try:
            qty = float(qty)  
            price = float(price)
            total = qty * price
            
            item = {
                'product': product,
                'quantity': qty,
                'unit': unit,
                'price': price,
                'total': total
            }
            
            self.items.append(item)
            self.items_tree.insert("", END, values=(product, qty, unit, f"{price:,.2f}", f"{total:,.2f}"))
            
            # Clear fields
            self.product_name.delete(0, END)
            self.quantity.delete(0, END)
            self.quantity_unit.current(0)
            self.unit_price.delete(0, END)
            
            self.update_total()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity or price!")
    
    def remove_item(self):
        selected = self.items_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to remove!")
            return
        
        index = self.items_tree.index(selected[0])
        self.items.pop(index)
        self.items_tree.delete(selected[0])
        self.update_total()
    
    def update_total(self):
        total = sum(item['total'] for item in self.items)
        self.total_label.config(text=f"KES {total:,.2f}")
    
    def clear_all(self):
        confirm = messagebox.askyesno("Confirm", "Clear all items?")
        if confirm:
            self.items = []
            for item in self.items_tree.get_children():
                self.items_tree.delete(item)
            self.update_total()
    
    def save_to_database(self):
        if not self.items:
            messagebox.showwarning("Warning", "No items to save!")
            return
        
        client_name = self.client_name.get().strip()
        if not client_name:
            messagebox.showwarning("Warning", "Client name is required!")
            return
        
        try:
            total = sum(item['total'] for item in self.items)
            
            # Insert invoice - FIXED for SQLite (uses ? instead of %s)
            query = """INSERT INTO invoices (quotation_number, document_type, client_name, 
                       client_address, client_phone, client_email, total_amount) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)"""
            
            self.cursor.execute(query, (
                self.quotation_number.get(),
                self.doc_type.get(),
                client_name,
                self.client_address.get("1.0", END).strip(),
                self.client_phone.get().strip(),
                self.client_email.get().strip(),
                total
            ))
            
            invoice_id = self.cursor.lastrowid
            
            # Insert items - FIXED for SQLite
            item_query = """INSERT INTO invoice_items (invoice_id, product_name, quantity, unit,
                            unit_price, total_price) VALUES (?, ?, ?, ?, ?, ?)"""
            
            for item in self.items:
                self.cursor.execute(item_query, (
                    invoice_id, item['product'], item['quantity'], item['unit'],
                    item['price'], item['total']
                ))
            
            self.connection.commit()
            messagebox.showinfo("Success", "Document saved to database!")
            
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to save: {e}")
            self.connection.rollback()
    
    def generate_pdf(self):
        if not self.items:
            messagebox.showwarning("Warning", "No items to generate PDF!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"{self.doc_type.get()}_{self.quotation_number.get()}.pdf"
        )
        
        if not filename:
            return
        
        try:
            c = canvas.Canvas(filename, pagesize=letter)
            width, height = letter
            
            # Get data
            doc_type = self.doc_type.get()
            quotation_number = self.quotation_number.get()
            client_name = self.client_name.get()
            client_address = self.client_address.get("1.0", END).strip()
            client_phone = self.client_phone.get()
            client_email = self.client_email.get()
            items = self.items
            
            # --- Company Header ---
            c.setFont("Helvetica-Bold", 20)
            c.drawString(1 * inch, height - 1 * inch, "MABIDIS TECHNOLOGIES LTD")
            c.setFont("Helvetica", 10)
            c.drawString(1 * inch, height - 1.2 * inch, "P.O. Box 1234, Nairobi, Kenya")
            c.drawString(1 * inch, height - 1.4 * inch, "Email: support@mabidis.co.ke | Phone: +254 712 345678")

            # --- Document Title ---
            c.setFont("Helvetica-Bold", 18)
            c.drawString(1 * inch, height - 2 * inch, doc_type.upper())

            c.setFont("Helvetica", 10)
            c.drawString(1 * inch, height - 2.3 * inch, f"Number: {quotation_number}")
            c.drawString(1 * inch, height - 2.5 * inch, f"Date: {datetime.now().strftime('%Y-%m-%d')}")

            # --- Client Info ---
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1 * inch, height - 3 * inch, "BILL TO:")
            c.setFont("Helvetica", 10)
            c.drawString(1 * inch, height - 3.2 * inch, client_name)
            c.drawString(1 * inch, height - 3.4 * inch, client_address)
            c.drawString(1 * inch, height - 3.6 * inch, f"Phone: {client_phone}")
            c.drawString(1 * inch, height - 3.8 * inch, f"Email: {client_email}")

            # --- Items Table Header ---
            y = height - 4.5 * inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1 * inch, y, "Item")
            c.drawString(3.5 * inch, y, "Qty")
            c.drawString(4.5 * inch, y, "Unit")
            c.drawString(5.5 * inch, y, "Price")
            c.drawString(6.5 * inch, y, "Total")

            y -= 0.2 * inch
            c.line(1 * inch, y, 7.5 * inch, y)
            y -= 0.3 * inch

            # --- Items ---
            c.setFont("Helvetica", 9)
            subtotal = 0
            for item in items:
                c.drawString(1 * inch, y, item['product'][:30])
                c.drawString(3.5 * inch, y, str(item['quantity']))
                c.drawString(4.5 * inch, y, item['unit'])
                c.drawString(5.5 * inch, y, f"KES {item['price']:,.2f}")
                c.drawString(6.5 * inch, y, f"KES {item['total']:,.2f}")
                subtotal += item['total']
                y -= 0.25 * inch

            # --- Totals ---
            tax_rate = 0.16
            tax = subtotal * tax_rate
            total = subtotal + tax
            y -= 0.3 * inch
            c.line(4.8 * inch, y, 7.5 * inch, y)

            c.setFont("Helvetica", 10)
            y -= 0.25 * inch
            c.drawString(5 * inch, y, f"Subtotal: KES {subtotal:,.2f}")
            y -= 0.25 * inch
            c.drawString(5 * inch, y, f"VAT (16%): KES {tax:,.2f}")
            y -= 0.3 * inch
            c.setFont("Helvetica-Bold", 12)
            c.drawString(5 * inch, y, f"TOTAL: KES {total:,.2f}")

            # --- Footer ---
            c.setFont("Helvetica-Oblique", 8)
            c.drawString(1 * inch, 0.75 * inch, "Thank you for your business!")
            c.drawString(1 * inch, 0.55 * inch, "This document was generated automatically by MABIDIS System.")
            
            # Save PDF
            c.showPage()
            c.save()
            
            messagebox.showinfo("Success", f"PDF generated successfully!\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF: {e}")
    
    def __del__(self):
        """Close database connection when app closes"""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()

if __name__ == "__main__":
    import sys
    root = Tk()
    app = QuotationGenerator(root)
    root.mainloop()