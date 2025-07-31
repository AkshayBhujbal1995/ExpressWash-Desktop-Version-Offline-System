#!/usr/bin/env python3
"""
Express Wash - Professional Tkinter Desktop Application
Simple GUI with CRUD operations, collection tracking, and professional design
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
import pandas as pd
from datetime import datetime, date, timedelta
import json
import os
from PIL import Image, ImageTk
import threading
import webbrowser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ExpressWashApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧺 Express Wash - Smart Laundry Billing System")
        self.root.geometry("1400x900")
        self.root.configure(bg='white')
        
        # Database configuration
        self.DB_CONFIG = {
            'host': 'localhost',
            'user': 'root',
            'password': '16021995',
            'database': 'express_wash'
        }
        
        # Pricing configuration
        self.PRICING = {
            'regular_clothes': 50,  # ₹50/kg
            'blankets': 100,        # ₹100/kg
            'white_clothes': 40     # ₹40/piece
        }
        
        # Initialize database
        self.init_database()
        
        # Create main interface
        self.create_widgets()
        
        # Load initial data
        self.load_orders()
        
    def init_database(self):
        """Initialize MySQL database connection with enhanced schema"""
        try:
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor()
            
            # Create enhanced orders table
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
            
            # Add collection_date column if upgrading existing database
            try:
                cursor.execute('ALTER TABLE orders ADD COLUMN collection_date DATETIME NULL')
            except Exception:
                pass
                
            conn.commit()
            conn.close()
            print("✅ Database initialized successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
    
    def create_widgets(self):
        """Create the main GUI widgets with simple design"""
        # Title frame
        title_frame = tk.Frame(self.root, bg='#1e40af', height=80)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🧺 Express Wash - Smart Laundry Billing System", 
                              font=('Arial', 20, 'bold'), fg='white', bg='#1e40af')
        title_label.pack(pady=20)
        
        # Main container
        main_container = tk.Frame(self.root, bg='white')
        main_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Order Form (now takes full width)
        self.create_order_form(main_container)
        
        # Add button to open order list window
        self.create_order_list_button(main_container)
        
    def create_order_form(self, parent):
        """Create the order form panel with simple design"""
        # Main form container - made larger
        form_frame = tk.LabelFrame(parent, text="📝 New Order", 
                                  font=('Arial', 16, 'bold'),
                                  bg='white', fg='#1e3a8a',
                                  padx=15, pady=15)
        form_frame.pack(fill='both', expand=True)
        
        # Create a main content frame with left and right sections
        main_content = tk.Frame(form_frame, bg='white')
        main_content.pack(fill='both', expand=True)
        
        # Left section for form fields
        self.left_section = tk.Frame(main_content, bg='white')
        self.left_section.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Right section for buttons and actions
        self.right_section = tk.Frame(main_content, bg='white')
        self.right_section.pack(side='right', fill='y', padx=(10, 0))
        
        # Create a scrollable canvas for the form content
        canvas = tk.Canvas(self.left_section, bg='white')
        scrollbar = ttk.Scrollbar(self.left_section, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Customer Information Section - made smaller
        customer_frame = tk.LabelFrame(scrollable_frame, text="👤 Customer Information", 
                                      font=('Arial', 12, 'bold'),
                                      bg='white', fg='#1e3a8a',
                                      padx=8, pady=8)
        customer_frame.pack(fill='x', pady=(0, 10))
        
        # Create a grid layout for customer information to make it more compact
        customer_frame.columnconfigure(0, weight=1)
        customer_frame.columnconfigure(1, weight=1)
        
        # More compact layout for customer information with 2 columns
        # Receipt Number and Customer Name in first row
        tk.Label(customer_frame, text="Receipt Number *", 
                font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.receipt_number_var = tk.StringVar()
        self.receipt_number_entry = tk.Entry(customer_frame, textvariable=self.receipt_number_var,
                                            font=('Arial', 11), width=20)
        self.receipt_number_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        tk.Label(customer_frame, text="Customer Name *", 
                font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=2, sticky='w', pady=5, padx=5)
        self.customer_name_var = tk.StringVar()
        self.customer_name_entry = tk.Entry(customer_frame, textvariable=self.customer_name_var,
                                           font=('Arial', 11), width=25)
        self.customer_name_entry.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        
        # Mobile Number and Order Date in second row
        tk.Label(customer_frame, text="Mobile Number", 
                font=('Arial', 10, 'bold'), bg='white').grid(row=1, column=0, sticky='w', pady=5, padx=5)
        self.mobile_var = tk.StringVar()
        self.mobile_entry = tk.Entry(customer_frame, textvariable=self.mobile_var,
                                    font=('Arial', 11), width=20)
        self.mobile_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        tk.Label(customer_frame, text="Order Date *", 
                font=('Arial', 10, 'bold'), bg='white').grid(row=1, column=2, sticky='w', pady=5, padx=5)
        self.order_date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        self.order_date_entry = tk.Entry(customer_frame, textvariable=self.order_date_var,
                                        font=('Arial', 11), width=20)
        self.order_date_entry.grid(row=1, column=3, padx=5, pady=5, sticky='w')
        
        # Service Details Section - more compact layout
        service_frame = tk.LabelFrame(scrollable_frame, text="🧺 Service Details", 
                                     font=('Arial', 12, 'bold'),
                                     bg='white', fg='#1e3a8a',
                                     padx=8, pady=8)
        service_frame.pack(fill='x', pady=(0, 10))
        
        # Configure columns for better layout
        service_frame.columnconfigure(0, weight=1)
        service_frame.columnconfigure(1, weight=1)
        service_frame.columnconfigure(2, weight=1)
        service_frame.columnconfigure(3, weight=1)
        
        # Regular Clothes and Blankets in first row
        tk.Label(service_frame, text="Regular Clothes (kg):", 
                font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', pady=3, padx=3)
        self.regular_clothes_var = tk.StringVar()
        self.regular_clothes_entry = tk.Entry(service_frame, textvariable=self.regular_clothes_var,
                                             font=('Arial', 10), width=8)
        self.regular_clothes_entry.grid(row=0, column=1, padx=3, pady=3, sticky='w')
        tk.Label(service_frame, text="₹50/kg", 
                font=('Arial', 9), bg='white', fg='#059669').grid(row=0, column=1, padx=(60, 0), pady=3, sticky='w')
        
        tk.Label(service_frame, text="Blankets/Bedsheets (kg):", 
                font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=2, sticky='w', pady=3, padx=3)
        self.blankets_var = tk.StringVar()
        self.blankets_entry = tk.Entry(service_frame, textvariable=self.blankets_var,
                                      font=('Arial', 10), width=8)
        self.blankets_entry.grid(row=0, column=3, padx=3, pady=3, sticky='w')
        tk.Label(service_frame, text="₹100/kg", 
                font=('Arial', 9), bg='white', fg='#d97706').grid(row=0, column=3, padx=(60, 0), pady=3, sticky='w')
        
        # White Clothes in second row
        tk.Label(service_frame, text="White Clothes (pieces):", 
                font=('Arial', 10, 'bold'), bg='white').grid(row=1, column=0, sticky='w', pady=3, padx=3)
        self.white_clothes_var = tk.StringVar()
        self.white_clothes_entry = tk.Entry(service_frame, textvariable=self.white_clothes_var,
                                           font=('Arial', 10), width=8)
        self.white_clothes_entry.grid(row=1, column=1, padx=3, pady=3, sticky='w')
        tk.Label(service_frame, text="₹40/piece", 
                font=('Arial', 9), bg='white', fg='#7c3aed').grid(row=1, column=1, padx=(60, 0), pady=3, sticky='w')
        
        # Bill Summary Section - more compact
        bill_frame = tk.LabelFrame(scrollable_frame, text="💰 Bill Summary", 
                                  font=('Arial', 12, 'bold'),
                                  bg='white', fg='#1e3a8a',
                                  padx=8, pady=8)
        bill_frame.pack(fill='x', pady=(0, 10))
        
        self.bill_text = tk.Text(bill_frame, height=4, width=40, 
                                 font=('Courier', 10), bg='#f8fafc', fg='#374151')
        self.bill_text.pack(fill='x')
        
        # Quick Actions at the bottom
        quick_actions_frame = tk.LabelFrame(scrollable_frame, text="⚡ Quick Actions", 
                                         font=('Arial', 12, 'bold'),
                                         bg='white', fg='#1e3a8a',
                                         padx=8, pady=8)
        quick_actions_frame.pack(fill='x', pady=(0, 10))
        
        # Create a grid for quick action buttons
        quick_actions_frame.columnconfigure(0, weight=1)
        quick_actions_frame.columnconfigure(1, weight=1)
        quick_actions_frame.columnconfigure(2, weight=1)
        
        # Calculate Bill Button
        calc_button_bottom = tk.Button(quick_actions_frame, text="🧮 Calculate Bill", 
                                     command=self.calculate_bill,
                                     font=('Arial', 11, 'bold'),
                                     bg='#3b82f6', fg='white',
                                     relief='raised', bd=2,
                                     padx=15, pady=8)
        calc_button_bottom.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        
        # Save Order Button
        save_button_bottom = tk.Button(quick_actions_frame, text="💾 Save Order", 
                                     command=self.save_order,
                                     font=('Arial', 11, 'bold'),
                                     bg='#10b981', fg='white',
                                     relief='raised', bd=2,
                                     padx=15, pady=8)
        save_button_bottom.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Clear Form Button
        clear_button_bottom = tk.Button(quick_actions_frame, text="🗑️ Clear Form", 
                                      command=self.clear_form,
                                      font=('Arial', 11, 'bold'),
                                      bg='#ef4444', fg='white',
                                      relief='raised', bd=2,
                                      padx=15, pady=8)
        clear_button_bottom.grid(row=0, column=2, padx=5, pady=5, sticky='ew')
        
        # Removed quick actions from right side panel as requested
        
        # Collection Tracking Section - moved to right panel
        collection_frame = tk.LabelFrame(self.right_section, text="📦 Collection Tracking", 
                                        font=('Arial', 12, 'bold'),
                                        bg='white', fg='#1e3a8a',
                                        padx=8, pady=8)
        collection_frame.pack(fill='x', pady=(0, 10))
        
        # Receipt Number for Collection
        tk.Label(collection_frame, text="Receipt Number:", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor='w', pady=(5, 2))
        self.collection_receipt_var = tk.StringVar()
        self.collection_receipt_entry = tk.Entry(collection_frame, textvariable=self.collection_receipt_var,
                                                font=('Arial', 10), width=20)
        self.collection_receipt_entry.pack(fill='x', pady=(0, 5))
        
        # Collection action buttons - vertical layout
        collect_button = tk.Button(collection_frame, text="✅ Mark as Collected", 
                                  command=self.mark_as_collected,
                                  font=('Arial', 10, 'bold'),
                                  bg='#059669', fg='white',
                                  relief='raised', bd=2,
                                  padx=12, pady=4)
        collect_button.pack(fill='x', pady=(0, 5))
        
        invoice_button = tk.Button(collection_frame, text="📄 Generate Invoice", 
                                  command=self.generate_invoice,
                                  font=('Arial', 10, 'bold'),
                                  bg='#7c3aed', fg='white',
                                  relief='raised', bd=2,
                                  padx=12, pady=4)
        invoice_button.pack(fill='x', pady=(0, 5))
        
        # Reports button removed from main page as it's now available in the order list window
        
    def create_order_list_button(self, parent):
        """Create button to open order list window - moved to right panel"""
        # Create a frame in the right section for the order list button
        button_frame = tk.LabelFrame(self.right_section, text="📋 Order Management", 
                                    font=('Arial', 12, 'bold'),
                                    bg='white', fg='#1e3a8a',
                                    padx=8, pady=8)
        button_frame.pack(fill='x', pady=(0, 10))
        
        # Open Order List Button
        open_list_button = tk.Button(button_frame, text="VIEW ALL ORDERS", 
                                    command=self.open_order_list_window,
                                    font=('Arial', 12, 'bold'),
                                    bg='#1e40af', fg='white',
                                    relief='raised', bd=2,
                                    padx=15, pady=8)
        open_list_button.pack(fill='x', pady=5)
        
    def open_order_list_window(self):
        """Open a new window with order list and management tools"""
        # Create new window
        self.order_window = tk.Toplevel(self.root)
        self.order_window.title("📋 Express Wash - Order List & Management")
        self.order_window.geometry("1300x800")  # Increased window size
        self.order_window.configure(bg='white')
        
        # Make window modal (user must close it to return to main window)
        self.order_window.transient(self.root)
        self.order_window.grab_set()
        
        # Create order history in the new window
        self.create_order_history(self.order_window)
        
        # Load orders data into the new window
        self.load_orders()
        

        
    def create_order_history(self, parent):
        """Create the order history panel with simple design"""
        # Main history container
        history_frame = tk.LabelFrame(parent, text="📊 Order History & Management", 
                                     font=('Arial', 14, 'bold'),
                                     bg='white', fg='#1e3a8a',
                                     padx=15, pady=15)
        history_frame.pack(fill='both', expand=True)
        
        # Search and Filter Section
        search_frame = tk.LabelFrame(history_frame, text="🔍 Search Orders", 
                                    font=('Arial', 12, 'bold'),
                                    bg='white', fg='#1e3a8a',
                                    padx=10, pady=10)
        search_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(search_frame, text="Search by Receipt Number or Customer Name:", 
                font=('Arial', 10, 'bold'), bg='white').pack(anchor='w')
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                                    font=('Arial', 10), width=40)
        self.search_entry.pack(fill='x', pady=(5, 0))
        self.search_var.trace('w', self.filter_orders)
        
        # CRUD Actions Section
        crud_frame = tk.LabelFrame(history_frame, text="⚡ Quick Actions", 
                                  font=('Arial', 12, 'bold'),
                                  bg='white', fg='#1e3a8a',
                                  padx=10, pady=10)
        crud_frame.pack(fill='x', pady=(0, 15))
        
        # Action buttons
        self.edit_button = tk.Button(crud_frame, text="✏️ EDIT ORDER", 
                                    command=self.edit_order,
                                    font=('Arial', 10, 'bold'),
                                    bg='#f59e0b', fg='white',
                                    relief='raised', bd=2,
                                    padx=15, pady=5)
        self.edit_button.pack(side='left', padx=(0, 10))
        
        self.delete_button = tk.Button(crud_frame, text="🗑️ DELETE", 
                                      command=self.delete_order,
                                      font=('Arial', 10, 'bold'),
                                      bg='#ef4444', fg='white',
                                      relief='raised', bd=2,
                                      padx=15, pady=5)
        self.delete_button.pack(side='left', padx=(0, 10))
        
        self.refresh_button = tk.Button(crud_frame, text="🔄 REFRESH", 
                                       command=self.load_orders,
                                       font=('Arial', 10, 'bold'),
                                       bg='#3b82f6', fg='white',
                                       relief='raised', bd=2,
                                       padx=15, pady=5)
        self.refresh_button.pack(side='left', padx=(0, 10))
        
        self.export_button = tk.Button(crud_frame, text="📥 EXPORT CSV", 
                                      command=self.export_data,
                                      font=('Arial', 10, 'bold'),
                                      bg='#8b5cf6', fg='white',
                                      relief='raised', bd=2,
                                      padx=15, pady=5)
        self.export_button.pack(side='left', padx=(0, 10))
        
        # Add Report Button with distinctive visualization
        self.report_button = tk.Button(crud_frame, text="📊 REPORTS", 
                                     command=self.show_reports,
                                     font=('Arial', 10, 'bold'),
                                     bg='#f59e0b', fg='white',  # Amber color for distinction
                                     relief='raised', bd=2,
                                     padx=15, pady=5)
        self.report_button.pack(side='left')
        
        # Add a tooltip/hint for the report button
        report_hint = tk.Label(crud_frame, text="View business analytics", 
                              font=('Arial', 8), bg='white', fg='#6b7280')
        report_hint.pack(side='left', padx=5)
        
        # Orders Table Section
        table_frame = tk.LabelFrame(history_frame, text="📋 Orders List", 
                                   font=('Arial', 12, 'bold'),
                                   bg='white', fg='#1e3a8a',
                                   padx=10, pady=10)
        table_frame.pack(fill='both', expand=True)
        
        # Create Treeview
        columns = ('ID', 'Receipt', 'Customer', 'Mobile', 'Date', 'Collection', 'Total', 'Created')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        self.tree.heading('ID', text='ID')
        self.tree.heading('Receipt', text='Receipt Number')
        self.tree.heading('Customer', text='Customer Name')
        self.tree.heading('Mobile', text='Mobile')
        self.tree.heading('Date', text='Order Date')
        self.tree.heading('Collection', text='Collection Date')
        self.tree.heading('Total', text='Total (₹)')
        self.tree.heading('Created', text='Created At')
        
        # Define columns
        self.tree.column('ID', width=50)
        self.tree.column('Receipt', width=120)
        self.tree.column('Customer', width=120)
        self.tree.column('Mobile', width=100)
        self.tree.column('Date', width=100)
        self.tree.column('Collection', width=120)
        self.tree.column('Total', width=80)
        self.tree.column('Created', width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

    def generate_receipt_number(self):
        """Generate a unique, sequential receipt number for today"""
        today_str = date.today().strftime('%Y%m%d')
        prefix = f"RW-{today_str}-"
        conn = mysql.connector.connect(**self.DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT receipt_number FROM orders WHERE receipt_number LIKE %s ORDER BY id DESC LIMIT 1", (prefix+'%',))
        last = cursor.fetchone()
        conn.close()
        if last and last[0]:
            last_num = int(last[0].split('-')[-1])
            next_num = last_num + 1
        else:
            next_num = 1
        return f"{prefix}{next_num:04d}"
    
    def calculate_bill(self):
        """Calculate and display bill"""
        try:
            regular_kg = float(self.regular_clothes_var.get() or 0)
            blankets_kg = float(self.blankets_var.get() or 0)
            white_pieces = int(self.white_clothes_var.get() or 0)
            regular_cost = regular_kg * self.PRICING['regular_clothes']
            blankets_cost = blankets_kg * self.PRICING['blankets']
            white_cost = white_pieces * self.PRICING['white_clothes']
            total = regular_cost + blankets_cost + white_cost
            self.bill_text.delete(1.0, tk.END)
            lines = ["🧺 Express Wash - Bill Summary\n"]
            # Only show nonzero services
            if regular_kg > 0:
                lines.append(f"Regular Clothes: {regular_kg}kg × ₹{self.PRICING['regular_clothes']} = ₹{regular_cost:.2f}")
            if blankets_kg > 0:
                lines.append(f"Blankets/Bedsheets: {blankets_kg}kg × ₹{self.PRICING['blankets']} = ₹{blankets_cost:.2f}")
            if white_pieces > 0:
                lines.append(f"White Clothes: {white_pieces} pieces × ₹{self.PRICING['white_clothes']} = ₹{white_cost:.2f}")
            lines.append("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
            lines.append(f"💵 TOTAL AMOUNT: ₹{total:.2f}\n")
            lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            self.bill_text.insert(1.0, '\n'.join(lines))
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for services.")
        except Exception as e:
            messagebox.showerror("Error", f"Error calculating bill: {str(e)}")
    
    def save_order(self):
        """Save order to database"""
        try:
            receipt_number = self.receipt_number_var.get().strip()
            if not receipt_number:
                messagebox.showerror("Error", "Receipt number cannot be empty!")
                return
            customer_name = self.customer_name_var.get().strip()
            mobile_number = self.mobile_var.get().strip()
            order_date = self.order_date_var.get().strip()
            if not customer_name or not order_date:
                messagebox.showerror("Error", "Please fill in customer name and order date!")
                return
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
            ''', (receipt_number, customer_name, mobile_number, order_date, regular_kg, blankets_kg, white_pieces, total))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"✅ Order saved successfully!\nReceipt Number: {receipt_number}")
            self.clear_form()
            self.load_orders()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for services.")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving order: {str(e)}")
    
    def clear_form(self):
        """Clear the order form"""
        self.receipt_number_var.set("")
        self.customer_name_var.set("")
        self.mobile_var.set("")
        self.order_date_var.set(date.today().strftime('%Y-%m-%d'))
        self.regular_clothes_var.set("")
        self.blankets_var.set("")
        self.white_clothes_var.set("")
        self.bill_text.delete(1.0, tk.END)
    
    def load_orders(self):
        """Load orders from database"""
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, receipt_number, customer_name, mobile_number, order_date, 
                       regular_clothes_kg, blankets_kg, white_clothes_pieces, total_amount, 
                       collection_date, created_at
                FROM orders 
                ORDER BY created_at DESC
            ''')
            orders = cursor.fetchall()
            
            if not orders:
                # If no records found, display a message in the tree view
                self.tree.insert('', 'end', values=(
                    "", "No records found", "Please add new orders", "", "", "", "", ""
                ))
            else:
                # Display the orders
                for order in orders:
                    self.tree.insert('', 'end', values=(
                        order[0],  # ID
                        order[1],  # Receipt Number
                        order[2],  # Customer Name
                        order[3] or "",  # Mobile
                        order[4],  # Order Date
                        order[9] if order[9] else "Not Collected",  # Collection Date
                        f"₹{order[8]:.2f}",  # Total
                        order[10].strftime('%Y-%m-%d %H:%M') if order[10] else ""  # Created
                    ))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error loading orders: {str(e)}")
    
    def filter_orders(self, *args):
        """Filter orders based on search term"""
        search_term = self.search_var.get().strip()
        
        # Clear current display
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not search_term:
            # If no search term, show all orders
            self.load_orders()
            return
        
        try:
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor()
            
            # Search by receipt number or customer name
            cursor.execute('''
                SELECT id, receipt_number, customer_name, mobile_number, order_date, 
                       regular_clothes_kg, blankets_kg, white_clothes_pieces, total_amount, 
                       collection_date, created_at
                FROM orders 
                WHERE receipt_number LIKE %s OR customer_name LIKE %s
                ORDER BY created_at DESC
            ''', (f'%{search_term}%', f'%{search_term}%'))
            
            orders = cursor.fetchall()
            conn.close()
            
            # Display filtered results
            if not orders:
                # If no matching records found, display a message
                self.tree.insert('', 'end', values=(
                    "", "No matching records", f"No results for '{search_term}'", "", "", "", "", ""
                ))
            else:
                # Display the matching orders
                for order in orders:
                    self.tree.insert('', 'end', values=(
                        order[0],  # ID
                        order[1],  # Receipt Number
                        order[2],  # Customer Name
                        order[3] or "",  # Mobile
                        order[4],  # Order Date
                        order[9] if order[9] else "Not Collected",  # Collection Date
                        f"₹{order[8]:.2f}",  # Total
                        order[10].strftime('%Y-%m-%d %H:%M') if order[10] else ""  # Created
                    ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error searching orders: {str(e)}")
    
    def on_select(self, event):
        """Handle order selection"""
        selection = self.tree.selection()
        if selection:
            # Enable edit and delete buttons
            self.edit_button.config(state='normal')
            self.delete_button.config(state='normal')
        else:
            # Disable edit and delete buttons
            self.edit_button.config(state='disabled')
            self.delete_button.config(state='disabled')
    
    def edit_order(self):
        """Edit selected order"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an order to edit!")
            return
        
        # Get selected order ID from tree
        item = self.tree.item(selection[0])
        order_id = item['values'][0]  # ID is the first column
        
        # Fetch complete order data from database
        try:
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, receipt_number, customer_name, mobile_number, order_date, 
                       regular_clothes_kg, blankets_kg, white_clothes_pieces, total_amount, 
                       collection_date, created_at
                FROM orders 
                WHERE id = %s
            ''', (order_id,))
            order_data = cursor.fetchone()
            conn.close()
            
            if order_data:
                # Create edit window with complete database data
                self.create_edit_window(order_data)
            else:
                messagebox.showerror("Error", "Order not found in database!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching order data: {str(e)}")
    
    def create_edit_window(self, order_data):
        """Create edit order window"""
        edit_window = tk.Toplevel(self.root)
        edit_window.title("✏️ Edit Order")
        edit_window.geometry("600x800")
        edit_window.configure(bg='#f0f8ff')
        # Make sure this window stays on top and grabs focus
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Order ID
        order_id = order_data[0]
        
        # Create scrollable frame
        canvas = tk.Canvas(edit_window, bg='#f0f8ff', highlightthickness=0)
        scrollbar = ttk.Scrollbar(edit_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f8ff')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create form similar to main form
        form_frame = tk.LabelFrame(scrollable_frame, text="Edit Order Details", 
                                  font=('Arial', 12, 'bold'),
                                  bg='white', fg='#1e3a8a',
                                  padx=15, pady=15)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Receipt Number
        tk.Label(form_frame, text="Receipt Number:", font=('Arial', 10, 'bold'), bg='white').grid(row=0, column=0, sticky='w', pady=5)
        receipt_number_var = tk.StringVar(value=order_data[1])
        receipt_number_entry = tk.Entry(form_frame, textvariable=receipt_number_var, font=('Arial', 10), width=25, state='normal')
        receipt_number_entry.grid(row=0, column=1, padx=(10, 0), pady=5, sticky='w')
        
        # Customer Name
        tk.Label(form_frame, text="Customer Name:", font=('Arial', 10, 'bold'), bg='white').grid(row=1, column=0, sticky='w', pady=5)
        customer_name_var = tk.StringVar(value=order_data[2])
        customer_name_entry = tk.Entry(form_frame, textvariable=customer_name_var, font=('Arial', 10), width=25, state='normal')
        customer_name_entry.grid(row=1, column=1, padx=(10, 0), pady=5, sticky='w')
        
        tk.Label(form_frame, text="Mobile Number:", font=('Arial', 10, 'bold'), bg='white').grid(row=2, column=0, sticky='w', pady=5)
        mobile_var = tk.StringVar(value=order_data[3] or "")
        mobile_entry = tk.Entry(form_frame, textvariable=mobile_var, font=('Arial', 10), width=25, state='normal')
        mobile_entry.grid(row=2, column=1, padx=(10, 0), pady=5, sticky='w')
        
        tk.Label(form_frame, text="Order Date:", font=('Arial', 10, 'bold'), bg='white').grid(row=3, column=0, sticky='w', pady=5)
        order_date_var = tk.StringVar(value=order_data[4])
        order_date_entry = tk.Entry(form_frame, textvariable=order_date_var, font=('Arial', 10), width=25, state='normal')
        order_date_entry.grid(row=3, column=1, padx=(10, 0), pady=5, sticky='w')
        
        # Service Details
        tk.Label(form_frame, text="Regular Clothes (kg):", font=('Arial', 10, 'bold'), bg='white').grid(row=4, column=0, sticky='w', pady=5)
        regular_kg_var = tk.DoubleVar(value=float(order_data[5]))
        regular_kg_entry = tk.Entry(form_frame, textvariable=regular_kg_var, font=('Arial', 10), width=15, state='normal')
        regular_kg_entry.grid(row=4, column=1, padx=(10, 0), pady=5, sticky='w')
        
        tk.Label(form_frame, text="Blankets (kg):", font=('Arial', 10, 'bold'), bg='white').grid(row=5, column=0, sticky='w', pady=5)
        blankets_kg_var = tk.DoubleVar(value=float(order_data[6]))
        blankets_kg_entry = tk.Entry(form_frame, textvariable=blankets_kg_var, font=('Arial', 10), width=15, state='normal')
        blankets_kg_entry.grid(row=5, column=1, padx=(10, 0), pady=5, sticky='w')
        
        tk.Label(form_frame, text="White Clothes (pieces):", font=('Arial', 10, 'bold'), bg='white').grid(row=6, column=0, sticky='w', pady=5)
        white_pieces_var = tk.IntVar(value=int(order_data[7]))
        white_pieces_entry = tk.Entry(form_frame, textvariable=white_pieces_var, font=('Arial', 10), width=15, state='normal')
        white_pieces_entry.grid(row=6, column=1, padx=(10, 0), pady=5, sticky='w')
        
        # Set focus to the first entry field
        receipt_number_entry.focus_set()
        
        # Current Total Display
        current_total = order_data[8] if len(order_data) > 8 else 0
        tk.Label(form_frame, text="Current Total:", font=('Arial', 10, 'bold'), bg='white').grid(row=7, column=0, sticky='w', pady=5)
        tk.Label(form_frame, text=f"₹{current_total:.2f}", font=('Arial', 10, 'bold'), bg='white', fg='#059669').grid(row=7, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Button Frame
        button_frame = tk.Frame(form_frame, bg='white')
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        # Update button
        def update_order():
            try:
                # Validate inputs
                if not receipt_number_var.get().strip():
                    messagebox.showerror("Validation Error", "❌ Receipt number is required!")
                    return
                
                if not customer_name_var.get().strip():
                    messagebox.showerror("Validation Error", "❌ Customer name is required!")
                    return
                
                # Validate numeric inputs
                try:
                    regular_kg = regular_kg_var.get()
                    blankets_kg = blankets_kg_var.get()
                    white_pieces = white_pieces_var.get()
                    
                    if regular_kg < 0 or blankets_kg < 0 or white_pieces < 0:
                        messagebox.showerror("Validation Error", "❌ Quantities cannot be negative!")
                        return
                        
                except tk.TclError:
                    messagebox.showerror("Validation Error", "❌ Please enter valid numbers for quantities!")
                    return
                
                # Calculate new total
                total = (regular_kg * self.PRICING['regular_clothes'] + 
                        blankets_kg * self.PRICING['blankets'] + 
                        white_pieces * self.PRICING['white_clothes'])
                
                # Show confirmation dialog
                confirmation = messagebox.askyesno("Confirm Update", 
                    f"Are you sure you want to update this order?\n\n"
                    f"Receipt: {receipt_number_var.get()}\n"
                    f"Customer: {customer_name_var.get()}\n"
                    f"New Total: ₹{total:.2f}")
                
                if not confirmation:
                    return
                
                # Update database
                conn = mysql.connector.connect(**self.DB_CONFIG)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE orders 
                    SET receipt_number = %s, customer_name = %s, mobile_number = %s, order_date = %s,
                        regular_clothes_kg = %s, blankets_kg = %s, white_clothes_pieces = %s,
                        total_amount = %s
                    WHERE id = %s
                ''', (receipt_number_var.get(), customer_name_var.get(), mobile_var.get(), order_date_var.get(),
                     regular_kg, blankets_kg, white_pieces, total, order_id))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Update Success", f"✅ Order updated successfully!\n\nReceipt: {receipt_number_var.get()}\nNew Total: ₹{total:.2f}")
                # Make sure to release grab before destroying
                edit_window.grab_release()
                edit_window.destroy()
                self.load_orders()
                
            except Exception as e:
                messagebox.showerror("Update Error", f"Error updating order: {str(e)}")
        
        # Save button with prominent styling
        save_button = tk.Button(button_frame, text="💾 SAVE CHANGES", 
                               command=update_order,
                               font=('Arial', 16, 'bold'),
                               bg='#10b981', fg='white',
                               relief='raised', bd=5,
                               padx=50, pady=15,
                               cursor='hand2',
                               activebackground='#059669',
                               activeforeground='white')
        save_button.pack(side='left', padx=(0, 20))
        
        # Cancel button
        def close_edit_window():
            edit_window.grab_release()
            edit_window.destroy()
            
        cancel_button = tk.Button(button_frame, text="❌ Cancel", 
                                 command=close_edit_window,
                                 font=('Arial', 10, 'bold'),
                                 bg='#6b7280', fg='white',
                                 relief='raised', bd=2,
                                 padx=20, pady=8,
                                 cursor='hand2')
        cancel_button.pack(side='left')
        
        # Instructions with enhanced styling
        instruction_frame = tk.Frame(edit_window, bg='#f0f8ff')
        instruction_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # Highlight the save button importance
        highlight_frame = tk.Frame(instruction_frame, bg='#fef3c7', relief='solid', bd=1)
        highlight_frame.pack(fill='x', pady=(0, 5))
        
        tk.Label(highlight_frame, 
                text="💡 IMPORTANT: Make your changes above and click the green 'SAVE CHANGES' button to update the order",
                font=('Arial', 10, 'bold'),
                bg='#fef3c7', fg='#92400e').pack(pady=5)
        
        tk.Label(instruction_frame, 
                text="💡 Tip: The SAVE CHANGES button is prominently displayed in green above",
                font=('Arial', 9, 'italic'),
                bg='#f0f8ff', fg='#6b7280').pack()
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def delete_order(self):
        """Delete selected order"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an order to delete!")
            return
        
        # Confirm deletion
        result = messagebox.askyesno("Confirm Delete", 
                                   "Are you sure you want to delete this order?\nThis action cannot be undone!")
        if not result:
            return
        
        try:
            # Get order ID
            item = self.tree.item(selection[0])
            order_id = item['values'][0]
            
            # Delete from database
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM orders WHERE id = %s', (order_id,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "✅ Order deleted successfully!")
            self.load_orders()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting order: {str(e)}")
    
    def export_data(self):
        """Export data to CSV"""
        try:
            # Check if there's data to export
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM orders')
            count = cursor.fetchone()[0]
            conn.close()
            
            if count == 0:
                messagebox.showwarning("No Data", "No orders found to export!")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Orders to CSV"
            )
            
            if filename:
                conn = mysql.connector.connect(**self.DB_CONFIG)
                df = pd.read_sql_query('''
                    SELECT 
                        receipt_number as 'Receipt Number',
                        customer_name as 'Customer Name',
                        mobile_number as 'Mobile Number',
                        order_date as 'Order Date',
                        regular_clothes_kg as 'Regular Clothes (kg)',
                        blankets_kg as 'Blankets (kg)',
                        white_clothes_pieces as 'White Clothes (pieces)',
                        total_amount as 'Total Amount (₹)',
                        collection_date as 'Collection Date',
                        created_at as 'Created At'
                    FROM orders 
                    ORDER BY created_at DESC
                ''', conn)
                conn.close()
                
                df.to_csv(filename, index=False)
                messagebox.showinfo("Export Success", f"✅ {count} orders exported to:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting data: {str(e)}")

    def mark_as_collected(self):
        """Mark order as collected using manual receipt number input"""
        receipt_number = self.collection_receipt_var.get().strip()
        
        if not receipt_number:
            messagebox.showwarning("Warning", "Please enter a receipt number!")
            return
        
        try:
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor()
            
            # First, check if the order exists and get its details
            cursor.execute('''
                SELECT id, receipt_number, customer_name, mobile_number, order_date, 
                       total_amount, regular_clothes_kg, blankets_kg, white_clothes_pieces, collection_date
                FROM orders 
                WHERE receipt_number = %s
            ''', (receipt_number,))
            
            order = cursor.fetchone()
            
            if not order:
                messagebox.showerror("Error", f"Order with receipt number '{receipt_number}' not found!")
                conn.close()
                return
            
            order_id, receipt_num, customer_name, mobile_number, order_date, total_amount, regular_kg, blankets_kg, white_pieces, collection_date = order
            
            if collection_date:
                messagebox.showwarning("Warning", "This order is already marked as collected!")
                conn.close()
                return

            # Show order details for confirmation
            order_details = f"""
