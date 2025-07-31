# Express Wash v3.5 - Complete Laundry Management System

## 🎯 Project Overview

Express Wash v3.5 is a comprehensive laundry management solution designed for real-world laundry shops. The system provides three distinct applications catering to different user needs:

1. **Tkinter Desktop App** (`tkinter_app.py`) - For shop staff
2. **Streamlit Web App** (`app.py`) - For owner/staff remote access
3. **Customer Portal** (`app_for_customer.py`) - For customer self-service

## 🏗️ System Architecture

### Database Schema
```sql
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    receipt_number VARCHAR(50) UNIQUE,
    customer_name VARCHAR(255) NOT NULL,
    mobile_number VARCHAR(20),
    order_date DATE NOT NULL,
    regular_clothes_kg DECIMAL(5,2) DEFAULT 0,
    blankets_kg DECIMAL(5,2) DEFAULT 0,
    white_clothes_pieces INT DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    status ENUM('pending', 'ready', 'collected') DEFAULT 'pending',
    collection_date DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Pricing Structure
- **Regular Clothes**: ₹50/kg
- **Blankets/Bedsheets/Rugs/Duvets**: ₹100/kg
- **White Clothes**: ₹40/piece

## 📱 Application Features

### 1. Tkinter Desktop App (`tkinter_app.py`)

#### Core Features:
- **Manual Receipt Number Entry**: Primary key for order tracking
- **Real-time Bill Calculation**: Dynamic pricing based on service quantities
- **Order Management**: Create, Read, Update, Delete operations
- **Collection Tracking**: Mark orders as collected with timestamp
- **SMS Notifications**: Fast2SMS API integration
- **Invoice Generation**: Print-friendly order summaries
- **Comprehensive Reports**: Business analytics with charts

#### Advanced Features:
- **Multi-tab Reports Dashboard**:
  - Summary Dashboard with key metrics
  - Revenue Analysis with time-based filters
  - Order Status Distribution (pie charts)
  - Time-based Reports (daily/weekly/monthly)
- **Visual Analytics**: Matplotlib charts for business insights
- **Order Status Management**: Pending → Ready → Collected workflow
- **Collection Date Tracking**: Automatic timestamp on collection

#### SMS Integration:
```python
# Fast2SMS API Configuration
SMS_API_KEY = "XerDBCLIaGm0dR2AHO6phqNcunktPogVvF9w1jWxfK38EUQyJMNDId3H9pbPKGuxohtUQjMrBAizl1L7"
SMS_API_URL = "https://www.fast2sms.com/dev/bulkV2"
```

### 2. Streamlit Web App (`app.py`)

#### Core Features:
- **Remote Order Management**: Access from any device
- **CRUD Operations**: Full order lifecycle management
- **Order Collection**: Receipt-based collection tracking
- **SMS Notifications**: Customer collection confirmations
- **Data Export**: CSV download functionality
- **Search & Filter**: Advanced order filtering

#### Enhanced Features:
- **Order Collection Section**: 
  - Receipt number input
  - Automatic status update
  - SMS notification on collection
- **Visual Charts**: Plotly-based analytics
- **Responsive Design**: Mobile-friendly interface
- **Real-time Updates**: Live data synchronization

### 3. Customer Portal (`app_for_customer.py`)

#### Core Features:
- **Self-Service Order Placement**: Customer-friendly interface
- **Receipt Number Management**: Auto-generation or manual entry
- **Bill Preview**: Real-time cost calculation
- **SMS Confirmation**: Order placement notifications
- **Order Status**: Pending order tracking

#### User Experience:
- **Clean Interface**: Minimal, intuitive design
- **Mobile Optimized**: Responsive layout
- **Auto-receipt Generation**: RW-YYYYMMDD-HHMMSS format
- **Order Confirmation**: Detailed order summary
- **SMS Integration**: Instant order confirmations

## 🔧 Technical Implementation

### Database Connectivity
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '16021995',
    'database': 'express_wash'
}
```

### SMS Integration (Fast2SMS)
```python
def send_sms(phone_number, message):
    payload = {
        "sender_id": "FSTSMS",
        "message": message,
        "language": "english",
        "route": "v3",
        "numbers": phone_number
    }
    headers = {
        'authorization': SMS_API_KEY,
        'Content-Type': "application/json"
    }
    response = requests.post(SMS_API_URL, json=payload, headers=headers)
    return response.json().get('return') == True
```

### Receipt Number Generation
```python
def generate_receipt_number():
    today = date.today()
    return f"RW-{today.strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
```

## 📊 Business Intelligence Features

### 1. Summary Dashboard
- Total Orders Count
- Total Revenue
- Pending Orders
- Collected Orders
- Revenue Trend Charts
- Service Usage Breakdown

