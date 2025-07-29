# 🍽️Food Chatbot 

A FastAPI-based chatbot application for managing food orders through Dialogflow webhook integration.

## 🚀 Features

[old README content]
# 🍽️ Mishraji Eatery - Food Ordering Chatbot

A modern, interactive food ordering chatbot built with FastAPI. Includes a beautiful web interface, smart order management, and demo mode for instant testing.

---

## 🚀 Features

- **Modern Chat UI**: Responsive, animated chat interface
- **Menu Display**: All food items and prices shown
- **Order Management**: Add, remove, and complete orders
- **Order Tracking**: Simulated order status
- **Quick Order Buttons**: One-click sample orders
- **API Documentation**: Auto-generated docs at `/docs`
- **Demo Mode**: Works instantly without database setup

---

## 🛠️ Getting Started

### 1. **Demo Mode (No Database Required)**

1. Run the demo app:
   ```bash
   python demo_app.py
   ```
2. Open your browser at [http://localhost:8000](http://localhost:8000)
3. Try placing orders, adding/removing items, and tracking orders!

### 2. **Full Database Mode (Production)**

1. Set your MySQL password in `.env`:
   ```env
   DB_PASSWORD=your_mysql_password
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the database:
   ```bash
   python setup_database.py
   ```
4. Start the app:
   ```bash
   python run.py
   ```
5. Visit [http://localhost:8000](http://localhost:8000)

---

## 📋 Menu Items

- Pav Bhaji - $2.50
- Chole Bhature - $3.00
- Pizza - $8.50
- Mango Lassi - $2.00
- Masala Dosa - $4.00
- Biryani - $6.50
- Vada Pav - $1.50
- Samosa - $1.00
- Idli - $2.50
- Dhokla - $2.00

---

## 🤖 Example Interactions

- **Place Order**: `I want 2 pizza and 1 biryani`
- **Add Item**: `Add 1 samosa`
- **Remove Item**: `Remove pizza`
- **Complete Order**: `That's all`
- **Track Order**: `Track order 123`

---

## 🔧 Project Structure

```
food_chat_bot/
├── demo_app.py           # Demo version (no database needed)
├── main.py               # Full FastAPI app (with database)
├── db_helper.py          # Database operations
├── generic_helper.py     # Utility functions
├── setup_database.py     # Database setup script
├── run.py                # App startup script
├── quick_setup.py        # Quick MySQL password setup
├── interactive_setup.py  # Step-by-step setup wizard
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── templates/index.html  # Web interface template
├── static/               # Static files (CSS, JS, images)
└── README.md             # Project documentation
```

---

## 📖 API Endpoints

- `/` - Web chat interface
- `/webhook` - Dialogflow webhook endpoint
- `/api` - API status/info
- `/docs` - Interactive API documentation

---

## 🐛 Troubleshooting

- **MySQL Not Running**: Start MySQL service (see TROUBLESHOOTING.md)
- **Wrong Password**: Edit `.env` and re-run `quick_setup.py`
- **No Data/Website**: Run `demo_app.py` for instant demo

---

## 💡 Tips

- Use demo mode for instant testing and UI preview
- Switch to full mode for real database-backed orders
- All code is modular and easy to extend

---

## 📞 Support

- See `TROUBLESHOOTING.md` for common issues
- Ask questions or request features any time!

---

## 📝 License

Open source, based on Codebasics YouTube project, improved for modern web and chatbot experience.
## 📋 Prerequisites

- Python 3.8+
- MySQL Server 5.7+ or 8.0+
- Dialogflow Project (for chatbot integration)

## 🛠️ Installation

1. **Clone or download the project**
   ```bash
   cd food_chat_bot
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   - Copy `.env` file and update with your settings:
   ```env
   # Database Configuration
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=pandeyji_eatery
   
   # Server Configuration
   SERVER_HOST=0.0.0.0
   SERVER_PORT=8000
   
   # Logging Configuration
   LOG_LEVEL=INFO
   ```

4. **Set up the database**
   ```bash
   python setup_database.py
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

## 🗄️ Database Setup

The `setup_database.py` script will automatically create:

- **Database**: `pandeyji_eatery`
- **Tables**:
  - `food_items` - Menu items with prices
  - `orders` - Order details with quantities and prices
  - `order_tracking` - Order status tracking
- **Stored Procedures**: For inserting order items
- **Functions**: For calculating order totals
- **Sample Data**: Pre-populated menu items

### Sample Menu Items
- Pav Bhaji - $2.50
- Chole Bhature - $3.00
- Pizza - $8.50
- Mango Lassi - $2.00
- Masala Dosa - $4.00
- Biryani - $6.50
- Vada Pav - $1.50
- Samosa - $1.00
- Idli - $2.50
- Dhokla - $2.00

## 🔌 API Endpoints

### Health Check
- **GET** `/` - Check if the API is running

### Webhook
- **POST** `/` - Main webhook endpoint for Dialogflow

## 🤖 Supported Intents

1. **Add to Order** (`order.add - context: ongoing-order`)
   - Add food items with quantities to current order
   - Example: "I want 2 pizza and 1 mango lassi"

2. **Remove from Order** (`order.remove - context: ongoing-order`)
   - Remove items from current order
   - Example: "Remove pizza from my order"

3. **Complete Order** (`order.complete - context: ongoing-order`)
   - Finalize and save order to database
   - Returns order ID and total price

4. **Track Order** (`track.order - context: ongoing-tracking`)
   - Check order status by order ID
   - Example: "Track order 123"

## 📱 Usage Examples

### Starting an Order
1. User: "I want to order food"
2. Bot: "Sure! What would you like to order?"
3. User: "2 pizza and 1 biryani"
4. Bot: "Great! I've added that to your order. So far you have: 2 pizza, 1 biryani. Would you like to add anything else?"

### Completing an Order
1. User: "That's all"
2. Bot: "Awesome. We have placed your order. Here is your order id # 456. Your order total is $23.50 which you can pay at the time of delivery!"

### Tracking an Order
1. User: "Track my order 456"
2. Bot: "The order status for order id: 456 is: in progress"

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | MySQL host | `localhost` |
| `DB_USER` | MySQL username | `root` |
| `DB_PASSWORD` | MySQL password | *(required)* |
| `DB_NAME` | Database name | `pandeyji_eatery` |
| `SERVER_HOST` | Server bind address | `0.0.0.0` |
| `SERVER_PORT` | Server port | `8000` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Dialogflow Setup

1. Create a new Dialogflow project
2. Set up intents with the names mentioned above
3. Configure webhook URL to point to your FastAPI server
4. Train your model with appropriate training phrases

## 📝 Logging

The application logs all activities to:
- Console output
- `app.log` file

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## 🔒 Security Features

- Environment-based configuration
- SQL injection prevention with parameterized queries
- CORS middleware for cross-origin requests
- Comprehensive error handling
- Input validation and sanitization

## 🛠️ Development

### Project Structure
```
food_chat_bot/
├── main.py              # FastAPI application
├── db_helper.py         # Database operations
├── generic_helper.py    # Utility functions
├── run.py              # Application startup script
├── setup_database.py   # Database setup script
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── .gitignore         # Git ignore rules
└── README.md          # Documentation
```

### Adding New Features

1. **New Intent**: Add handler function and update `intent_handler_dict` in `main.py`
2. **New Database Operation**: Add function in `db_helper.py`
3. **New Utility**: Add function in `generic_helper.py`

## 🐛 Troubleshooting

### Database Connection Issues
- Verify MySQL is running
- Check credentials in `.env` file
- Ensure database exists (run `setup_database.py`)

### Import Errors
- Install dependencies: `pip install -r requirements.txt`
- Check Python version (3.8+ required)

### Dialogflow Integration
- Verify webhook URL is accessible
- Check intent names match exactly
- Ensure proper training phrases are configured

## 📄 License

This project is based on the original work by Dhaval Patel from Codebasics YouTube Channel, with improvements and enhancements.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in `app.log`
3. Ensure all prerequisites are met
4. Verify configuration in `.env` file
