"""
Test MySQL connection without password to check if service is running
"""

import mysql.connector
from mysql.connector import Error

def test_mysql_service():
    print("🔍 Testing if MySQL service is running...")
    
    try:
        # Try to connect without password to see if service is running
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""  # Empty password
        )
        print("✅ MySQL is running (no password set)")
        connection.close()
        return True
        
    except Error as e:
        if "Access denied" in str(e):
            print("✅ MySQL is running (password required)")
            return True
        elif "Can't connect" in str(e):
            print("❌ MySQL service is not running!")
            print("\n🔧 How to start MySQL:")
            print("1. Windows Services: Press Win+R → services.msc → Find MySQL → Start")
            print("2. XAMPP: Open XAMPP Control Panel → Start MySQL")
            print("3. Command line: net start mysql80 (or your MySQL service name)")
            return False
        else:
            print(f"❌ MySQL connection error: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_mysql_status():
    """Check MySQL service status on Windows"""
    import subprocess
    try:
        # Check if MySQL service is running
        result = subprocess.run(['sc', 'query', 'mysql80'], 
                              capture_output=True, text=True)
        if 'RUNNING' in result.stdout:
            print("✅ MySQL80 service is running")
            return True
        elif 'STOPPED' in result.stdout:
            print("❌ MySQL80 service is stopped")
            print("💡 Start it with: net start mysql80")
            return False
        else:
            # Try other common MySQL service names
            for service in ['mysql', 'mysql57', 'mysql84']:
                result = subprocess.run(['sc', 'query', service], 
                                      capture_output=True, text=True)
                if 'RUNNING' in result.stdout:
                    print(f"✅ {service} service is running")
                    return True
            print("❌ No MySQL service found running")
            return False
    except Exception as e:
        print(f"⚠️  Could not check service status: {e}")
        return False

if __name__ == "__main__":
    print("🔍 MySQL Service Diagnostic")
    print("=" * 30)
    
    # Check service status
    service_running = check_mysql_status()
    print()
    
    # Test connection
    connection_test = test_mysql_service()
    
    print("\n📋 Summary:")
    print(f"Service Status: {'✅ Running' if service_running else '❌ Stopped'}")
    print(f"Connection Test: {'✅ Accessible' if connection_test else '❌ Failed'}")
    
    if connection_test:
        print("\n🎉 MySQL is ready! You can now run: python quick_setup.py")
    else:
        print("\n❌ Please start MySQL service first, then try again.")