### 2. Revenue Analysis
- Time-based filtering (Today, Week, 15/30 Days, 3/6 Months)
- Revenue trend visualization
- Period comparison charts

### 3. Order Status Analytics
- Status distribution pie charts
- Collection rate analysis
- Service popularity metrics

### 4. Time-based Reports
- Daily order summaries
- Weekly revenue reports
- Monthly business analytics

## 🚀 Deployment & Usage

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run applications
python tkinter_app.py                    # Desktop app
streamlit run app.py --server.port 8501  # Web app
streamlit run app_for_customer.py --server.port 8502  # Customer portal
```

### Database Setup
```bash
# Initialize database
python mysql_setup.py

# Add sample data (optional)
python sample_data.py
```

## 📱 SMS Notifications

### Order Placement
```
Order placed successfully!
Receipt: RW-20241201-143022
Customer: John Doe
Date: 2024-12-01
Total: ₹150.00
Status: Pending
We'll notify you when ready!
```

### Order Collection
```
Hi John Doe, your laundry order #RW-20241201-143022 has been collected. 
Thank you for using Express Wash!
```

## 🎯 Key Benefits

### For Shop Staff:
- **Efficient Order Management**: Quick order entry and tracking
- **Real-time Analytics**: Business insights and reports
- **Collection Tracking**: Automated status updates
- **Customer Communication**: SMS notifications

### For Shop Owner:
- **Remote Access**: Manage business from anywhere
- **Business Intelligence**: Comprehensive analytics
- **Customer Satisfaction**: Automated notifications
- **Data Export**: Backup and reporting capabilities

### For Customers:
- **Self-Service**: Place orders independently
- **Transparency**: Real-time bill calculation
- **Communication**: SMS confirmations
- **Convenience**: Mobile-friendly interface

## 🔒 Security & Data Management

### Data Protection:
- MySQL database with proper indexing
- CSV backup synchronization
- Receipt number uniqueness validation
- Input validation and sanitization

### Backup Strategy:
- Automatic CSV backup
- Database transaction logging
- Order history preservation
- Export functionality

## 📈 Scalability Features

### Multi-User Support:
- Concurrent access handling
- Database connection pooling
- Real-time data synchronization
- Conflict resolution

### Performance Optimization:
- Efficient database queries
- Cached calculations
- Responsive UI design
- Minimal resource usage

## 🎨 User Interface Design

### Tkinter App:
- Professional desktop interface
- Intuitive navigation
- Color-coded status indicators
- Responsive layout

### Streamlit Apps:
- Modern web interface
- Mobile-responsive design
- Interactive charts
- Clean typography

## 🔄 Workflow Integration

### Order Lifecycle:
1. **Order Placement** → SMS confirmation
2. **Processing** → Status tracking
3. **Ready** → Customer notification
4. **Collection** → SMS thank you

### Business Process:
1. **Customer Input** → Order creation
2. **Service Selection** → Bill calculation
3. **Payment** → Receipt generation
4. **Collection** → Status update

## 📋 Future Enhancements

### Planned Features:
- **Payment Integration**: Online payment processing
- **Inventory Management**: Stock tracking
- **Customer Portal**: Order history and tracking
- **Advanced Analytics**: Predictive analytics
- **Multi-location Support**: Branch management
- **API Integration**: Third-party integrations

### Technical Improvements:
- **Cloud Deployment**: AWS/Azure hosting
- **Mobile App**: React Native application
- **Real-time Updates**: WebSocket integration
- **Advanced Security**: OAuth authentication

## 🏆 Project Achievements

### Real-World Application:
- **Complete Business Solution**: End-to-end laundry management
- **Professional Grade**: Production-ready code
- **User-Friendly**: Intuitive interfaces
- **Scalable Architecture**: Extensible design

### Technical Excellence:
- **Multi-Platform**: Desktop and web applications
- **Database Integration**: MySQL with proper schema
- **SMS Integration**: Fast2SMS API
- **Data Visualization**: Matplotlib and Plotly charts
- **CRUD Operations**: Full data management

### Portfolio Value:
- **Real-World Problem**: Actual business use case
- **Modern Technologies**: Python, Streamlit, Tkinter, MySQL
- **Professional Features**: SMS, analytics, reporting
- **Complete Documentation**: Comprehensive guides

## 📞 Support & Maintenance

### System Requirements:
- Python 3.8+
- MySQL 8.0+
- Windows/Linux/macOS compatibility
- Internet connection for SMS

### Maintenance:
- Regular database backups
- SMS API key management
- System updates and patches
- Performance monitoring

---

**Express Wash v3.5** represents a complete, professional-grade laundry management solution that demonstrates real-world application development with modern technologies and best practices. 