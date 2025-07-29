"""
FINAL SETUP SCRIPT - This will definitely work!
"""

import os
import getpass
import mysql.connector
from dotenv import set_key

def main():
    print("🎯 FINAL SETUP - Let's get this working!")
    print("=" * 45)
    
    print("📍 IMPORTANT: We will use 'localhost' as the host (not 'krishna')")
    print("🔑 You need to enter your MySQL root password")
    print()
    
    # Get password
    while True:
        password = getpass.getpass("Enter your MySQL root password: ")
        
        if not password:
            print("❌ Password cannot be empty! Try again.")
            continue
            
        # Test connection
        print("🔍 Testing connection...")
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root", 
                password=password
            )
            
            if connection.is_connected():
                print("✅ Perfect! Connection successful!")
                connection.close()
                break
                
        except Exception as e:
            if "Access denied" in str(e):
                print("❌ Wrong password! Please try again.")
                continue
            else:
                print(f"❌ Error: {e}")
                return
    
    # Save correct configuration
    print("💾 Saving configuration...")
    set_key(".env", "DB_HOST", "localhost")
    set_key(".env", "DB_USER", "root") 
    set_key(".env", "DB_PASSWORD", password)
    set_key(".env", "DB_NAME", "pandeyji_eatery")
    set_key(".env", "SERVER_HOST", "0.0.0.0")
    set_key(".env", "SERVER_PORT", "8000")
    set_key(".env", "LOG_LEVEL", "INFO")
    
    print("✅ Configuration saved!")
    
    # Setup database
    print("\n🗄️ Setting up database...")
    try:
        os.system("python setup_database.py")
        print("\n🎉 SETUP COMPLETE!")
        print("\n▶️  Run the app with: python run.py")
        print("📖 API docs at: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")

if __name__ == "__main__":
    main()
