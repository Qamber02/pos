#!/usr/bin/env python3
"""Enhanced Professional POS System - Complete Version

Key Improvements:
- Fixed checkout button visibility and styling issues
- Enhanced modern UI with better color schemes and layout
- Added barcode scanner simulation
- Improved keyboard shortcuts
- Added quick payment buttons
- Enhanced dashboard with real-time updates
- Better error handling and user feedback
- Added transaction history viewer
- Improved receipt formatting
- Added backup and restore functionality
- Implemented advanced sales reporting with export options
- Added calculator and barcode test dialogs
- Enhanced product display using cards
- Integrated modern theme manager
- Added low stock alerts
- Implemented advanced customer management
- Added hover effects and animations
- Fixed Add to Cart functionality
- Added PKR currency option
- Removed calculator button
- Added View Cart button
- Fixed quantity updating
- Added category management
- Enhanced UI with professional frames and category filtering
- Added Dark/Light mode toggle
- Improved receipt number generation
- Added Hold/Resume Cart feature
- Added Quick Discount button
- Added Daily Sales Summary popup
- Added Top 5 Products report
- Added customer purchase history
- Implemented auto-backup on exit
- Added database indexes
- Enhanced data safety
"""

import sys
import io
import os
import sqlite3
import datetime
import time
import json
import shutil
import csv
import uuid
import random
from tkinter import *
from tkinter import ttk, messagebox, filedialog, scrolledtext

# Attempt to import pandas for Excel export (optional feature)
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Ensure UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- Constants ---
DB_PATH = 'pos_system.db'
BACKUP_FOLDER = 'backups'
os.makedirs(BACKUP_FOLDER, exist_ok=True)


# --- Modern Theme Manager ---
class ModernThemeManager:
    """Manages modern color themes for the application with dark/light mode support"""
    def __init__(self):
        self.light_colors = {
            'primary': '#2c3e50',  # Dark blue-gray
            'secondary': '#3498db', # Bright blue
            'success': '#27ae60',   # Green
            'warning': '#f39c12',   # Orange
            'danger': '#e74c3c',    # Red
            'light': '#ecf0f1',     # Light gray
            'dark': '#34495e',      # Dark gray
            'white': '#ffffff',
            'accent': '#bb8fce',    # Purple
            'info': '#48c9b0'       # Turquoise
        }
        
        self.dark_colors = {
            'primary': '#1a252f',  # Darker blue-gray
            'secondary': '#2980b9', # Darker blue
            'success': '#229954',   # Darker green
            'warning': '#d68910',   # Darker orange
            'danger': '#c0392b',    # Darker red
            'light': '#2c3e50',     # Darker light gray
            'dark': '#ecf0f1',      # Light gray (inverted)
            'white': '#1c2833',     # Dark white
            'accent': '#8e44ad',    # Darker purple
            'info': '#16a085'       # Darker turquoise
        }
        
        self.current_theme = 'light'
        self.colors = self.light_colors.copy()

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.current_theme == 'light':
            self.current_theme = 'dark'
            self.colors = self.dark_colors.copy()
        else:
            self.current_theme = 'light'
            self.colors = self.light_colors.copy()
        return self.current_theme

    def get_color(self, color):
        """Get a specific color from the theme"""
        if self.current_theme == 'light':
            color_map = {
                self.light_colors['primary']: '#34495e',
                self.light_colors['secondary']: '#5dade2',
                self.light_colors['success']: '#58d68d',
                self.light_colors['warning']: '#f8c471',
                self.light_colors['danger']: '#ec7063',
                self.light_colors['accent']: '#bb8fce',
                self.light_colors['info']: '#48c9b0',
                self.light_colors['dark']: '#5d6d7e'
            }
        else:
            color_map = {
                self.dark_colors['primary']: '#2c3e50',
                self.dark_colors['secondary']: '#3498db',
                self.dark_colors['success']: '#27ae60',
                self.dark_colors['warning']: '#f39c12',
                self.dark_colors['danger']: '#e74c3c',
                self.dark_colors['accent']: '#bb8fce',
                self.dark_colors['info']: '#48c9b0',
                self.dark_colors['dark']: '#ecf0f1'
            }
        return color_map.get(color, color)

    def apply_styles(self, style):
        """Apply modern styles using ttk"""
        style.theme_use('clam') # Use a modern theme
        
        # Configure styles based on current theme
        bg_color = self.colors['white']
        fg_color = self.colors['dark']
        
        style.configure('Treeview', background=bg_color, fieldbackground=bg_color, foreground=fg_color)
        style.map('Treeview', background=[('selected', self.colors['secondary'])])
        
        # Configure custom styles
        style.configure('Accent.TButton', background=self.colors['success'], foreground='white', 
                        font=('Arial', 12, 'bold'), focuscolor='none')
        style.map('Accent.TButton', background=[('active', self.colors['secondary'])])
        
        style.configure('Card.TFrame', background=bg_color, relief='solid', borderwidth=1)
        style.configure('Category.TButton', background=self.colors['light'], foreground=self.colors['dark'],
                        font=('Arial', 10, 'bold'), focuscolor='none', relief='raised', borderwidth=1)
        style.map('Category.TButton', background=[('active', self.colors['secondary']), 
                                               ('selected', self.colors['primary'])])


# --- Backup and Restore Manager ---
class BackupRestoreManager:
    """Handles database backup and restore operations"""
    @staticmethod
    def create_backup():
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.db"
        backup_path = os.path.join(BACKUP_FOLDER, backup_name)
        try:
            shutil.copy2(DB_PATH, backup_path)
            messagebox.showinfo("Backup Successful", f"Backup created: {backup_path}")
            return True
        except Exception as e:
            messagebox.showerror("Backup Failed", f"Could not create backup: {str(e)}")
            return False

    @staticmethod
    def restore_backup(backup_file_path):
        if not os.path.exists(backup_file_path):
            messagebox.showerror("Restore Failed", "Backup file does not exist.")
            return False
        try:
            # Create a backup before restoring
            BackupRestoreManager.create_backup()
            shutil.copy2(backup_file_path, DB_PATH)
            messagebox.showinfo("Restore Successful", f"Database restored from: {backup_file_path}")
            return True
        except Exception as e:
            messagebox.showerror("Restore Failed", f"Could not restore database: {str(e)}")
            return False

    @staticmethod
    def list_backups():
        """List available backup files"""
        backups = []
        if os.path.exists(BACKUP_FOLDER):
            for filename in os.listdir(BACKUP_FOLDER):
                if filename.endswith('.db'):
                    backups.append(os.path.join(BACKUP_FOLDER, filename))
        return sorted(backups, reverse=True) # Newest first


# --- Database Manager ---
class DatabaseManager:
    @staticmethod
    def get_conn():
        """Get a database connection with proper error handling and security features"""
        try:
            conn = sqlite3.connect(DB_PATH)
            
            # Fix deprecation warning by setting a proper date adapter
            def adapt_datetime(dt):
                return dt.isoformat()
            
            sqlite3.register_adapter(datetime.datetime, adapt_datetime)
            
            conn.row_factory = sqlite3.Row # Enable column access by name
            
            # Enable foreign key support for data integrity
            conn.execute("PRAGMA foreign_keys = ON")
            
            return conn
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {str(e)}")
            return None

    @staticmethod
    def init_db():
        conn = DatabaseManager.get_conn()
        cursor = conn.cursor()

        # Create tables if they don't exist
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            price REAL NOT NULL,
            cost REAL DEFAULT 0,
            barcode TEXT UNIQUE,
            stock INTEGER DEFAULT 0,
            description TEXT,
            min_stock INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_number TEXT UNIQUE NOT NULL,
            customer_id INTEGER,
            subtotal REAL NOT NULL,
            discount REAL DEFAULT 0,
            tax REAL NOT NULL,
            total REAL NOT NULL,
            paid REAL NOT NULL,
            change_amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            cashier_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_price REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        );

        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        
        CREATE TABLE IF NOT EXISTS held_carts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cart_data TEXT NOT NULL,
            customer_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        );
        """)
        
        # Create indexes for better performance
        cursor.executescript("""
        CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode);
        CREATE INDEX IF NOT EXISTS idx_sales_created_at ON sales(created_at);
        CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
        """)
        
        conn.commit()
        conn.close()

        # Insert default settings if they don't exist
        default_settings = {
            'tax_percent': '0.0',
            'currency_symbol': 'PKR',  # Changed from '$' to 'PKR'
            'receipt_footer': 'Thank you for your business!',
            'cashier_name': 'Admin',
            'theme': 'light'
        }
        for key, value in default_settings.items():
            DatabaseManager.set_setting(key, value)

        # Insert sample data if tables are empty
        DatabaseManager.insert_sample_data()

    @staticmethod
    def set_setting(key, value):
        with DatabaseManager.get_conn() as conn:
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
            conn.commit()

    @staticmethod
    def insert_sample_data():
        """Insert sample data for initial setup"""
        conn = DatabaseManager.get_conn()
        cur = conn.cursor()

        # Check if categories exist
        cur.execute("SELECT COUNT(*) FROM categories")
        if cur.fetchone()[0] == 0:
            # Insert sample categories
            sample_categories = [
                ('Food & Drinks', 'Edible items and beverages'),
                ('Snacks', 'Light food items'),
                ('Electronics', 'Electronic gadgets and accessories'),
                ('Clothing', 'Apparel and accessories')
            ]
            cur.executemany("INSERT INTO categories(name, description) VALUES(?,?)", sample_categories)

        # Check if products exist
        cur.execute("SELECT COUNT(*) FROM products")
        if cur.fetchone()[0] == 0:
            # Insert sample products
            sample_products = [
                ('Water', 1, 1.50, 0.75, '123456789012', 50, 'Bottled water', 10),
                ('Soda', 1, 2.00, 1.00, '123456789013', 40, 'Carbonated soft drink', 10),
                ('Chips', 2, 1.75, 0.90, '123456789014', 30, 'Potato chips', 10),
                ('Chocolate Bar', 2, 2.50, 1.25, '123456789015', 25, 'Milk chocolate', 10),
                ('Headphones', 3, 29.99, 15.00, '123456789016', 15, 'In-ear headphones', 5),
                ('Phone Charger', 3, 19.99, 10.00, '123456789017', 20, 'USB charging cable', 5),
                ('T-Shirt', 4, 15.99, 8.00, '123456789018', 30, 'Cotton t-shirt', 10),
                ('Jeans', 4, 39.99, 20.00, '123456789019', 20, 'Denim jeans', 10)
            ]
            cur.executemany("""
                INSERT INTO products(name, category_id, price, cost, barcode, stock, description, min_stock)
                VALUES(?,?,?,?,?,?,?,?)
            """, sample_products)

        conn.commit()
        conn.close()


# --- Data Manager ---
class DataManager:
    @staticmethod
    def get_setting(key):
        with DatabaseManager.get_conn() as conn:
            result = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
            return result['value'] if result else None

    @staticmethod
    def get_products(category_id=None, search_query=None):
        query = "SELECT * FROM products WHERE is_active = 1"
        params = []
        if category_id:
            query += " AND category_id = ?"
            params.append(category_id)
        if search_query:
            query += " AND (name LIKE ? OR barcode LIKE ?)"
            search_param = f"%{search_query}%"
            params.extend([search_param, search_param])
        query += " ORDER BY name ASC"
        
        with DatabaseManager.get_conn() as conn:
            return conn.execute(query, params).fetchall()

    @staticmethod
    def get_product_by_barcode(barcode):
        with DatabaseManager.get_conn() as conn:
            return conn.execute("SELECT * FROM products WHERE barcode = ? AND is_active = 1", (barcode,)).fetchone()

    @staticmethod
    def get_categories():
        with DatabaseManager.get_conn() as conn:
            return conn.execute("SELECT * FROM categories ORDER BY name ASC").fetchall()

    @staticmethod
    def get_customers(search_query=None):
        query = "SELECT * FROM customers"
        params = []
        if search_query:
            query += " WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?"
            search_param = f"%{search_query}%"
            params.extend([search_param, search_param, search_param])
        query += " ORDER BY name ASC"

        with DatabaseManager.get_conn() as conn:
            return conn.execute(query, params).fetchall()

    @staticmethod
    def add_customer(name, phone, email, address):
        with DatabaseManager.get_conn() as conn:
            conn.execute(
                "INSERT INTO customers (name, phone, email, address) VALUES (?, ?, ?, ?)",
                (name, phone, email, address)
            )
            conn.commit()

    @staticmethod
    def update_customer(cid, name, phone, email, address):
        with DatabaseManager.get_conn() as conn:
            conn.execute(
                """UPDATE customers SET name=?, phone=?, email=?, address=?, updated_at=CURRENT_TIMESTAMP WHERE id=?""",
                (name, phone, email, address, cid)
            )
            conn.commit()

    @staticmethod
    def get_sales(start_date=None, end_date=None, limit=None):
        query = """
            SELECT s.*, c.name as customer_name
            FROM sales s
            LEFT JOIN customers c ON s.customer_id = c.id
        """
        params = []
        if start_date and end_date:
            query += " WHERE DATE(s.created_at) BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        query += " ORDER BY s.created_at DESC"
        if limit:
            query += f" LIMIT {limit}"
        
        with DatabaseManager.get_conn() as conn:
            return conn.execute(query, params).fetchall()

    @staticmethod
    def get_sale_details(sale_id):
        with DatabaseManager.get_conn() as conn:
            sale = conn.execute("SELECT * FROM sales WHERE id=?", (sale_id,)).fetchone()
            items = conn.execute("""
                SELECT si.*, p.name as product_name
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                WHERE si.sale_id=?
            """, (sale_id,)).fetchall()
            return sale, items

    @staticmethod
    def get_low_stock_products():
        with DatabaseManager.get_conn() as conn:
            return conn.execute("SELECT * FROM products WHERE stock <= min_stock AND is_active = 1").fetchall()

    @staticmethod
    def get_top_products(limit=5):
        """Get top selling products by quantity"""
        with DatabaseManager.get_conn() as conn:
            return conn.execute("""
                SELECT p.id, p.name, SUM(si.quantity) as total_quantity
                FROM products p
                JOIN sale_items si ON p.id = si.product_id
                GROUP BY p.id, p.name
                ORDER BY total_quantity DESC
                LIMIT ?
            """, (limit,)).fetchall()
    
    @staticmethod
    def get_customer_purchases(customer_id, limit=5):
        """Get recent purchases for a customer"""
        with DatabaseManager.get_conn() as conn:
            return conn.execute("""
                SELECT s.id, s.receipt_number, s.total, s.created_at
                FROM sales s
                WHERE s.customer_id = ?
                ORDER BY s.created_at DESC
                LIMIT ?
            """, (customer_id, limit)).fetchall()
    
    @staticmethod
    def hold_cart(cart_data, customer_id=None):
        """Save current cart for later use"""
        with DatabaseManager.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO held_carts (cart_data, customer_id) VALUES (?, ?)",
                (json.dumps(cart_data), customer_id)
            )
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def get_held_carts():
        """Get all held carts"""
        with DatabaseManager.get_conn() as conn:
            return conn.execute("""
                SELECT hc.*, c.name as customer_name
                FROM held_carts hc
                LEFT JOIN customers c ON hc.customer_id = c.id
                ORDER BY hc.created_at DESC
            """).fetchall()
    
    @staticmethod
    def get_held_cart(cart_id):
        """Get a specific held cart"""
        with DatabaseManager.get_conn() as conn:
            result = conn.execute("SELECT * FROM held_carts WHERE id=?", (cart_id,)).fetchone()
            if result:
                return json.loads(result['cart_data']), result['customer_id']
            return None, None
    
    @staticmethod
    def delete_held_cart(cart_id):
        """Delete a held cart"""
        with DatabaseManager.get_conn() as conn:
            conn.execute("DELETE FROM held_carts WHERE id=?", (cart_id,))
            conn.commit()

    @staticmethod
    def save_sale(cart, subtotal, discount, tax, total, paid, payment_method, cashier_name, customer_id=None):
        # Generate a better receipt number using UUID + timestamp
        timestamp = int(time.time())
        random_part = random.randint(1000, 9999)
        receipt_number = f"R{timestamp}{random_part}"
        
        change = paid - total
        
        try:
            with DatabaseManager.get_conn() as conn:
                if conn is None:
                    raise ValueError("Database connection failed")
                
                cursor = conn.cursor()
                
                # First, check all items have sufficient stock to prevent partial updates
                for item in cart:
                    cursor.execute("SELECT stock FROM products WHERE id = ?", (item['id'],))
                    result = cursor.fetchone()
                    if not result:
                        raise ValueError(f"Product {item['name']} not found")
                    
                    current_stock = result['stock']
                    if current_stock < item['qty']:
                        raise ValueError(f"Not enough stock for {item['name']}. Available: {current_stock}, Requested: {item['qty']}")
                
                # Insert sale
                cursor.execute("""
                    INSERT INTO sales (receipt_number, customer_id, subtotal, discount, tax, total, paid, change_amount, payment_method, cashier_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (receipt_number, customer_id, subtotal, discount, tax, total, paid, change, payment_method, cashier_name))
                
                sale_id = cursor.lastrowid
                
                # Insert sale items and update stock
                for item in cart:
                    total_price = item['price'] * item['qty']
                    cursor.execute("""
                        INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, total_price)
                        VALUES (?, ?, ?, ?, ?)
                    """, (sale_id, item['id'], item['qty'], item['price'], total_price))
                    
                    # Update stock with atomic operation
                    cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", 
                                  (item['qty'], item['id']))
                
                conn.commit()
                
            return sale_id, receipt_number
        except sqlite3.Error as e:
            # Database error - rollback any changes
            if 'conn' in locals() and conn:
                conn.rollback()
            raise ValueError(f"Database error: {str(e)}")
        except ValueError as e:
            # Business logic error - re-raise
            raise e
        except Exception as e:
            # Unexpected error
            if 'conn' in locals() and conn:
                conn.rollback()
            raise ValueError(f"Unexpected error: {str(e)}")


# --- Enhanced Dialogs ---

