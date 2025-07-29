# 🚨 Troubleshooting Guide - Food Chatbot Issues

## Current Error Analysis

Based on your setup attempt, here are the issues and solutions:

### ❌ **Problem 1: Wrong MySQL Host**
**Error:** `Host 'krishna' is not allowed to connect to this MySQL server`

**Solution:** 
- Always use `localhost` for local MySQL installations
- Don't use custom names like "krishna" for the host

### ❌ **Problem 2: Database Password Not Set**
**Error:** Using placeholder password `your_password_here`

**Solution:**
1. Set your actual MySQL password in the `.env` file
2. Or use the quick setup script: `python quick_setup.py`

## 🔧 **Quick Fix Steps:**

### Option 1: Manual Fix
1. Open `.env` file
2. Change this line:
   ```
   DB_PASSWORD=your_password_here
   ```
   To:
   ```
   DB_PASSWORD=your_actual_mysql_password
   ```
3. Run: `python setup_database.py`

### Option 2: Use Quick Setup
```bash
python quick_setup.py
```
This will:
- Ask for your MySQL password
- Test the connection
- Set up the database automatically

### Option 3: Step by Step
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure password (edit .env file)
# Set DB_PASSWORD=your_mysql_password

# 3. Setup database
python setup_database.py

# 4. Run application
python run.py
```

## 🔍 **Common Issues & Solutions:**

### Issue: "Access denied for user 'root'"
**Causes:**
- Wrong password
- MySQL user doesn't exist
- MySQL service not running

**Solutions:**
1. Check MySQL is running
2. Try connecting with MySQL Workbench or command line first
3. Reset MySQL root password if needed

### Issue: "Can't connect to MySQL server"
**Causes:**
- MySQL service not running
- Wrong host (should be localhost)
- Firewall blocking connection

**Solutions:**
1. Start MySQL service:
   - Windows: Services.msc → MySQL → Start
   - XAMPP: Start MySQL from control panel
2. Use `localhost` as host
3. Check firewall settings

### Issue: "Unknown database 'pandeyji_eatery'"
**Solution:**
- Run `python setup_database.py` to create the database

### Issue: "Module not found"
**Solution:**
```bash
pip install -r requirements.txt
```

## 🧪 **Testing Your Setup:**

### Test 1: Check MySQL Connection
```bash
mysql -u root -p
# Enter your password
# If this works, MySQL is running correctly
```

### Test 2: Test Python Dependencies
```bash
python -c "import mysql.connector, fastapi, uvicorn; print('All modules imported successfully!')"
```

### Test 3: Test Database Setup
```bash
python setup_database.py
```

### Test 4: Test Application
```bash
python run.py
# Should start server at http://localhost:8000
```

## 📱 **Verification Steps:**

After setup, verify everything works:

1. **Database Test:**
   ```bash
   python -c "import db_helper; print('Database connection:', 'OK' if db_helper.cnx else 'Failed')"
   ```

2. **API Test:**
   - Start server: `python run.py`
   - Visit: http://localhost:8000
   - Should show: "Pandeyji Eatery API is running"

3. **API Docs Test:**
   - Visit: http://localhost:8000/docs
   - Should show FastAPI documentation

## 🆘 **If Nothing Works:**

### Nuclear Option - Complete Reset:
```bash
# 1. Delete .env file
del .env

# 2. Run interactive setup
python interactive_setup.py

# 3. When prompted for host, ALWAYS enter: localhost
# 4. Enter your actual MySQL password
```

### Check MySQL Installation:
1. **Windows:** Check if MySQL is in Services
2. **XAMPP:** Use XAMPP Control Panel
3. **Standalone:** Check MySQL Workbench

### Alternative: Use Different Database:
If MySQL is too complex, consider SQLite for testing:
- Modify `db_helper.py` to use SQLite instead
- No server setup required

## 📞 **Getting Help:**

If you're still stuck:

1. **Check Logs:** Look at `app.log` for detailed errors
2. **Test MySQL:** Use MySQL Workbench to connect first
3. **Check Versions:** Ensure Python 3.8+ and MySQL 5.7+
4. **Permissions:** Run as Administrator if needed

## 💡 **Pro Tips:**

1. **Always use `localhost`** for local MySQL
2. **Test MySQL connection first** before running the app
3. **Check firewall** if connection fails
4. **Use MySQL Workbench** to verify credentials
5. **Run as Administrator** if you get permission errors
