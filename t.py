#!/usr/bin/env python3
"""
Express Wash - Professional Tkinter Desktop Application (Modern UI)
This version uses ttkbootstrap for a modern and clean user interface.
All core logic from the original tkinter_app.py is preserved.
"""

import tkinter as tk
from tkinter import ttk, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.widgets import DateEntry

import mysql.connector
import pandas as pd
from datetime import datetime, date
import os
import webbrowser
import shutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Set a consistent style for matplotlib charts
plt.style.use('seaborn-v0_8-whitegrid')
# Set a default font size for better readability in charts
plt.rcParams.update({'font.size': 10})


class ExpressWashAppModern:
    def __init__(self, root):
        self.root = root
        self.root.title("🧺 Express Wash - Smart Laundry Billing System")
        self.root.geometry("1400x850") # Adjusted size for better fit
        
        # --- Configuration ---
        self.DB_CONFIG = {
            'host': 'localhost',
            'user': 'root',
            'password': '16021995', # IMPORTANT: Use your actual password
            'database': 'express_wash'
        }
        
        self.PRICING = {
            'regular_clothes': 50,  # ₹50/kg
            'blankets': 100,        # ₹100/kg
            'white_clothes': 40     # ₹40/piece
        }
        
        # --- Initialization ---
        self.init_database()
        self.create_widgets()
        
    def init_database(self):
        """Initialize MySQL database connection and schema."""
        try:
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    receipt_number VARCHAR(32) UNIQUE,
                    customer_name VARCHAR(255) NOT NULL,
                    mobile_number VARCHAR(20),
                    order_date DATE NOT NULL,
                    regular_clothes_kg DECIMAL(5,2) DEFAULT 0,
                    blankets_kg DECIMAL(5,2) DEFAULT 0,
                    white_clothes_pieces INT DEFAULT 0,
                    total_amount DECIMAL(10,2) NOT NULL,
                    collection_date DATETIME NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            try:
                # Ensure collection_date column exists
                cursor.execute('ALTER TABLE orders ADD COLUMN collection_date DATETIME NULL')
            except mysql.connector.Error:
                pass  # Column already exists
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            Messagebox.show_error(f"Database Connection Failed:\n{err}\nPlease check your database credentials in DB_CONFIG.", "Database Error")
            self.root.quit()

    def create_widgets(self):
        """Create the main GUI layout and widgets."""
        # --- Header ---
        header_frame = ttk.Frame(self.root, bootstyle="primary", padding=15)
        header_frame.pack(fill=X)
        ttk.Label(header_frame, text="🧺 Express Wash - Smart Laundry Billing System", 
                  font=('Helvetica', 20, 'bold'), bootstyle="primary inverse").pack()

        # --- Main Content Area ---
        main_paned_window = ttk.PanedWindow(self.root, orient=HORIZONTAL)
        main_paned_window.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # --- Left Pane: Order Form ---
        form_pane = ttk.Frame(main_paned_window, padding=10)
        self.create_order_form(form_pane)
        main_paned_window.add(form_pane, weight=2) # Give more weight to the form

        # --- Right Pane: Actions ---
        actions_pane = ttk.Frame(main_paned_window, padding=10)
        self.create_actions_panel(actions_pane)
        main_paned_window.add(actions_pane, weight=1)

    def create_order_form(self, parent):
        """Creates the new order form with ttkbootstrap widgets."""
        form_frame = ttk.LabelFrame(parent, text="📝 New Order Details", bootstyle="primary", padding=20)
        form_frame.pack(fill=BOTH, expand=True)

        # --- Customer Information ---
        customer_frame = ttk.LabelFrame(form_frame, text="👤 Customer Information", padding=15)
        customer_frame.pack(fill=X, pady=(0, 15))
        customer_frame.columnconfigure(1, weight=1)
        customer_frame.columnconfigure(3, weight=1)
        
        ttk.Label(customer_frame, text="Receipt Number:", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.receipt_number_var = tk.StringVar()
        self.receipt_number_entry = ttk.Entry(customer_frame, textvariable=self.receipt_number_var)
        self.receipt_number_entry.grid(row=0, column=1, sticky=EW, padx=5, pady=5)
        
        ttk.Label(customer_frame, text="Customer Name:", font=('Helvetica', 10, 'bold')).grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.customer_name_var = tk.StringVar()
        self.customer_name_entry = ttk.Entry(customer_frame, textvariable=self.customer_name_var)
        self.customer_name_entry.grid(row=1, column=1, sticky=EW, padx=5, pady=5)

        ttk.Label(customer_frame, text="Mobile Number:", font=('Helvetica', 10, 'bold')).grid(row=0, column=2, sticky=W, padx=15, pady=5)
        self.mobile_var = tk.StringVar()
        self.mobile_entry = ttk.Entry(customer_frame, textvariable=self.mobile_var)
        self.mobile_entry.grid(row=0, column=3, sticky=EW, padx=5, pady=5)

        ttk.Label(customer_frame, text="Order Date:", font=('Helvetica', 10, 'bold')).grid(row=1, column=2, sticky=W, padx=15, pady=5)
        self.order_date_entry = DateEntry(customer_frame, bootstyle="primary", dateformat="%Y-%m-%d")
        self.order_date_entry.grid(row=1, column=3, sticky=EW, padx=5, pady=5)
        
        # --- Service Details ---
        service_frame = ttk.LabelFrame(form_frame, text="🧺 Service Details", padding=15)
        service_frame.pack(fill=X, pady=(0, 15))
        service_frame.columnconfigure((1, 3), weight=1)
        
        ttk.Label(service_frame, text="Regular Clothes (kg):", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.regular_clothes_var = tk.StringVar(value="0")
        self.regular_clothes_entry = ttk.Entry(service_frame, textvariable=self.regular_clothes_var)
        self.regular_clothes_entry.grid(row=0, column=1, sticky=EW, padx=5, pady=5)

        ttk.Label(service_frame, text="Blankets (kg):", font=('Helvetica', 10, 'bold')).grid(row=0, column=2, sticky=W, padx=15, pady=5)
        self.blankets_var = tk.StringVar(value="0")
        self.blankets_entry = ttk.Entry(service_frame, textvariable=self.blankets_var)
        self.blankets_entry.grid(row=0, column=3, sticky=EW, padx=5, pady=5)
        
        ttk.Label(service_frame, text="White Clothes (pcs):", font=('Helvetica', 10, 'bold')).grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.white_clothes_var = tk.StringVar(value="0")
        self.white_clothes_entry = ttk.Entry(service_frame, textvariable=self.white_clothes_var)
        self.white_clothes_entry.grid(row=1, column=1, sticky=EW, padx=5, pady=5)
        
        # --- Bill Summary ---
        bill_frame = ttk.LabelFrame(form_frame, text="💰 Bill Summary", padding=15)
        bill_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        self.bill_text = ScrolledText(bill_frame, height=6, font=('Courier New', 10), wrap="word", hbar=False)
        self.bill_text.pack(fill=BOTH, expand=True)
        self.bill_text.text.config(state='disabled')
        
        # --- Action Buttons for Form ---
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=X, pady=(10, 0))
        button_frame.columnconfigure((0, 1, 2), weight=1)

        ttk.Button(button_frame, text="🧮 Calculate Bill", command=self.calculate_bill, bootstyle="info").grid(row=0, column=0, sticky=EW, padx=5)
        ttk.Button(button_frame, text="💾 Save Order", command=self.save_order, bootstyle="success").grid(row=0, column=1, sticky=EW, padx=5)
        ttk.Button(button_frame, text="🗑️ Clear Form", command=self.clear_form, bootstyle="danger").grid(row=0, column=2, sticky=EW, padx=5)
    
    def create_actions_panel(self, parent):
        """Creates the right-side panel for collection and management."""
        actions_frame = ttk.Frame(parent)
        actions_frame.pack(fill=BOTH, expand=True)

        # --- Collection Tracking ---
        collection_frame = ttk.LabelFrame(actions_frame, text="📦 Collection Tracking", bootstyle="info", padding=15)
        collection_frame.pack(fill=X, pady=(0, 20))

        ttk.Label(collection_frame, text="Enter Receipt Number:", font=('Helvetica', 10, 'bold')).pack(fill=X, pady=(0, 5))
        self.collection_receipt_var = tk.StringVar()
        self.collection_receipt_entry = ttk.Entry(collection_frame, textvariable=self.collection_receipt_var)
        self.collection_receipt_entry.pack(fill=X, pady=(0, 10))

        ttk.Button(collection_frame, text="✅ Mark as Collected", command=self.mark_as_collected, bootstyle="success-outline").pack(fill=X, pady=5)
        ttk.Button(collection_frame, text="📄 Generate Invoice", command=self.generate_invoice, bootstyle="primary-outline").pack(fill=X, pady=5)

        # --- Order Management ---
        management_frame = ttk.LabelFrame(actions_frame, text="📋 Order Management", bootstyle="info", padding=15)
        management_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Button(management_frame, text="VIEW ALL ORDERS", command=self.open_order_list_window, bootstyle="primary").pack(fill=X, ipady=10)

    def open_order_list_window(self):
        """Open a new window with the order list and management tools."""
        self.order_window = tk.Toplevel(self.root)
        self.order_window.title("📋 Express Wash - Order List & Management")
        self.order_window.geometry("1300x700")
        
        self.order_window.transient(self.root)
        self.order_window.grab_set()
        
        self.create_order_history_view(self.order_window)
        self.load_orders()

    def create_order_history_view(self, parent):
        """Create the order history view in the new window."""
        history_frame = ttk.Frame(parent, padding=15)
        history_frame.pack(fill=BOTH, expand=True)

        # --- Top Controls: Search & Actions ---
        controls_frame = ttk.Frame(history_frame)
        controls_frame.pack(fill=X, pady=(0, 15))
        
        search_frame = ttk.LabelFrame(controls_frame, text="🔍 Search Orders", padding=10)
        search_frame.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(fill=X)
        self.search_var.trace('w', self.filter_orders)
        
        actions_frame = ttk.LabelFrame(controls_frame, text="⚡ Quick Actions", padding=10)
        actions_frame.pack(side=LEFT)

        ttk.Button(actions_frame, text="✏️ Edit", command=self.edit_order, bootstyle="warning").pack(side=LEFT, padx=5)
        ttk.Button(actions_frame, text="🗑️ Delete", command=self.delete_order, bootstyle="danger").pack(side=LEFT, padx=5)
        ttk.Button(actions_frame, text="🔄 Refresh", command=self.load_orders, bootstyle="info").pack(side=LEFT, padx=5)
        ttk.Button(actions_frame, text="📥 Export CSV", command=self.export_data, bootstyle="secondary").pack(side=LEFT, padx=5)
        ttk.Button(actions_frame, text="📊 Reports", command=self.show_reports, bootstyle="primary").pack(side=LEFT, padx=5)

        # --- Orders Table ---
        table_frame = ttk.Frame(history_frame)
        table_frame.pack(fill=BOTH, expand=True)
        
        columns = ('id', 'receipt', 'customer', 'mobile', 'order_date', 'collection_date', 'total', 'created_at')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', bootstyle="primary")

        # Define headings
        self.tree.heading('id', text='ID')
        self.tree.heading('receipt', text='Receipt No.')
        self.tree.heading('customer', text='Customer Name')
        self.tree.heading('mobile', text='Mobile')
        self.tree.heading('order_date', text='Order Date')
        self.tree.heading('collection_date', text='Collected')
        self.tree.heading('total', text='Total (₹)')
        self.tree.heading('created_at', text='Created At')

        # Define column properties
        self.tree.column('id', width=50, anchor=CENTER)
        self.tree.column('receipt', width=150)
        self.tree.column('customer', width=180)
        self.tree.column('mobile', width=120)
        self.tree.column('order_date', width=120, anchor=CENTER)
        self.tree.column('collection_date', width=180)
        self.tree.column('total', width=100, anchor=E)
        self.tree.column('created_at', width=180)

        # Scrollbar
        scrollbar_y = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar_y.pack(side=RIGHT, fill=Y)
        scrollbar_x.pack(side=BOTTOM, fill=X)
        
    def calculate_bill(self):
        """Calculate and display the bill in the ScrolledText widget."""
        try:
            regular_kg = float(self.regular_clothes_var.get() or 0)
            blankets_kg = float(self.blankets_var.get() or 0)
            white_pieces = int(self.white_clothes_var.get() or 0)

            regular_cost = regular_kg * self.PRICING['regular_clothes']
            blankets_cost = blankets_kg * self.PRICING['blankets']
            white_cost = white_pieces * self.PRICING['white_clothes']
            total = regular_cost + blankets_cost + white_cost
            
            self.bill_text.text.config(state='normal')
            self.bill_text.delete(1.0, tk.END)
            
            lines = ["🧺 Express Wash - Bill Summary\n\n"]
            if regular_kg > 0:
                lines.append(f"{'Regular Clothes:':<25} {regular_kg:>5.2f}kg x ₹{self.PRICING['regular_clothes']:<5.2f} = ₹{regular_cost:>8.2f}")
            if blankets_kg > 0:
                lines.append(f"{'Blankets/Bedsheets:':<25} {blankets_kg:>5.2f}kg x ₹{self.PRICING['blankets']:<5.2f} = ₹{blankets_cost:>8.2f}")
            if white_pieces > 0:
                lines.append(f"{'White Clothes:':<25} {white_pieces:>5} pcs x ₹{self.PRICING['white_clothes']:<5.2f} = ₹{white_cost:>8.2f}")
            
            lines.append("\n" + "─" * 50)
            lines.append(f"{'💵 TOTAL AMOUNT:':<40} ₹{total:>8.2f}")
            lines.append("─" * 50)

            self.bill_text.insert(1.0, '\n'.join(lines))
            self.bill_text.text.config(state='disabled')
        except ValueError:
            Messagebox.show_error("Please enter valid numbers for weights and quantities.", "Invalid Input")
        except Exception as e:
            Messagebox.show_error(f"An error occurred: {e}", "Error")

    def save_order(self):
        """Save the new order to the database."""
        receipt_number = self.receipt_number_var.get().strip()
        customer_name = self.customer_name_var.get().strip()
        order_date = self.order_date_entry.entry.get().strip()

        if not receipt_number or not customer_name or not order_date:
            Messagebox.show_warning("Receipt Number, Customer Name, and Order Date are required.", "Missing Information")
            return

        try:
            regular_kg = float(self.regular_clothes_var.get() or 0)
            blankets_kg = float(self.blankets_var.get() or 0)
            white_pieces = int(self.white_clothes_var.get() or 0)
            total = (regular_kg * self.PRICING['regular_clothes'] + 
                     blankets_kg * self.PRICING['blankets'] + 
                     white_pieces * self.PRICING['white_clothes'])

            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO orders (receipt_number, customer_name, mobile_number, order_date, 
                                   regular_clothes_kg, blankets_kg, white_clothes_pieces, total_amount)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (receipt_number, customer_name, self.mobile_var.get().strip(), order_date, 
                  regular_kg, blankets_kg, white_pieces, total))
            conn.commit()
            conn.close()
            Messagebox.show_info(f"Order saved successfully!\nReceipt Number: {receipt_number}", "Success")
            self.clear_form()
            # If order window is open, refresh it
            if hasattr(self, 'order_window') and self.order_window.winfo_exists():
                self.load_orders()
        except mysql.connector.Error as err:
            Messagebox.show_error(f"Database error: {err}", "Error Saving Order")
        except ValueError:
            Messagebox.show_error("Please enter valid numbers for services.", "Invalid Input")
        except Exception as e:
            Messagebox.show_error(f"An unexpected error occurred: {e}", "Error")

    def clear_form(self):
        """Clear all entry fields in the new order form."""
        self.receipt_number_var.set("")
        self.customer_name_var.set("")
        self.mobile_var.set("")
        self.order_date_entry.entry.delete(0, END)
        self.order_date_entry.entry.insert(0, date.today().strftime('%Y-%m-%d'))
        self.regular_clothes_var.set("0")
        self.blankets_var.set("0")
        self.white_clothes_var.set("0")
        self.bill_text.text.config(state='normal')
        self.bill_text.delete(1.0, tk.END)
        self.bill_text.text.config(state='disabled')
        
    def load_orders(self):
        """Load all orders from the database into the Treeview."""
        if not hasattr(self, 'tree'):
            return # Don't load if the treeview doesn't exist yet
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, receipt_number, customer_name, mobile_number, order_date, 
                       collection_date, total_amount, created_at
                FROM orders ORDER BY created_at DESC
            ''')
            orders = cursor.fetchall()
            conn.close()
            
            if not orders:
                self.tree.insert('', 'end', values=("", "No records found.", "", "", "", "", "", ""))
            else:
                for order in orders:
                    (id_val, receipt, name, mobile, o_date, c_date, total, created) = order
                    collection_status = c_date.strftime('%Y-%m-%d %H:%M') if c_date else "Not Collected"
                    self.tree.insert('', 'end', values=(
                        id_val, receipt, name, mobile or "", 
                        o_date.strftime('%Y-%m-%d'), 
                        collection_status, 
                        f"{total:.2f}", 
                        created.strftime('%Y-%m-%d %H:%M')
                    ))
        except Exception as e:
            Messagebox.show_error(f"Error loading orders: {e}", "Database Error")

    def filter_orders(self, *args):
        """Filter orders in the Treeview based on the search term."""
        search_term = self.search_var.get().strip().lower()
        
        # DB-based filtering is more scalable and efficient
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor()
            query = '''
                SELECT id, receipt_number, customer_name, mobile_number, order_date, 
                       collection_date, total_amount, created_at
                FROM orders 
                WHERE LOWER(receipt_number) LIKE %s OR LOWER(customer_name) LIKE %s
                ORDER BY created_at DESC
            '''
            like_term = f'%{search_term}%'
            cursor.execute(query, (like_term, like_term))
            orders = cursor.fetchall()
            conn.close()
            
            if not orders:
                self.tree.insert('', 'end', values=("", f"No results for '{search_term}'", "", "", "", "", "", ""))
            else:
                for order in orders:
                    (id_val, receipt, name, mobile, o_date, c_date, total, created) = order
                    collection_status = c_date.strftime('%Y-%m-%d %H:%M') if c_date else "Not Collected"
                    self.tree.insert('', 'end', values=(
                        id_val, receipt, name, mobile or "", 
                        o_date.strftime('%Y-%m-%d'), 
                        collection_status, 
                        f"{total:.2f}", 
                        created.strftime('%Y-%m-%d %H:%M')
                    ))
        except Exception as e:
            Messagebox.show_error(f"Error searching orders: {e}", "Search Error")
            
    def edit_order(self):
        """Open a window to edit the selected order."""
        selection = self.tree.selection()
        if not selection:
            Messagebox.show_warning("Please select an order from the list to edit.", "No Selection")
            return

        order_id = self.tree.item(selection[0], 'values')[0]

        try:
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            order_data = cursor.fetchone()
            conn.close()
            
            if order_data:
                self.create_edit_window(order_data)
            else:
                Messagebox.show_error("Could not find the selected order in the database.", "Order Not Found")
        except Exception as e:
            Messagebox.show_error(f"Error fetching order data: {e}", "Database Error")
    
    def create_edit_window(self, order_data):
        """Create the modal window for editing an order."""
        edit_window = tk.Toplevel(self.root)
        edit_window.title("✏️ Edit Order")
        edit_window.geometry("500x550")
        edit_window.transient(self.root)
        edit_window.grab_set()

        form_frame = ttk.LabelFrame(edit_window, text="Update Order Information", padding=20, bootstyle="primary")
        form_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        form_frame.columnconfigure(1, weight=1)

        # Map data to variables
        (order_id, receipt, name, mobile, o_date, reg_kg, blan_kg, white_pcs, total, _, _) = order_data
        
        # Fields
        ttk.Label(form_frame, text="Receipt Number:").grid(row=0, column=0, sticky=W, padx=5, pady=8)
        receipt_var = tk.StringVar(value=receipt)
        ttk.Entry(form_frame, textvariable=receipt_var).grid(row=0, column=1, sticky=EW, padx=5, pady=8)

        ttk.Label(form_frame, text="Customer Name:").grid(row=1, column=0, sticky=W, padx=5, pady=8)
        name_var = tk.StringVar(value=name)
        ttk.Entry(form_frame, textvariable=name_var).grid(row=1, column=1, sticky=EW, padx=5, pady=8)

        ttk.Label(form_frame, text="Mobile Number:").grid(row=2, column=0, sticky=W, padx=5, pady=8)
        mobile_var = tk.StringVar(value=mobile or "")
        ttk.Entry(form_frame, textvariable=mobile_var).grid(row=2, column=1, sticky=EW, padx=5, pady=8)
        
        ttk.Label(form_frame, text="Order Date:").grid(row=3, column=0, sticky=W, padx=5, pady=8)
        date_var = tk.StringVar(value=o_date.strftime('%Y-%m-%d'))
        ttk.Entry(form_frame, textvariable=date_var).grid(row=3, column=1, sticky=EW, padx=5, pady=8)

        ttk.Label(form_frame, text="Regular (kg):").grid(row=4, column=0, sticky=W, padx=5, pady=8)
        reg_kg_var = tk.DoubleVar(value=reg_kg)
        ttk.Entry(form_frame, textvariable=reg_kg_var).grid(row=4, column=1, sticky=EW, padx=5, pady=8)
        
        ttk.Label(form_frame, text="Blankets (kg):").grid(row=5, column=0, sticky=W, padx=5, pady=8)
        blan_kg_var = tk.DoubleVar(value=blan_kg)
        ttk.Entry(form_frame, textvariable=blan_kg_var).grid(row=5, column=1, sticky=EW, padx=5, pady=8)

        ttk.Label(form_frame, text="White (pcs):").grid(row=6, column=0, sticky=W, padx=5, pady=8)
        white_pcs_var = tk.IntVar(value=white_pcs)
        ttk.Entry(form_frame, textvariable=white_pcs_var).grid(row=6, column=1, sticky=EW, padx=5, pady=8)

        def update_order_action():
            try:
                new_total = (reg_kg_var.get() * self.PRICING['regular_clothes'] +
                             blan_kg_var.get() * self.PRICING['blankets'] +
                             white_pcs_var.get() * self.PRICING['white_clothes'])
                
                confirm = Messagebox.ask_yes_no(
                    f"Confirm Update\n\nNew Total will be ₹{new_total:.2f}. Proceed?",
                    "Confirm"
                )
                if not confirm:
                    return

                conn_update = mysql.connector.connect(**self.DB_CONFIG)
                cursor_update = conn_update.cursor()
                cursor_update.execute('''
                    UPDATE orders SET 
                    receipt_number = %s, customer_name = %s, mobile_number = %s, order_date = %s,
                    regular_clothes_kg = %s, blankets_kg = %s, white_clothes_pieces = %s, total_amount = %s
                    WHERE id = %s
                ''', (receipt_var.get(), name_var.get(), mobile_var.get(), date_var.get(),
                      reg_kg_var.get(), blan_kg_var.get(), white_pcs_var.get(), new_total, order_id))
                conn_update.commit()
                conn_update.close()
                
                Messagebox.show_info("Order updated successfully!", "Success")
                edit_window.destroy()
                self.load_orders()
            except Exception as e:
                Messagebox.show_error(f"Error updating order: {e}", "Update Error")

        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="💾 SAVE CHANGES", command=update_order_action, bootstyle="success").pack(side=LEFT, padx=10, ipady=5)
        ttk.Button(button_frame, text="❌ Cancel", command=edit_window.destroy, bootstyle="secondary").pack(side=LEFT, padx=10, ipady=5)

    def delete_order(self):
        """Delete the selected order from the database."""
        selection = self.tree.selection()
        if not selection:
            Messagebox.show_warning("Please select an order to delete.", "No Selection")
            return

        confirm = Messagebox.ask_yes_no("Are you sure you want to permanently delete this order?", "Confirm Deletion", parent=self.order_window)
        if not confirm:
            return

        try:
            order_id = self.tree.item(selection[0], 'values')[0]
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM orders WHERE id = %s', (order_id,))
            conn.commit()
            conn.close()
            Messagebox.show_info("Order deleted successfully!", "Success")
            self.load_orders()
        except Exception as e:
            Messagebox.show_error(f"Error deleting order: {e}", "Deletion Error")

    def export_data(self):
        """Export all orders to a CSV file."""
        try:
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM orders')
            if cursor.fetchone()[0] == 0:
                Messagebox.show_warning("There is no data to export.", "No Data")
                conn.close()
                return

            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save Orders As CSV"
            )
            if not filepath:
                return

            df = pd.read_sql_query('SELECT * FROM orders ORDER BY created_at DESC', conn)
            conn.close()
            
            df.to_csv(filepath, index=False)
            Messagebox.show_info(f"Data successfully exported to:\n{filepath}", "Export Success")
        except Exception as e:
            Messagebox.show_error(f"Error exporting data: {e}", "Export Error")

    def mark_as_collected(self):
        """Mark an order as collected by its receipt number."""
        receipt_number = self.collection_receipt_var.get().strip()
        if not receipt_number:
            Messagebox.show_warning("Please enter a receipt number.", "Input Required")
            return

        try:
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute('SELECT collection_date FROM orders WHERE receipt_number = %s', (receipt_number,))
            result = cursor.fetchone()

            if not result:
                Messagebox.show_error(f"Order with receipt number '{receipt_number}' not found.", "Not Found")
                conn.close()
                return
            if result[0] is not None:
                Messagebox.show_warning("This order has already been marked as collected.", "Already Collected")
                conn.close()
                return
            
            confirm = Messagebox.ask_yes_no(f"Mark order '{receipt_number}' as collected?", "Confirm Collection")
            if confirm:
                cursor.execute('UPDATE orders SET collection_date = NOW() WHERE receipt_number = %s', (receipt_number,))
                conn.commit()
                Messagebox.show_info("Order marked as collected!", "Success")
                self.collection_receipt_var.set("")
                if hasattr(self, 'order_window') and self.order_window.winfo_exists():
                    self.load_orders()
            conn.close()
        except Exception as e:
            Messagebox.show_error(f"Error updating order: {e}", "Database Error")

    # --- THIS IS THE CORRECTED INVOICE FUNCTION ---
    def generate_invoice(self):
        """Generate an HTML invoice for a given order from input field or treeview selection."""
        receipt_number = None

        # Priority 1: Check the manual input field first.
        if self.collection_receipt_var.get().strip():
            receipt_number = self.collection_receipt_var.get().strip()
        # Priority 2: If the input is empty, check the treeview selection.
        elif hasattr(self, 'tree') and self.tree.selection():
            try:
                selection = self.tree.selection()
                if selection:
                    item = self.tree.item(selection[0])
                    receipt_number = item['values'][1]  # Index 1 is the Receipt Number
            except (IndexError, AttributeError):
                pass # Selection might be invalid, proceed to check receipt_number

        # If no receipt number could be found from either source, show a warning and exit.
        if not receipt_number:
            Messagebox.show_warning("Please select an order from the list or enter a receipt number to generate an invoice.", "No Selection")
            return

        # Now, use the obtained receipt_number to get all data directly from the database.
        try:
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor(dictionary=True)  # Fetch as a dictionary for easy access
            cursor.execute("SELECT * FROM orders WHERE receipt_number = %s", (receipt_number,))
            order = cursor.fetchone()
            conn.close()
        except Exception as e:
            Messagebox.show_error(f"Error fetching invoice data: {e}", "Database Error")
            return

        if not order:
            Messagebox.show_error(f"Order '{receipt_number}' not found.", "Not Found")
            return
            
        if not order.get('collection_date'):
            Messagebox.show_warning("This order has not been collected yet. Cannot generate invoice.", "Order Not Collected")
            return

        # Costs calculation
        regular_cost = float(order['regular_clothes_kg']) * self.PRICING['regular_clothes']
        blanket_cost = float(order['blankets_kg']) * self.PRICING['blankets']
        white_cost = float(order['white_clothes_pieces']) * self.PRICING['white_clothes']

        # HTML invoice template
        html_invoice = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Invoice - {order['receipt_number']}</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 20px; color: #333; }}
        .invoice-box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #eee; box-shadow: 0 0 10px rgba(0, 0, 0, 0.15); font-size: 16px; line-height: 24px; }}
        .invoice-box table {{ width: 100%; line-height: inherit; text-align: left; border-collapse: collapse; }}
        .invoice-box table td {{ padding: 5px; vertical-align: top; }}
        .invoice-box table tr.top table td {{ padding-bottom: 20px; }}
        .invoice-box table tr.heading td {{ background: #eee; border-bottom: 1px solid #ddd; font-weight: bold; }}
        .invoice-box table tr.item td {{ border-bottom: 1px solid #eee; }}
        .invoice-box table tr.total td:nth-child(2) {{ border-top: 2px solid #eee; font-weight: bold; text-align: right; }}
        .header h1 {{ margin: 0; font-size: 28px; color: #0d6efd; }}
    </style>
</head>
<body>
    <div class="invoice-box">
        <table>
            <tr class="top">
                <td colspan="4">
                    <table>
                        <tr>
                            <td class="header"><h1>Express Wash</h1></td>
                            <td>
                                Invoice #: {order['receipt_number']}<br>
                                Created: {order['created_at'].strftime('%Y-%m-%d')}<br>
                                Collected: {order['collection_date'].strftime('%Y-%m-%d %H:%M')}
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr class="information">
                <td colspan="4">
                    <table>
                        <tr>
                            <td>Customer: {order['customer_name']}<br>{order['mobile_number'] or 'N/A'}</td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr class="heading"><td>Service</td><td style="text-align:center;">Quantity</td><td style="text-align:center;">Rate</td><td style="text-align:right;">Price</td></tr>
            <tr class="item"><td>Regular Clothes</td><td style="text-align:center;">{order['regular_clothes_kg']} kg</td><td style="text-align:center;">₹{self.PRICING['regular_clothes']:.2f}</td><td style="text-align:right;">₹{regular_cost:.2f}</td></tr>
            <tr class="item"><td>Blankets/Bedsheets</td><td style="text-align:center;">{order['blankets_kg']} kg</td><td style="text-align:center;">₹{self.PRICING['blankets']:.2f}</td><td style="text-align:right;">₹{blanket_cost:.2f}</td></tr>
            <tr class="item"><td>White Clothes</td><td style="text-align:center;">{order['white_clothes_pieces']} pcs</td><td style="text-align:center;">₹{self.PRICING['white_clothes']:.2f}</td><td style="text-align:right;">₹{white_cost:.2f}</td></tr>
            <tr class="total"><td colspan="3"></td><td>Total: ₹{order['total_amount']:.2f}</td></tr>
        </table>
    </div>
</body>
</html>
"""
        # Save and open the invoice
        invoice_filename = f"invoice_{order['receipt_number']}.html"
        with open(invoice_filename, 'w', encoding='utf-8') as f:
            f.write(html_invoice)
        
        webbrowser.open(f"file://{os.path.abspath(invoice_filename)}")

    # --- THIS IS THE CORRECTED REPORTS/GRAPHS SECTION ---
    def show_reports(self):
        """Show a comprehensive reports window with charts."""
        reports_window = tk.Toplevel(self.root)
        reports_window.title("📊 Business Reports")
        reports_window.geometry("1250x850") # Adjusted size
        reports_window.transient(self.root)
        reports_window.grab_set()

        try:
            conn = mysql.connector.connect(**self.DB_CONFIG)
            df = pd.read_sql("SELECT * FROM orders", conn)
            conn.close()
            if not df.empty:
                df['order_date'] = pd.to_datetime(df['order_date'])
        except Exception as e:
            Messagebox.show_error(f"Could not load report data: {e}", "Report Error", parent=reports_window)
            reports_window.destroy()
            return
        
        if df.empty:
            Messagebox.show_warning("No data available to generate reports.", "No Data", parent=reports_window)
            reports_window.destroy()
            return

        notebook = ttk.Notebook(reports_window, bootstyle="primary")
        notebook.pack(fill=BOTH, expand=True, padx=15, pady=15)

        # Tab 1: Revenue Over Time
        revenue_tab = ttk.Frame(notebook, padding=10)
        notebook.add(revenue_tab, text="💰 Revenue Trends")
        self.create_revenue_trend_chart(revenue_tab, df)

        # Tab 2: Service Popularity
        service_tab = ttk.Frame(notebook, padding=10)
        notebook.add(service_tab, text="🧺 Service Popularity")
        self.create_service_popularity_chart(service_tab, df)
        
        # Tab 3: Order Status
        status_tab = ttk.Frame(notebook, padding=10)
        notebook.add(status_tab, text="📋 Order Status")
        self.create_order_status_chart(status_tab, df)

    def create_revenue_trend_chart(self, parent, df):
        """Creates and embeds a revenue trend chart."""
        fig, ax = plt.subplots(figsize=(12, 6))
        daily_revenue = df.groupby(df['order_date'].dt.to_period('D'))['total_amount'].sum()
        
        if not daily_revenue.empty:
            daily_revenue.plot(kind='line', ax=ax, marker='o', linestyle='-', color=ttk.Style().colors.primary)
            ax.set_title("Daily Revenue Trend", fontsize=16, weight='bold')
            ax.set_ylabel("Total Revenue (₹)", fontsize=12)
            ax.set_xlabel("Date", fontsize=12)
            ax.grid(True, which='both', linestyle='--', linewidth=0.5)
            fig.autofmt_xdate() # Auto-formats the x-axis labels (like rotation)
            plt.tight_layout() # Adjust plot to fit into figure area
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True, padx=10, pady=10)

    def create_service_popularity_chart(self, parent, df):
        """Creates a pie chart for service popularity based on revenue."""
        fig, ax = plt.subplots(figsize=(8, 8))
        
        revenue_regular = (df['regular_clothes_kg'] * self.PRICING['regular_clothes']).sum()
        revenue_blankets = (df['blankets_kg'] * self.PRICING['blankets']).sum()
        revenue_white = (df['white_clothes_pieces'] * self.PRICING['white_clothes']).sum()
        
        labels = ['Regular Clothes', 'Blankets/Bedsheets', 'White Clothes']
        revenues = [revenue_regular, revenue_blankets, revenue_white]
        colors = [ttk.Style().colors.info, ttk.Style().colors.success, ttk.Style().colors.warning]
        
        ax.pie(revenues, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors,
               wedgeprops=dict(width=0.4, edgecolor='w'))
        ax.set_title("Revenue by Service Type", fontsize=16, weight='bold')
        ax.axis('equal')
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True, padx=10, pady=10)
        
    def create_order_status_chart(self, parent, df):
        """Creates a bar chart showing pending vs. collected orders."""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        collected_count = df['collection_date'].notna().sum()
        pending_count = df['collection_date'].isna().sum()
        
        status = ['Collected', 'Pending']
        counts = [collected_count, pending_count]
        colors = [ttk.Style().colors.success, ttk.Style().colors.danger]
        
        bars = ax.bar(status, counts, color=colors)
        ax.bar_label(bars)
        
        ax.set_title("Order Status", fontsize=16, weight='bold')
        ax.set_ylabel("Number of Orders", fontsize=12)
        ax.grid(axis='y', linestyle='--', linewidth=0.5)
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True, padx=10, pady=10)


if __name__ == "__main__":
    # Use ttkbootstrap for modern styling
    # Available themes: litera, cosmo, flatly, journal, lumen, minty, pulse, sandstone,
    # united, yeti, darkly, superhero, solar, cyborg
    root = ttk.Window(themename="litera")
    app = ExpressWashAppModern(root)
    root.mainloop()