class CustomerSelectionDialog(Toplevel):
    def __init__(self, parent, callback=None):
        super().__init__(parent)
        self.parent = parent
        self.callback = callback
        self.customers = DataManager.get_customers()
        
        # Add colors attribute if parent doesn't have it
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors if parent doesn't have them
            self.colors = {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'success': '#27ae60',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'light': '#ecf0f1',
                'dark': '#34495e',
                'white': '#ffffff',
                'accent': '#bb8fce',
                'info': '#48c9b0'
            }

        self.title("Select Customer")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.center_window()

    def create_widgets(self):
        main_frame = Frame(self, bg='white', padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)

        Label(main_frame, text="Select Customer", font=('Arial', 14, 'bold'), bg='white').pack(pady=(0, 10))

        # Search frame
        search_frame = Frame(main_frame, bg='white')
        search_frame.pack(fill=X, pady=(0, 10))
        
        Label(search_frame, text="Search:", font=('Arial', 10, 'bold'), bg='white').pack(side=LEFT, padx=(0, 5))
        self.search_var = StringVar()
        Entry(search_frame, textvariable=self.search_var, font=('Arial', 10)).pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        Button(search_frame, text="Search", command=self.search_customers,
               font=('Arial', 10, 'bold'), bg=self.colors['primary'], fg='white', relief=FLAT).pack(side=LEFT)

        # Treeview for customers
        columns = ('ID', 'Name', 'Phone', 'Email')
        self.customer_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=10)
        for col in columns:
            self.customer_tree.heading(col, text=col)
            self.customer_tree.column(col, width=120)
        self.customer_tree.pack(fill=BOTH, expand=True, pady=(0, 10))

        # Populate treeview
        self.populate_customer_tree()

        # Buttons
        btn_frame = Frame(main_frame, bg='white')
        btn_frame.pack(fill=X)

        Button(btn_frame, text="Select", command=self.select_customer,
               font=('Arial', 10, 'bold'), bg=self.colors['success'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="New Customer", command=self.add_new_customer,
               font=('Arial', 10, 'bold'), bg=self.colors['primary'], fg='white', relief=FLAT).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Walk-in", command=self.select_walkin,
               font=('Arial', 10, 'bold'), bg=self.colors['secondary'], fg='white', relief=FLAT).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Cancel", command=self.destroy,
               font=('Arial', 10, 'bold'), bg=self.colors['dark'], fg='white', relief=FLAT).pack(side=RIGHT)

    def populate_customer_tree(self):
        # Clear existing items
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        
        # Add customers to treeview
        for customer in self.customers:
            self.customer_tree.insert('', 'end', iid=str(customer['id']), values=(
                customer['id'], customer['name'], customer['phone'] or 'N/A', customer['email'] or 'N/A'
            ))

    def search_customers(self):
        query = self.search_var.get().strip()
        self.customers = DataManager.get_customers(search_query=query)
        self.populate_customer_tree()

    def add_new_customer(self):
        dialog = CustomerFormDialog(self)
        if dialog.result:
            # Refresh customer list and select the new one
            self.customers = DataManager.get_customers()
            self.populate_customer_tree()
            # Auto-select the newly created customer
            if self.customers:
                new_customer = self.customers[-1]
                if self.callback:
                    self.callback(new_customer)
                self.destroy()

    def select_customer(self):
        """Select highlighted customer"""
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a customer.")
            return
        customer_id = int(selection[0])
        customer = next((c for c in self.customers if c['id'] == customer_id), None)
        if self.callback:
            self.callback(customer)
        self.destroy()

    def select_walkin(self):
        """Select walk-in customer (no customer record)"""
        if self.callback:
            self.callback(None) # Pass None for walk-in
        self.destroy()

    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class CustomerFormDialog(Toplevel):
    def __init__(self, parent, customer=None):
        super().__init__(parent)
        self.parent = parent
        self.customer = customer
        self.result = None
        
        # Add colors attribute if parent doesn't have it
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors if parent doesn't have them
            self.colors = {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'success': '#27ae60',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'light': '#ecf0f1',
                'dark': '#34495e',
                'white': '#ffffff',
                'accent': '#bb8fce',
                'info': '#48c9b0'
            }

        title = "Edit Customer" if customer else "New Customer"
        self.title(title)
        self.geometry("450x400")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        if customer:
            self.load_customer_data()
        self.center_window()

    def create_widgets(self):
        main_frame = Frame(self, bg='white', padx=25, pady=25)
        main_frame.pack(fill=BOTH, expand=True)

        # Header
        Label(main_frame, text=self.title(), font=('Arial', 16, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=(0, 20))

        # Form fields
        Label(main_frame, text="Name*", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        self.name_var = StringVar()
        Entry(main_frame, textvariable=self.name_var, font=('Arial', 10), relief=SOLID, bd=1).pack(fill=X, pady=(0, 10))

        Label(main_frame, text="Phone", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        self.phone_var = StringVar()
        Entry(main_frame, textvariable=self.phone_var, font=('Arial', 10), relief=SOLID, bd=1).pack(fill=X, pady=(0, 10))

        Label(main_frame, text="Email", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        self.email_var = StringVar()
        Entry(main_frame, textvariable=self.email_var, font=('Arial', 10), relief=SOLID, bd=1).pack(fill=X, pady=(0, 10))

        Label(main_frame, text="Address", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        self.address_text = Text(main_frame, height=4, font=('Arial', 10), relief=SOLID, bd=1)
        self.address_text.pack(fill=BOTH, expand=True, pady=(0, 15))

        # Buttons
        btn_frame = Frame(main_frame, bg='white')
        btn_frame.pack(fill=X)

        Button(btn_frame, text="Save", command=self.save_customer,
               font=('Arial', 11, 'bold'), bg=self.colors['success'], fg='white',
               relief=FLAT, pady=8, padx=20).pack(side=LEFT, padx=(0, 10))
        Button(btn_frame, text="Cancel", command=self.destroy,
               font=('Arial', 11, 'bold'), bg=self.colors['dark'], fg='white',
               relief=FLAT, pady=8, padx=20).pack(side=LEFT)

        # Bind Enter key to save
        self.bind('<Return>', lambda e: self.save_customer())

    def load_customer_data(self):
        self.name_var.set(self.customer['name'])
        self.phone_var.set(self.customer['phone'] or '')
        self.email_var.set(self.customer['email'] or '')
        self.address_text.insert('1.0', self.customer['address'] or '')

    def save_customer(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Validation Error", "Customer name is required.")
            return

        phone = self.phone_var.get().strip()
        email = self.email_var.get().strip()
        address = self.address_text.get('1.0', END).strip()

        # Basic email validation
        if email and '@' not in email:
            messagebox.showerror("Validation Error", "Please enter a valid email address.")
            return

        try:
            if self.customer:  # Edit existing
                DataManager.update_customer(self.customer['id'], name, phone, email, address)
                messagebox.showinfo("Success", "Customer updated successfully.")
            else:  # Add New
                DataManager.add_customer(name, phone, email, address)
                messagebox.showinfo("Success", "Customer created successfully.")
            self.result = True
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save customer: {str(e)}")

    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class EnhancedPaymentDialog(Toplevel):
    """Enhanced payment processing dialog"""
    def __init__(self, parent, total_amount):
        super().__init__(parent)
        self.parent = parent
        self.total_amount = total_amount
        self.result = None
        
        # Add colors attribute if parent doesn't have it
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors if parent doesn't have them
            self.colors = {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'success': '#27ae60',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'light': '#ecf0f1',
                'dark': '#34495e',
                'white': '#ffffff',
                'accent': '#bb8fce',
                'info': '#48c9b0'
            }

        self.title("Process Payment")
        self.geometry("450x400")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        self.create_widgets()
        self.center_window()

    def create_widgets(self):
        main_frame = Frame(self, bg='white', padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)

        Label(main_frame, text="Payment Details", font=('Arial', 14, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=(0, 15))

        # Total amount
        currency = self.parent.settings.get('currency_symbol', '$')
        Label(main_frame, text=f"Total Amount: {currency}{self.total_amount:.2f}", font=('Arial', 12, 'bold'), bg='white').pack(pady=(0, 10))

        # Payment method
        Label(main_frame, text="Payment Method:", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        self.payment_method_var = StringVar(value="Cash")
        method_frame = Frame(main_frame, bg='white')
        method_frame.pack(fill=X, pady=(0, 10))
        Radiobutton(method_frame, text="Cash", variable=self.payment_method_var, value="Cash", bg='white').pack(side=LEFT)
        Radiobutton(method_frame, text="Card", variable=self.payment_method_var, value="Card", bg='white').pack(side=LEFT, padx=(10, 0))
        Radiobutton(method_frame, text="Other", variable=self.payment_method_var, value="Other", bg='white').pack(side=LEFT, padx=(10, 0))

        # Paid amount
        Label(main_frame, text="Amount Paid:", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        self.paid_var = DoubleVar(value=self.total_amount)
        Entry(main_frame, textvariable=self.paid_var, font=('Arial', 12), relief=SOLID, bd=1).pack(fill=X, pady=(0, 10))

        # Change display
        change_frame = Frame(main_frame, bg='white')
        change_frame.pack(fill=X, pady=(0, 15))
        Label(change_frame, text="Change:", font=('Arial', 10, 'bold'), bg='white').pack(side=LEFT)
        self.change_var = StringVar(value="0.00")
        self.change_label = Label(change_frame, textvariable=self.change_var, font=('Arial', 12, 'bold'), bg='white', fg=self.colors['success'])
        self.change_label.pack(side=RIGHT)

        # Bind entry change to update change calculation
        self.paid_var.trace_add('write', self.update_change)

        # Quick pay buttons
        quick_frame = Frame(main_frame, bg='white')
        quick_frame.pack(fill=X, pady=(0, 10))
        Label(quick_frame, text="Quick Pay:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w')
        quick_amounts = [self.total_amount, self.total_amount + 5, self.total_amount + 10]
        for amount in quick_amounts:
            Button(quick_frame, text=f"{currency}{amount:.2f}",
                   command=lambda a=amount: self.set_quick_amount(a),
                   font=('Arial', 9), bg=self.colors['secondary'], fg='white',
                   relief=FLAT, padx=5, pady=2).pack(side=LEFT, padx=2)

        # Buttons
        btn_frame = Frame(main_frame, bg='white')
        btn_frame.pack(fill=X)

        Button(btn_frame, text="Process Payment", command=self.process_payment,
               font=('Arial', 11, 'bold'), bg=self.colors['success'], fg='white',
               relief=FLAT, pady=8).pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        Button(btn_frame, text="Cancel", command=self.cancel,
               font=('Arial', 11, 'bold'), bg=self.colors['dark'], fg='white',
               relief=FLAT, pady=8).pack(side=LEFT, fill=X, expand=True, padx=(5, 0))

    def update_change(self, *args):
        try:
            paid = self.paid_var.get()
            change = paid - self.total_amount
            currency = self.parent.settings.get('currency_symbol', '$')
            if change < 0:
                self.change_var.set(f"Insufficient: {currency}{abs(change):.2f}")
                self.change_label.configure(fg=self.colors['danger'])
            else:
                self.change_var.set(f"{currency}{change:.2f}")
                self.change_label.configure(fg=self.colors['success'])
        except:
            self.change_var.set("Invalid amount")
            self.change_label.configure(fg=self.colors['danger'])

    def set_quick_amount(self, amount):
        self.paid_var.set(amount)

    def process_payment(self):
        """Process the payment with validation"""
        try:
            paid = self.paid_var.get()
            if paid < self.total_amount:
                messagebox.showerror("Insufficient Payment", "Payment amount is less than total.")
                return
            self.result = (paid, self.payment_method_var.get())
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid payment amount: {str(e)}")

    def cancel(self):
        """Cancel payment"""
        self.result = None
        self.destroy()

    def center_window(self):
        """Center the dialog on parent window"""
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class QuantityEditDialog(Toplevel):
    """Enhanced quantity editing dialog"""
    def __init__(self, parent, cart_item, callback=None):
        super().__init__(parent)
        self.parent = parent
        self.cart_item = cart_item
        self.callback = callback
        self.result = None
        
        # Add colors attribute if parent doesn't have it
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors if parent doesn't have them
            self.colors = {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'success': '#27ae60',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'light': '#ecf0f1',
                'dark': '#34495e',
                'white': '#ffffff',
                'accent': '#bb8fce',
                'info': '#48c9b0'
            }

        self.title("Edit Quantity")
        self.geometry("300x200")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.center_window()

    def create_widgets(self):
        main_frame = Frame(self, bg='white', padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)

        Label(main_frame, text=f"Edit Quantity: {self.cart_item['name']}", font=('Arial', 12, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=(0, 15))

        # Quantity controls
        qty_frame = Frame(main_frame, bg='white')
        qty_frame.pack(fill=X)

        Button(qty_frame, text="-", command=self.decrease_qty, font=('Arial', 14, 'bold'), width=3).pack(side=LEFT)
        self.qty_var = IntVar(value=self.cart_item['qty'])
        Label(qty_frame, textvariable=self.qty_var, font=('Arial', 14, 'bold'), width=5).pack(side=LEFT, padx=10)
        Button(qty_frame, text="+", command=self.increase_qty, font=('Arial', 14, 'bold'), width=3).pack(side=LEFT)

        # Total display
        self.total_var = StringVar()
        self.update_total()
        Label(main_frame, textvariable=self.total_var, font=('Arial', 12, 'bold'), bg='white', fg=self.colors['success']).pack(pady=(10, 15))

        # Buttons
        btn_frame = Frame(main_frame, bg='white')
        btn_frame.pack(fill=X)

        Button(btn_frame, text="Save", command=self.save_quantity,
               font=('Arial', 11, 'bold'), bg=self.colors['success'], fg='white',
               relief=FLAT, pady=8).pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        Button(btn_frame, text="Remove", command=self.remove_item,
               font=('Arial', 11, 'bold'), bg=self.colors['danger'], fg='white',
               relief=FLAT, pady=8).pack(side=LEFT, fill=X, expand=True, padx=5)
        Button(btn_frame, text="Cancel", command=self.cancel,
               font=('Arial', 11, 'bold'), bg=self.colors['dark'], fg='white',
               relief=FLAT, pady=8).pack(side=LEFT, fill=X, expand=True, padx=(5, 0))

        # Bind events
        self.bind('<KeyRelease-Up>', lambda e: self.increase_qty())
        self.bind('<KeyRelease-Down>', lambda e: self.decrease_qty())
        self.bind('<Return>', lambda e: self.save_quantity())
        self.bind('<Escape>', lambda e: self.cancel())

    def decrease_qty(self):
        current = self.qty_var.get()
        if current > 1:
            self.qty_var.set(current - 1)
            self.update_total()

    def increase_qty(self):
        current = self.qty_var.get()
        self.qty_var.set(current + 1)
        self.update_total()

    def update_total(self):
        try:
            qty = self.qty_var.get()
            total = self.cart_item['price'] * qty
            currency = self.parent.settings.get('currency_symbol', '$')
            self.total_var.set(f"Total: {currency}{total:.2f}")
        except:
            self.total_var.set("Total: Invalid")

    def save_quantity(self):
        try:
            qty = self.qty_var.get()
            if qty <= 0:
                messagebox.showerror("Invalid Quantity", "Quantity must be greater than zero.")
                return
            self.result = qty
            self.destroy()
        except:
            messagebox.showerror("Error", "Please enter a valid quantity.")

    def remove_item(self):
        if messagebox.askyesno("Remove Item", f"Remove {self.cart_item['name']} from cart?"):
            self.result = 0 # Signal for removal
            self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class BarcodeTestDialog(Toplevel):
    """Barcode scanner test dialog"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Add colors attribute if parent doesn't have it
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors if parent doesn't have them
            self.colors = {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'success': '#27ae60',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'light': '#ecf0f1',
                'dark': '#34495e',
                'white': '#ffffff',
                'accent': '#bb8fce',
                'info': '#48c9b0'
            }
            
        self.title("Barcode Scanner Test")
        self.geometry("400x300")
        self.transient(parent)
        self.resizable(False, False)

        self.create_widgets()
        self.center_window()

    def create_widgets(self):
        main_frame = Frame(self, bg='white', padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)

        Label(main_frame, text="Barcode Scanner Test", font=('Arial', 14, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=(0, 10))

        Label(main_frame, text="Scan a barcode or enter manually:", font=('Arial', 10), bg='white').pack(pady=(0, 10))

        self.barcode_var = StringVar()
        barcode_entry = Entry(main_frame, textvariable=self.barcode_var, font=('Arial', 12), relief=SOLID, bd=1)
        barcode_entry.pack(fill=X, pady=(0, 10))

        self.result_label = Label(main_frame, text="Ready to scan...", font=('Arial', 10), bg='white', fg=self.colors['secondary'])
        self.result_label.pack(fill=X, pady=(0, 15))

        # Sample barcodes
        sample_frame = Frame(main_frame, bg='white')
        sample_frame.pack(fill=X, pady=(0, 15))
        Label(sample_frame, text="Sample Barcodes:", font=('Arial', 10, 'bold'), bg='white').pack(anchor='w')
        sample_barcodes = ['123456789012', '987654321098', '555555555555']
        for barcode in sample_barcodes:
            Button(sample_frame, text=barcode,
                   command=lambda b=barcode: self.test_barcode(b),
                   font=('Arial', 9), bg=self.colors['secondary'], fg='white',
                   relief=FLAT, padx=10).pack(side=LEFT, padx=5)

        # Close button
        Button(main_frame, text="Close", command=self.destroy,
               font=('Arial', 11, 'bold'), bg=self.colors['primary'], fg='white',
               relief=FLAT, pady=8).pack(pady=20)

        # Bind events
        barcode_entry.bind('<Return>', self.process_scan)
        barcode_entry.bind('<KeyRelease>', self.on_input_change)

    def on_input_change(self, event):
        barcode = self.barcode_var.get()
        if len(barcode) >= 8:  # Minimum barcode length
            self.after(500, self.process_scan)  # Process after slight delay

    def process_scan(self, event=None):
        barcode = self.barcode_var.get().strip()
        if not barcode:
            return
        self.test_barcode(barcode)
        self.barcode_var.set("")  # Clear for next scan

    def test_barcode(self, barcode):
        product = DataManager.get_product_by_barcode(barcode)
        if product:
            self.result_label.configure(text=f"Found: {product['name']} ({self.parent.settings.get('currency_symbol', '$')}{product['price']:.2f})", fg=self.colors['success'])
        else:
            self.result_label.configure(text=f"Product not found for barcode: {barcode}", fg=self.colors['danger'])

    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class TransactionHistoryDialog(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Add colors attribute if parent doesn't have it
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors if parent doesn't have them
            self.colors = {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'success': '#27ae60',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'light': '#ecf0f1',
                'dark': '#34495e',
                'white': '#ffffff',
                'accent': '#bb8fce',
                'info': '#48c9b0'
            }
            
        self.title("Transaction History")
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.load_transactions()
        self.center_window()

    def create_widgets(self):
        main_frame = Frame(self, bg='white', padx=10, pady=10)
        main_frame.pack(fill=BOTH, expand=True)

        Label(main_frame, text="Recent Transactions", font=('Arial', 14, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=(0, 10))

        # Treeview for transactions
        columns = ('Date', 'Receipt #', 'Total', 'Method')
        self.trans_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.trans_tree.heading(col, text=col)
            self.trans_tree.column(col, width=150)
        self.trans_tree.pack(fill=BOTH, expand=True, pady=(0, 10))

        # Details text area
        details_frame = LabelFrame(main_frame, text="Transaction Details", font=('Arial', 10, 'bold'), bg='white', padx=10, pady=10)
        details_frame.pack(fill=BOTH, expand=True)

        self.details_text = Text(details_frame, wrap=WORD, state=DISABLED, font=('Courier', 10))
        self.details_text.pack(fill=BOTH, expand=True)

        # Scrollbar for details
        detail_scrollbar = Scrollbar(details_frame, orient=VERTICAL, command=self.details_text.yview)
        detail_scrollbar.pack(side=RIGHT, fill=Y)
        self.details_text.config(yscrollcommand=detail_scrollbar.set)

        # Buttons
        btn_frame = Frame(main_frame, bg='white')
        btn_frame.pack(fill=X)

        Button(btn_frame, text="View Details", command=self.view_details,
               font=('Arial', 10, 'bold'), bg=self.colors['secondary'], fg='white',
               relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Refresh", command=self.load_transactions,
               font=('Arial', 10, 'bold'), bg=self.colors['primary'], fg='white',
               relief=FLAT).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Close", command=self.destroy,
               font=('Arial', 10, 'bold'), bg=self.colors['dark'], fg='white',
               relief=FLAT).pack(side=RIGHT)

        # Bind double-click to view details
        self.trans_tree.bind('<Double-1>', lambda e: self.view_details())

    def load_transactions(self):
        # Clear existing items
        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)

        # Get sales data
        limit_text = "All"  # For this simple view, show all
        limit = None if limit_text == "All" else int(limit_text)
        sales = DataManager.get_sales(limit=limit)
        currency = self.parent.settings.get('currency_symbol', '$')

        for sale in sales:
            # Parse datetime
            dt = datetime.datetime.fromisoformat(sale['created_at'])
            time_str = dt.strftime('%H:%M')
            date_str = dt.strftime('%Y-%m-%d')
            self.trans_tree.insert('', 'end', iid=str(sale['id']),
                                   text=time_str,
                                   values=(date_str, sale['receipt_number'], f"{currency}{sale['total']:.2f}", sale['payment_method']))

    def view_details(self):
        selection = self.trans_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a transaction.")
            return

        sale_id = int(selection[0])
        sale, items = DataManager.get_sale_details(sale_id)

        if not sale:
            messagebox.showerror("Error", "Could not retrieve transaction details.")
            return

        # Format details
        lines = []
        lines.append("=" * 50)
        lines.append(f"RECEIPT: {sale['receipt_number']}")
        lines.append(f"DATE: {datetime.datetime.fromisoformat(sale['created_at']).strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"CASHIER: {sale['cashier_name']}")
        lines.append(f"PAYMENT: {sale['payment_method']}")
        lines.append("-" * 50)
        lines.append("ITEMS:")
        currency = self.parent.settings.get('currency_symbol', '$')
        for item in items:
            lines.append(f" {item['product_name']}")
            lines.append(f"  Qty: {item['quantity']} × {currency}{item['unit_price']:.2f} = {currency}{item['total_price']:.2f}")
        lines.append("")
        lines.append("-" * 50)
        lines.append(f"Subtotal: {currency}{sale['subtotal']:.2f}")
        if sale['discount'] > 0:
            lines.append(f"Discount: -{currency}{sale['discount']:.2f}")
        lines.append(f"Tax: {currency}{sale['tax']:.2f}")
        lines.append(f"TOTAL: {currency}{sale['total']:.2f}")
        lines.append(f"PAID: {currency}{sale['paid']:.2f}")
        lines.append(f"CHANGE: {currency}{sale['change_amount']:.2f}")
        
        self.details_text.config(state=NORMAL)
        self.details_text.delete('1.0', END)
        self.details_text.insert('1.0', '\n'.join(lines))
        self.details_text.config(state=DISABLED)

    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class ShortcutsDialog(Toplevel):
    """Show enhanced keyboard shortcuts help"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Add colors attribute if parent doesn't have it
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors if parent doesn't have them
            self.colors = {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'success': '#27ae60',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'light': '#ecf0f1',
                'dark': '#34495e',
                'white': '#ffffff',
                'accent': '#bb8fce',
                'info': '#48c9b0'
            }
            
        self.title("Keyboard Shortcuts")
        self.geometry("600x500")
        self.transient(parent)
        self.resizable(True, True)

        self.create_widgets()
        self.center_window()

    def create_widgets(self):
        main_frame = Frame(self, bg='white', padx=10, pady=10)
        main_frame.pack(fill=BOTH, expand=True)

        Label(main_frame, text="Keyboard Shortcuts", font=('Arial', 16, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=(0, 10))

        canvas = Canvas(main_frame, bg='white', highlightthickness=0)
        scrollbar = Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Define shortcuts
        shortcut_sections = [
            ("General", [("F1", "New Sale"), ("F2", "Product Manager"), ("F3", "Sales Report"), ("F5", "Refresh Products"), ("F12", "Show Shortcuts"), ("Ctrl+N", "New Sale"), ("Ctrl+S", "Settings"), ("Ctrl+Q", "Quick Barcode Add"), ("Escape", "Clear Search")]),
            ("Cart Operations", [("Enter", "Checkout (if cart ready)"), ("Delete", "Remove Selected Item"), ("Ctrl+Delete", "Clear All Items")]),
            ("Navigation", [("Tab", "Move Between Fields"), ("Arrow Keys", "Navigate Lists"), ("Space", "Select/Toggle"), ("Enter", "Confirm/Execute")]),
            ("Barcode Scanner", [("Scan", "Auto-add to cart"), ("Enter after scan", "Process barcode")])
        ]

        for section_title, shortcuts in shortcut_sections:
            section_frame = Frame(scrollable_frame, bg='white', relief=SOLID, bd=1, padx=10, pady=5)
            section_frame.pack(fill=X, pady=5)

            Label(section_frame, text=section_title, font=('Arial', 12, 'bold'), bg='white', fg=self.colors['primary']).pack(anchor='w')

            for key, description in shortcuts:
                shortcut_frame = Frame(section_frame, bg='white')
                shortcut_frame.pack(fill=X, pady=2)

                key_label = Label(shortcut_frame, text=key, font=('Arial', 10, 'bold'),
                                  bg=self.colors['light'], fg=self.colors['dark'],
                                  relief=SOLID, bd=1, padx=8, pady=2)
                key_label.pack(side=LEFT)

                # Description
                Label(shortcut_frame, text=description, font=('Arial', 10), bg='white').pack(side=LEFT, padx=(10, 0))

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Close button
        Button(main_frame, text="Close", command=self.destroy,
               font=('Arial', 11, 'bold'), bg=self.colors['dark'], fg='white',
               relief=FLAT, pady=8).pack(pady=20)

    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class AboutDialog(Toplevel):
    """Show enhanced about dialog"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Add colors attribute if parent doesn't have it
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors if parent doesn't have them
            self.colors = {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'success': '#27ae60',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'light': '#ecf0f1',
                'dark': '#34495e',
                'white': '#ffffff',
                'accent': '#bb8fce',
                'info': '#48c9b0'
            }
            
        self.title("About POS System")
        self.geometry("400x300")
        self.transient(parent)
        self.resizable(False, False)

        self.create_widgets()
        self.center_window()

    def create_widgets(self):
        main_frame = Frame(self, bg='white', padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)

        Label(main_frame, text="Professional POS System", font=('Arial', 16, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=(0, 5))
        Label(main_frame, text="Version 2.0", font=('Arial', 12), bg='white').pack(pady=(0, 5))
        Label(main_frame, text="Developed with Python and Tkinter", font=('Arial', 10), bg='white').pack(pady=(0, 5))
        Label(main_frame, text="© 2024 POS Systems Inc.", font=('Arial', 10), bg='white').pack(pady=(0, 15))

        Button(main_frame, text="OK", command=self.destroy,
               font=('Arial', 11, 'bold'), bg=self.colors['primary'], fg='white',
               relief=FLAT, pady=8).pack(pady=20)

    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


# --- Additional Dialogs for Missing Features ---

class ProductManagerDialog(Toplevel):
    """Product management dialog"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Add colors attribute if parent doesn't have it
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors if parent doesn't have them
            self.colors = {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'success': '#27ae60',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'light': '#ecf0f1',
                'dark': '#34495e',
                'white': '#ffffff',
                'accent': '#bb8fce',
                'info': '#48c9b0'
            }
            
        self.title("Product Manager")
        self.geometry("900x600")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.load_products()
        self.center_window()

    def create_widgets(self):
        main_frame = Frame(self, bg='white', padx=10, pady=10)
        main_frame.pack(fill=BOTH, expand=True)

        # Header
        header_frame = Frame(main_frame, bg='white')
        header_frame.pack(fill=X, pady=(0, 10))
        Label(header_frame, text="Product Manager", font=('Arial', 16, 'bold'), bg='white', fg=self.colors['primary']).pack(side=LEFT)
        Button(header_frame, text="Manage Categories", command=self.manage_categories,
               font=('Arial', 10, 'bold'), bg=self.colors['accent'], fg='white', relief=FLAT).pack(side=RIGHT, padx=(0, 5))
        Button(header_frame, text="Add Product", command=self.add_product,
               font=('Arial', 10, 'bold'), bg=self.colors['success'], fg='white', relief=FLAT).pack(side=RIGHT)

        # Search and filter
        search_frame = Frame(main_frame, bg='white')
        search_frame.pack(fill=X, pady=(0, 10))
        Label(search_frame, text="Search:", font=('Arial', 10, 'bold'), bg='white').pack(side=LEFT, padx=(0, 5))
        self.search_var = StringVar()
        Entry(search_frame, textvariable=self.search_var, font=('Arial', 10)).pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        Button(search_frame, text="Search", command=self.search_products,
               font=('Arial', 10, 'bold'), bg=self.colors['primary'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(search_frame, text="Clear", command=self.clear_search,
               font=('Arial', 10, 'bold'), bg=self.colors['dark'], fg='white', relief=FLAT).pack(side=LEFT)

        # Product list
        list_frame = Frame(main_frame, bg='white')
        list_frame.pack(fill=BOTH, expand=True, pady=(0, 10))

        # Treeview for products
        columns = ('ID', 'Name', 'Category', 'Price', 'Cost', 'Stock', 'Barcode')
        self.product_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.product_tree.heading(col, text=col)
            self.product_tree.column(col, width=100)
        self.product_tree.pack(side=LEFT, fill=BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.product_tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.product_tree.configure(yscrollcommand=scrollbar.set)

        # Buttons
        btn_frame = Frame(main_frame, bg='white')
        btn_frame.pack(fill=X)

        Button(btn_frame, text="Edit", command=self.edit_product,
               font=('Arial', 10, 'bold'), bg=self.colors['secondary'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Delete", command=self.delete_product,
               font=('Arial', 10, 'bold'), bg=self.colors['danger'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Update Stock", command=self.update_stock,
               font=('Arial', 10, 'bold'), bg=self.colors['warning'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Refresh", command=self.load_products,
               font=('Arial', 10, 'bold'), bg=self.colors['primary'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Close", command=self.destroy,
               font=('Arial', 10, 'bold'), bg=self.colors['dark'], fg='white', relief=FLAT).pack(side=RIGHT)

        # Bind double-click to edit
        self.product_tree.bind('<Double-1>', lambda e: self.edit_product())

    def load_products(self):
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)

        # Get products
        products = DataManager.get_products()
        categories = {c['id']: c['name'] for c in DataManager.get_categories()}
        currency = self.parent.settings.get('currency_symbol', '$')

        for product in products:
            category_name = categories.get(product['category_id'], 'N/A')
            self.product_tree.insert('', 'end', iid=str(product['id']),
                                   values=(
                                       product['id'],
                                       product['name'],
                                       category_name,
                                       f"{currency}{product['price']:.2f}",
                                       f"{currency}{product['cost']:.2f}",
                                       product['stock'],
                                       product['barcode'] or 'N/A'
                                   ))

    def search_products(self):
        query = self.search_var.get().strip().lower()
        
        # Clear existing items
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        # Get products with search
        products = DataManager.get_products(search_query=query)
        categories = {c['id']: c['name'] for c in DataManager.get_categories()}
        currency = self.parent.settings.get('currency_symbol', '$')

        for product in products:
            category_name = categories.get(product['category_id'], 'N/A')
            self.product_tree.insert('', 'end', iid=str(product['id']),
                                   values=(
                                       product['id'],
                                       product['name'],
                                       category_name,
                                       f"{currency}{product['price']:.2f}",
                                       f"{currency}{product['cost']:.2f}",
                                       product['stock'],
                                       product['barcode'] or 'N/A'
                                   ))

    def clear_search(self):
        self.search_var.set("")
        self.load_products()

    def add_product(self):
        dialog = ProductFormDialog(self)
        if dialog.result:
            self.load_products()

    def edit_product(self):
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a product to edit.")
            return
        
        product_id = int(selection[0])
        product = None
        
        # Find the product in the database
        for p in DataManager.get_products():
            if p['id'] == product_id:
                product = p
                break
        
        if product:
            dialog = ProductFormDialog(self, product)
            if dialog.result:
                self.load_products()

    def delete_product(self):
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a product to delete.")
            return
        
        product_id = int(selection[0])
        product_name = self.product_tree.item(selection[0])['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{product_name}'?"):
            with DatabaseManager.get_conn() as conn:
                conn.execute("UPDATE products SET is_active = 0 WHERE id = ?", (product_id,))
                conn.commit()
            self.load_products()
            messagebox.showinfo("Success", f"Product '{product_name}' has been deleted.")

    def update_stock(self):
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a product to update stock.")
            return
        
        product_id = int(selection[0])
        product_name = self.product_tree.item(selection[0])['values'][1]
        current_stock = self.product_tree.item(selection[0])['values'][5]
        
        dialog = StockUpdateDialog(self, product_id, product_name, current_stock)
        if dialog.result:
            self.load_products()

    def manage_categories(self):
        """Open category manager dialog"""
        CategoryManagerDialog(self)

    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class ProductFormDialog(Toplevel):
    """Product form dialog for adding/editing products"""
    def __init__(self, parent, product=None):
        super().__init__(parent)
        self.parent = parent
        self.product = product
        self.result = None
        
        # Add colors attribute if parent doesn't have it
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors if parent doesn't have them
            self.colors = {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'success': '#27ae60',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'light': '#ecf0f1',
                'dark': '#34495e',
                'white': '#ffffff',
                'accent': '#bb8fce',
                'info': '#48c9b0'
            }

        title = "Edit Product" if product else "Add Product"
        self.title(title)
        self.geometry("500x600")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        if product:
            self.load_product_data()
        self.center_window()

    def create_widgets(self):
        main_frame = Frame(self, bg='white', padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)

        # Header
        Label(main_frame, text=self.title(), font=('Arial', 16, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=(0, 20))

        # Form fields
        Label(main_frame, text="Name*", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        self.name_var = StringVar()
        Entry(main_frame, textvariable=self.name_var, font=('Arial', 10), relief=SOLID, bd=1).pack(fill=X, pady=(0, 10))

        Label(main_frame, text="Category", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        self.category_var = StringVar()
        categories = DataManager.get_categories()
        category_names = [c['name'] for c in categories]
        self.category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, values=category_names, state='readonly')
        self.category_combo.pack(fill=X, pady=(0, 10))
        if category_names:
            self.category_combo.current(0)

        Label(main_frame, text="Price*", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        self.price_var = DoubleVar()
        Entry(main_frame, textvariable=self.price_var, font=('Arial', 10), relief=SOLID, bd=1).pack(fill=X, pady=(0, 10))

        Label(main_frame, text="Cost", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        self.cost_var = DoubleVar()
        Entry(main_frame, textvariable=self.cost_var, font=('Arial', 10), relief=SOLID, bd=1).pack(fill=X, pady=(0, 10))

        Label(main_frame, text="Stock*", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        self.stock_var = IntVar()
        Entry(main_frame, textvariable=self.stock_var, font=('Arial', 10), relief=SOLID, bd=1).pack(fill=X, pady=(0, 10))

        Label(main_frame, text="Min Stock", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        self.min_stock_var = IntVar()
        Entry(main_frame, textvariable=self.min_stock_var, font=('Arial', 10), relief=SOLID, bd=1).pack(fill=X, pady=(0, 10))

        Label(main_frame, text="Barcode", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        self.barcode_var = StringVar()
        Entry(main_frame, textvariable=self.barcode_var, font=('Arial', 10), relief=SOLID, bd=1).pack(fill=X, pady=(0, 10))

        Label(main_frame, text="Description", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        self.description_text = Text(main_frame, height=4, font=('Arial', 10), relief=SOLID, bd=1)
        self.description_text.pack(fill=BOTH, expand=True, pady=(0, 15))

        # Buttons
        btn_frame = Frame(main_frame, bg='white')
        btn_frame.pack(fill=X)

        Button(btn_frame, text="Save", command=self.save_product,
               font=('Arial', 11, 'bold'), bg=self.colors['success'], fg='white',
               relief=FLAT, pady=8, padx=20).pack(side=LEFT, padx=(0, 10))
        Button(btn_frame, text="Cancel", command=self.destroy,
               font=('Arial', 11, 'bold'), bg=self.colors['dark'], fg='white',
               relief=FLAT, pady=8, padx=20).pack(side=LEFT)

        # Bind Enter key to save
        self.bind('<Return>', lambda e: self.save_product())

    def load_product_data(self):
        self.name_var.set(self.product['name'])
        
        # Set category
        categories = DataManager.get_categories()
        category_names = [c['name'] for c in categories]
        self.category_combo['values'] = category_names
        
        for category in categories:
            if category['id'] == self.product['category_id']:
                self.category_var.set(category['name'])
                break
        
        self.price_var.set(self.product['price'])
        self.cost_var.set(self.product['cost'])
        self.stock_var.set(self.product['stock'])
        self.min_stock_var.set(self.product['min_stock'])
        self.barcode_var.set(self.product['barcode'] or '')
        self.description_text.insert('1.0', self.product['description'] or '')

    def save_product(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Validation Error", "Product name is required.")
            return

        try:
            price = float(self.price_var.get())
            if price <= 0:
                messagebox.showerror("Validation Error", "Price must be greater than zero.")
                return
        except:
            messagebox.showerror("Validation Error", "Please enter a valid price.")
            return

        try:
            cost = float(self.cost_var.get())
            if cost < 0:
                messagebox.showerror("Validation Error", "Cost cannot be negative.")
                return
        except:
            messagebox.showerror("Validation Error", "Please enter a valid cost.")
            return

        try:
            stock = int(self.stock_var.get())
            if stock < 0:
                messagebox.showerror("Validation Error", "Stock cannot be negative.")
                return
        except:
            messagebox.showerror("Validation Error", "Please enter a valid stock quantity.")
            return

        try:
            min_stock = int(self.min_stock_var.get())
            if min_stock < 0:
                messagebox.showerror("Validation Error", "Min stock cannot be negative.")
                return
        except:
            messagebox.showerror("Validation Error", "Please enter a valid min stock quantity.")
            return

        barcode = self.barcode_var.get().strip()
        description = self.description_text.get('1.0', END).strip()

        # Get category ID
        category_name = self.category_var.get()
        categories = DataManager.get_categories()
        category_id = None
        for category in categories:
            if category['name'] == category_name:
                category_id = category['id']
                break

        try:
            if self.product:  # Edit existing
                with DatabaseManager.get_conn() as conn:
                    conn.execute("""
                        UPDATE products SET 
                            name=?, category_id=?, price=?, cost=?, stock=?, 
                            min_stock=?, barcode=?, description=?, updated_at=CURRENT_TIMESTAMP
                        WHERE id=?
                    """, (name, category_id, price, cost, stock, min_stock, barcode, description, self.product['id']))
                    conn.commit()
                messagebox.showinfo("Success", "Product updated successfully.")
            else:  # Add New
                with DatabaseManager.get_conn() as conn:
                    conn.execute("""
                        INSERT INTO products 
                            (name, category_id, price, cost, stock, min_stock, barcode, description)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (name, category_id, price, cost, stock, min_stock, barcode, description))
                    conn.commit()
                messagebox.showinfo("Success", "Product created successfully.")
            self.result = True
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save product: {str(e)}")

    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class StockUpdateDialog(Toplevel):
    """Dialog for updating product stock"""
    def __init__(self, parent, product_id, product_name, current_stock):
        super().__init__(parent)
        self.parent = parent
        self.product_id = product_id
        self.product_name = product_name
        self.current_stock = current_stock
        self.result = None
        
        # Add colors attribute if parent doesn't have it
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors if parent doesn't have them
            self.colors = {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'success': '#27ae60',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'light': '#ecf0f1',
                'dark': '#34495e',
                'white': '#ffffff',
                'accent': '#bb8fce',
                'info': '#48c9b0'
            }

        self.title("Update Stock")
        self.geometry("400x250")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.center_window()

    def create_widgets(self):
        main_frame = Frame(self, bg='white', padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)

        Label(main_frame, text=f"Update Stock: {self.product_name}", font=('Arial', 14, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=(0, 15))

        # Current stock
        stock_frame = Frame(main_frame, bg='white')
        stock_frame.pack(fill=X, pady=(0, 15))
        Label(stock_frame, text="Current Stock:", font=('Arial', 10, 'bold'), bg='white').pack(side=LEFT)
        Label(stock_frame, text=str(self.current_stock), font=('Arial', 12, 'bold'), bg='white', fg=self.colors['info']).pack(side=RIGHT)

        # Update options
        Label(main_frame, text="Update Option:", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        self.update_var = StringVar(value="set")
        Radiobutton(main_frame, text="Set to specific value", variable=self.update_var, value="set", bg='white').pack(anchor='w')
        Radiobutton(main_frame, text="Add to current stock", variable=self.update_var, value="add", bg='white').pack(anchor='w')
        Radiobutton(main_frame, text="Subtract from current stock", variable=self.update_var, value="subtract", bg='white').pack(anchor='w')

        # Amount
        Label(main_frame, text="Amount:", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X, pady=(10, 0))
        self.amount_var = IntVar(value=0)
        Entry(main_frame, textvariable=self.amount_var, font=('Arial', 12), relief=SOLID, bd=1).pack(fill=X, pady=(5, 15))

        # Buttons
        btn_frame = Frame(main_frame, bg='white')
        btn_frame.pack(fill=X)

        Button(btn_frame, text="Update", command=self.update_stock,
               font=('Arial', 11, 'bold'), bg=self.colors['success'], fg='white',
               relief=FLAT, pady=8).pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        Button(btn_frame, text="Cancel", command=self.destroy,
               font=('Arial', 11, 'bold'), bg=self.colors['dark'], fg='white',
               relief=FLAT, pady=8).pack(side=LEFT, fill=X, expand=True, padx=(5, 0))

        # Bind Enter key to update
        self.bind('<Return>', lambda e: self.update_stock())

    def update_stock(self):
        try:
            amount = int(self.amount_var.get())
            if amount < 0:
                messagebox.showerror("Validation Error", "Amount cannot be negative.")
                return

            update_type = self.update_var.get()
            new_stock = self.current_stock

            if update_type == "set":
                new_stock = amount
            elif update_type == "add":
                new_stock = self.current_stock + amount
            elif update_type == "subtract":
                if amount > self.current_stock:
                    messagebox.showerror("Validation Error", "Cannot subtract more than current stock.")
                    return
                new_stock = self.current_stock - amount

            if new_stock < 0:
                messagebox.showerror("Validation Error", "Stock cannot be negative.")
                return

            # Update the database
            with DatabaseManager.get_conn() as conn:
                conn.execute("UPDATE products SET stock = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", 
                            (new_stock, self.product_id))
                conn.commit()

            self.result = new_stock
            messagebox.showinfo("Success", f"Stock updated to {new_stock}.")
            self.destroy()

        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid integer amount.")

    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class CustomerManagerDialog(Toplevel):
    """Customer management dialog"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Add colors attribute if parent doesn't have it
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors if parent doesn't have them
            self.colors = {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'success': '#27ae60',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'light': '#ecf0f1',
                'dark': '#34495e',
                'white': '#ffffff',
                'accent': '#bb8fce',
                'info': '#48c9b0'
            }
            
        self.title("Customer Manager")
        self.geometry("800x500")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.load_customers()
        self.center_window()

    def create_widgets(self):
        main_frame = Frame(self, bg='white', padx=10, pady=10)
        main_frame.pack(fill=BOTH, expand=True)

        # Header
        header_frame = Frame(main_frame, bg='white')
        header_frame.pack(fill=X, pady=(0, 10))
        Label(header_frame, text="Customer Manager", font=('Arial', 16, 'bold'), bg='white', fg=self.colors['primary']).pack(side=LEFT)
        Button(header_frame, text="Add Customer", command=self.add_customer,
               font=('Arial', 10, 'bold'), bg=self.colors['success'], fg='white', relief=FLAT).pack(side=RIGHT)

        # Search
        search_frame = Frame(main_frame, bg='white')
        search_frame.pack(fill=X, pady=(0, 10))
        Label(search_frame, text="Search:", font=('Arial', 10, 'bold'), bg='white').pack(side=LEFT, padx=(0, 5))
        self.search_var = StringVar()
        Entry(search_frame, textvariable=self.search_var, font=('Arial', 10)).pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        Button(search_frame, text="Search", command=self.search_customers,
               font=('Arial', 10, 'bold'), bg=self.colors['primary'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(search_frame, text="Clear", command=self.clear_search,
               font=('Arial', 10, 'bold'), bg=self.colors['dark'], fg='white', relief=FLAT).pack(side=LEFT)

        # Customer list
        list_frame = Frame(main_frame, bg='white')
        list_frame.pack(fill=BOTH, expand=True, pady=(0, 10))

        # Treeview for customers
        columns = ('ID', 'Name', 'Phone', 'Email')
        self.customer_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.customer_tree.heading(col, text=col)
            self.customer_tree.column(col, width=100)
        self.customer_tree.pack(side=LEFT, fill=BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.customer_tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.customer_tree.configure(yscrollcommand=scrollbar.set)

        # Buttons
        btn_frame = Frame(main_frame, bg='white')
        btn_frame.pack(fill=X)

        Button(btn_frame, text="Edit", command=self.edit_customer,
               font=('Arial', 10, 'bold'), bg=self.colors['secondary'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Delete", command=self.delete_customer,
               font=('Arial', 10, 'bold'), bg=self.colors['danger'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="View Purchases", command=self.view_purchases,
               font=('Arial', 10, 'bold'), bg=self.colors['info'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Refresh", command=self.load_customers,
               font=('Arial', 10, 'bold'), bg=self.colors['primary'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Close", command=self.destroy,
               font=('Arial', 10, 'bold'), bg=self.colors['dark'], fg='white', relief=FLAT).pack(side=RIGHT)

        # Bind double-click to edit
        self.customer_tree.bind('<Double-1>', lambda e: self.edit_customer())

    def load_customers(self):
        # Clear existing items
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)

        # Get customers
        customers = DataManager.get_customers()

        for customer in customers:
            self.customer_tree.insert('', 'end', iid=str(customer['id']),
                                   values=(
                                       customer['id'],
                                       customer['name'],
                                       customer['phone'] or 'N/A',
                                       customer['email'] or 'N/A'
                                   ))

    def search_customers(self):
        query = self.search_var.get().strip()
        
        # Clear existing items
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        
        # Get customers with search
        customers = DataManager.get_customers(search_query=query)
        
        for customer in customers:
            self.customer_tree.insert('', 'end', iid=str(customer['id']),
                                   values=(
                                       customer['id'],
                                       customer['name'],
                                       customer['phone'] or 'N/A',
                                       customer['email'] or 'N/A'
                                   ))

    def clear_search(self):
        self.search_var.set("")
        self.load_customers()

    def add_customer(self):
        dialog = CustomerFormDialog(self)
        if dialog.result:
            self.load_customers()

    def edit_customer(self):
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a customer to edit.")
            return
        
        customer_id = int(selection[0])
        customer = None
        
        # Find the customer in the database
        for c in DataManager.get_customers():
            if c['id'] == customer_id:
                customer = c
                break
        
        if customer:
            dialog = CustomerFormDialog(self, customer)
            if dialog.result:
                self.load_customers()

    def delete_customer(self):
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a customer to delete.")
            return
        
        customer_id = int(selection[0])
        customer_name = self.customer_tree.item(selection[0])['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{customer_name}'?"):
            with DatabaseManager.get_conn() as conn:
                conn.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
                conn.commit()
            self.load_customers()
            messagebox.showinfo("Success", f"Customer '{customer_name}' has been deleted.")

    def view_purchases(self):
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a customer to view purchases.")
            return
        
        customer_id = int(selection[0])
        customer_name = self.customer_tree.item(selection[0])['values'][1]
        
        # Get customer purchases
        purchases = DataManager.get_customer_purchases(customer_id)
        
        if not purchases:
            messagebox.showinfo("No Purchases", f"No purchase history found for {customer_name}.")
            return
        
        # Create purchase history dialog
        purchase_dialog = Toplevel(self)
        purchase_dialog.title(f"Purchase History - {customer_name}")
        purchase_dialog.geometry("700x400")
        purchase_dialog.transient(self)
        purchase_dialog.grab_set()
        
        main_frame = Frame(purchase_dialog, bg='white', padx=15, pady=15)
        main_frame.pack(fill=BOTH, expand=True)
        
        Label(main_frame, text=f"Purchase History for {customer_name}", font=('Arial', 14, 'bold'), 
              bg='white', fg=self.colors['primary']).pack(pady=(0, 10))
        
        # Treeview for purchases
        columns = ('Date', 'Receipt #', 'Total')
        purchase_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=10)
        for col in columns:
            purchase_tree.heading(col, text=col)
            purchase_tree.column(col, width=150)
        purchase_tree.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=purchase_tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        purchase_tree.configure(yscrollcommand=scrollbar.set)
        
        # Populate treeview
        currency = self.parent.settings.get('currency_symbol', 'PKR')
        for purchase in purchases:
            dt = datetime.datetime.fromisoformat(purchase['created_at'])
            date_str = dt.strftime('%Y-%m-%d %H:%M')
            purchase_tree.insert('', 'end', values=(
                date_str,
                purchase['receipt_number'],
                f"{currency}{purchase['total']:.2f}"
            ))
        
        # Close button
        Button(main_frame, text="Close", command=purchase_dialog.destroy,
               font=('Arial', 10, 'bold'), bg=self.colors['dark'], fg='white', relief=FLAT).pack()
        
        purchase_dialog.center_window = lambda: purchase_dialog.geometry(
            f"+{self.winfo_x() + (self.winfo_width() // 2) - (purchase_dialog.winfo_width() // 2)}"
            f"+{self.winfo_y() + (self.winfo_height() // 2) - (purchase_dialog.winfo_height() // 2)}"
        )
        purchase_dialog.center_window()

    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class SalesReportDialog(Toplevel):
    """Sales report dialog with export options"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Add colors attribute if parent doesn't have it
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors if parent doesn't have them
            self.colors = {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'success': '#27ae60',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'light': '#ecf0f1',
                'dark': '#34495e',
                'white': '#ffffff',
                'accent': '#bb8fce',
                'info': '#48c9b0'
            }
            
        self.title("Sales Report")
        self.geometry("900x600")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.load_report_data()
        self.center_window()

    def create_widgets(self):
        main_frame = Frame(self, bg='white', padx=10, pady=10)
        main_frame.pack(fill=BOTH, expand=True)

        # Header
        header_frame = Frame(main_frame, bg='white')
        header_frame.pack(fill=X, pady=(0, 10))
        Label(header_frame, text="Sales Report", font=('Arial', 16, 'bold'), bg='white', fg=self.colors['primary']).pack(side=LEFT)

        # Date range
        date_frame = Frame(main_frame, bg='white')
        date_frame.pack(fill=X, pady=(0, 10))
        
        Label(date_frame, text="From:", font=('Arial', 10, 'bold'), bg='white').pack(side=LEFT, padx=(0, 5))
        self.from_date_var = StringVar(value=(datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d'))
        Entry(date_frame, textvariable=self.from_date_var, font=('Arial', 10)).pack(side=LEFT, padx=(0, 10))
        
        Label(date_frame, text="To:", font=('Arial', 10, 'bold'), bg='white').pack(side=LEFT, padx=(0, 5))
        self.to_date_var = StringVar(value=datetime.date.today().strftime('%Y-%m-%d'))
        Entry(date_frame, textvariable=self.to_date_var, font=('Arial', 10)).pack(side=LEFT, padx=(0, 10))
        
        Button(date_frame, text="Generate Report", command=self.load_report_data,
               font=('Arial', 10, 'bold'), bg=self.colors['primary'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        
        Button(date_frame, text="Today's Summary", command=self.show_daily_summary,
               font=('Arial', 10, 'bold'), bg=self.colors['success'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))

        # Summary statistics
        self.summary_frame = Frame(main_frame, bg='white', relief=SOLID, bd=1, padx=10, pady=10)
        self.summary_frame.pack(fill=X, pady=(0, 10))
        
        # Sales list
        list_frame = Frame(main_frame, bg='white')
        list_frame.pack(fill=BOTH, expand=True, pady=(0, 10))

        # Treeview for sales
        columns = ('Date', 'Receipt #', 'Customer', 'Subtotal', 'Discount', 'Tax', 'Total', 'Payment Method')
        self.sales_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=100)
        self.sales_tree.pack(side=LEFT, fill=BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.sales_tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.sales_tree.configure(yscrollcommand=scrollbar.set)

        # Buttons
        btn_frame = Frame(main_frame, bg='white')
        btn_frame.pack(fill=X)

        Button(btn_frame, text="Export to CSV", command=self.export_csv,
               font=('Arial', 10, 'bold'), bg=self.colors['secondary'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        
        if PANDAS_AVAILABLE:
            Button(btn_frame, text="Export to Excel", command=self.export_excel,
                   font=('Arial', 10, 'bold'), bg=self.colors['success'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        
        Button(btn_frame, text="View Details", command=self.view_sale_details,
               font=('Arial', 10, 'bold'), bg=self.colors['info'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Top 5 Products", command=self.show_top_products,
               font=('Arial', 10, 'bold'), bg=self.colors['accent'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Close", command=self.destroy,
               font=('Arial', 10, 'bold'), bg=self.colors['dark'], fg='white', relief=FLAT).pack(side=RIGHT)

        # Bind double-click to view details
        self.sales_tree.bind('<Double-1>', lambda e: self.view_sale_details())

    def load_report_data(self):
        try:
            from_date = self.from_date_var.get()
            to_date = self.to_date_var.get()
            
            # Clear existing items
            for item in self.sales_tree.get_children():
                self.sales_tree.delete(item)
            
            # Get sales data
            sales = DataManager.get_sales(from_date, to_date)
            currency = self.parent.settings.get('currency_symbol', 'PKR')
            
            # Calculate summary statistics
            total_sales = sum(s['total'] for s in sales)
            total_transactions = len(sales)
            avg_sale = total_sales / total_transactions if total_transactions > 0 else 0
            total_discount = sum(s['discount'] for s in sales)
            total_tax = sum(s['tax'] for s in sales)
            
            # Update summary
            for widget in self.summary_frame.winfo_children():
                widget.destroy()
            
            stats = [
                ("Total Sales:", f"{currency}{total_sales:.2f}"),
                ("Transactions:", str(total_transactions)),
                ("Avg. Sale:", f"{currency}{avg_sale:.2f}"),
                ("Total Discount:", f"{currency}{total_discount:.2f}"),
                ("Total Tax:", f"{currency}{total_tax:.2f}")
            ]
            
            for i, (label, value) in enumerate(stats):
                stat_frame = Frame(self.summary_frame, bg='white')
                stat_frame.grid(row=0, column=i, sticky='nsew', padx=5)
                self.summary_frame.columnconfigure(i, weight=1)
                
                Label(stat_frame, text=label, font=('Arial', 10, 'bold'), bg='white').pack()
                Label(stat_frame, text=value, font=('Arial', 12, 'bold'), bg='white', fg=self.colors['primary']).pack()
            
            # Populate sales tree
            for sale in sales:
                # Format date
                dt = datetime.datetime.fromisoformat(sale['created_at'])
                date_str = dt.strftime('%Y-%m-%d %H:%M')
                
                # Get customer name if available
                customer_name = sale['customer_name'] or "Walk-in"
                
                self.sales_tree.insert('', 'end', iid=str(sale['id']),
                                    values=(
                                        date_str,
                                        sale['receipt_number'],
                                        customer_name,
                                        f"{currency}{sale['subtotal']:.2f}",
                                        f"{currency}{sale['discount']:.2f}",
                                        f"{currency}{sale['tax']:.2f}",
                                        f"{currency}{sale['total']:.2f}",
                                        sale['payment_method']
                                    ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load report data: {str(e)}")

    def show_daily_summary(self):
        """Show daily sales summary popup"""
        today = datetime.date.today().strftime('%Y-%m-%d')
        self.from_date_var.set(today)
        self.to_date_var.set(today)
        self.load_report_data()
        
        # Create summary popup
        summary_popup = Toplevel(self)
        summary_popup.title("Daily Sales Summary")
        summary_popup.geometry("500x400")
        summary_popup.transient(self)
        summary_popup.grab_set()
        
        main_frame = Frame(summary_popup, bg='white', padx=15, pady=15)
        main_frame.pack(fill=BOTH, expand=True)
        
        Label(main_frame, text=f"Daily Sales Summary - {today}", font=('Arial', 14, 'bold'), 
              bg='white', fg=self.colors['primary']).pack(pady=(0, 15))
        
        # Get today's sales
        sales = DataManager.get_sales(today, today)
        currency = self.parent.settings.get('currency_symbol', 'PKR')
        
        # Calculate statistics
        total_sales = sum(s['total'] for s in sales)
        total_transactions = len(sales)
        avg_sale = total_sales / total_transactions if total_transactions > 0 else 0
        total_discount = sum(s['discount'] for s in sales)
        total_tax = sum(s['tax'] for s in sales)
        
        # Calculate profit (total - cost)
        total_profit = 0
        for sale in sales:
            sale_id = sale['id']
            _, items = DataManager.get_sale_details(sale_id)
            for item in items:
                # Get product cost
                with DatabaseManager.get_conn() as conn:
                    product = conn.execute("SELECT cost FROM products WHERE id = ?", (item['product_id'],)).fetchone()
                    if product:
                        cost = product['cost'] * item['quantity']
                        total_profit += (item['total_price'] - cost)
        
        # Display statistics
        stats = [
            ("Total Sales:", f"{currency}{total_sales:.2f}"),
            ("Transactions:", str(total_transactions)),
            ("Average Sale:", f"{currency}{avg_sale:.2f}"),
            ("Total Discount:", f"{currency}{total_discount:.2f}"),
            ("Total Tax:", f"{currency}{total_tax:.2f}"),
            ("Total Profit:", f"{currency}{total_profit:.2f}")
        ]
        
        for label, value in stats:
            stat_frame = Frame(main_frame, bg='white')
            stat_frame.pack(fill=X, pady=5)
            
            Label(stat_frame, text=label, font=('Arial', 11, 'bold'), bg='white').pack(side=LEFT)
            Label(stat_frame, text=value, font=('Arial', 11), bg='white', fg=self.colors['primary']).pack(side=RIGHT)
        
        # Close button
        Button(main_frame, text="Close", command=summary_popup.destroy,
               font=('Arial', 11, 'bold'), bg=self.colors['dark'], fg='white', relief=FLAT, pady=8).pack(pady=15)
        
        summary_popup.center_window = lambda: summary_popup.geometry(
            f"+{self.winfo_x() + (self.winfo_width() // 2) - (summary_popup.winfo_width() // 2)}"
            f"+{self.winfo_y() + (self.winfo_height() // 2) - (summary_popup.winfo_height() // 2)}"
        )
        summary_popup.center_window()

    def show_top_products(self):
        """Show top 5 products report"""
        top_products = DataManager.get_top_products(5)
        
        if not top_products:
            messagebox.showinfo("No Data", "No product sales data found.")
            return
        
        # Create top products popup
        top_popup = Toplevel(self)
        top_popup.title("Top 5 Products")
        top_popup.geometry("500x400")
        top_popup.transient(self)
        top_popup.grab_set()
        
        main_frame = Frame(top_popup, bg='white', padx=15, pady=15)
        main_frame.pack(fill=BOTH, expand=True)
        
        Label(main_frame, text="Top 5 Products by Sales Volume", font=('Arial', 14, 'bold'), 
              bg='white', fg=self.colors['primary']).pack(pady=(0, 15))
        
        # Create treeview for products
        columns = ('Rank', 'Product', 'Quantity Sold')
        product_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=10)
        for col in columns:
            product_tree.heading(col, text=col)
            product_tree.column(col, width=150)
        product_tree.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # Populate treeview
        for i, product in enumerate(top_products, 1):
            product_tree.insert('', 'end', values=(
                i,
                product['name'],
                product['total_quantity']
            ))
        
        # Close button
        Button(main_frame, text="Close", command=top_popup.destroy,
               font=('Arial', 11, 'bold'), bg=self.colors['dark'], fg='white', relief=FLAT, pady=8).pack()
        
        top_popup.center_window = lambda: top_popup.geometry(
            f"+{self.winfo_x() + (self.winfo_width() // 2) - (top_popup.winfo_width() // 2)}"
            f"+{self.winfo_y() + (self.winfo_height() // 2) - (top_popup.winfo_height() // 2)}"
        )
        top_popup.center_window()

    def view_sale_details(self):
        selection = self.sales_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a sale to view details.")
            return
        
        sale_id = int(selection[0])
        sale, items = DataManager.get_sale_details(sale_id)
        
        if not sale:
            messagebox.showerror("Error", "Could not retrieve sale details.")
            return
        
        # Create details dialog
        details_dialog = Toplevel(self)
        details_dialog.title("Sale Details")
        details_dialog.geometry("500x400")
        details_dialog.transient(self)
        details_dialog.grab_set()
        
        main_frame = Frame(details_dialog, bg='white', padx=15, pady=15)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Sale information
        info_frame = LabelFrame(main_frame, text="Sale Information", font=('Arial', 10, 'bold'), bg='white', padx=10, pady=10)
        info_frame.pack(fill=X, pady=(0, 10))
        
        dt = datetime.datetime.fromisoformat(sale['created_at'])
        currency = self.parent.settings.get('currency_symbol', 'PKR')
        
        info_text = f"Receipt #: {sale['receipt_number']}\n"
        info_text += f"Date: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
        info_text += f"Cashier: {sale['cashier_name']}\n"
        info_text += f"Payment Method: {sale['payment_method']}\n"
        
        Label(info_frame, text=info_text, font=('Arial', 10), bg='white', justify=LEFT).pack(anchor='w')
        
        # Items
        items_frame = LabelFrame(main_frame, text="Items", font=('Arial', 10, 'bold'), bg='white', padx=10, pady=10)
        items_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # Create treeview for items
        columns = ('Product', 'Quantity', 'Unit Price', 'Total')
        items_tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=8)
        for col in columns:
            items_tree.heading(col, text=col)
            items_tree.column(col, width=100)
        items_tree.pack(fill=BOTH, expand=True)
        
        for item in items:
            items_tree.insert('', 'end', values=(
                item['product_name'],
                item['quantity'],
                f"{currency}{item['unit_price']:.2f}",
                f"{currency}{item['total_price']:.2f}"
            ))
        
        # Totals
        totals_frame = LabelFrame(main_frame, text="Totals", font=('Arial', 10, 'bold'), bg='white', padx=10, pady=10)
        totals_frame.pack(fill=X)
        
        totals_text = f"Subtotal: {currency}{sale['subtotal']:.2f}\n"
        if sale['discount'] > 0:
            totals_text += f"Discount: -{currency}{sale['discount']:.2f}\n"
        totals_text += f"Tax: {currency}{sale['tax']:.2f}\n"
        totals_text += f"Total: {currency}{sale['total']:.2f}\n"
        totals_text += f"Paid: {currency}{sale['paid']:.2f}\n"
        totals_text += f"Change: {currency}{sale['change_amount']:.2f}"
        
        Label(totals_frame, text=totals_text, font=('Arial', 10, 'bold'), bg='white', justify=LEFT).pack(anchor='w')
        
        # Close button
        Button(main_frame, text="Close", command=details_dialog.destroy,
               font=('Arial', 10, 'bold'), bg=self.colors['dark'], fg='white', relief=FLAT).pack(pady=10)
        
        details_dialog.center_window = lambda: details_dialog.geometry(
            f"+{self.winfo_x() + (self.winfo_width() // 2) - (details_dialog.winfo_width() // 2)}"
            f"+{self.winfo_y() + (self.winfo_height() // 2) - (details_dialog.winfo_height() // 2)}"
        )
        details_dialog.center_window()

    def export_csv(self):
        try:
            # Get file path
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Sales Report"
            )
            
            if not file_path:
                return
            
            # Get sales data
            from_date = self.from_date_var.get()
            to_date = self.to_date_var.get()
            sales = DataManager.get_sales(from_date, to_date)
            
            # Write to CSV
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['Date', 'Receipt #', 'Customer', 'Subtotal', 'Discount', 'Tax', 'Total', 'Payment Method']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                currency = self.parent.settings.get('currency_symbol', 'PKR')
                
                for sale in sales:
                    # Format date
                    dt = datetime.datetime.fromisoformat(sale['created_at'])
                    date_str = dt.strftime('%Y-%m-%d %H:%M')
                    
                    # Get customer name if available
                    customer_name = sale['customer_name'] or "Walk-in"
                    
                    writer.writerow({
                        'Date': date_str,
                        'Receipt #': sale['receipt_number'],
                        'Customer': customer_name,
                        'Subtotal': f"{currency}{sale['subtotal']:.2f}",
                        'Discount': f"{currency}{sale['discount']:.2f}",
                        'Tax': f"{currency}{sale['tax']:.2f}",
                        'Total': f"{currency}{sale['total']:.2f}",
                        'Payment Method': sale['payment_method']
                    })
            
            messagebox.showinfo("Export Successful", f"Sales report exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")

    def export_excel(self):
        if not PANDAS_AVAILABLE:
            messagebox.showinfo("Export Not Available", "Excel export requires pandas library.")
            return
            
        try:
            # Get file path
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Export Sales Report"
            )
            
            if not file_path:
                return
            
            # Get sales data
            from_date = self.from_date_var.get()
            to_date = self.to_date_var.get()
            sales = DataManager.get_sales(from_date, to_date)
            
            # Prepare data for DataFrame
            data = []
            currency = self.parent.settings.get('currency_symbol', 'PKR')
            
            for sale in sales:
                # Format date
                dt = datetime.datetime.fromisoformat(sale['created_at'])
                date_str = dt.strftime('%Y-%m-%d %H:%M')
                
                # Get customer name if available
                customer_name = sale['customer_name'] or "Walk-in"
                
                data.append({
                    'Date': date_str,
                    'Receipt #': sale['receipt_number'],
                    'Customer': customer_name,
                    'Subtotal': f"{currency}{sale['subtotal']:.2f}",
                    'Discount': f"{currency}{sale['discount']:.2f}",
                    'Tax': f"{currency}{sale['tax']:.2f}",
                    'Total': f"{currency}{sale['total']:.2f}",
                    'Payment Method': sale['payment_method']
                })
            
            # Create DataFrame and export
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            
            messagebox.showinfo("Export Successful", f"Sales report exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")

    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class SettingsDialog(Toplevel):
    """System settings dialog"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Add colors attribute if parent doesn't have it
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors if parent doesn't have them
            self.colors = {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'success': '#27ae60',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'light': '#ecf0f1',
                'dark': '#34495e',
                'white': '#ffffff',
                'accent': '#bb8fce',
                'info': '#48c9b0'
            }
            
        self.title("System Settings")
        self.geometry("500x450")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.load_settings()
        self.center_window()

    def create_widgets(self):
        main_frame = Frame(self, bg='white', padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)

        # Header
        Label(main_frame, text="System Settings", font=('Arial', 16, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=(0, 20))

        # Form fields
        Label(main_frame, text="Tax Percent (%)", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        self.tax_var = StringVar()
        Entry(main_frame, textvariable=self.tax_var, font=('Arial', 10), relief=SOLID, bd=1).pack(fill=X, pady=(0, 10))

        Label(main_frame, text="Currency Symbol", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        
        # Create a frame for currency selection
        currency_frame = Frame(main_frame, bg='white')
        currency_frame.pack(fill=X, pady=(0, 10))
        
        # Currency options
        currencies = [
            ("US Dollar ($)", "$"),
            ("Euro (€)", "€"),
            ("British Pound (£)", "£"),
            ("Pakistani Rupee (PKR)", "PKR"),
            ("Japanese Yen (¥)", "¥"),
            ("Indian Rupee (₹)", "₹"),
            ("Custom", "custom")
        ]
        
        self.currency_option = StringVar()
        
        for text, value in currencies:
            Radiobutton(currency_frame, text=text, variable=self.currency_option, 
                        value=value, bg='white', command=self.update_currency_display).pack(anchor='w')
        
        # Custom currency entry
        self.custom_currency_frame = Frame(main_frame, bg='white')
        self.custom_currency_entry = Entry(self.custom_currency_frame, font=('Arial', 10), relief=SOLID, bd=1)
        self.custom_currency_entry.pack(side=LEFT, fill=X, expand=True)
    
        Label(main_frame, text="Cashier Name", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        self.cashier_var = StringVar()
        Entry(main_frame, textvariable=self.cashier_var, font=('Arial', 10), relief=SOLID, bd=1).pack(fill=X, pady=(0, 10))

        Label(main_frame, text="Receipt Footer", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        self.footer_text = Text(main_frame, height=4, font=('Arial', 10), relief=SOLID, bd=1)
        self.footer_text.pack(fill=BOTH, expand=True, pady=(0, 15))

        # Theme selection
        theme_frame = Frame(main_frame, bg='white')
        theme_frame.pack(fill=X, pady=(0, 15))
        
        Label(theme_frame, text="Theme:", font=('Arial', 10, 'bold'), bg='white').pack(side=LEFT, padx=(0, 5))
        self.theme_var = StringVar(value=self.parent.theme_manager.current_theme)
        Radiobutton(theme_frame, text="Light", variable=self.theme_var, value="light", bg='white').pack(side=LEFT, padx=5)
        Radiobutton(theme_frame, text="Dark", variable=self.theme_var, value="dark", bg='white').pack(side=LEFT, padx=5)

        # Backup and restore
        backup_frame = LabelFrame(main_frame, text="Backup & Restore", font=('Arial', 10, 'bold'), bg='white', padx=10, pady=10)
        backup_frame.pack(fill=X, pady=(0, 15))

        Button(backup_frame, text="Create Backup", command=self.create_backup,
               font=('Arial', 10, 'bold'), bg=self.colors['success'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(backup_frame, text="Restore Backup", command=self.restore_backup,
               font=('Arial', 10, 'bold'), bg=self.colors['warning'], fg='white', relief=FLAT).pack(side=LEFT)

        # Buttons
        btn_frame = Frame(main_frame, bg='white')
        btn_frame.pack(fill=X)

        Button(btn_frame, text="Save", command=self.save_settings,
               font=('Arial', 11, 'bold'), bg=self.colors['success'], fg='white',
               relief=FLAT, pady=8, padx=20).pack(side=LEFT, padx=(0, 10))
        Button(btn_frame, text="Cancel", command=self.destroy,
               font=('Arial', 11, 'bold'), bg=self.colors['dark'], fg='white',
               relief=FLAT, pady=8, padx=20).pack(side=LEFT)

        # Bind Enter key to save
        self.bind('<Return>', lambda e: self.save_settings())

    def update_currency_display(self):
        if self.currency_option.get() == "custom":
            self.custom_currency_frame.pack(fill=X, pady=(0, 10))
            self.currency_var.set(self.custom_currency_entry.get())
        else:
            self.custom_currency_frame.pack_forget()
            self.currency_var.set(self.currency_option.get())

    def load_settings(self):
        self.tax_var.set(self.parent.settings.get('tax_percent', '0'))
        
        # Load currency setting
        currency = self.parent.settings.get('currency_symbol', '$')
        
        # Check if currency matches any predefined option
        currencies = ["$", "€", "£", "PKR", "¥", "₹"]
        if currency in currencies:
            self.currency_option.set(currency)
            self.custom_currency_frame.pack_forget()
        else:
            self.currency_option.set("custom")
            self.custom_currency_entry.delete(0, END)
            self.custom_currency_entry.insert(0, currency)
            self.custom_currency_frame.pack(fill=X, pady=(0, 10))
        
        self.cashier_var.set(self.parent.settings.get('cashier_name', 'Admin'))
        self.footer_text.insert('1.0', self.parent.settings.get('receipt_footer', 'Thank you for your business!'))
        self.theme_var.set(self.parent.theme_manager.current_theme)

    def save_settings(self):
        try:
            tax_percent = float(self.tax_var.get())
            if tax_percent < 0 or tax_percent > 100:
                messagebox.showerror("Validation Error", "Tax percent must be between 0 and 100.")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid tax percent.")
            return

        currency_symbol = ""
        if self.currency_option.get() == "custom":
            currency_symbol = self.custom_currency_entry.get().strip()
        else:
            currency_symbol = self.currency_option.get()
        
        if not currency_symbol:
            messagebox.showerror("Validation Error", "Currency symbol is required.")
            return

        cashier_name = self.cashier_var.get().strip()
        if not cashier_name:
            messagebox.showerror("Validation Error", "Cashier name is required.")
            return

        receipt_footer = self.footer_text.get('1.0', END).strip()

        # Save settings
        DatabaseManager.set_setting('tax_percent', tax_percent)
        DatabaseManager.set_setting('currency_symbol', currency_symbol)
        DatabaseManager.set_setting('cashier_name', cashier_name)
        DatabaseManager.set_setting('receipt_footer', receipt_footer)
        DatabaseManager.set_setting('theme', self.theme_var.get())

        # Update parent settings
        self.parent.settings['tax_percent'] = str(tax_percent)
        self.parent.settings['currency_symbol'] = currency_symbol
        self.parent.settings['cashier_name'] = cashier_name
        self.parent.settings['receipt_footer'] = receipt_footer
        self.parent.tax_percent = tax_percent

        # Apply theme if changed
        if self.theme_var.get() != self.parent.theme_manager.current_theme:
            new_theme = self.parent.theme_manager.toggle_theme()
            self.parent.theme_manager.apply_styles(self.parent.style)
            self.parent.update_theme_colors()
            messagebox.showinfo("Theme Changed", f"Theme changed to {new_theme}. Restart may be required for full effect.")

        messagebox.showinfo("Success", "Settings saved successfully.")
        self.destroy()

    def create_backup(self):
        BackupRestoreManager.create_backup()

    def restore_backup(self):
        backups = BackupRestoreManager.list_backups()
        if not backups:
            messagebox.showinfo("No Backups", "No backup files found.")
            return

        # Create backup selection dialog
        backup_dialog = Toplevel(self)
        backup_dialog.title("Select Backup to Restore")
        backup_dialog.geometry("500x300")
        backup_dialog.transient(self)
        backup_dialog.grab_set()

        main_frame = Frame(backup_dialog, bg='white', padx=15, pady=15)
        main_frame.pack(fill=BOTH, expand=True)

        Label(main_frame, text="Select a backup file to restore:", font=('Arial', 12, 'bold'), bg='white').pack(pady=(0, 10))

        # List of backups
        list_frame = Frame(main_frame, bg='white')
        list_frame.pack(fill=BOTH, expand=True, pady=(0, 10))

        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        backup_listbox = Listbox(list_frame, yscrollcommand=scrollbar.set, font=('Arial', 10))
        backup_listbox.pack(fill=BOTH, expand=True)
        scrollbar.config(command=backup_listbox.yview)

        for backup in backups:
            filename = os.path.basename(backup)
            backup_listbox.insert(END, filename)

        # Buttons
        btn_frame = Frame(main_frame, bg='white')
        btn_frame.pack(fill=X)

        def restore_selected():
            selection = backup_listbox.curselection()
            if not selection:
                messagebox.showinfo("No Selection", "Please select a backup file.")
                return

            backup_file = backups[selection[0]]
            if messagebox.askyesno("Confirm Restore", 
                                  f"Are you sure you want to restore from {os.path.basename(backup_file)}?\n\n"
                                  "This will replace all current data with the backup data."):
                if BackupRestoreManager.restore_backup(backup_file):
                    backup_dialog.destroy()
                    self.destroy()
                    messagebox.showinfo("Restart Required", 
                                      "Backup restored successfully. Please restart the application for changes to take effect.")

        Button(btn_frame, text="Restore", command=restore_selected,
               font=('Arial', 10, 'bold'), bg=self.colors['warning'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Cancel", command=backup_dialog.destroy,
               font=('Arial', 10, 'bold'), bg=self.colors['dark'], fg='white', relief=FLAT).pack(side=RIGHT)

        backup_dialog.center_window = lambda: backup_dialog.geometry(
            f"+{self.winfo_x() + (self.winfo_width() // 2) - (backup_dialog.winfo_width() // 2)}"
            f"+{self.winfo_y() + (self.winfo_height() // 2) - (backup_dialog.winfo_height() // 2)}"
        )
        backup_dialog.center_window()

    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class QuickBarcodeAddDialog(Toplevel):
    """Quick barcode add dialog"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Add colors attribute if parent doesn't have it
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors if parent doesn't have them
            self.colors = {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'success': '#27ae60',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'light': '#ecf0f1',
                'dark': '#34495e',
                'white': '#ffffff',
                'accent': '#bb8fce',
                'info': '#48c9b0'
            }
            
        self.title("Quick Barcode Add")
        self.geometry("400x200")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.center_window()

    def create_widgets(self):
        main_frame = Frame(self, bg='white', padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)

        Label(main_frame, text="Enter or Scan Barcode", font=('Arial', 14, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=(0, 15))

        self.barcode_var = StringVar()
        barcode_entry = Entry(main_frame, textvariable=self.barcode_var, font=('Arial', 12), relief=SOLID, bd=1)
        barcode_entry.pack(fill=X, pady=(0, 15))
        barcode_entry.focus_set()

        # Buttons
        btn_frame = Frame(main_frame, bg='white')
        btn_frame.pack(fill=X)

        Button(btn_frame, text="Add to Cart", command=self.add_to_cart,
               font=('Arial', 11, 'bold'), bg=self.colors['success'], fg='white',
               relief=FLAT, pady=8).pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        Button(btn_frame, text="Cancel", command=self.destroy,
               font=('Arial', 11, 'bold'), bg=self.colors['dark'], fg='white',
               relief=FLAT, pady=8).pack(side=LEFT, fill=X, expand=True, padx=(5, 0))

        # Bind events
        barcode_entry.bind('<Return>', lambda e: self.add_to_cart())
        barcode_entry.bind('<KeyRelease>', self.on_input_change)

    def on_input_change(self, event):
        barcode = self.barcode_var.get()
        if len(barcode) >= 8:  # Minimum barcode length
            self.after(500, self.add_to_cart)  # Process after slight delay

    def add_to_cart(self, event=None):
        barcode = self.barcode_var.get().strip()
        if not barcode:
            return

        product = DataManager.get_product_by_barcode(barcode)
        if product:
            self.parent.add_to_cart(product)
            self.destroy()
        else:
            messagebox.showinfo("Product Not Found", f"No product found with barcode: {barcode}")

    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class CategoryManagerDialog(Toplevel):
    """Dialog for managing product categories"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Add colors attribute if parent doesn't have it
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors if parent doesn't have them
            self.colors = {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'success': '#27ae60',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'light': '#ecf0f1',
                'dark': '#34495e',
                'white': '#ffffff',
                'accent': '#bb8fce',
                'info': '#48c9b0'
            }
            
        self.title("Category Manager")
        self.geometry("600x400")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.load_categories()
        self.center_window()

    def create_widgets(self):
        main_frame = Frame(self, bg='white', padx=15, pady=15)
        main_frame.pack(fill=BOTH, expand=True)

        Label(main_frame, text="Category Manager", font=('Arial', 14, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=(0, 10))

        # Category list
        list_frame = Frame(main_frame, bg='white')
        list_frame.pack(fill=BOTH, expand=True, pady=(0, 10))

        # Treeview for categories
        columns = ('ID', 'Name', 'Description')
        self.category_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        for col in columns:
            self.category_tree.heading(col, text=col)
            self.category_tree.column(col, width=150)
        self.category_tree.pack(side=LEFT, fill=BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.category_tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.category_tree.configure(yscrollcommand=scrollbar.set)

        # Buttons
        btn_frame = Frame(main_frame, bg='white')
        btn_frame.pack(fill=X)

        Button(btn_frame, text="Add Category", command=self.add_category,
               font=('Arial', 10, 'bold'), bg=self.colors['success'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Edit Category", command=self.edit_category,
               font=('Arial', 10, 'bold'), bg=self.colors['secondary'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Delete Category", command=self.delete_category,
               font=('Arial', 10, 'bold'), bg=self.colors['danger'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Refresh", command=self.load_categories,
               font=('Arial', 10, 'bold'), bg=self.colors['primary'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Close", command=self.destroy,
               font=('Arial', 10, 'bold'), bg=self.colors['dark'], fg='white', relief=FLAT).pack(side=RIGHT)

        # Bind double-click to edit
        self.category_tree.bind('<Double-1>', lambda e: self.edit_category())

    def load_categories(self):
        # Clear existing items
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)

        # Get categories
        categories = DataManager.get_categories()

        for category in categories:
            self.category_tree.insert('', 'end', iid=str(category['id']),
                                   values=(
                                       category['id'],
                                       category['name'],
                                       category['description'] or 'N/A'
                                   ))

    def add_category(self):
        dialog = CategoryFormDialog(self)
        if dialog.result:
            self.load_categories()

    def edit_category(self):
        selection = self.category_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a category to edit.")
            return
        
        category_id = int(selection[0])
        category = None
        
        # Find the category in the database
        for c in DataManager.get_categories():
            if c['id'] == category_id:
                category = c
                break
        
        if category:
            dialog = CategoryFormDialog(self, category)
            if dialog.result:
                self.load_categories()

    def delete_category(self):
        selection = self.category_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a category to delete.")
            return
        
        category_id = int(selection[0])
        category_name = self.category_tree.item(selection[0])['values'][1]
        
        # Check if category is in use
        with DatabaseManager.get_conn() as conn:
            products = conn.execute("SELECT COUNT(*) FROM products WHERE category_id = ?", (category_id,)).fetchone()
            if products[0] > 0:
                messagebox.showerror("Cannot Delete", 
                                    f"Category '{category_name}' is in use by {products[0]} product(s).\n\n"
                                    "Please reassign or delete these products first.")
                return
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{category_name}'?"):
            with DatabaseManager.get_conn() as conn:
                conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
                conn.commit()
            self.load_categories()
            messagebox.showinfo("Success", f"Category '{category_name}' has been deleted.")

    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class CategoryFormDialog(Toplevel):
    """Dialog for adding/editing categories"""
    def __init__(self, parent, category=None):
        super().__init__(parent)
        self.parent = parent
        self.category = category
        self.result = None
        
        # Add colors attribute if parent doesn't have it
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors if parent doesn't have them
            self.colors = {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'success': '#27ae60',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'light': '#ecf0f1',
                'dark': '#34495e',
                'white': '#ffffff',
                'accent': '#bb8fce',
                'info': '#48c9b0'
            }

        title = "Edit Category" if category else "Add Category"
        self.title(title)
        self.geometry("450x250")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        if category:
            self.load_category_data()
        self.center_window()

    def create_widgets(self):
        main_frame = Frame(self, bg='white', padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)

        # Header
        Label(main_frame, text=self.title(), font=('Arial', 16, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=(0, 20))

        # Form fields
        Label(main_frame, text="Name*", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        self.name_var = StringVar()
        Entry(main_frame, textvariable=self.name_var, font=('Arial', 10), relief=SOLID, bd=1).pack(fill=X, pady=(0, 10))

        Label(main_frame, text="Description", font=('Arial', 10, 'bold'), bg='white', anchor='w').pack(fill=X)
        self.description_text = Text(main_frame, height=4, font=('Arial', 10), relief=SOLID, bd=1)
        self.description_text.pack(fill=BOTH, expand=True, pady=(0, 15))

        # Buttons
        btn_frame = Frame(main_frame, bg='white')
        btn_frame.pack(fill=X)

        Button(btn_frame, text="Save", command=self.save_category,
               font=('Arial', 11, 'bold'), bg=self.colors['success'], fg='white',
               relief=FLAT, pady=8, padx=20).pack(side=LEFT, padx=(0, 10))
        Button(btn_frame, text="Cancel", command=self.destroy,
               font=('Arial', 11, 'bold'), bg=self.colors['dark'], fg='white',
               relief=FLAT, pady=8, padx=20).pack(side=LEFT)

        # Bind Enter key to save
        self.bind('<Return>', lambda e: self.save_category())

    def load_category_data(self):
        self.name_var.set(self.category['name'])
        self.description_text.insert('1.0', self.category['description'] or '')

    def save_category(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Validation Error", "Category name is required.")
            return

        description = self.description_text.get('1.0', END).strip()

        try:
            if self.category:  # Edit existing
                with DatabaseManager.get_conn() as conn:
                    conn.execute("""
                        UPDATE categories SET 
                            name=?, description=?
                        WHERE id=?
                    """, (name, description, self.category['id']))
                    conn.commit()
                messagebox.showinfo("Success", "Category updated successfully.")
            else:  # Add New
                with DatabaseManager.get_conn() as conn:
                    conn.execute("""
                        INSERT INTO categories (name, description)
                        VALUES (?, ?)
                    """, (name, description))
                    conn.commit()
                messagebox.showinfo("Success", "Category created successfully.")
            self.result = True
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save category: {str(e)}")

    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class CartViewDialog(Toplevel):
    """Dialog for viewing and managing cart items"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Add colors attribute if parent doesn't have it
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors if parent doesn't have them
            self.colors = {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'success': '#27ae60',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'light': '#ecf0f1',
                'dark': '#34495e',
                'white': '#ffffff',
                'accent': '#bb8fce',
                'info': '#48c9b0'
            }
            
        self.title("Shopping Cart")
        self.geometry("600x400")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.load_cart_items()
        self.center_window()

    def create_widgets(self):
        main_frame = Frame(self, bg='white', padx=15, pady=15)
        main_frame.pack(fill=BOTH, expand=True)

        Label(main_frame, text="Shopping Cart", font=('Arial', 14, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=(0, 10))

        # Cart items
        columns = ('ID', 'Name', 'Price', 'Quantity', 'Total')
        self.cart_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=10)
        for col in columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=100)
        self.cart_tree.pack(fill=BOTH, expand=True, pady=(0, 10))

        # Buttons
        btn_frame = Frame(main_frame, bg='white')
        btn_frame.pack(fill=X)

        Button(btn_frame, text="Edit Quantity", command=self.edit_quantity,
               font=('Arial', 10, 'bold'), bg=self.colors['secondary'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Remove Item", command=self.remove_item,
               font=('Arial', 10, 'bold'), bg=self.colors['danger'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Checkout", command=self.checkout,
               font=('Arial', 12, 'bold'), bg=self.colors['success'], fg='white', relief=FLAT, width=15).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Close", command=self.destroy,
               font=('Arial', 10, 'bold'), bg=self.colors['dark'], fg='white', relief=FLAT).pack(side=RIGHT)

    def load_cart_items(self):
        # Clear existing items
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        currency = self.parent.settings.get('currency_symbol', 'PKR')
        
        for i, item in enumerate(self.parent.cart):
            total = item['price'] * item['qty']
            self.cart_tree.insert('', 'end', iid=str(i), values=(
                item['id'],
                item['name'],
                f"{currency}{item['price']:.2f}",
                item['qty'],
                f"{currency}{total:.2f}"
            ))

    def edit_quantity(self):
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select an item to edit.")
            return
        
        index = int(selection[0])
        cart_item = self.parent.cart[index]
        
        dialog = QuantityEditDialog(self.parent, cart_item)
        self.wait_window(dialog)  # Wait for dialog to close
        
        if dialog.result is not None:
            if dialog.result == 0:  # Remove signal
                del self.parent.cart[index]
                self.parent.show_notification("Item removed from cart", "info")
            else:  # Update quantity
                self.parent.cart[index]['qty'] = dialog.result
                self.parent.show_notification(f"Updated quantity for {cart_item['name']}", "success")
            
            # Refresh cart display and totals
            self.load_cart_items()
            self.parent.refresh_cart()

    def remove_item(self):
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select an item to remove.")
            return
        
        index = int(selection[0])
        del self.parent.cart[index]
        self.load_cart_items()
        self.parent.refresh_cart()

    def checkout(self):
        self.destroy()
        self.parent.checkout()

    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


class HoldCartDialog(Toplevel):
    """Dialog for managing held carts"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Add colors attribute if parent doesn't have it
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors if parent doesn't have them
            self.colors = {
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'success': '#27ae60',
                'warning': '#f39c12',
                'danger': '#e74c3c',
                'light': '#ecf0f1',
                'dark': '#34495e',
                'white': '#ffffff',
                'accent': '#bb8fce',
                'info': '#48c9b0'
            }
            
        self.title("Hold/Resume Cart")
        self.geometry("700x400")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.load_held_carts()
        self.center_window()

    def create_widgets(self):
        main_frame = Frame(self, bg='white', padx=15, pady=15)
        main_frame.pack(fill=BOTH, expand=True)

        Label(main_frame, text="Hold/Resume Cart", font=('Arial', 14, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=(0, 10))

        # Held carts list
        list_frame = Frame(main_frame, bg='white')
        list_frame.pack(fill=BOTH, expand=True, pady=(0, 10))

        # Treeview for held carts
        columns = ('ID', 'Customer', 'Items', 'Created At')
        self.cart_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        for col in columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=150)
        self.cart_tree.pack(side=LEFT, fill=BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.cart_tree.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.cart_tree.configure(yscrollcommand=scrollbar.set)

        # Buttons
        btn_frame = Frame(main_frame, bg='white')
        btn_frame.pack(fill=X)

        Button(btn_frame, text="Resume Cart", command=self.resume_cart,
               font=('Arial', 10, 'bold'), bg=self.colors['success'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Delete Cart", command=self.delete_cart,
               font=('Arial', 10, 'bold'), bg=self.colors['danger'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Refresh", command=self.load_held_carts,
               font=('Arial', 10, 'bold'), bg=self.colors['primary'], fg='white', relief=FLAT).pack(side=LEFT, padx=(0, 5))
        Button(btn_frame, text="Close", command=self.destroy,
               font=('Arial', 10, 'bold'), bg=self.colors['dark'], fg='white', relief=FLAT).pack(side=RIGHT)

        # Bind double-click to resume
        self.cart_tree.bind('<Double-1>', lambda e: self.resume_cart())

    def load_held_carts(self):
        # Clear existing items
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        # Get held carts
        held_carts = DataManager.get_held_carts()

        for cart in held_carts:
            # Parse cart data to count items
            cart_data = json.loads(cart['cart_data'])
            item_count = sum(item['qty'] for item in cart_data)
            
            # Format datetime
            dt = datetime.datetime.fromisoformat(cart['created_at'])
            time_str = dt.strftime('%Y-%m-%d %H:%M')
            
            self.cart_tree.insert('', 'end', iid=str(cart['id']),
                               values=(
                                   cart['id'],
                                   cart['customer_name'] or 'Walk-in',
                                   f"{item_count} items",
                                   time_str
                               ))

    def resume_cart(self):
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a cart to resume.")
            return
        
        cart_id = int(selection[0])
        cart_data, customer_id = DataManager.get_held_cart(cart_id)
        
        if cart_data:
            # Confirm with user
            if messagebox.askyesno("Resume Cart", "This will replace your current cart. Continue?"):
                # Load the cart
                self.parent.cart = cart_data
                
                # Load customer if available
                if customer_id:
                    customers = DataManager.get_customers()
                    for customer in customers:
                        if customer['id'] == customer_id:
                            self.parent.selected_customer = customer
                            self.parent.customer_label.configure(text=f"{customer['name']} ({customer['phone'] or 'No Phone'})")
                            break
                
                # Delete held cart
                DataManager.delete_held_cart(cart_id)
                
                # Refresh display
                self.parent.refresh_cart()
                self.parent.show_notification("Cart resumed successfully", "success")
                
                # Close dialog
                self.destroy()

    def delete_cart(self):
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a cart to delete.")
            return
        
        cart_id = int(selection[0])
        
        if messagebox.askyesno("Delete Cart", "Are you sure you want to delete this held cart?"):
            DataManager.delete_held_cart(cart_id)
            self.load_held_carts()
            messagebox.showinfo("Success", "Held cart deleted successfully.")

    def center_window(self):
        self.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")


# --- Main Application ---
class ModernPOSApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("Professional POS System v2.0")
        self.geometry("1400x900")
        self.state('zoomed') # Maximize on Windows

        # Initialize managers
        self.theme_manager = ModernThemeManager()
        self.colors = self.theme_manager.colors

        # Initialize database
        DatabaseManager.init_db()

        # Load settings
        self.load_settings()

        # Initialize variables
        self.cart = []
        self.selected_customer = None
        self.barcode_buffer = ""
        self.last_barcode_time = time.time()
        self.selected_category_id = None
        self.product_card_cache = {}

        # Initialize totals variables BEFORE creating widgets
        self.subtotal_var = StringVar(value="PKR0.00")
        self.discount_amount_var = StringVar(value="PKR0.00")
        self.tax_var = StringVar(value="PKR0.00")
        self.total_var = StringVar(value="PKR0.00")

        # Setup UI
        self.setup_modern_styles()
        self.create_widgets()
        self.bind_shortcuts()
        self.bind_barcode_scanner()
        self.update_time()
        self.update_dashboard()
        self.check_low_stock()

    def load_settings(self):
        settings_keys = ['tax_percent', 'currency_symbol', 'receipt_footer', 'cashier_name', 'theme']
        self.settings = {}
        for key in settings_keys:
            self.settings[key] = DataManager.get_setting(key) or ""
        self.tax_percent = float(self.settings.get('tax_percent', 0))
        
        # Apply theme setting
        theme = self.settings.get('theme', 'light')
        if theme != self.theme_manager.current_theme:
            self.theme_manager.toggle_theme()

    def setup_modern_styles(self):
        """Configure modern styling with better colors and themes"""
        self.style = ttk.Style()
        self.theme_manager.apply_styles(self.style)

    def create_widgets(self):
        # Main container with professional layout
        main_container = Frame(self, bg=self.colors['primary'])
        main_container.pack(fill=BOTH, expand=True)

        # Top header with gradient effect
        header_frame = Frame(main_container, bg=self.colors['primary'], height=70)
        header_frame.pack(fill=X)
        header_frame.pack_propagate(False)

        # App title with modern styling
        title_container = Frame(header_frame, bg=self.colors['primary'])
        title_container.pack(side=LEFT, padx=20, pady=10)
        
        title_frame = Frame(title_container, bg=self.colors['dark'], padx=15, pady=5)
        title_frame.pack()
        
        Label(title_frame, text="POS", font=('Arial', 28, 'bold'), bg=self.colors['dark'], fg='white').pack()
        Label(title_frame, text="Professional POS System", font=('Arial', 12), bg=self.colors['dark'], fg=self.colors['light']).pack()

        # Time and date display with card effect
        time_frame = Frame(header_frame, bg=self.colors['primary'])
        time_frame.pack(side=RIGHT, padx=20, pady=10)
        time_card = Frame(time_frame, bg='white', padx=15, pady=10, relief=RIDGE, bd=2)
        time_card.pack()
        self.time_label = Label(time_card, font=('Arial', 12, 'bold'), bg='white', fg=self.colors['dark'])
        self.time_label.pack()
        self.day_label = Label(time_card, font=('Arial', 10), bg='white', fg=self.colors['secondary'])
        self.day_label.pack()

        # Barcode scanner status
        barcode_frame = Frame(header_frame, bg=self.colors['primary'])
        barcode_frame.pack(side=RIGHT, padx=(0, 20), pady=10)
        barcode_card = Frame(barcode_frame, bg=self.colors['success'], padx=10, pady=5, relief=RIDGE, bd=1)
        barcode_card.pack()
        self.barcode_label = Label(barcode_card, text="📱 Barcode Ready", font=('Arial', 10, 'bold'), bg=self.colors['success'], fg='white')
        self.barcode_label.pack()

        # Theme toggle button
        theme_btn = Button(header_frame, text="🌓", command=self.toggle_theme,
                          font=('Arial', 12), bg=self.colors['dark'], fg='white',
                          relief=FLAT, padx=10, pady=5)
        theme_btn.pack(side=RIGHT, padx=(0, 10), pady=10)

        # Enhanced toolbar with modern buttons
        toolbar_frame = Frame(main_container, bg=self.colors['light'], height=60)
        toolbar_frame.pack(fill=X, padx=10, pady=5)
        toolbar_frame.pack_propagate(False)

        toolbar_buttons = [
            ("🔍 Search", self.show_search_dialog, self.colors['secondary']),
            ("📦 Products", self.open_product_manager, self.colors['primary']),
            ("👥 Customers", self.open_customer_manager, self.colors['accent']),
            ("📊 Reports", self.open_sales_report, self.colors['info']),
            ("⚙️ Settings", self.open_settings, self.colors['dark']),
            ("📋 History", self.show_transaction_history, self.colors['info']),
            ("❓ Help", self.show_shortcuts, self.colors['dark'])
        ]

        for text, command, color in toolbar_buttons:
            btn = Button(toolbar_frame, text=text, command=command,
                         font=('Arial', 10, 'bold'), bg=color, fg='white',
                         relief=FLAT, padx=15, pady=8)
            btn.pack(side=LEFT, padx=5, pady=5)
            # Add hover effects
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=self.theme_manager.get_color(b.cget('bg'))))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=color))

        # Main content area with professional paned window
        main_pane = ttk.PanedWindow(main_container, orient=HORIZONTAL)
        main_pane.pack(fill=BOTH, expand=True, padx=10, pady=5)

        # Left side - Products (70% width) with professional styling
        left_frame = ttk.Frame(main_pane, style='Card.TFrame', padding=15)
        main_pane.add(left_frame, weight=7)

        # Category filter section with modern styling
        category_frame = Frame(left_frame, bg='white', relief=GROOVE, bd=2)
        category_frame.pack(fill=X, pady=(0, 10))
        
        category_header = Frame(category_frame, bg=self.colors['primary'])
        category_header.pack(fill=X)
        
        Label(category_header, text="📂 Product Categories", font=('Arial', 12, 'bold'), 
              bg=self.colors['primary'], fg='white', padx=10, pady=5).pack(side=LEFT)
        
        # Category buttons container
        self.category_buttons_frame = Frame(category_frame, bg='white')
        self.category_buttons_frame.pack(fill=X, padx=10, pady=10)
        
        # Load categories and create buttons
        self.load_category_buttons()

        # Product search with modern styling
        search_frame = Frame(left_frame, bg='white', relief=GROOVE, bd=2)
        search_frame.pack(fill=X, pady=(0, 10))
        
        search_header = Frame(search_frame, bg=self.colors['secondary'])
        search_header.pack(fill=X)
        
        Label(search_header, text="🔍 Search Products", font=('Arial', 12, 'bold'), 
              bg=self.colors['secondary'], fg='white', padx=10, pady=5).pack(side=LEFT)
        
        search_container = Frame(search_frame, bg='white', padx=10, pady=10)
        search_container.pack(fill=X)
        
        self.search_var = StringVar()
        search_entry = ttk.Entry(search_container, textvariable=self.search_var, font=('Arial', 12))
        search_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        search_btn = ttk.Button(search_container, text="Search", command=self.search_products)
        search_btn.pack(side=RIGHT)
        search_entry.bind('<Return>', lambda e: self.search_products())

        # Scrollable product container with modern styling
        products_canvas_frame = Frame(left_frame, bg='white', relief=GROOVE, bd=2)
        products_canvas_frame.pack(fill=BOTH, expand=True)
        
        products_header = Frame(products_canvas_frame, bg=self.colors['info'])
        products_header.pack(fill=X)
        
        Label(products_header, text="🛍️ Available Products", font=('Arial', 12, 'bold'), 
              bg=self.colors['info'], fg='white', padx=10, pady=5).pack(side=LEFT)
        
        canvas_container = Frame(products_canvas_frame, bg='white', padx=10, pady=10)
        canvas_container.pack(fill=BOTH, expand=True)
        
        canvas = Canvas(canvas_container, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient=VERTICAL, command=canvas.yview)
        self.scrollable_products = ttk.Frame(canvas, style='Card.TFrame')

        self.scrollable_products.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_products, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Right side - Cart and Checkout (30% width) with professional styling
        right_frame = ttk.Frame(main_pane, style='Card.TFrame', padding=15)
        main_pane.add(right_frame, weight=3)

        # Customer selection with modern card styling
        customer_frame = ttk.LabelFrame(right_frame, text="👤 Customer Information", padding=10)
        customer_frame.pack(fill=X, pady=(0, 15))
        customer_info_frame = ttk.Frame(customer_frame)
        customer_info_frame.pack(fill=X)
        self.customer_label = ttk.Label(customer_info_frame, text="Walk-in Customer",
                                        font=('Arial', 11, 'bold'), foreground=self.colors['primary'])
        self.customer_label.pack(side=LEFT)
        ttk.Button(customer_info_frame, text="Change", command=self.select_customer).pack(side=RIGHT)

        # Cart list with modern styling
        cart_frame = ttk.LabelFrame(right_frame, text="🛒 Current Cart", padding=10)
        cart_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        cart_container = Frame(cart_frame)
        cart_container.pack(fill=BOTH, expand=True)
        
        cart_columns = ('Item', 'Qty', 'Price', 'Total')
        self.cart_tree = ttk.Treeview(cart_container, columns=cart_columns, show='headings', height=8)
        for col in cart_columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=80)
        self.cart_tree.pack(side=LEFT, fill=BOTH, expand=True)
        
        cart_scroll = ttk.Scrollbar(cart_container, orient=VERTICAL, command=self.cart_tree.yview)
        cart_scroll.pack(side=RIGHT, fill=Y)
        self.cart_tree.configure(yscrollcommand=cart_scroll.set)

        # Cart controls with modern styling
        controls_frame = Frame(right_frame, bg='white')
        controls_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Button(controls_frame, text="View Cart", command=self.view_cart).pack(side=LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Edit Qty", command=self.edit_cart_item).pack(side=LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Remove", command=self.remove_cart_item).pack(side=LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Clear", command=self.clear_cart).pack(side=LEFT, padx=5)
        
        # Hold/Resume Cart button
        self.hold_cart_btn = ttk.Button(controls_frame, text="Hold Cart", command=self.hold_cart)
        self.hold_cart_btn.pack(side=LEFT, padx=5)

        # Discount input with modern styling
        discount_frame = Frame(right_frame, bg='white', relief=GROOVE, bd=1)
        discount_frame.pack(fill=X, pady=(0, 15))
        
        discount_header = Frame(discount_frame, bg=self.colors['warning'])
        discount_header.pack(fill=X)
        
        Label(discount_header, text="💸 Discount", font=('Arial', 11, 'bold'), 
              bg=self.colors['warning'], fg='white', padx=10, pady=3).pack(side=LEFT)
        
        discount_container = Frame(discount_frame, bg='white', padx=10, pady=8)
        discount_container.pack(fill=X)
        
        Label(discount_container, text="Amount:", font=('Arial', 10, 'bold')).pack(side=LEFT)
        self.discount_var = StringVar(value="0")
        ttk.Entry(discount_container, textvariable=self.discount_var, width=10).pack(side=RIGHT)
        
        # Quick Discount button (5%)
        self.quick_discount_btn = Button(discount_container, text="5% Off", 
                                         command=self.apply_quick_discount,
                                         font=('Arial', 9, 'bold'), bg=self.colors['accent'], fg='white',
                                         relief=FLAT, padx=5, pady=2)
        self.quick_discount_btn.pack(side=RIGHT, padx=5)

        # Totals display with enhanced styling
        totals_display = ttk.LabelFrame(right_frame, text="💰 Order Summary", padding=15)
        totals_display.pack(fill=X, pady=(0, 15))

        totals_labels = [
            ("Subtotal:", self.subtotal_var, ('Arial', 10)),
            ("Discount:", self.discount_amount_var, ('Arial', 10)),
            ("Tax:", self.tax_var, ('Arial', 10)),
            ("TOTAL:", self.total_var, ('Arial', 14, 'bold'))
        ]

        for i, (label_text, var, font) in enumerate(totals_labels):
            label_frame = Frame(totals_display, bg='white')
            label_frame.pack(fill=X, pady=5)
            ttk.Label(label_frame, text=label_text, font=font).pack(side=LEFT)
            value_label = ttk.Label(label_frame, textvariable=var, font=font)
            if label_text == "TOTAL:":
                value_label.configure(foreground=self.colors['success'])
            value_label.pack(side=RIGHT)

        # Enhanced checkout section with prominent buttons
        checkout_frame = ttk.LabelFrame(right_frame, text="💳 Checkout", padding=15)
        checkout_frame.pack(fill=X)

        # Main checkout button - made more prominent
        self.checkout_button = Button(checkout_frame, text="✅ CHECKOUT", command=self.checkout,
                                     font=('Arial', 14, 'bold'), bg=self.colors['success'], fg='white',
                                     relief=RAISED, bd=3, padx=20, pady=12, cursor="hand2")
        self.checkout_button.pack(fill=X, pady=(10, 15))

        # Add hover effects for better visibility
        def on_checkout_enter(e):
            self.checkout_button.config(bg=self.theme_manager.get_color(self.colors['success']))
        def on_checkout_leave(e):
            self.checkout_button.config(bg=self.colors['success'])
            
        self.checkout_button.bind("<Enter>", on_checkout_enter)
        self.checkout_button.bind("<Leave>", on_checkout_leave)

        # Quick pay buttons
        quick_pay_frame = Frame(right_frame, bg='white')
        quick_pay_frame.pack(fill=X, pady=(0, 15))
        
        quick_header = Frame(quick_pay_frame, bg=self.colors['secondary'])
        quick_header.pack(fill=X)
        
        Label(quick_header, text="⚡ Quick Pay", font=('Arial', 11, 'bold'), 
              bg=self.colors['secondary'], fg='white', padx=10, pady=3).pack(side=LEFT)
        
        self.quick_pay_buttons_frame = Frame(quick_pay_frame, bg='white', padx=10, pady=8)
        self.quick_pay_buttons_frame.pack(fill=X)

        # Status bar with modern styling
        status_frame = Frame(main_container, bg=self.colors['dark'], height=35)
        status_frame.pack(fill=X, side=BOTTOM)
        status_frame.pack_propagate(False)
        self.status_label = Label(status_frame, text="🟢 System Ready", font=('Arial', 10), bg=self.colors['dark'], fg=self.colors['light'])
        self.status_label.pack(side=LEFT, padx=15, pady=8)

        # Dashboard (Bottom) with professional styling
        dashboard_frame = Frame(main_container, bg='white', relief=GROOVE, bd=2, padx=15, pady=15)
        dashboard_frame.pack(fill=X, pady=(5, 0))

        dashboard_header = Frame(dashboard_frame, bg=self.colors['primary'])
        dashboard_header.pack(fill=X)
        
        Label(dashboard_header, text="📊 Today's Dashboard", font=('Arial', 14, 'bold'), 
              bg=self.colors['primary'], fg='white', padx=15, pady=8).pack(side=LEFT)

        stats_frame = Frame(dashboard_frame, bg='white')
        stats_frame.pack(fill=X, pady=10)

        self.dashboard_stats = {}
        stats_info = [
            ("Total Sales", "total_sales"),
            ("Total Transactions", "total_transactions"),
            ("Avg. Sale", "avg_sale")
        ]
        for i, (name, key) in enumerate(stats_info):
            stat_card = Frame(stats_frame, bg=self.colors['light'], relief=RIDGE, bd=2, padx=15, pady=12)
            stat_card.grid(row=0, column=i, sticky='nsew', padx=8)
            stats_frame.columnconfigure(i, weight=1)
            
            Label(stat_card, text=name, font=('Arial', 11, 'bold'), bg=self.colors['light'], fg=self.colors['dark']).pack()
            self.dashboard_stats[key] = Label(stat_card, text="0", font=('Arial', 16, 'bold'), bg=self.colors['light'], fg=self.colors['primary'])
            self.dashboard_stats[key].pack()

        # Load initial data
        self.refresh_products()
        self.refresh_cart()

    def load_category_buttons(self):
        # Clear existing buttons
        for widget in self.category_buttons_frame.winfo_children():
            widget.destroy()
        
        # Add "All Categories" button
        all_btn = Button(self.category_buttons_frame, text="📦 All Categories", 
                         command=lambda: self.filter_by_category(None),
                         font=('Arial', 10, 'bold'), bg=self.colors['primary'], fg='white',
                         relief=RAISED, bd=2, padx=10, pady=5)
        all_btn.pack(side=LEFT, padx=5, pady=5)
        
        # Add category buttons
        categories = DataManager.get_categories()
        for category in categories:
            # Create a closure to capture the current category
            def make_filter_command(cat_id):
                return lambda: self.filter_by_category(cat_id)
            
            category_btn = Button(self.category_buttons_frame, text=f"📂 {category['name']}", 
                                 command=make_filter_command(category['id']),
                                 font=('Arial', 10, 'bold'), bg=self.colors['secondary'], fg='white',
                                 relief=RAISED, bd=2, padx=10, pady=5)
            category_btn.pack(side=LEFT, padx=5, pady=5)
            
            # Add hover effects
            category_btn.bind("<Enter>", lambda e, b=category_btn: b.configure(bg=self.theme_manager.get_color(b.cget('bg'))))
            category_btn.bind("<Leave>", lambda e, b=category_btn: b.configure(bg=self.colors['secondary']))

    def filter_by_category(self, category_id):
        """Filter products by category"""
        self.selected_category_id = category_id
        self.refresh_products()
        
        # Update button states to show selected category
        for i, widget in enumerate(self.category_buttons_frame.winfo_children()):
            if i == 0:  # "All Categories" button
                if category_id is None:
                    widget.configure(bg=self.colors['success'])
                else:
                    widget.configure(bg=self.colors['primary'])
            else:
                # Check if this button corresponds to the selected category
                categories = DataManager.get_categories()
                if i-1 < len(categories) and categories[i-1]['id'] == category_id:
                    widget.configure(bg=self.colors['success'])
                else:
                    widget.configure(bg=self.colors['secondary'])

    def refresh_products(self, search_query=None):
        # Hide all cards first
        for card in self.product_card_cache.values():
            card.grid_remove()

        # Get products filtered by selected category
        products = DataManager.get_products(category_id=self.selected_category_id, search_query=search_query)
        currency = self.settings.get('currency_symbol', 'PKR')
        columns = 3 # Number of columns for product cards

        for i, product in enumerate(products):
            row = i // columns
            col = i % columns

            product_id = product['id']
            if product_id in self.product_card_cache:
                # Update existing card
                product_card = self.product_card_cache[product_id]
                # Update labels and button states inside the card
                # This part is simplified; in a real app, you'd have references to labels
                for widget in product_card.winfo_children():
                    widget.destroy() # Simple way to refresh card content

                # Re-create content
                self.create_product_card_content(product_card, product, currency)
            else:
                # Create new card
                product_card = Frame(self.scrollable_products, relief=RIDGE, bd=2, bg='white', padx=12, pady=12)
                self.create_product_card_content(product_card, product, currency)
                self.product_card_cache[product_id] = product_card

            product_card.grid(row=row, column=col, sticky='nsew', padx=8, pady=8)
            self.scrollable_products.columnconfigure(col, weight=1)
            self.scrollable_products.rowconfigure(row, weight=1)

        # Configure grid weights for responsive layout
        for i in range(columns):
            self.scrollable_products.columnconfigure(i, weight=1, minsize=200)

        # Update quick pay buttons based on cart
        self.update_quick_pay_buttons()

    def create_product_card_content(self, product_card, product, currency):
        # Product name with modern styling
        name_frame = Frame(product_card, bg='white')
        name_frame.pack(fill=X, pady=(0, 8))

        name_label = Label(name_frame, text=product['name'], font=('Arial', 12, 'bold'),
                          bg='white', fg=self.colors['dark'], wraplength=180)
        name_label.pack(anchor='w')

        # Product price with modern styling
        price_frame = Frame(product_card, bg='white')
        price_frame.pack(fill=X, pady=(0, 8))

        price_label = Label(price_frame, text=f"{currency}{product['price']:.2f}",
                           font=('Arial', 11, 'bold'), bg='white', fg=self.colors['primary'])
        price_label.pack(anchor='w')

        # Stock info with modern styling
        stock_frame = Frame(product_card, bg='white')
        stock_frame.pack(fill=X, pady=(0, 8))

        stock_text = f"Stock: {product['stock']}"
        if product['stock'] <= product['min_stock']:
            stock_text += " ⚠️"
            stock_color = self.colors['warning']
        else:
            stock_color = self.colors['success']
        stock_label = Label(stock_frame, text=stock_text, font=('Arial', 10, 'bold'),
                           bg='white', fg=stock_color)
        stock_label.pack(anchor='w')

        # Add to cart button with modern styling
        button_frame = Frame(product_card, bg='white')
        button_frame.pack(fill=BOTH, expand=True, pady=(8, 0))

        if product['stock'] > 0:
            # Create a closure to capture the current product
            def make_add_command(p):
                return lambda: self.add_to_cart(p)

            add_btn = Button(button_frame, text="Add to Cart", font=('Arial', 10, 'bold'),
                             bg=self.colors['success'], fg='white', pady=8,
                             command=make_add_command(product))
            add_btn.pack(fill=BOTH, expand=True)
            # Add hover effects
            add_btn.bind("<Enter>", lambda e, b=add_btn: b.configure(bg=self.colors['secondary']))
            add_btn.bind("<Leave>", lambda e, b=add_btn: b.configure(bg=self.colors['success']))
        else:
            out_btn = Label(button_frame, text="Out of Stock", font=('Arial', 10, 'bold'),
                            bg=self.colors['danger'], fg='white', pady=8)
            out_btn.pack(fill=BOTH, expand=True)

    def refresh_cart(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        currency = self.settings.get('currency_symbol', 'PKR')
        for item in self.cart:
            total = item['price'] * item['qty']
            self.cart_tree.insert('', 'end', values=(
                item['name'], item['qty'], f"{currency}{item['price']:.2f}", f"{currency}{total:.2f}"
            ))
        self.update_totals()

    def add_to_cart(self, product):
        if product['stock'] <= 0:
            self.show_notification(f"{product['name']} is out of stock!", "error")
            return

        # Check if product already in cart
        for item in self.cart:
            if item['id'] == product['id']:
                if item['qty'] < product['stock']:
                    item['qty'] += 1
                    self.show_notification(f"Increased {product['name']} quantity", "success")
                else:
                    self.show_notification(f"Only {product['stock']} units available!", "warning")
                break
        else:
            # Add new item to cart
            # Fix for the AttributeError: use dictionary-style access for sqlite3.Row
            self.cart.append({
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'cost': product['cost'] if 'cost' in product.keys() else 0,
                'qty': 1
            })
            self.show_notification(f"Added {product['name']} to cart", "success")

        self.refresh_cart()

    def edit_cart_item(self):
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select an item to edit.")
            return

        index = self.cart_tree.index(selection[0])
        cart_item = self.cart[index]

        dialog = QuantityEditDialog(self, cart_item)
        self.wait_window(dialog)  # Make sure to wait for dialog to close
        
        if dialog.result is not None:
            if dialog.result == 0:  # Remove signal
                del self.cart[index]
                self.show_notification("Item removed from cart", "info")
            else:  # Update quantity
                self.cart[index]['qty'] = dialog.result
                self.show_notification(f"Updated quantity for {cart_item['name']}", "success")
            
            # Ensure the cart is refreshed and totals are updated
            self.refresh_cart()
            self.update_totals()

    def remove_cart_item(self):
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select an item to remove.")
            return

        index = self.cart_tree.index(selection[0])
        del self.cart[index]
        self.refresh_cart()

    def clear_cart(self):
        if not self.cart:
            return
        if messagebox.askyesno("Clear Cart", "Are you sure you want to clear the entire cart?"):
            self.cart = []
            self.refresh_cart()

    def view_cart(self):
        """Open cart view dialog"""
        CartViewDialog(self)

    def hold_cart(self):
        """Hold current cart for later use"""
        if not self.cart:
            self.show_notification("Cart is empty!", "error")
            return
        
        # Hold the cart
        customer_id = getattr(self.selected_customer, 'id', None) if self.selected_customer else None
        cart_id = DataManager.hold_cart(self.cart, customer_id)
        
        if cart_id:
            # Clear current cart
            self.cart = []
            self.selected_customer = None
            self.customer_label.configure(text="Walk-in Customer")
            self.refresh_cart()
            self.show_notification(f"Cart held successfully with ID: {cart_id}", "success")
        else:
            self.show_notification("Failed to hold cart", "error")

    def apply_quick_discount(self):
        """Apply 5% discount to current cart"""
        if not self.cart:
            self.show_notification("Cart is empty!", "error")
            return
        
        # Calculate 5% of subtotal
        subtotal = sum(item['price'] * item['qty'] for item in self.cart)
        discount_amount = subtotal * 0.05
        
        # Set discount as percentage
        self.discount_var.set("5%")
        self.update_totals()
        self.show_notification("5% discount applied", "success")

    def parse_discount(self, discount_text, subtotal):
        """Enhanced discount parsing with validation"""
        if not discount_text:
            return 0.0
        try:
            if discount_text.endswith('%'):
                percentage = float(discount_text[:-1])
                if percentage < 0 or percentage > 100:
                    return 0.0
                return subtotal * (percentage / 100)
            else:
                amount = float(discount_text)
                if amount < 0:
                    return 0.0
                return amount
        except ValueError:
            return 0.0

    def update_totals(self):
        subtotal = sum(item['price'] * item['qty'] for item in self.cart)
        discount_amount = self.parse_discount(self.discount_var.get(), subtotal)
        tax_amount = (subtotal - discount_amount) * (self.tax_percent / 100)
        total = subtotal - discount_amount + tax_amount

        currency = self.settings.get('currency_symbol', 'PKR')
        self.subtotal_var.set(f"{currency}{subtotal:.2f}")
        self.discount_amount_var.set(f"-{currency}{discount_amount:.2f}")
        self.tax_var.set(f"{currency}{tax_amount:.2f}")
        self.total_var.set(f"{currency}{total:.2f}")

        # Update quick pay buttons
        self.update_quick_pay_buttons()

    def update_quick_pay_buttons(self):
        for widget in self.quick_pay_buttons_frame.winfo_children():
            widget.destroy()

        if not self.cart:
            return

        total = float(self.total_var.get().replace(self.settings.get('currency_symbol', 'PKR'), ''))
        quick_amounts = [total * 0.25, total * 0.5, total * 0.75, total + 5, total + 10]
        currency = self.settings.get('currency_symbol', 'PKR')

        for amount in quick_amounts:
            btn = Button(self.quick_pay_buttons_frame, text=f"{currency}{amount:.2f}",
                         command=lambda a=amount: self.process_payment_with_amount(a),
                         font=('Arial', 9), bg=self.colors['secondary'], fg='white',
                         relief=FLAT, padx=5, pady=2)
            btn.pack(side=LEFT, padx=2)
            # Add hover effects
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=self.theme_manager.get_color(b.cget('bg'))))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=self.colors['secondary']))

    def process_payment_with_amount(self, amount):
        if not self.cart:
            self.show_notification("Cart is empty!", "error")
            return

        payment_dialog = EnhancedPaymentDialog(self, float(self.total_var.get().replace(self.settings.get('currency_symbol', 'PKR'), '')))
        payment_dialog.paid_var.set(amount)
        self.wait_window(payment_dialog)

        if payment_dialog.result:
            self.complete_sale(float(self.total_var.get().replace(self.settings.get('currency_symbol', 'PKR'), '')), 
                              payment_dialog.result[0], payment_dialog.result[1])

    def checkout(self):
        if not self.cart:
            self.show_notification("Cart is empty!", "error")
            return
        self.process_payment()

    def process_payment(self):
        if not self.cart:
            return

        currency = self.settings.get('currency_symbol', 'PKR')
        total = float(self.total_var.get().replace(currency, ''))
        subtotal = float(self.subtotal_var.get().replace(currency, ''))
        discount = float(self.discount_amount_var.get().replace(f"-{currency}", ''))
        tax = float(self.tax_var.get().replace(currency, ''))

        payment_dialog = EnhancedPaymentDialog(self, total)
        self.wait_window(payment_dialog)

        if payment_dialog.result:
            paid_amount, payment_method = payment_dialog.result
            self.complete_sale(total, paid_amount, payment_method, subtotal, discount, tax)

    def complete_sale(self, total, paid_amount, payment_method, subtotal, discount_amount, tax_amount):
        """Complete the sale transaction"""
        cashier = self.settings.get('cashier_name', 'Unknown')

        try:
            # Save sale
            customer_id = getattr(self.selected_customer, 'id', None) if self.selected_customer else None
            sale_id, receipt_number = DataManager.save_sale(
                self.cart, subtotal, discount_amount, tax_amount, total,
                paid_amount, payment_method, cashier, customer_id
            )

            # Show success message with change
            change = paid_amount - total
            currency = self.settings.get('currency_symbol', 'PKR')
            success_msg = f"Sale completed successfully!\n"
            success_msg += f"Receipt: {receipt_number}\n"
            success_msg += f"Total: {currency}{total:.2f}\n"
            success_msg += f"Paid: {currency}{paid_amount:.2f}\n"
            success_msg += f"Change: {currency}{change:.2f}"
            messagebox.showinfo("Sale Complete", success_msg)

            # Generate and print receipt (simulated)
            self.generate_enhanced_receipt(sale_id, receipt_number)

            # Clear cart and reset
            self.new_sale()
            self.update_dashboard()
            self.set_status("Sale completed successfully", "success")

        except ValueError as e:
            # Handle stock-related errors
            messagebox.showerror("Stock Error", str(e))
            self.set_status("Sale failed - insufficient stock", "error")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process sale: {str(e)}")
            self.set_status("Sale failed", "error")

    def generate_enhanced_receipt(self, sale_id, receipt_number):
        # This is a simulation - in a real app, this might interface with a printer
        sale, items = DataManager.get_sale_details(sale_id)
        if not sale or not items:
            return

        lines = []
        lines.append("=" * 60)
        lines.append(f"RECEIPT #: {receipt_number}".center(60))
        lines.append(f"DATE: {datetime.datetime.fromisoformat(sale['created_at']).strftime('%Y-%m-%d %H:%M:%S')}".center(60))
        lines.append(f"CASHIER: {sale['cashier_name']}".center(60))
        lines.append("=" * 60)

        # Items header
        lines.append(f"{'ITEM':<30} {'QTY':>5} {'PRICE':>10} {'TOTAL':>12}")
        lines.append("-" * 60)

        # Items with better formatting
        currency = self.settings.get('currency_symbol', 'PKR')
        for item in items:
            name = item['product_name'][:29] # Truncate long names
            qty = item['quantity']
            price = item['unit_price']
            total = item['total_price']
            lines.append(f"{name:<30} {qty:>5} {currency}{price:>9.2f} {currency}{total:>11.2f}")
        lines.append("-" * 60)

        # Totals section with proper alignment
        lines.append(f"{'Subtotal:':<48} {currency}{sale['subtotal']:>11.2f}")
        if sale['discount'] > 0:
            lines.append(f"{'Discount:':<48} -{currency}{sale['discount']:>10.2f}")
        lines.append(f"{'Tax ({:.1f}%):'.format(self.tax_percent):<48} {currency}{sale['tax']:>11.2f}")
        lines.append("=" * 60)
        lines.append(f"{'TOTAL:':<48} {currency}{sale['total']:>11.2f}")
        lines.append(f"{'PAID:':<48} {currency}{sale['paid']:>11.2f}")
        lines.append(f"{'CHANGE:':<48} {currency}{sale['change_amount']:>11.2f}")
        lines.append("=" * 60)

        # Footer message
        if self.settings['receipt_footer']:
            lines.append("")
            for line in self.settings['receipt_footer'].split('\n'):
                lines.append(f"{line.strip().center(60)}")
        lines.append("")

        receipt_text = "\n".join(lines)
        print("\n--- GENERATED RECEIPT ---")
        print(receipt_text)
        print("--- END RECEIPT ---\n")

    def new_sale(self):
        self.cart = []
        self.discount_var.set("0")
        self.selected_customer = None
        self.customer_label.configure(text="Walk-in Customer")
        self.refresh_cart()
        self.refresh_products() # Refresh product display
        self.show_notification("New sale started", "success")
        self.set_status("Ready for new sale", "success")

    def select_customer(self):
        """Open enhanced customer selection dialog"""
        CustomerSelectionDialog(self, callback=self.on_customer_selected)

    def on_customer_selected(self, customer):
        if customer:
            self.selected_customer = customer
            self.customer_label.configure(text=f"{customer['name']} ({customer['phone'] or 'No Phone'})")
        else: # Walk-in
            self.selected_customer = None
            self.customer_label.configure(text="Walk-in Customer")
        self.set_status(f"Customer: {self.selected_customer['name'] if self.selected_customer else 'Walk-in'}", "info")

    def search_products(self):
        query = self.search_var.get().strip().lower()
        self.refresh_products(search_query=query)

    def bind_shortcuts(self):
        """Bind enhanced keyboard shortcuts"""
        shortcuts = [
            ('<F1>', lambda e: self.new_sale()),
            ('<F2>', lambda e: self.open_product_manager()),
            ('<F3>', lambda e: self.open_sales_report()),
            ('<F5>', lambda e: self.refresh_products()),
            ('<F12>', lambda e: self.show_shortcuts()),
            ('<Control-n>', lambda e: self.new_sale()),
            ('<Control-p>', lambda e: self.open_product_manager()),
            ('<Control-r>', lambda e: self.open_sales_report()),
            ('<Control-s>', lambda e: self.open_settings()),
            ('<Control-q>', lambda e: self.quick_barcode_add()),
            ('<Delete>', lambda e: self.remove_cart_item()),
            ('<Control-Delete>', lambda e: self.clear_cart()),
            ('<Return>', lambda e: self.process_checkout_if_ready(e)),
            ('<Escape>', lambda e: self.clear_search(e))
        ]
        for key, command in shortcuts:
            self.bind_all(key, command)

    def bind_barcode_scanner(self):
        """Enhanced barcode scanner support"""
        self.bind_all('<Key>', self.handle_barcode_input)

    def handle_barcode_input(self, event):
        """Handle barcode scanner input"""
        current_time = time.time()

        # Reset buffer if too much time has passed (500ms)
        if current_time - self.last_barcode_time > 0.5:
            self.barcode_buffer = ""

        # Add character to buffer if printable
        if event.char.isprintable():
            self.barcode_buffer += event.char

        # Process if Enter is pressed and buffer is long enough (likely a barcode)
        if event.keysym == 'Return' and len(self.barcode_buffer) > 5:
            # Barcode scan complete
            self.process_barcode_scan(self.barcode_buffer)
            self.barcode_buffer = ""

        self.last_barcode_time = current_time

    def process_barcode_scan(self, barcode):
        """Process scanned barcode"""
        product = DataManager.get_product_by_barcode(barcode.strip())
        if product:
            self.add_to_cart(product)
            self.show_barcode_feedback(f"Added: {product['name']}", success=True)
        else:
            self.show_barcode_feedback(f"Product not found: {barcode}", success=False)

    def show_barcode_feedback(self, message, success=True):
        """Show visual feedback for barcode scanning"""
        color = self.colors['success'] if success else self.colors['danger']
        self.barcode_label.configure(text=f"📱 {message}", foreground=color)
        # Reset after 3 seconds
        self.after(3000, lambda: self.barcode_label.configure(text="📱 Barcode Ready", foreground=self.colors['success']))

    def update_time(self):
        """Update current time display"""
        current_time = datetime.datetime.now()
        time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        day_str = current_time.strftime("%A")
        self.time_label.configure(text=time_str)
        self.day_label.configure(text=day_str)
        # Schedule next update
        self.after(1000, self.update_time) # Update every second

    def update_dashboard(self):
        """Enhanced dashboard with comprehensive statistics"""
        try:
            today = datetime.date.today()
            sales = DataManager.get_sales(today, today)
            total_sales = sum(s['total'] for s in sales)
            total_transactions = len(sales)
            avg_sale = total_sales / total_transactions if total_transactions > 0 else 0

            currency = self.settings.get('currency_symbol', 'PKR')
            stats = {
                "Total Sales": f"{currency}{total_sales:.2f}",
                "Transactions": str(total_transactions),
                "Avg. Sale": f"{currency}{avg_sale:.2f}"
            }
            for stat_name, value in stats.items():
                if stat_name in self.dashboard_stats:
                    self.dashboard_stats[stat_name].configure(text=value)
        except Exception as e:
            print(f"Dashboard update error: {e}")
            for stat_name in self.dashboard_stats:
                self.dashboard_stats[stat_name].configure(text="Error")

    def check_low_stock(self):
        """Check and display low stock alerts"""
        low_stock_products = DataManager.get_low_stock_products()
        if low_stock_products:
            count = len(low_stock_products)
            self.show_alert(f"⚠️ {count} product{'s' if count != 1 else ''} have low stock!", "warning")

    def show_alert(self, message, alert_type="info"):
        """Show alert message with better styling"""
        # Create a temporary frame for the alert
        alert_container = Frame(self, bg=self.colors.get(alert_type, self.colors['secondary']), relief=SOLID, bd=1)
        alert_container.pack(side=TOP, fill=X, padx=10, pady=(0, 10))

        Label(alert_container, text=message, font=('Arial', 10, 'bold'), bg=self.colors.get(alert_type, self.colors['secondary']), fg='white').pack(side=LEFT, padx=10, pady=5)

        Button(alert_container, text="✕",
               command=lambda: alert_container.destroy(),
               bg=self.colors.get(alert_type, self.colors['secondary']), fg='white', relief=FLAT, font=('Arial', 12, 'bold'), cursor='hand2').pack(side=RIGHT, padx=5)

        # Auto-hide after 5 seconds for info messages
        if alert_type == "info":
            self.after(5000, lambda: alert_container.destroy() if alert_container.winfo_exists() else None)

    def show_notification(self, message, notification_type="info"):
        """Show temporary notification"""
        self.show_alert(message, notification_type)

    def set_status(self, message, status_type="info"):
        """Set status bar message"""
        colors = {
            "info": self.colors['secondary'],
            "success": self.colors['success'],
            "warning": self.colors['warning'],
            "error": self.colors['danger']
        }
        status_text = f"● {message}"
        self.status_label.configure(text=status_text, fg=colors.get(status_type, self.colors['secondary']))
        # Reset to default after 5 seconds
        self.after(5000, lambda: self.status_label.configure(text="● System Ready", fg=self.colors['success']))

    def process_checkout_if_ready(self, event=None):
        # Only process checkout if Enter is pressed in the main window and cart is not empty
        if not self.cart:
            return
        # Check if focus is on an entry field to avoid accidental checkout
        widget = self.focus_get()
        if isinstance(widget, Entry):
            return # Don't checkout if typing in an entry
        self.checkout()

    def clear_search(self, event=None):
        self.search_var.set("")
        self.refresh_products()

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        new_theme = self.theme_manager.toggle_theme()
        self.theme_manager.apply_styles(self.style)
        self.update_theme_colors()
        self.show_notification(f"Theme changed to {new_theme}", "success")
        
        # Save theme setting
        DatabaseManager.set_setting('theme', new_theme)
        self.settings['theme'] = new_theme

    def update_theme_colors(self):
        """Update UI colors when theme changes"""
        # Update main container colors
        self.configure(bg=self.colors['primary'])
        
        # Update all frames with background colors
        for widget in self.winfo_children():
            self.update_widget_colors(widget)
        
        # Refresh product display to apply new colors
        self.refresh_products()
        self.refresh_cart()

    def update_widget_colors(self, widget):
        """Recursively update widget colors based on current theme"""
        try:
            # Update frames
            if isinstance(widget, Frame) or isinstance(widget, ttk.Frame):
                widget.configure(bg=self.colors['white'])
            
            # Update labels
            if isinstance(widget, Label):
                if widget.cget('bg') == self.colors['primary'] or widget.cget('bg') == self.colors['dark']:
                    # Keep header colors
                    pass
                else:
                    widget.configure(bg=self.colors['white'])
                    
                if widget.cget('fg') == self.colors['dark']:
                    widget.configure(fg=self.colors['dark'])
            
            # Update buttons
            if isinstance(widget, Button):
                # Determine button type by its text
                text = widget.cget('text')
                if 'CHECKOUT' in text:
                    widget.configure(bg=self.colors['success'])
                elif any(word in text for word in ['Add to Cart', 'Save', 'Yes']):
                    widget.configure(bg=self.colors['success'])
                elif any(word in text for word in ['Delete', 'Remove', 'No', 'Cancel']):
                    widget.configure(bg=self.colors['danger'])
                elif any(word in text for word in ['Edit', 'Update']):
                    widget.configure(bg=self.colors['secondary'])
            
            # Recursively update child widgets
            for child in widget.winfo_children():
                self.update_widget_colors(child)
        except:
            # Skip widgets that don't support the configure method
            pass

    # Implementation of all the missing features
    def show_search_dialog(self):
        """Show search dialog"""
        search_dialog = Toplevel(self)
        search_dialog.title("Search Products")
        search_dialog.geometry("500x200")
        search_dialog.transient(self)
        search_dialog.grab_set()
        
        main_frame = Frame(search_dialog, bg='white', padx=20, pady=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        Label(main_frame, text="Search Products", font=('Arial', 14, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=(0, 15))
        
        search_frame = Frame(main_frame, bg='white')
        search_frame.pack(fill=X, pady=(0, 15))
        
        Label(search_frame, text="Search:", font=('Arial', 10, 'bold'), bg='white').pack(side=LEFT, padx=(0, 5))
        search_var = StringVar()
        Entry(search_frame, textvariable=search_var, font=('Arial', 12)).pack(side=LEFT, fill=X, expand=True)
        
        def do_search():
            self.search_var.set(search_var.get())
            self.search_products()
            search_dialog.destroy()
        
        Button(main_frame, text="Search", command=do_search,
               font=('Arial', 10, 'bold'), bg=self.colors['primary'], fg='white', relief=FLAT).pack(pady=10)
        
        search_dialog.center_window = lambda: search_dialog.geometry(
            f"+{self.winfo_x() + (self.winfo_width() // 2) - (search_dialog.winfo_width() // 2)}"
            f"+{self.winfo_y() + (self.winfo_height() // 2) - (search_dialog.winfo_height() // 2)}"
        )
        search_dialog.center_window()

    def open_product_manager(self):
        """Open product manager dialog"""
        ProductManagerDialog(self)

    def open_customer_manager(self):
        """Open customer manager dialog"""
        CustomerManagerDialog(self)

    def open_sales_report(self):
        """Open sales report dialog"""
        SalesReportDialog(self)

    def open_settings(self):
        """Open settings dialog"""
        SettingsDialog(self)

    def quick_barcode_add(self):
        """Open quick barcode add dialog"""
        QuickBarcodeAddDialog(self)

    def show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        ShortcutsDialog(self)

    def show_about(self):
        """Show about dialog"""
        AboutDialog(self)

    def show_transaction_history(self):
        """Show transaction history dialog"""
        TransactionHistoryDialog(self)

    def auto_backup_on_exit(self):
        """Create backup automatically when application exits"""
        try:
            BackupRestoreManager.create_backup()
            print("Auto backup created successfully")
        except Exception as e:
            print(f"Auto backup failed: {e}")


# --- Main Application Entry Point ---
if __name__ == '__main__':
    try:
        app = ModernPOSApp()
        
        # Set up auto-backup on exit
        app.protocol("WM_DELETE_WINDOW", lambda: (
            app.auto_backup_on_exit(),
            app.destroy()
        ))
        
        app.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        try:
            messagebox.showerror("Startup Error", f"Failed to start the POS application:\n{str(e)}")
        except:
            print("Critical error - unable to show error dialog")
