"""
Simple web interface for testing the Pandeyji Eatery chatbot
This creates a basic HTML interface to interact with the chatbot
"""

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import logging
import os
from pathlib import Path

# Create templates directory if it doesn't exist
templates_dir = Path("templates")
templates_dir.mkdir(exist_ok=True)

# Create static directory if it doesn't exist
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# Create the HTML template
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🍽️ Pandeyji Eatery - Food Ordering Chatbot</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .chat-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            width: 90%;
            max-width: 800px;
            height: 80vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: #4CAF50;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
        }
        
        .message.user {
            flex-direction: row-reverse;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 18px;
            border-radius: 18px;
            font-size: 16px;
            line-height: 1.4;
        }
        
        .message.bot .message-content {
            background: #e3f2fd;
            color: #1976d2;
        }
        
        .message.user .message-content {
            background: #4CAF50;
            color: white;
        }
        
        .message-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            margin: 0 10px;
        }
        
        .message.bot .message-avatar {
            background: #ff9800;
        }
        
        .message.user .message-avatar {
            background: #2196f3;
        }
        
        .chat-input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #eee;
        }
        
        .chat-input-form {
            display: flex;
            gap: 10px;
        }
        
        .chat-input {
            flex: 1;
            padding: 12px 18px;
            border: 2px solid #ddd;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .chat-input:focus {
            border-color: #4CAF50;
        }
        
        .send-button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }
        
        .send-button:hover {
            background: #45a049;
        }
        
        .status-indicator {
            text-align: center;
            padding: 10px;
            background: #e8f5e8;
            color: #2e7d32;
            font-size: 14px;
        }
        
        .error-indicator {
            background: #ffebee;
            color: #c62828;
        }
        
        .menu-section {
            background: #fff3e0;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        }
        
        .menu-title {
            font-weight: bold;
            color: #e65100;
            margin-bottom: 10px;
        }
        
        .menu-items {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }
        
        .menu-item {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px dotted #ddd;
        }
        
        .typing-indicator {
            display: none;
            padding: 10px;
            text-align: center;
            color: #666;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            🍽️ Pandeyji Eatery - Order Your Favorite Food!
        </div>
        
        <div class="status-indicator" id="status">
            ✅ Connected to Pandeyji Eatery API
        </div>
        
        <div class="chat-messages" id="messages">
            <div class="message bot">
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    Welcome to Pandeyji Eatery! 🍽️<br><br>
                    I'm your food ordering assistant. Here's what I can help you with:<br>
                    • 📝 <strong>Place an order:</strong> "I want 2 pizza and 1 biryani"<br>
                    • ➕ <strong>Add items:</strong> "Add 1 samosa to my order"<br>
                    • ➖ <strong>Remove items:</strong> "Remove pizza from my order"<br>
                    • ✅ <strong>Complete order:</strong> "That's all" or "Place my order"<br>
                    • 📦 <strong>Track order:</strong> "Track order 123"<br><br>
                    What would you like to order today?
                </div>
            </div>
            
            <div class="menu-section">
                <div class="menu-title">📋 Our Menu</div>
                <div class="menu-items">
                    <div class="menu-item"><span>🥘 Pav Bhaji</span><span>$2.50</span></div>
                    <div class="menu-item"><span>🍛 Chole Bhature</span><span>$3.00</span></div>
                    <div class="menu-item"><span>🍕 Pizza</span><span>$8.50</span></div>
                    <div class="menu-item"><span>🥤 Mango Lassi</span><span>$2.00</span></div>
                    <div class="menu-item"><span>🥞 Masala Dosa</span><span>$4.00</span></div>
                    <div class="menu-item"><span>🍚 Biryani</span><span>$6.50</span></div>
                    <div class="menu-item"><span>🥙 Vada Pav</span><span>$1.50</span></div>
                    <div class="menu-item"><span>🥟 Samosa</span><span>$1.00</span></div>
                    <div class="menu-item"><span>🥘 Idli</span><span>$2.50</span></div>
                    <div class="menu-item"><span>🍰 Dhokla</span><span>$2.00</span></div>
                </div>
            </div>
        </div>
        
        <div class="typing-indicator" id="typing">
            🤖 Bot is typing...
        </div>
        
        <div class="chat-input-container">
            <form class="chat-input-form" onsubmit="sendMessage(event)">
                <input type="text" class="chat-input" id="messageInput" placeholder="Type your order here... (e.g., 'I want 2 pizza and 1 biryani')" required>
                <button type="submit" class="send-button">Send 📤</button>
            </form>
        </div>
    </div>

    <script>
        function addMessage(content, isUser = false) {
            const messagesContainer = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
            
            messageDiv.innerHTML = `
                <div class="message-avatar">${isUser ? '👤' : '🤖'}</div>
                <div class="message-content">${content}</div>
            `;
            
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        function showTyping() {
            document.getElementById('typing').style.display = 'block';
        }
        
        function hideTyping() {
            document.getElementById('typing').style.display = 'none';
        }
        
        function updateStatus(message, isError = false) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = `status-indicator ${isError ? 'error-indicator' : ''}`;
        }
        
        async function sendMessage(event) {
            event.preventDefault();
            
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message
            addMessage(message, true);
            input.value = '';
            
            // Show typing indicator
            showTyping();
            
            try {
                // Simulate Dialogflow request format
                const payload = {
                    queryResult: {
                        intent: {
                            displayName: "order.add - context: ongoing-order"
                        },
                        parameters: {
                            "food-item": extractFoodItems(message),
                            "number": extractQuantities(message)
                        },
                        outputContexts: [{
                            name: "projects/test/agent/sessions/test-session/contexts/ongoing-order"
                        }]
                    }
                };
                
                // Send to webhook
                const response = await fetch('/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
                
                if (response.ok) {
                    const data = await response.json();
                    addMessage(data.fulfillmentText || "Sorry, I didn't understand that.");
                    updateStatus("✅ Connected to Pandeyji Eatery API");
                } else {
                    throw new Error(`HTTP ${response.status}`);
                }
                
            } catch (error) {
                console.error('Error:', error);
                addMessage("Sorry, I'm having trouble connecting to the server. Please make sure the API is running.", false);
                updateStatus("❌ Connection error - Check if server is running", true);
            }
            
            hideTyping();
        }
        
        function extractFoodItems(message) {
            const items = [];
            const menuItems = ['pav bhaji', 'chole bhature', 'pizza', 'mango lassi', 'masala dosa', 'biryani', 'vada pav', 'samosa', 'idli', 'dhokla'];
            
            menuItems.forEach(item => {
                if (message.toLowerCase().includes(item)) {
                    items.push(item);
                }
            });
            
            return items;
        }
        
        function extractQuantities(message) {
            const numbers = message.match(/\d+/g);
            return numbers ? numbers.map(Number) : [1];
        }
        
        // Quick order buttons
        function addQuickOrders() {
            const container = document.getElementById('messages');
            const quickOrderDiv = document.createElement('div');
            quickOrderDiv.innerHTML = `
                <div class="menu-section">
                    <div class="menu-title">🚀 Quick Orders</div>
                    <button onclick="quickOrder('I want 2 pizza and 1 mango lassi')" style="margin: 5px; padding: 10px; border: none; background: #4CAF50; color: white; border-radius: 15px; cursor: pointer;">2 Pizza + 1 Mango Lassi</button>
                    <button onclick="quickOrder('I want 1 biryani and 2 samosa')" style="margin: 5px; padding: 10px; border: none; background: #4CAF50; color: white; border-radius: 15px; cursor: pointer;">1 Biryani + 2 Samosa</button>
                    <button onclick="quickOrder('I want 3 vada pav')" style="margin: 5px; padding: 10px; border: none; background: #4CAF50; color: white; border-radius: 15px; cursor: pointer;">3 Vada Pav</button>
                </div>
            `;
            container.appendChild(quickOrderDiv);
        }
        
        function quickOrder(orderText) {
            document.getElementById('messageInput').value = orderText;
        }
        
        // Add quick orders after page loads
        window.onload = function() {
            setTimeout(addQuickOrders, 1000);
        };
    </script>
</body>
</html>
"""

# Write the HTML template
with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("✅ Web interface template created!")
print("📁 Created: templates/index.html")
print("📁 Created: static/ directory")