Order Details:
Receipt Number: {receipt_num}
Customer: {customer_name}
Mobile: {mobile_number}
Date: {order_date}
Total: ₹{total_amount}

Services:
- Regular Clothes: {regular_kg}kg
- Blankets/Bedsheets: {blankets_kg}kg  
- White Clothes: {white_pieces} pieces
"""
            
            result = messagebox.askyesno("Confirm Collection", 
                                       f"Are you sure you want to mark this order as collected?\n{order_details}")
            if not result:
                conn.close()
                return

            # Update the order collection date
            cursor.execute('''
                UPDATE orders 
                SET collection_date = NOW()
                WHERE receipt_number = %s
            ''', (receipt_number,))
            
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"✅ Order #{receipt_number} marked as collected!")
            self.collection_receipt_var.set("")  # Clear the input field
            self.load_orders()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error marking order as collected: {str(e)}")

    def generate_invoice(self):
        """Generate and display invoice for selected order or by receipt number"""
        receipt_number = None
        values = None
        
        # Check if we have a receipt number from the collection tracking section
        if hasattr(self, 'collection_receipt_var') and self.collection_receipt_var.get().strip():
            receipt_number = self.collection_receipt_var.get().strip()
            
            # Get order details from database using receipt number
            try:
                conn = mysql.connector.connect(**self.DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute('''
                SELECT id, receipt_number, customer_name, mobile_number, order_date, collection_date, total_amount,
                       regular_clothes_kg, blankets_kg, white_clothes_pieces
                FROM orders WHERE receipt_number = %s
                ''', (receipt_number,))
                
                order_details = cursor.fetchone()
                conn.close()
            except Exception as e:
                messagebox.showerror("Database Error", f"Error retrieving order details: {e}")
                return
            
            if not order_details:
                messagebox.showerror("Error", "No order found with this receipt number")
                return
                
            # Create values list similar to treeview selection
            values = list(order_details)
            customer_name = values[2]
            mobile_number = values[3]
            order_date = values[4]
            collection_date = values[5]
            total_amount = float(values[6])
            
        else:
            # Try to get selected order from treeview if available
            try:
                selection = self.tree.selection()
                if not selection:
                    messagebox.showwarning("Warning", "Please select an order or enter a receipt number in the Collection Tracking section!")
                    return
                
                # Get selected order data
                item = self.tree.item(selection[0])
                values = item['values']
                receipt_number = values[1]
                customer_name = values[2]
                mobile_number = values[3]
                order_date = values[4]
                collection_date = values[5]
                total_amount = values[6]
            except (IndexError, AttributeError):
                messagebox.showerror("Error", "Please enter a receipt number in the Collection Tracking section")
                return
        
        if collection_date == "Not Collected":
            messagebox.showwarning("Warning", "This order has not been collected yet. Cannot generate invoice.")
            return

        # Get service details based on where the data came from
        try:
            regular_clothes = values[7]
            blankets = values[8]
            white_clothes = values[9]
        except (IndexError, TypeError):
            # If we can't get from values, try to get from database
            try:
                conn = mysql.connector.connect(**self.DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute('''
                SELECT regular_clothes_kg, blankets_kg, white_clothes_pieces
                FROM orders WHERE receipt_number = %s
                ''', (receipt_number,))
                
                service_details = cursor.fetchone()
                conn.close()
            except Exception as e:
                messagebox.showerror("Database Error", f"Error retrieving service details: {e}")
                return
            
            if service_details:
                regular_clothes, blankets, white_clothes = service_details
            else:
                regular_clothes = blankets = white_clothes = 0
        
        # Calculate service costs
        regular_cost = float(regular_clothes) * self.PRICING['regular_clothes']
        blanket_cost = float(blankets) * self.PRICING['blankets']
        white_cost = float(white_clothes) * self.PRICING['white_clothes']
        
        invoice_text = f"""
