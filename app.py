import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
import os

# Page configuration
st.set_page_config(
    page_title="Express Wash - Smart Laundry Billing",
    page_icon="🧺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .price-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #c3e6cb;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .bill-summary {
        background-color: #e3f2fd;
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #2196f3;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .form-section {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .stButton > button {
        border-radius: 10px;
        font-weight: bold;
        padding: 0.5rem 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
    }
    .stTextInput > div > div > input:focus {
        border-color: #1f77b4;
        box-shadow: 0 0 0 2px rgba(31, 119, 180, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '16021995',
    'database': 'express_wash'
}

# Initialize database
def init_database():
    """Initialize MySQL database and create tables if they don't exist"""
    try:
        # First connect without database to create it if it doesn't exist
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        # Create orders table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_name VARCHAR(255) NOT NULL,
                mobile_number VARCHAR(20),
                order_date DATE NOT NULL,
                regular_clothes_kg DECIMAL(5,2) DEFAULT 0,
                blankets_kg DECIMAL(5,2) DEFAULT 0,
                white_clothes_pieces INT DEFAULT 0,
                total_amount DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                receipt_number VARCHAR(50),
                collection_date DATETIME NULL
            )
        ''')
        
        # Add collection_date column if it doesn't exist (for existing databases)
        try:
            cursor.execute('ALTER TABLE orders ADD COLUMN collection_date DATETIME NULL')
        except Exception:
            pass  # Column already exists
        
        conn.commit()
        conn.close()
        
        st.success("✅ Database initialized successfully!")
        
    except mysql.connector.Error as err:
        st.error(f"❌ Database error: {err}")
        st.info("Please make sure MySQL is running and credentials are correct.")

# Pricing configuration
PRICING = {
    'regular_clothes': 50,  # ₹50/kg
    'blankets': 100,        # ₹100/kg
    'white_clothes': 40     # ₹40/piece
}

def calculate_bill(regular_kg, blankets_kg, white_pieces):
    """Calculate total bill based on services"""
    regular_cost = regular_kg * PRICING['regular_clothes']
    blankets_cost = blankets_kg * PRICING['blankets']
    white_cost = white_pieces * PRICING['white_clothes']
    
    total = regular_cost + blankets_cost + white_cost
    return {
        'regular_cost': regular_cost,
        'blankets_cost': blankets_cost,
        'white_cost': white_cost,
        'total': total
    }

def save_order_to_csv(order_data):
    """Save order to CSV file"""
    csv_file = 'orders.csv'
    
    # Check if file exists, if not create with headers
    if not os.path.exists(csv_file):
        df = pd.DataFrame([order_data])
    else:
        df = pd.read_csv(csv_file)
        df = pd.concat([df, pd.DataFrame([order_data])], ignore_index=True)
    
    df.to_csv(csv_file, index=False)

def update_csv_backup():
    """Update CSV file to match database"""
    try:
        df = load_orders()
        if not df.empty:
            df.to_csv('orders.csv', index=False)
    except Exception as e:
        st.error(f"Error updating CSV backup: {str(e)}")

def save_order_to_db(order_data):
    """Save order to MySQL database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Use provided receipt number (mandatory)
        receipt_number = order_data.get('receipt_number')
        
        cursor.execute('''
            INSERT INTO orders (customer_name, mobile_number, order_date, regular_clothes_kg, 
                               blankets_kg, white_clothes_pieces, total_amount, receipt_number)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            order_data['customer_name'],
            order_data['mobile_number'],
            order_data['order_date'],
            order_data['regular_clothes_kg'],
            order_data['blankets_kg'],
            order_data['white_clothes_pieces'],
            order_data['total_amount'],
            receipt_number
        ))
        
        conn.commit()
        conn.close()
        
    except mysql.connector.Error as err:
        st.error(f"❌ Database error: {err}")
        raise

