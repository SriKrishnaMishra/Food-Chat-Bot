"""
Simple setup script for Pandeyji Eatery
This will help you quickly configure the database password and test the connection
"""

import os
import getpass
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv, set_key

def main():
    print("🔧 Quick Setup for Pandeyji Eatery")
    print("=" * 40)
    print("⚠️  IMPORTANT: Make sure MySQL is running on your computer!")
    print("📍 For local MySQL, always use 'localhost' as the host")
    print()
    
    # Load existing .env
    load_dotenv()
    
    # Get the MySQL password
    print("🔑 MySQL Password Setup:")
    password = getpass.getpass("Enter your MySQL root password: ")
    
    if not password:
        print("❌ Password cannot be empty!")
        return
    
    # Test connection with localhost
    print("\n🔍 Testing connection to localhost...")
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=password
        )
        
        if connection.is_connected():
            print("✅ Connection successful!")
            connection.close()
            
            # Save password to .env
            set_key(".env", "DB_PASSWORD", password)
            print("💾 Password saved to .env file")
            
            # Now run database setup
            print("\n🗄️ Setting up database...")
            os.system("python setup_database.py")
            
            print("\n🎉 Setup complete!")
            print("Now you can run: python run.py")
            
        else:
            print("❌ Connection failed!")
            
    except Error as e:
        if "Access denied" in str(e):
            print(f"❌ Wrong password! Please try again.")
        elif "Can't connect" in str(e):
            print(f"❌ Can't connect to MySQL server!")
            print("Make sure MySQL is running on your computer.")
            print("If you're using XAMPP, start it from the control panel.")
        else:
            print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