🧺 Express Wash - Invoice
========================================
Receipt Number: {receipt_number}
Customer: {customer_name}
Mobile: {mobile_number}
Order Date: {order_date}
Collection Date: {collection_date}

Service Details:
----------------------------------------
Regular Clothes: {regular_clothes}kg × ₹{self.PRICING['regular_clothes']} = ₹{regular_cost:.2f}
Blankets/Bedsheets: {blankets}kg × ₹{self.PRICING['blankets']} = ₹{blanket_cost:.2f}
White Clothes: {white_clothes} pieces × ₹{self.PRICING['white_clothes']} = ₹{white_cost:.2f}

Total Amount: ₹{total_amount:.2f}
========================================
"""
        
        # Create HTML version for download
        html_invoice = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Invoice - {receipt_number}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .invoice {{ border: 1px solid #ddd; padding: 20px; max-width: 600px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 20px; }}
        .details {{ margin-bottom: 20px; }}
        .service-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .service-table th, .service-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .service-table th {{ background-color: #f2f2f2; }}
        .total {{ font-weight: bold; text-align: right; margin-top: 20px; }}
        .footer {{ margin-top: 30px; text-align: center; font-size: 12px; color: #777; }}
    </style>
</head>
<body>
    <div class="invoice">
        <div class="header">
            <h1>Express Wash Laundry</h1>
            <h2>Invoice</h2>
        </div>
        <div class="details">
            <p><strong>Receipt Number:</strong> {receipt_number}</p>
            <p><strong>Customer:</strong> {customer_name}</p>
            <p><strong>Mobile:</strong> {mobile_number}</p>
            <p><strong>Order Date:</strong> {order_date}</p>
            <p><strong>Collection Date:</strong> {collection_date}</p>
        </div>
        <h3>Service Details</h3>
        <table class="service-table">
            <tr>
                <th>Service</th>
                <th>Quantity</th>
                <th>Rate</th>
                <th>Amount</th>
            </tr>
            <tr>
                <td>Regular Clothes</td>
                <td>{regular_clothes}kg</td>
                <td>₹{self.PRICING['regular_clothes']}</td>
                <td>₹{regular_cost:.2f}</td>
            </tr>
            <tr>
                <td>Blankets/Bedsheets</td>
                <td>{blankets}kg</td>
                <td>₹{self.PRICING['blankets']}</td>
                <td>₹{blanket_cost:.2f}</td>
            </tr>
            <tr>
                <td>White Clothes</td>
                <td>{white_clothes} pieces</td>
                <td>₹{self.PRICING['white_clothes']}</td>
                <td>₹{white_cost:.2f}</td>
            </tr>
        </table>
        <div class="total">
            <p>Total Amount: ₹{total_amount:.2f}</p>
        </div>
        <div class="footer">
            <p>Thank you for choosing Express Wash Laundry!</p>
            <p>For any queries, please contact us.</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Save HTML invoice to file
        invoice_filename = f"invoice_{receipt_number}.html"
        with open(invoice_filename, 'w') as f:
            f.write(html_invoice)
        
        # Create invoice window
        invoice_window = tk.Toplevel(self.root)
        invoice_window.title(f"Invoice for {receipt_number}")
        invoice_window.geometry("600x500")
        invoice_window.configure(bg='#f0f8ff')
        invoice_window.transient(self.root)  # Make it stay on top of the main window
        invoice_window.grab_set()  # Make it modal

        # Add a title label
        title_label = tk.Label(invoice_window, text="📄 Express Wash - Invoice", 
                              font=('Arial', 14, 'bold'), bg='#f0f8ff', fg='#1e3a8a')
        title_label.pack(pady=(15, 10))

        # Create a frame for the invoice text
        invoice_frame = tk.Frame(invoice_window, bg='#f0f8ff', bd=2, relief='groove')
        invoice_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Add the invoice text widget
        invoice_text_widget = tk.Text(invoice_frame, height=15, width=60, 
                                     font=('Courier', 10), bg='#f9fafb', fg='#374151')
        invoice_text_widget.pack(padx=10, pady=10, fill='both', expand=True)
        invoice_text_widget.insert(1.0, invoice_text)

        # Allow copying invoice text
        invoice_text_widget.configure(state='disabled')

        # Create a frame for buttons
        button_frame = tk.Frame(invoice_window, bg='#f0f8ff')
        button_frame.pack(fill='x', padx=20, pady=10)

        # Add buttons for actions
        open_button = tk.Button(button_frame, text="🌐 Open in Browser", 
                               command=lambda: webbrowser.open(f"file://{os.path.abspath(invoice_filename)}"),
                               font=('Arial', 10, 'bold'),
                               bg='#3b82f6', fg='white',
                               relief='raised', bd=2,
                               padx=15, pady=6)
        open_button.pack(side='left', padx=5)
        
        # Add download button
        download_button = tk.Button(button_frame, text="💾 Download Invoice", 
                                  command=lambda: self.save_invoice_as(invoice_filename, receipt_number),
                                  font=('Arial', 10, 'bold'),
                                  bg='#10b981', fg='white',
                                  relief='raised', bd=2,
                                  padx=15, pady=6)
        download_button.pack(side='left', padx=5)
        
        # Add close button
        close_button = tk.Button(button_frame, text="❌ Close", 
                                command=lambda: self.close_invoice_window(invoice_window),
                                font=('Arial', 10, 'bold'),
                                bg='#ef4444', fg='white',
                                relief='raised', bd=2,
                                padx=15, pady=6)
        close_button.pack(side='right', padx=5)

    def save_invoice_as(self, source_filename, receipt_number):
        """Save the invoice to a user-specified location"""
        from tkinter import filedialog
        
        # Ask user for save location
        target_filename = filedialog.asksaveasfilename(
            initialdir="/",
            title="Save Invoice As",
            initialfile=f"Express_Wash_Invoice_{receipt_number}.html",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if target_filename:
            # Copy the file to the selected location
            import shutil
            try:
                shutil.copy2(source_filename, target_filename)
                messagebox.showinfo("Success", f"Invoice saved to {target_filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save invoice: {str(e)}")
    
    def close_invoice_window(self, window):
        """Close the invoice window properly"""
        window.grab_release()
        window.destroy()
        
    def close_reports_window(self, window):
        """Close the reports window properly"""
        window.grab_release()
        window.destroy()
    
    def show_reports(self):
        """Show comprehensive reports window with charts"""
        reports_window = tk.Toplevel(self.root)
        reports_window.title("📊 Express Wash - Business Reports")
        reports_window.geometry("1200x800")
        reports_window.configure(bg='#f0f8ff')
        reports_window.transient(self.root)  # Make it stay on top of the main window
        
        # Add a close button at the top right
        close_button = tk.Button(reports_window, text="❌ Close", 
                               command=lambda: self.close_reports_window(reports_window),
                               font=('Arial', 10, 'bold'),
                               bg='#ef4444', fg='white',
                               relief='raised', bd=2,
                               padx=10, pady=5)
        close_button.pack(anchor='ne', padx=10, pady=10)

        # Create visualization type selector frame
        viz_selector_frame = tk.Frame(reports_window, bg='#f0f8ff', bd=2, relief='ridge')
        viz_selector_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(viz_selector_frame, text="Visualization Type:", font=('Arial', 12, 'bold'), 
                bg='#f0f8ff').pack(side='left', padx=(10, 10))
        
        # Create dropdown for visualization type
        viz_types = ["Bar Charts", "Pie Charts", "Line Charts", "Area Charts", "Scatter Plots"]
        viz_var = tk.StringVar(value=viz_types[0])
        viz_dropdown = ttk.Combobox(viz_selector_frame, textvariable=viz_var, values=viz_types, width=15, state="readonly")
        viz_dropdown.pack(side='left', padx=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(reports_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: Summary Dashboard
        summary_frame = tk.Frame(notebook, bg='#f0f8ff')
        notebook.add(summary_frame, text="📈 Summary Dashboard")
        
        # Tab 2: Revenue Analysis
        revenue_frame = tk.Frame(notebook, bg='#f0f8ff')
        notebook.add(revenue_frame, text="💰 Revenue Analysis")
        
        # Tab 3: Order Status
        status_frame = tk.Frame(notebook, bg='#f0f8ff')
        notebook.add(status_frame, text="📋 Order Status")
        
        # Tab 4: Time-based Reports
        time_frame = tk.Frame(notebook, bg='#f0f8ff')
        notebook.add(time_frame, text="⏰ Time-based Reports")
        
        # Store visualization type and notebook for later reference
        self.current_viz_type = viz_var
        self.reports_notebook = notebook
        
        # Function to update visualizations based on selected type
        def update_visualizations(event=None):
            viz_type = viz_var.get()
            # Clear all frames
            for frame in [summary_frame, revenue_frame, status_frame, time_frame]:
                for widget in frame.winfo_children():
                    widget.destroy()
            
            # Create content for each tab with selected visualization type
            self.create_summary_dashboard(summary_frame, viz_type)
            self.create_revenue_analysis(revenue_frame, viz_type)
            self.create_order_status_analysis(status_frame, viz_type)
            self.create_time_based_reports(time_frame, viz_type)
        
        # Bind the dropdown to update visualizations
        viz_dropdown.bind("<<ComboboxSelected>>", update_visualizations)
        
        # Initial creation of visualizations
        update_visualizations()

    def create_summary_dashboard(self, parent, viz_type="Bar Charts"):
        """Create summary dashboard with key metrics"""
        # Get summary data
        summary_data = self.get_summary_data()
        
        # Create metrics display
        metrics_frame = tk.Frame(parent, bg='#f0f8ff')
        metrics_frame.pack(fill='x', padx=20, pady=20)
        
        # Key metrics
        metrics = [
            ("Total Orders", summary_data['total_orders'], "#3b82f6"),
            ("Total Revenue", f"₹{summary_data['total_revenue']:.2f}", "#10b981"),
            ("Pending Orders", summary_data['pending_orders'], "#f59e0b"),
            ("Collected Orders", summary_data['collected_orders'], "#8b5cf6")
        ]
        
        for i, (label, value, color) in enumerate(metrics):
            metric_frame = tk.Frame(metrics_frame, bg=color, relief='raised', bd=2)
            metric_frame.grid(row=0, column=i, padx=10, pady=10, sticky='ew')
            
            tk.Label(metric_frame, text=label, font=('Arial', 12, 'bold'), 
                    fg='white', bg=color).pack(pady=(10, 5))
            tk.Label(metric_frame, text=str(value), font=('Arial', 16, 'bold'), 
                    fg='white', bg=color).pack(pady=(0, 10))
        
        metrics_frame.columnconfigure((0,1,2,3), weight=1)
        
        # Create charts
        charts_frame = tk.Frame(parent, bg='#f0f8ff')
        charts_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Revenue trend chart
        self.create_revenue_chart(charts_frame)
        
        # Service breakdown chart
        self.create_service_chart(charts_frame)

    def create_revenue_analysis(self, parent, viz_type="Bar Charts"):
        """Create detailed revenue analysis with different visualization types"""
        # Time period selection
        period_frame = tk.Frame(parent, bg='#f0f8ff')
        period_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(period_frame, text="Select Time Period:", font=('Arial', 12, 'bold'), 
                bg='#f0f8ff').pack(side='left', padx=(0, 10))
        
        period_var = tk.StringVar(value="30")
        periods = [("Today", "1"), ("This Week", "7"), ("Last 15 Days", "15"), 
                  ("Last 30 Days", "30"), ("Last 3 Months", "90"), ("Last 6 Months", "180")]
        
        for text, value in periods:
            tk.Radiobutton(period_frame, text=text, variable=period_var, value=value,
                          bg='#f0f8ff', command=lambda: self.update_revenue_chart(parent, period_var.get())).pack(side='left', padx=5)
        
        # Revenue chart container
        self.revenue_chart_frame = tk.Frame(parent, bg='#f0f8ff')
        self.revenue_chart_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Initial chart
        self.update_revenue_chart(parent, "30")

    def create_order_status_analysis(self, parent, viz_type="Bar Charts"):
        """Create order status analysis with different visualization types"""
        # Status breakdown
        status_data = self.get_status_data()
        
        # Create chart based on visualization type
        fig, ax = plt.subplots(figsize=(8, 6))
        labels = ['Pending', 'Collected']
        sizes = [status_data['pending'], status_data['collected']]
        colors = ['#f59e0b', '#10b981']
        
        if viz_type == "Pie Charts":
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.set_title('Order Status Distribution - Pie Chart', fontsize=14, fontweight='bold')
        
        elif viz_type == "Bar Charts":
            ax.bar(labels, sizes, color=colors)
            ax.set_title('Order Status Distribution - Bar Chart', fontsize=14, fontweight='bold')
            ax.set_ylabel('Number of Orders')
            # Add value labels on bars
            for i, v in enumerate(sizes):
                ax.text(i, v + 0.5, str(v), ha='center')
        
        elif viz_type == "Line Charts" or viz_type == "Area Charts" or viz_type == "Scatter Plots":
            # These chart types don't make much sense for just two categories,
            # so we'll create a more detailed time-based status chart
            try:
                conn = mysql.connector.connect(**self.DB_CONFIG)
                cursor = conn.cursor()
                
                # Get status counts by date for the last 30 days
                cursor.execute('''
                    SELECT DATE(order_date) as date,
                           SUM(CASE WHEN collection_date IS NULL THEN 1 ELSE 0 END) as pending,
                           SUM(CASE WHEN collection_date IS NOT NULL THEN 1 ELSE 0 END) as collected
                    FROM orders
                    WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                    GROUP BY DATE(order_date)
                    ORDER BY date
                ''')
                
                results = cursor.fetchall()
                conn.close()
                
                if results:
                    dates = [row[0] for row in results]
                    pending = [int(row[1]) for row in results]
                    collected = [int(row[2]) for row in results]
                    
                    if viz_type == "Line Charts":
                        ax.plot(dates, pending, marker='o', linewidth=2, label='Pending', color='#f59e0b')
                        ax.plot(dates, collected, marker='s', linewidth=2, label='Collected', color='#10b981')
                        ax.set_title('Order Status Trend - Line Chart (Last 30 Days)', fontsize=14, fontweight='bold')
                    
                    elif viz_type == "Area Charts":
                        ax.fill_between(dates, pending, color='#f59e0b', alpha=0.5, label='Pending')
                        ax.fill_between(dates, collected, color='#10b981', alpha=0.5, label='Collected')
                        ax.set_title('Order Status Trend - Area Chart (Last 30 Days)', fontsize=14, fontweight='bold')
                    
                    elif viz_type == "Scatter Plots":
                        ax.scatter(dates, pending, s=80, color='#f59e0b', label='Pending')
                        ax.scatter(dates, collected, s=80, color='#10b981', label='Collected')
                        ax.set_title('Order Status Trend - Scatter Plot (Last 30 Days)', fontsize=14, fontweight='bold')
                    
                    ax.set_xlabel('Date')
                    ax.set_ylabel('Number of Orders')
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    plt.setp(ax.get_xticklabels(), rotation=45)
            except Exception as e:
                print(f"Error creating time-based status chart: {e}")
                # Fallback to pie chart if there's an error
                ax.clear()
                ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                ax.set_title('Order Status Distribution', fontsize=14, fontweight='bold')
        
        # Embed chart in tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=20, pady=20)

    def create_time_based_reports(self, parent, viz_type="Bar Charts"):
        """Create time-based reports with filters and different visualization types"""
        # Filter frame
        filter_frame = tk.Frame(parent, bg='#f0f8ff')
        filter_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(filter_frame, text="Report Type:", font=('Arial', 12, 'bold'), 
                bg='#f0f8ff').pack(side='left', padx=(0, 10))
        
        report_var = tk.StringVar(value="daily")
        reports = [("Daily", "daily"), ("Weekly", "weekly"), ("Monthly", "monthly")]
        
        for text, value in reports:
            tk.Radiobutton(filter_frame, text=text, variable=report_var, value=value,
                          bg='#f0f8ff', command=lambda: self.update_time_report(parent, report_var.get())).pack(side='left', padx=5)
        
        # Report container
        self.time_report_frame = tk.Frame(parent, bg='#f0f8ff')
        self.time_report_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Initial report
        self.update_time_report(parent, "daily")

    def get_summary_data(self):
        """Get summary statistics"""
        try:
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor()
            
            # Total orders and revenue
            cursor.execute('''
                SELECT COUNT(*) as total_orders, 
                       SUM(total_amount) as total_revenue,
                       SUM(CASE WHEN collection_date IS NULL THEN 1 ELSE 0 END) as pending_orders,
                       SUM(CASE WHEN collection_date IS NOT NULL THEN 1 ELSE 0 END) as collected_orders
                FROM orders
            ''')
            
            result = cursor.fetchone()
            conn.close()
            
            return {
                'total_orders': result[0] or 0,
                'total_revenue': result[1] or 0,
                'pending_orders': result[2] or 0,
                'collected_orders': result[3] or 0
            }
        except Exception as e:
            print(f"Error getting summary data: {e}")
            return {'total_orders': 0, 'total_revenue': 0, 'pending_orders': 0, 'collected_orders': 0}

    def get_status_data(self):
        """Get order status breakdown"""
        try:
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN collection_date IS NULL THEN 'pending'
                        ELSE 'collected'
                    END as status,
                    COUNT(*) as count
                FROM orders
                GROUP BY 
                    CASE 
                        WHEN collection_date IS NULL THEN 'pending'
                        ELSE 'collected'
                    END
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            status_data = {'pending': 0, 'collected': 0}
            for status, count in results:
                status_data[status] = count
            
            return status_data
        except Exception as e:
            print(f"Error getting status data: {e}")
            return {'pending': 0, 'collected': 0}

    def create_revenue_chart(self, parent):
        """Create revenue trend chart"""
        try:
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor()
            
            # Get last 30 days revenue
            cursor.execute('''
                SELECT DATE(order_date) as date, SUM(total_amount) as revenue
                FROM orders
                WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY DATE(order_date)
                ORDER BY date
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            if results:
                dates = [row[0] for row in results]
                revenues = [float(row[1]) for row in results]
                
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(dates, revenues, marker='o', linewidth=2, markersize=6)
                ax.set_title('Revenue Trend (Last 30 Days)', fontsize=14, fontweight='bold')
                ax.set_xlabel('Date')
                ax.set_ylabel('Revenue (₹)')
                ax.grid(True, alpha=0.3)
                
                # Rotate x-axis labels
                plt.setp(ax.get_xticklabels(), rotation=45)
                
                canvas = FigureCanvasTkAgg(fig, parent)
                canvas.draw()
                canvas.get_tk_widget().pack(side='left', fill='both', expand=True, padx=(0, 10))
            
        except Exception as e:
            print(f"Error creating revenue chart: {e}")

    def create_service_chart(self, parent):
        """Create service breakdown chart"""
        try:
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    SUM(regular_clothes_kg) as regular,
                    SUM(blankets_kg) as blankets,
                    SUM(white_clothes_pieces) as white
                FROM orders
            ''')
            
            result = cursor.fetchone()
            conn.close()
            
            if result and any(result):
                services = ['Regular Clothes', 'Blankets/Bedsheets', 'White Clothes']
                quantities = [float(result[0] or 0), float(result[1] or 0), float(result[2] or 0)]
                
                fig, ax = plt.subplots(figsize=(8, 6))
                bars = ax.bar(services, quantities, color=['#3b82f6', '#10b981', '#f59e0b'])
                ax.set_title('Service Usage Breakdown', fontsize=14, fontweight='bold')
                ax.set_ylabel('Quantity')
                
                # Add value labels on bars
                for bar, value in zip(bars, quantities):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + max(quantities)*0.01,
                           f'{value:.1f}', ha='center', va='bottom')
                
                canvas = FigureCanvasTkAgg(fig, parent)
                canvas.draw()
                canvas.get_tk_widget().pack(side='right', fill='both', expand=True, padx=(10, 0))
            
        except Exception as e:
            print(f"Error creating service chart: {e}")

    def update_revenue_chart(self, parent, days):
        """Update revenue chart based on selected period and visualization type"""
        # Clear existing chart
        for widget in self.revenue_chart_frame.winfo_children():
            widget.destroy()
            
        # Get current visualization type
        viz_type = self.current_viz_type.get() if hasattr(self, 'current_viz_type') else "Bar Charts"
        
        try:
            # Show loading message
            loading_label = tk.Label(self.revenue_chart_frame, text="Loading chart...", font=("Arial", 14))
            loading_label.pack(pady=20)
            self.revenue_chart_frame.update()
            
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor(buffered=True)
            
            # Optimize query with index hint if available
            cursor.execute(f'''
                SELECT DATE(order_date) as date, SUM(total_amount) as revenue
                FROM orders USE INDEX (order_date_idx)
                WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
                GROUP BY DATE(order_date)
                ORDER BY date
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            # Remove loading message
            loading_label.destroy()
            
            if results:
                dates = [row[0] for row in results]
                revenues = [float(row[1]) for row in results]
                
                # Limit data points to improve performance
                if len(dates) > 30:
                    # If we have too many data points, sample them
                    step = len(dates) // 30 + 1
                    dates = dates[::step]
                    revenues = revenues[::step]
                
                # Use a smaller figure size for better performance
                fig, ax = plt.subplots(figsize=(10, 5), dpi=80)
                
                # Create different chart types based on selection
                if viz_type == "Bar Charts":
                    ax.bar(dates, revenues, color='#3b82f6', alpha=0.8, width=0.7)
                    ax.set_title(f'Revenue Trend - Bar Chart (Last {days} Days)', fontsize=12, fontweight='bold')
                
                elif viz_type == "Line Charts":
                    ax.plot(dates, revenues, marker='o', linewidth=1.5, markersize=5, color='#3b82f6')
                    ax.set_title(f'Revenue Trend - Line Chart (Last {days} Days)', fontsize=12, fontweight='bold')
                
                elif viz_type == "Area Charts":
                    ax.fill_between(dates, revenues, color='#3b82f6', alpha=0.5)
                    ax.plot(dates, revenues, color='#3b82f6', linewidth=1.5)
                    ax.set_title(f'Revenue Trend - Area Chart (Last {days} Days)', fontsize=12, fontweight='bold')
                
                elif viz_type == "Pie Charts":
                    # For pie chart, we'll show revenue distribution by date
                    # Only show the last 5 days in pie chart to avoid too many slices
                    if len(dates) > 5:
                        dates = dates[-5:]
                        revenues = revenues[-5:]
                    ax.pie(revenues, labels=[d.strftime('%m/%d') for d in dates], autopct='%1.1f%%', startangle=90)
                    ax.set_title(f'Revenue Distribution - Pie Chart (Last {min(5, len(dates))} Days)', fontsize=12, fontweight='bold')
                
                elif viz_type == "Scatter Plots":
                    ax.scatter(dates, revenues, s=80, color='#3b82f6', alpha=0.7)
                    ax.set_title(f'Revenue Trend - Scatter Plot (Last {days} Days)', fontsize=12, fontweight='bold')
                
                # Common settings for non-pie charts
                if viz_type != "Pie Charts":
                    ax.set_xlabel('Date', fontsize=10)
                    ax.set_ylabel('Revenue (₹)', fontsize=10)
                    ax.grid(True, alpha=0.3)
                    
                    # Reduce number of x-axis labels for better readability
                    if len(dates) > 10:
                        plt.xticks(dates[::len(dates)//10 + 1])
                
                # Rotate x-axis labels
                plt.setp(ax.get_xticklabels(), rotation=45, fontsize=8)
                
                # Use tight layout to optimize space
                plt.tight_layout()
                
                canvas = FigureCanvasTkAgg(fig, self.revenue_chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill='both', expand=True)
            
        except Exception as e:
            print(f"Error updating revenue chart: {e}")

    def update_time_report(self, parent, report_type):
        """Update time-based report based on selected type and visualization type"""
        # Clear existing report
        for widget in self.time_report_frame.winfo_children():
            widget.destroy()
            
        # Get current visualization type
        viz_type = self.current_viz_type.get() if hasattr(self, 'current_viz_type') else "Bar Charts"
        
        # Show loading message
        loading_label = tk.Label(self.time_report_frame, text="Loading report...", font=("Arial", 14))
        loading_label.pack(pady=20)
        self.time_report_frame.update()
        
        try:
            conn = mysql.connector.connect(**self.DB_CONFIG)
            cursor = conn.cursor(buffered=True)
            
            # Limit the amount of data to improve performance
            if report_type == "daily":
                cursor.execute('''
                    SELECT DATE(order_date) as date, COUNT(*) as orders, SUM(total_amount) as revenue
                    FROM orders USE INDEX (order_date_idx)
                    WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                    GROUP BY DATE(order_date)
                    ORDER BY date DESC
                    LIMIT 30
                ''')
            elif report_type == "weekly":
                cursor.execute('''
                    SELECT YEARWEEK(order_date) as week, COUNT(*) as orders, SUM(total_amount) as revenue
                    FROM orders USE INDEX (order_date_idx)
                    WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 12 WEEK)
                    GROUP BY YEARWEEK(order_date)
                    ORDER BY week DESC
                    LIMIT 12
                ''')
            else:  # monthly
                cursor.execute('''
                    SELECT DATE_FORMAT(order_date, '%Y-%m') as month, COUNT(*) as orders, SUM(total_amount) as revenue
                    FROM orders USE INDEX (order_date_idx)
                    WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
                    GROUP BY DATE_FORMAT(order_date, '%Y-%m')
                    ORDER BY month DESC
                    LIMIT 12
                ''')
            
            results = cursor.fetchall()
            conn.close()
            
            # Remove loading message
            loading_label.destroy()
            
            if results:
                # Create report display
                report_text = f"📊 {report_type.title()} Report\n"
                report_text += "=" * 50 + "\n\n"
                
                total_orders = 0
                total_revenue = 0
                
                for row in results:
                    period = row[0]
                    orders = row[1]
                    revenue = float(row[2])
                    
                    report_text += f"{period}: {orders} orders, ₹{revenue:.2f}\n"
                    total_orders += orders
                    total_revenue += revenue
                
                report_text += "\n" + "=" * 50 + "\n"
                report_text += f"Total: {total_orders} orders, ₹{total_revenue:.2f}\n"
                
                text_widget = tk.Text(self.time_report_frame, height=20, width=60, 
                                     font=('Courier', 10), bg='#f9fafb', fg='#374151')
                text_widget.pack(fill='both', expand=True, padx=20, pady=20)
                text_widget.insert(1.0, report_text)
                text_widget.configure(state='disabled')
            
        except Exception as e:
            print(f"Error updating time report: {e}")

def main():
    """Main function"""
    root = tk.Tk()
    app = ExpressWashApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()