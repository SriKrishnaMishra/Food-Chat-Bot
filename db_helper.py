# Author: Dhaval Patel. Codebasics YouTube Channel

import mysql.connector
from mysql.connector import Error
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database configuration from environment variables with fallbacks
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "pandeyji_eatery"),
    "autocommit": False,
    "use_unicode": True,
    "charset": "utf8mb4"
}

# Function to get a database connection with retry logic
def get_db_connection():
    """
    Get a database connection with proper error handling
    
    Returns:
        mysql.connector.connection: Database connection object or None if failed
    """
    try:
        # Check if password is set
        if not DB_CONFIG["password"]:
            logger.warning("Database password not set. Please configure DB_PASSWORD in .env file")
            return None
            
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            logger.info("Successfully connected to MySQL database")
            return connection
    except Error as e:
        if "Access denied" in str(e):
            logger.error(f"Database access denied. Please check your credentials in .env file: {e}")
        elif "Unknown database" in str(e):
            logger.error(f"Database '{DB_CONFIG['database']}' does not exist. Please create it first: {e}")
        else:
            logger.error(f"Error connecting to MySQL database: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error connecting to database: {e}")
        return None

# Global connection object - initialize as None to handle connection failures gracefully
cnx = None

try:
    cnx = get_db_connection()
    if not cnx:
        logger.warning("Database connection not established. Some features may not work properly.")
except Exception as e:
    logger.error(f"Failed to initialize database connection: {str(e)}", exc_info=True)

# Function to call the MySQL stored procedure and insert an order item
def insert_order_item(food_item, quantity, order_id):
    connection = None
    cursor = None
    try:
        # Get a new connection if the global one is not available
        connection = cnx if cnx and cnx.is_connected() else get_db_connection()
        if not connection:
            logger.error("Failed to get database connection")
            return -1

        cursor = connection.cursor()

        # Calling the stored procedure
        cursor.callproc('insert_order_item', (food_item, quantity, order_id))

        # Committing the changes
        connection.commit()

        logger.info(f"Order item '{food_item}' (qty: {quantity}) inserted successfully for order ID: {order_id}")
        return 1

    except mysql.connector.Error as err:
        logger.error(f"Error inserting order item: {err}")
        # Rollback changes if necessary
        if connection:
            connection.rollback()
        return -1

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        # Rollback changes if necessary
        if connection:
            connection.rollback()
        return -1

    finally:
        # Closing the cursor
        if cursor:
            cursor.close()

# Function to insert a record into the order_tracking table
def insert_order_tracking(order_id, status):
    connection = None
    cursor = None
    try:
        # Get a new connection if the global one is not available
        connection = cnx if cnx and cnx.is_connected() else get_db_connection()
        if not connection:
            logger.error("Failed to get database connection")
            return -1

        cursor = connection.cursor()

        # Inserting the record into the order_tracking table
        insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
        cursor.execute(insert_query, (order_id, status))

        # Committing the changes
        connection.commit()

        logger.info(f"Order tracking inserted successfully for order ID: {order_id}, status: {status}")
        return 1

    except mysql.connector.Error as err:
        logger.error(f"Error inserting order tracking: {err}")
        if connection:
            connection.rollback()
        return -1

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        if connection:
            connection.rollback()
        return -1

    finally:
        # Closing the cursor
        if cursor:
            cursor.close()

def get_total_order_price(order_id):
    connection = None
    cursor = None
    try:
        # Get a new connection if the global one is not available
        connection = cnx if cnx and cnx.is_connected() else get_db_connection()
        if not connection:
            logger.error("Failed to get database connection")
            return 0

        cursor = connection.cursor()

        # Executing the SQL query to get the total order price
        query = f"SELECT get_total_order_price({order_id})"
        cursor.execute(query)

        # Fetching the result
        result = cursor.fetchone()[0]

        logger.info(f"Total price for order ID {order_id}: {result}")
        return result

    except mysql.connector.Error as err:
        logger.error(f"Error getting total order price: {err}")
        return 0

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return 0

    finally:
        # Closing the cursor
        if cursor:
            cursor.close()

# Function to get the next available order_id
def get_next_order_id():
    connection = None
    cursor = None
    try:
        # Get a new connection if the global one is not available
        connection = cnx if cnx and cnx.is_connected() else get_db_connection()
        if not connection:
            logger.error("Failed to get database connection")
            return 1

        cursor = connection.cursor()

        # Executing the SQL query to get the next available order_id
        query = "SELECT MAX(order_id) FROM orders"
        cursor.execute(query)

        # Fetching the result
        result = cursor.fetchone()[0]

        # Returning the next available order_id
        next_id = 1 if result is None else result + 1
        logger.info(f"Next order ID: {next_id}")
        return next_id

    except mysql.connector.Error as err:
        logger.error(f"Error getting next order ID: {err}")
        return 1

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return 1

    finally:
        # Closing the cursor
        if cursor:
            cursor.close()

# Function to fetch the order status from the order_tracking table
def get_order_status(order_id):
    connection = None
    cursor = None
    try:
        # Get a new connection if the global one is not available
        connection = cnx if cnx and cnx.is_connected() else get_db_connection()
        if not connection:
            logger.error("Failed to get database connection")
            return None

        cursor = connection.cursor()

        # Using parameterized query to prevent SQL injection
        query = "SELECT status FROM order_tracking WHERE order_id = %s"
        cursor.execute(query, (order_id,))

        # Fetching the result
        result = cursor.fetchone()

        # Returning the order status
        if result:
            logger.info(f"Status for order ID {order_id}: {result[0]}")
            return result[0]
        else:
            logger.warning(f"No status found for order ID {order_id}")
            return None

    except mysql.connector.Error as err:
        logger.error(f"Error getting order status: {err}")
        return None

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None

    finally:
        # Closing the cursor
        if cursor:
            cursor.close()


if __name__ == "__main__":
    # print(get_total_order_price(56))
    # insert_order_item('Samosa', 3, 99)
    # insert_order_item('Pav Bhaji', 1, 99)
    # insert_order_tracking(99, "in progress")
    print(get_next_order_id())
