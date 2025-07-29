"""
Database setup script for Pandeyji Eatery
This script creates the necessary database and tables
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database_and_tables():
    """Create the database and required tables"""
    
    # Database configuration without specifying the database initially
    config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "")
    }
    
    database_name = os.getenv("DB_NAME", "pandeyji_eatery")
    
    connection = None
    cursor = None
    
    try:
        # Check if password is provided
        if not config["password"]:
            print("❌ Database password not found!")
            print("Please set DB_PASSWORD in your .env file")
            print("Example: DB_PASSWORD=your_mysql_password")
            return False
            
        # Connect to MySQL server
        print(f"Connecting to MySQL server at {config['host']}...")
        connection = mysql.connector.connect(**config)
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
            
    except Error as e:
        if "Access denied" in str(e):
            print(f"❌ Database access denied!")
            print("Please check your MySQL credentials in the .env file")
            print("Make sure MySQL is running and credentials are correct")
        elif "Unknown database" in str(e):
            print(f"❌ Database connection error: {e}")
        else:
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
    
    return True

if __name__ == "__main__":
    print("🗄️  Setting up Pandeyji Eatery Database...")
    print("=" * 50)
    
    if create_database_and_tables():
        print("\n🎉 Database setup completed successfully!")
        print("You can now run the application with: python run.py")
    else:
        print("\n❌ Database setup failed!")
        print("Please check your MySQL connection and credentials in .env file")
