# 🚀 Quick Start Guide for Pandeyji Eatery

## Step 1: Configure Database Password

1. Open the `.env` file in your project directory
2. Replace `your_password_here` with your actual MySQL password:
   ```
   DB_PASSWORD=your_actual_mysql_password
   ```

## Step 2: Set up Database

Run the database setup script:
```bash
python setup_database.py
```

If you get an "Access denied" error:
- Make sure MySQL is running
- Verify your password in the `.env` file
- Try connecting to MySQL manually to confirm credentials

## Step 3: Start the Application

```bash
python run.py
```

The server will start at: http://localhost:8000

## Step 4: Test the API

Visit these URLs in your browser:
- **Health Check**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs
- **Detailed Health**: http://localhost:8000/health

## Step 5: Test with Dialogflow

Configure your Dialogflow webhook to point to:
```
http://your-server-address:8000/
```

## Common Issues

### Database Connection Error
- Check if MySQL is running
- Verify credentials in `.env` file
- Ensure you have permission to create databases

### Module Not Found Error
- Install dependencies: `pip install -r requirements.txt`

### Port Already in Use
- Change SERVER_PORT in `.env` file
- Or kill the process using port 8000

## Need Help?

Check the detailed README.md file for comprehensive documentation.
