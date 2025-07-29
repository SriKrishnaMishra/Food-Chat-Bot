"""
Interactive setup script for Pandeyji Eatery
This script will help you configure the database connection step by step
"""

import mysql.connector
from mysql.connector import Error
import os
import getpass
from dotenv import load_dotenv, set_key

def test_mysql_connection(host, user, password):
    """Test MySQL connection with given credentials"""
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        if connection.is_connected():
            connection.close()
            return True, "Connection successful!"
    except Error as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)
    
    return False, "Unknown error"

def setup_environment():
    """Interactive setup for environment variables"""
    print("🔧 Pandeyji Eatery - Interactive Setup")
    print("=" * 50)
    
    # Load existing .env if it exists
    env_file = ".env"
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print("✅ Found existing .env file")
    else:
        print("📝 Creating new .env file")
    
    # Get database configuration
    print("\n📊 Database Configuration:")
    
    # Host
    db_host = input(f"Enter MySQL host [{os.getenv('DB_HOST', 'localhost')}]: ").strip()
    if not db_host:
        db_host = os.getenv('DB_HOST', 'localhost')
    
    # User
    db_user = input(f"Enter MySQL username [{os.getenv('DB_USER', 'root')}]: ").strip()
    if not db_user:
        db_user = os.getenv('DB_USER', 'root')
    
    # Password
    current_password = os.getenv('DB_PASSWORD', '')
    if current_password and current_password != 'your_password_here':
        use_existing = input(f"Use existing password? (y/n) [y]: ").strip().lower()
        if use_existing in ['', 'y', 'yes']:
            db_password = current_password
        else:
            db_password = getpass.getpass("Enter MySQL password: ")
    else:
        db_password = getpass.getpass("Enter MySQL password: ")
    
    # Database name
    db_name = input(f"Enter database name [{os.getenv('DB_NAME', 'pandeyji_eatery')}]: ").strip()
    if not db_name:
        db_name = os.getenv('DB_NAME', 'pandeyji_eatery')
    
    # Test connection
    print("\n🔍 Testing database connection...")
    success, message = test_mysql_connection(db_host, db_user, db_password)
    
    if not success:
        print(f"❌ Connection failed: {message}")
        print("\nPlease check:")
        print("1. MySQL service is running")
        print("2. Username and password are correct") 
        print("3. Host is accessible")
        return False
    
    print("✅ Database connection successful!")
    
    # Save to .env file
    print("\n💾 Saving configuration to .env file...")
    try:
        set_key(env_file, "DB_HOST", db_host)
        set_key(env_file, "DB_USER", db_user)
        set_key(env_file, "DB_PASSWORD", db_password)
        set_key(env_file, "DB_NAME", db_name)
        set_key(env_file, "SERVER_HOST", "0.0.0.0")
        set_key(env_file, "SERVER_PORT", "8000")
        set_key(env_file, "LOG_LEVEL", "INFO")
        
        print("✅ Configuration saved successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False

def create_database_and_tables(host, user, password, database_name):
    """Create the database and required tables"""
    connection = None
    cursor = None
    
    try:
        # Connect to MySQL server
        print(f"Connecting to MySQL server at {host}...")
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        print(f"Creating database '{database_name}' if it doesn't exist...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        print(f"✅ Database '{database_name}' is ready")
        
        # Switch to the database
        cursor.execute(f"USE {database_name}")
        
        # Create food_items table
        print("Creating food_items table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS food_items (
                item_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                price DECIMAL(10, 2) NOT NULL
            )
        """)
        
        # Create orders table
        print("Creating orders table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INT NOT NULL,
                item_id INT NOT NULL,
                quantity INT NOT NULL,
                total_price DECIMAL(10, 2) NOT NULL,
                PRIMARY KEY (order_id, item_id),
                FOREIGN KEY (item_id) REFERENCES food_items(item_id)
            )
        """)
        
        # Create order_tracking table
        print("Creating order_tracking table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_tracking (
                order_id INT PRIMARY KEY,
                status VARCHAR(100) NOT NULL
            )
        """)
        
        # Insert sample food items
        print("Inserting sample food items...")
        sample_items = [
            ("Pav Bhaji", 2.50),
            ("Chole Bhature", 3.00),
            ("Pizza", 8.50),
            ("Mango Lassi", 2.00),
            ("Masala Dosa", 4.00),
            ("Biryani", 6.50),
            ("Vada Pav", 1.50),
            ("Samosa", 1.00),
            ("Idli", 2.50),
            ("Dhokla", 2.00)
        ]
        
        cursor.executemany(
            "INSERT IGNORE INTO food_items (name, price) VALUES (%s, %s)",
            sample_items
        )
        
        # Create stored procedure for inserting order items
        print("Creating stored procedure...")
        cursor.execute("DROP PROCEDURE IF EXISTS insert_order_item")
        cursor.execute("""
            CREATE PROCEDURE insert_order_item(
                IN p_food_item VARCHAR(255),
                IN p_quantity INT,
                IN p_order_id INT
            )
            BEGIN
                DECLARE food_item_id INT;
                DECLARE item_price DECIMAL(10, 2);
                DECLARE total_item_price DECIMAL(10, 2);
                
                -- Get food item details
                SELECT item_id, price INTO food_item_id, item_price
                FROM food_items 
                WHERE name = p_food_item;
                
                -- Calculate total price for this item
                SET total_item_price = item_price * p_quantity;
                
                -- Insert into orders table
                INSERT INTO orders (order_id, item_id, quantity, total_price)
                VALUES (p_order_id, food_item_id, p_quantity, total_item_price);
            END
        """)
        
        # Create function to get total order price
        cursor.execute("DROP FUNCTION IF EXISTS get_total_order_price")
        cursor.execute("""
            CREATE FUNCTION get_total_order_price(p_order_id INT)
            RETURNS DECIMAL(10, 2)
            READS SQL DATA
            DETERMINISTIC
            BEGIN
                DECLARE total DECIMAL(10, 2) DEFAULT 0;
                
                SELECT SUM(total_price) INTO total
                FROM orders
                WHERE order_id = p_order_id;
                
                RETURN IFNULL(total, 0);
            END
        """)
        
        # Commit changes
        connection.commit()
        print("✅ Database setup completed successfully!")
        
        # Display sample data
        cursor.execute("SELECT * FROM food_items")
        items = cursor.fetchall()
        print(f"\n📋 Available food items ({len(items)} items):")
        for item in items:
            print(f"   {item[1]} - ${item[2]}")
            
        return True
            
    except Error as e:
        print(f"❌ Error setting up database: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def main():
    """Main setup function"""
    print("🍽️ Welcome to Pandeyji Eatery Setup!")
    print("This script will help you configure and set up the application.\n")
    
    # Step 1: Environment setup
    if not setup_environment():
        print("\n❌ Environment setup failed!")
        print("Please try again and ensure MySQL is running.")
        return
    
    # Reload environment variables
    load_dotenv()
    
    # Step 2: Database setup
    print("\n🗄️ Setting up database...")
    db_host = os.getenv('DB_HOST')
    db_user = os.getenv('DB_USER') 
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')
    
    if create_database_and_tables(db_host, db_user, db_password, db_name):
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run the application: python run.py")
        print("2. Visit http://localhost:8000/docs for API documentation")
        print("3. Configure your Dialogflow webhook to point to your server")
    else:
        print("\n❌ Database setup failed!")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