def load_orders():
    """Load orders from MySQL database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql_query('SELECT * FROM orders ORDER BY created_at DESC', conn)
        conn.close()
        return df
    except mysql.connector.Error as err:
        st.error(f"❌ Database error: {err}")
        return pd.DataFrame()  # Return empty DataFrame on error

def update_order(order_id, order_data):
    """Update an existing order in MySQL database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE orders 
            SET customer_name = %s, mobile_number = %s, order_date = %s,
                regular_clothes_kg = %s, blankets_kg = %s, white_clothes_pieces = %s,
                total_amount = %s
            WHERE id = %s
        ''', (
            order_data['customer_name'],
            order_data['mobile_number'],
            order_data['order_date'],
            order_data['regular_clothes_kg'],
            order_data['blankets_kg'],
            order_data['white_clothes_pieces'],
            order_data['total_amount'],
            order_id
        ))
        
        conn.commit()
        conn.close()
        
        # Update CSV backup
        update_csv_backup()
        
        return True
    except mysql.connector.Error as err:
        st.error(f"❌ Database error: {err}")
        return False

def delete_order(order_id):
    """Delete an order from MySQL database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM orders WHERE id = %s', (order_id,))
        
        conn.commit()
        conn.close()
        
        # Update CSV backup
        update_csv_backup()
        
        return True
    except mysql.connector.Error as err:
        st.error(f"❌ Database error: {err}")
        return False

def get_order_by_id(order_id):
    """Get a specific order by ID"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM orders WHERE id = %s', (order_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result
    except mysql.connector.Error as err:
        st.error(f"❌ Database error: {err}")
        return None

def main():
    # Initialize database
    init_database()
    
    # Main header
    st.markdown('<h1 class="main-header">🧺 Express Wash</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header" style="text-align: center;">Smart Laundry Billing System</h2>', unsafe_allow_html=True)
    
    # Sidebar for navigation
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 New Order", "📊 Order History", "📈 Analytics", "💰 Pricing"]
    )
    
    if page == "🏠 New Order":
        new_order_page()
    elif page == "📊 Order History":
        order_history_page()
    elif page == "📈 Analytics":
        analytics_page()
    elif page == "💰 Pricing":
        pricing_page()

def new_order_page():
    """Page for creating new orders"""
    st.markdown('<h2 class="sub-header">📝 New Order</h2>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        
        # Customer Information
        st.subheader("👤 Customer Information")
        col1, col2 = st.columns(2)
    
    with col1:
        customer_name = st.text_input("Customer Name *", placeholder="Enter customer name")
        mobile_number = st.text_input("Mobile Number", placeholder="Enter mobile number")
    
    with col2:
        order_date = st.date_input("Order Date *", value=date.today())
        receipt_number = st.text_input("Receipt Number *", 
                                     placeholder="Enter receipt number (e.g., 1, 2, 100, A-51)",
                                     help="Receipt number is mandatory for order tracking")
    
    # Service Details
    st.subheader("🧺 Service Details")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="price-card">', unsafe_allow_html=True)
        st.markdown("**Regular Clothes**")
        st.markdown("₹50/kg")
        st.markdown("</div>", unsafe_allow_html=True)
        regular_kg = st.number_input("Weight (kg)", min_value=0.0, value=0.0, step=0.5)
    
    with col2:
        st.markdown('<div class="price-card">', unsafe_allow_html=True)
        st.markdown("**Blankets/Bedsheets**")
        st.markdown("₹100/kg")
        st.markdown("</div>", unsafe_allow_html=True)
        blankets_kg = st.number_input("Weight (kg)", min_value=0.0, value=0.0, step=0.5, key="blankets")
    
    with col3:
        st.markdown('<div class="price-card">', unsafe_allow_html=True)
        st.markdown("**White Clothes**")
        st.markdown("₹40/piece")
        st.markdown("</div>", unsafe_allow_html=True)
        white_pieces = st.number_input("Number of pieces", min_value=0, value=0, key="white")
    
    # Calculate bill
    if regular_kg > 0 or blankets_kg > 0 or white_pieces > 0:
        bill = calculate_bill(regular_kg, blankets_kg, white_pieces)
        
        # Display bill summary
        st.markdown('<div class="bill-summary">', unsafe_allow_html=True)
        st.subheader("💰 Bill Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Regular Clothes:** {regular_kg}kg × ₹{PRICING['regular_clothes']} = ₹{bill['regular_cost']:.2f}")
            st.write(f"**Blankets/Bedsheets:** {blankets_kg}kg × ₹{PRICING['blankets']} = ₹{bill['blankets_cost']:.2f}")
            st.write(f"**White Clothes:** {white_pieces} pieces × ₹{PRICING['white_clothes']} = ₹{bill['white_cost']:.2f}")
        
        with col2:
            st.markdown(f"### **Total Amount: ₹{bill['total']:.2f}**")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Save order button
        if st.button("💾 Save Order", type="primary", use_container_width=True):
            if customer_name and order_date and receipt_number:
                # Prepare order data
                order_data = {
                    'customer_name': customer_name,
                    'mobile_number': mobile_number,
                    'order_date': order_date.strftime('%Y-%m-%d'),
                    'regular_clothes_kg': regular_kg,
                    'blankets_kg': blankets_kg,
                    'white_clothes_pieces': white_pieces,
                    'total_amount': bill['total'],
                    'receipt_number': receipt_number if receipt_number else None
                }
                
                # Save to both CSV and database
                save_order_to_csv(order_data)
                save_order_to_db(order_data)
                
                st.markdown('<div class="success-message">', unsafe_allow_html=True)
                st.success("✅ Order saved successfully!")
                st.write(f"**Customer:** {customer_name}")
                st.write(f"**Receipt Number:** {receipt_number}")
                st.write(f"**Total Amount:** ₹{bill['total']:.2f}")
                st.write(f"**Order Date:** {order_date.strftime('%B %d, %Y')}")
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Clear form
                st.rerun()
            else:
                st.error("❌ Please fill in customer name, order date, and receipt number!")

def order_history_page():
    """Page for viewing and managing order history with CRUD operations"""
    st.markdown('<h2 class="sub-header">📊 Order History & Management</h2>', unsafe_allow_html=True)
    
    try:
        df = load_orders()
        
        if df.empty:
            st.info("📝 No orders found. Create your first order!")
            return
        
        # CRUD Operations Section
        st.subheader("🛠️ Manage Orders")
        
        # Operation selection
        operation = st.selectbox(
            "Choose an operation:",
            ["📋 View Orders", "✏️ Edit Order", "🗑️ Delete Order", "📦 Order Collection", "➕ Add New Order"]
        )
        
        if operation == "📋 View Orders":
            view_orders_section(df)
        elif operation == "✏️ Edit Order":
            edit_order_section(df)
        elif operation == "🗑️ Delete Order":
            delete_order_section(df)
        elif operation == "📦 Order Collection":
            order_collection_section(df)
        elif operation == "➕ Add New Order":
            add_new_order_section()
        
    except Exception as e:
        st.error(f"Error loading orders: {str(e)}")

def view_orders_section(df):
    """Section for viewing orders with filters"""
    st.subheader("📋 View Orders")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("Search by receipt number or name", placeholder="Enter receipt number or name...", key="view_search")
    
    with col2:
        date_filter = st.date_input("Filter by date", value=None, key="view_date")
    
    with col3:
        min_amount = st.number_input("Minimum amount", min_value=0.0, value=0.0, key="view_amount")
    
    # Apply filters
    filtered_df = df.copy()
    if search_term:
        # Search by receipt number or customer name
        filtered_df = filtered_df[
            (filtered_df['receipt_number'].str.contains(search_term, case=False, na=False)) |
            (filtered_df['customer_name'].str.contains(search_term, case=False, na=False))
        ]
    
    if date_filter:
        filtered_df = filtered_df[filtered_df['order_date'] == date_filter.strftime('%Y-%m-%d')]
    
    if min_amount > 0:
        filtered_df = filtered_df[filtered_df['total_amount'] >= min_amount]
    
    # Display orders
    st.write(f"**📋 Orders ({len(filtered_df)} found)**")
    
    # Format the dataframe for display
    display_df = filtered_df.copy()
    display_df['order_date'] = pd.to_datetime(display_df['order_date']).dt.strftime('%B %d, %Y')
    display_df['total_amount'] = display_df['total_amount'].apply(lambda x: f"₹{x:.2f}")
    display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%B %d, %Y %H:%M')
    
    # Rename columns for better display
    display_df = display_df.rename(columns={
        'id': 'ID',
        'receipt_number': 'Receipt Number',
        'customer_name': 'Customer Name',
        'mobile_number': 'Mobile Number',
        'order_date': 'Order Date',
        'regular_clothes_kg': 'Regular (kg)',
        'blankets_kg': 'Blankets (kg)',
        'white_clothes_pieces': 'White (pieces)',
        'total_amount': 'Total Amount',
        'created_at': 'Created At'
    })
    
    # Select columns to display
    columns_to_show = ['ID', 'Receipt Number', 'Customer Name', 'Mobile Number', 'Order Date', 'Regular (kg)', 
                      'Blankets (kg)', 'White (pieces)', 'Total Amount', 'Created At']
    
    st.dataframe(display_df[columns_to_show], use_container_width=True)
    
    # Download options
    st.subheader("📥 Download Data")
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="📄 Download as CSV",
            data=csv_data,
            file_name=f"express_wash_orders_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col2:
        excel_data = filtered_df.to_excel(index=False)
        st.download_button(
            label="📊 Download as Excel",
            data=excel_data,
            file_name=f"express_wash_orders_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

def edit_order_section(df):
    """Section for editing orders"""
    st.subheader("✏️ Edit Order")
    
    # Select order to edit
    if df.empty:
        st.warning("No orders available to edit.")
        return
    
    # Create a selection list
    order_options = []
    for _, row in df.iterrows():
        order_options.append(f"ID: {row['id']} - {row['customer_name']} - ₹{row['total_amount']:.2f} - {row['order_date']}")
    
    selected_order = st.selectbox("Select order to edit:", order_options, key="edit_select")
    
    if selected_order:
        # Extract order ID from selection
        order_id = int(selected_order.split(" - ")[0].replace("ID: ", ""))
        
        # Get order details
        order_data = get_order_by_id(order_id)
        
        if order_data:
            st.write("**Current Order Details:**")
            
            # Display current values
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Customer Name:** {order_data[1]}")
                st.write(f"**Mobile Number:** {order_data[2]}")
                st.write(f"**Order Date:** {order_data[3]}")
            
            with col2:
                st.write(f"**Regular Clothes:** {order_data[4]} kg")
                st.write(f"**Blankets:** {order_data[5]} kg")
                st.write(f"**White Clothes:** {order_data[6]} pieces")
                st.write(f"**Total Amount:** ₹{order_data[7]:.2f}")
            
            st.divider()
            
            # Edit form
            st.write("**Edit Order Details:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_customer_name = st.text_input("Customer Name", value=order_data[1], key="edit_name")
                new_mobile_number = st.text_input("Mobile Number", value=order_data[2] or "", key="edit_mobile")
            
            with col2:
                new_order_date = st.date_input("Order Date", value=pd.to_datetime(order_data[3]).date(), key="edit_date")
            
            # Service details
            st.write("**Service Details:**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                new_regular_kg = st.number_input("Regular Clothes (kg)", min_value=0.0, value=float(order_data[4]), step=0.5, key="edit_regular")
            
            with col2:
                new_blankets_kg = st.number_input("Blankets (kg)", min_value=0.0, value=float(order_data[5]), step=0.5, key="edit_blankets")
            
            with col3:
                new_white_pieces = st.number_input("White Clothes (pieces)", min_value=0, value=int(order_data[6]), key="edit_white")
            
            # Calculate new total
            new_bill = calculate_bill(new_regular_kg, new_blankets_kg, new_white_pieces)
            
            st.markdown(f"**New Total Amount: ₹{new_bill['total']:.2f}**")
            
            # Update button
            if st.button("💾 Update Order", type="primary", key="edit_update"):
                if new_customer_name and new_order_date:
                    updated_order_data = {
                        'customer_name': new_customer_name,
                        'mobile_number': new_mobile_number,
                        'order_date': new_order_date.strftime('%Y-%m-%d'),
                        'regular_clothes_kg': new_regular_kg,
                        'blankets_kg': new_blankets_kg,
                        'white_clothes_pieces': new_white_pieces,
                        'total_amount': new_bill['total']
                    }
                    
                    if update_order(order_id, updated_order_data):
                        st.success("✅ Order updated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to update order!")
                else:
                    st.error("❌ Please fill in customer name and order date!")

def delete_order_section(df):
    """Section for deleting orders"""
    st.subheader("🗑️ Delete Order")
    
    if df.empty:
        st.warning("No orders available to delete.")
        return
    
    # Create a selection list
    order_options = []
    for _, row in df.iterrows():
        order_options.append(f"ID: {row['id']} - {row['customer_name']} - ₹{row['total_amount']:.2f} - {row['order_date']}")
    
    selected_order = st.selectbox("Select order to delete:", order_options, key="delete_select")
    
    if selected_order:
        # Extract order ID from selection
        order_id = int(selected_order.split(" - ")[0].replace("ID: ", ""))
        
        # Get order details for confirmation
        order_data = get_order_by_id(order_id)
        
        if order_data:
            st.write("**Order to Delete:**")
            st.write(f"**ID:** {order_data[0]}")
            st.write(f"**Customer Name:** {order_data[1]}")
            st.write(f"**Mobile Number:** {order_data[2]}")
            st.write(f"**Order Date:** {order_data[3]}")
            st.write(f"**Total Amount:** ₹{order_data[7]:.2f}")
            
            st.warning("⚠️ This action cannot be undone!")
            
            # Confirmation
            confirm_delete = st.checkbox("I confirm that I want to delete this order", key="delete_confirm")
            
            if confirm_delete:
                if st.button("🗑️ Delete Order", type="primary", key="delete_button"):
                    if delete_order(order_id):
                        st.success("✅ Order deleted successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete order!")

def order_collection_section(df):
    """Section for marking orders as collected"""
    st.subheader("📦 Order Collection")
    
    # Get all orders
    all_orders = df
    
    if all_orders.empty:
        st.info("📋 No orders found!")
        return
    
    # Receipt number input
    receipt_number = st.text_input("Enter Receipt Number:", 
                                  placeholder="e.g., 123, A-51, 055",
                                  key="collection_receipt")
    
    if receipt_number:
        # Find order by receipt number
        matching_orders = all_orders[all_orders['receipt_number'] == receipt_number]
        
        if not matching_orders.empty:
            order = matching_orders.iloc[0]
            
            st.markdown("**Order Found:**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Customer:** {order['customer_name']}")
                st.write(f"**Mobile:** {order['mobile_number']}")
                st.write(f"**Date:** {order['order_date']}")
            
            with col2:
                st.write(f"**Receipt:** {order['receipt_number']}")
                st.write(f"**Total:** ₹{order['total_amount']:.2f}")
                st.write(f"**Collection Date:** {order.get('collection_date', 'Not collected yet')}")
            
            if st.button("✅ Mark as Collected", type="primary", key="collect_button"):
                if mark_order_collected(order['id']):
                    st.success("✅ Order marked as collected!")
                    st.info("📱 SMS notification sent to customer!")
                    st.rerun()
                else:
                    st.error("❌ Failed to mark order as collected!")
        else:
            st.warning("⚠️ No order found with this receipt number!")
    
    # Show all orders
    st.markdown("**📋 All Orders:**")
    if 'receipt_number' in all_orders.columns:
        display_cols = ['receipt_number', 'customer_name', 'mobile_number', 'order_date', 'total_amount', 'collection_date']
        st.dataframe(all_orders[display_cols], use_container_width=True)
    else:
        st.dataframe(all_orders[['customer_name', 'mobile_number', 'order_date', 'total_amount']], 
                    use_container_width=True)

def mark_order_collected(order_id):
    """Mark order as collected in database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Update collection date
        cursor.execute('''
            UPDATE orders 
            SET collection_date = NOW()
            WHERE id = %s
        ''', (order_id,))
        
        # Get order details for SMS
        cursor.execute('''
            SELECT customer_name, mobile_number, receipt_number, total_amount
            FROM orders WHERE id = %s
        ''', (order_id,))
        
        order_details = cursor.fetchone()
        conn.commit()
        conn.close()
        
        if order_details:
            customer_name, mobile_number, receipt_number, total_amount = order_details
            
            # Send SMS notification
            if mobile_number:
                sms_message = f"Hi {customer_name}, your laundry order #{receipt_number} has been collected. Thank you for using Express Wash!"
                send_sms(mobile_number, sms_message)
        
        return True
    except Exception as e:
        st.error(f"Error marking order as collected: {str(e)}")
        return False

def send_sms(phone_number, message):
    """Send SMS using Fast2SMS API"""
    try:
        import requests
        
        payload = {
            "sender_id": "FSTSMS",
            "message": message,
            "language": "english",
            "route": "v3",
            "numbers": phone_number
        }
        headers = {
            'authorization': "XerDBCLIaGm0dR2AHO6phqNcunktPogVvF9w1jWxfK38EUQyJMNDId3H9pbPKGuxohtUQjMrBAizl1L7",
            'Content-Type': "application/json"
        }
        response = requests.post("https://www.fast2sms.com/dev/bulkV2", json=payload, headers=headers)
        result = response.json()
        
        return result.get('return') == True
    except Exception as e:
        print(f"SMS error: {str(e)}")
        return False

def add_new_order_section():
    """Section for adding new orders from the history page"""
    st.subheader("➕ Add New Order")
    
    # Customer Information
    st.write("**Customer Information:**")
    col1, col2 = st.columns(2)
    
    with col1:
        customer_name = st.text_input("Customer Name *", placeholder="Enter customer name", key="add_name")
        mobile_number = st.text_input("Mobile Number", placeholder="Enter mobile number", key="add_mobile")
    
    with col2:
        order_date = st.date_input("Order Date *", value=date.today(), key="add_date")
        receipt_number = st.text_input("Receipt Number *", placeholder="Enter receipt number", key="add_receipt")
    
    # Service Details
    st.write("**Service Details:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Regular Clothes** - ₹50/kg")
        regular_kg = st.number_input("Weight (kg)", min_value=0.0, value=0.0, step=0.5, key="add_regular")
    
    with col2:
        st.markdown("**Blankets/Bedsheets** - ₹100/kg")
        blankets_kg = st.number_input("Weight (kg)", min_value=0.0, value=0.0, step=0.5, key="add_blankets")
    
    with col3:
        st.markdown("**White Clothes** - ₹40/piece")
        white_pieces = st.number_input("Number of pieces", min_value=0, value=0, key="add_white")
    
    # Calculate bill
    if regular_kg > 0 or blankets_kg > 0 or white_pieces > 0:
        bill = calculate_bill(regular_kg, blankets_kg, white_pieces)
        
        st.markdown(f"**Total Amount: ₹{bill['total']:.2f}**")
        
        # Save order button
        if st.button("💾 Save New Order", type="primary", key="add_save"):
            if customer_name and order_date and receipt_number:
                # Prepare order data
                order_data = {
                    'customer_name': customer_name,
                    'mobile_number': mobile_number,
                    'order_date': order_date.strftime('%Y-%m-%d'),
                    'regular_clothes_kg': regular_kg,
                    'blankets_kg': blankets_kg,
                    'white_clothes_pieces': white_pieces,
                    'total_amount': bill['total'],
                    'receipt_number': receipt_number
                }
                
                # Save to both CSV and database
                save_order_to_csv(order_data)
                save_order_to_db(order_data)
                
                st.success("✅ New order saved successfully!")
                st.rerun()
            else:
                st.error("❌ Please fill in customer name, order date, and receipt number!")

def analytics_page():
    """Page for analytics and insights"""
    st.markdown('<h2 class="sub-header">📈 Analytics & Insights</h2>', unsafe_allow_html=True)
    
    try:
        df = load_orders()
        
        if df.empty:
            st.info("📝 No data available for analytics. Create some orders first!")
            return
        
        # Convert date columns
        df['order_date'] = pd.to_datetime(df['order_date'])
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Key metrics
        st.subheader("📊 Key Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_orders = len(df)
            st.metric("Total Orders", total_orders)
        
        with col2:
            total_revenue = df['total_amount'].sum()
            st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
        
        with col3:
            avg_order_value = df['total_amount'].mean()
            st.metric("Average Order Value", f"₹{avg_order_value:.2f}")
        
        with col4:
            unique_customers = df['customer_name'].nunique()
            st.metric("Unique Customers", unique_customers)
        
        # Charts
        st.subheader("📈 Revenue Trends")
        
        # Daily revenue
        daily_revenue = df.groupby('order_date')['total_amount'].sum().reset_index()
        
        fig_daily = px.line(daily_revenue, x='order_date', y='total_amount',
                           title='Daily Revenue Trend',
                           labels={'order_date': 'Date', 'total_amount': 'Revenue (₹)'})
        fig_daily.update_layout(height=400)
        st.plotly_chart(fig_daily, use_container_width=True)
        
        # Service breakdown
        st.subheader("🧺 Service Breakdown")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Service type breakdown
            service_data = {
                'Regular Clothes': df['regular_clothes_kg'].sum() * PRICING['regular_clothes'],
                'Blankets/Bedsheets': df['blankets_kg'].sum() * PRICING['blankets'],
                'White Clothes': df['white_clothes_pieces'].sum() * PRICING['white_clothes']
            }
            
            fig_pie = px.pie(values=list(service_data.values()), 
                           names=list(service_data.keys()),
                           title='Revenue by Service Type')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Top customers
            top_customers = df.groupby('customer_name')['total_amount'].sum().sort_values(ascending=False).head(10)
            
            fig_bar = px.bar(x=top_customers.values, y=top_customers.index,
                           orientation='h',
                           title='Top 10 Customers by Revenue',
                           labels={'x': 'Revenue (₹)', 'y': 'Customer Name'})
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Recent activity
        st.subheader("🕒 Recent Activity")
        recent_orders = df.head(5)[['customer_name', 'total_amount', 'created_at']]
        recent_orders['created_at'] = recent_orders['created_at'].dt.strftime('%B %d, %Y %H:%M')
        recent_orders['total_amount'] = recent_orders['total_amount'].apply(lambda x: f"₹{x:.2f}")
        
        st.dataframe(recent_orders, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

def pricing_page():
    """Page for pricing information"""
    st.markdown('<h2 class="sub-header">💰 Pricing Information</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 🧺 Express Wash Services & Pricing
    
    All services include **washing and folding** only.
    """)
    
    # Pricing table
    pricing_data = {
        'Service Category': [
            'Regular Clothes (per kg)',
            'Blankets / Bedsheets / Rugs / Duvets (per kg)',
            'White Clothes (per piece)'
        ],
        'Rate': ['₹50/kg', '₹100/kg', '₹40/piece'],
        'Description': [
            'Daily wear clothes, shirts, pants, etc.',
            'Heavy items requiring special care',
            'White clothes that need special treatment'
        ]
    }
    
    pricing_df = pd.DataFrame(pricing_data)
    st.dataframe(pricing_df, use_container_width=True)
    
    # Additional information
    st.markdown("""
    ### 📋 Additional Information
    
    - **Minimum Order:** No minimum order requirement
    - **Turnaround Time:** 24-48 hours (depending on load)
    - **Payment:** Cash on delivery
    - **Quality Guarantee:** 100% satisfaction guaranteed
    """)
    
    # Why Choose Express Wash section with better styling
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown("### 🎯 Why Choose Express Wash?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🏆 Professional Service**
        - Experienced staff with years of expertise
        - Modern equipment and quality detergents
        - Attention to detail in every order
        
        **💰 Competitive Pricing**
        - Transparent pricing with no hidden costs
        - Bulk order discounts available
        - Special rates for regular customers
        
        **⚡ Quick Turnaround**
        - Same day service for urgent orders
        - Regular orders completed in 24-48 hours
        - Express service available
        """)
    
    with col2:
        st.markdown("""
        **🧼 Quality Assurance**
        - 100% satisfaction guarantee
        - Quality check before delivery
        - Free re-wash if not satisfied
        
        **🚚 Convenient Location**
        - Located in Warje, Pune
        - Easy access and parking
        - Home pickup and delivery available
        
        **📞 Excellent Support**
        - 24/7 customer support
        - WhatsApp booking available
        - Quick response to queries
        """)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Payment Options section with better styling
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown("### 💳 Payment Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **💰 Cash on Delivery**
        - Pay when you collect your clothes
        - No advance payment required
        - Most popular option
        """)
    
    with col2:
        st.markdown("""
        **📱 UPI Payment**
        - Quick and secure digital payment
        - Multiple UPI apps supported
        - Instant payment confirmation
        """)
    
    with col3:
        st.markdown("""
        **🏦 Bank Transfer**
        - Direct bank transfer available
        - Account details provided on request
        - Receipt sent via WhatsApp
        """)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Contact information
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown("### 📞 Contact Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Express Wash**  
        📱 Mobile: +91 7499902809  
        📧 Email: expresswash@gmail.com  
        📍 Address: Mai Nivas, Bhalekar Wasti, Warje Jakat Naka, Pune - 411058
        """)
    
    with col2:
        st.markdown("""
        **🕒 Business Hours**  
        Monday - Sunday: 8:00 AM - 8:00 PM  
        
        **🗺️ Location**  
        18°29'02.3"N 73°48'43.1"E
        """)
    
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main() 