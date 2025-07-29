"""
Standalone demo version of Pandeyji Eatery
This version works without database for demonstration
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import random
from typing import Dict

# Initialize FastAPI app
app = FastAPI(
    title="Pandeyji Eatery Demo",
    description="Demo version of Pandeyji Eatery chatbot",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo
demo_orders: Dict[str, Dict[str, int]] = {}
order_counter = 100

# Demo menu with prices
MENU = {
    "pav bhaji": 2.50,
    "chole bhature": 3.00,
    "pizza": 8.50,
    "mango lassi": 2.00,
    "masala dosa": 4.00,
    "biryani": 6.50,
    "vada pav": 1.50,
    "samosa": 1.00,
    "idli": 2.50,
    "dhokla": 2.00
}

@app.get("/", response_class=HTMLResponse)
async def web_interface():
    """Serve the demo web interface"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🍽️ Pandeyji Eatery - Food Ordering Demo</title>
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
            height: 85vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .demo-badge {
            background: #ff9800;
            color: white;
            padding: 5px 15px;
            border-radius: 15px;
            font-size: 12px;
            margin-top: 5px;
            display: inline-block;
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
            animation: fadeInUp 0.3s ease;
        }
        
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.user {
            flex-direction: row-reverse;
        }
        
        .message-content {
            max-width: 75%;
            padding: 15px 20px;
            border-radius: 20px;
            font-size: 16px;
            line-height: 1.5;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .message.bot .message-content {
            background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
            color: #1976d2;
            border-bottom-left-radius: 5px;
        }
        
        .message.user .message-content {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            border-bottom-right-radius: 5px;
        }
        
        .message-avatar {
            width: 45px;
            height: 45px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            margin: 0 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }
        
        .message.bot .message-avatar {
            background: linear-gradient(135deg, #ff9800, #f57c00);
        }
        
        .message.user .message-avatar {
            background: linear-gradient(135deg, #2196f3, #1976d2);
        }
        
        .chat-input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #eee;
        }
        
        .chat-input-form {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        
        .chat-input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #ddd;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: all 0.3s;
        }
        
        .chat-input:focus {
            border-color: #4CAF50;
            box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
        }
        
        .send-button {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            border: none;
            padding: 15px 25px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        }
        
        .send-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
        }
        
        .menu-section {
            background: linear-gradient(135deg, #fff3e0, #ffe0b2);
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            border: 1px solid #ffcc02;
        }
        
        .menu-title {
            font-weight: bold;
            color: #e65100;
            margin-bottom: 15px;
            font-size: 18px;
        }
        
        .menu-items {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 12px;
        }
        
        .menu-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px dotted #ddd;
            transition: background 0.2s;
        }
        
        .menu-item:hover {
            background: rgba(255, 152, 0, 0.1);
            border-radius: 8px;
            padding: 8px 10px;
        }
        
        .quick-orders {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }
        
        .quick-order-btn {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
            box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
        }
        
        .quick-order-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
        }
        
        .typing-indicator {
            display: none;
            padding: 15px;
            text-align: center;
            color: #666;
            font-style: italic;
            background: #f0f0f0;
            border-radius: 10px;
            margin: 10px 20px;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
        
        .status-bar {
            background: #e8f5e8;
            color: #2e7d32;
            padding: 10px 20px;
            text-align: center;
            font-size: 14px;
            border-bottom: 1px solid #c8e6c9;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            🍽️ Pandeyji Eatery - Food Ordering System
            <div class="demo-badge">DEMO VERSION</div>
        </div>
        
        <div class="status-bar">
            ✅ Demo Mode Active - No Database Required
        </div>
        
        <div class="chat-messages" id="messages">
            <div class="message bot">
                <div class="message-avatar">🤖</div>
                <div class="message-content">
                    🎉 <strong>Welcome to Pandeyji Eatery!</strong><br><br>
                    I'm your AI food ordering assistant. I can help you:<br>
                    • 📝 <strong>Place orders:</strong> "I want 2 pizza and 1 biryani"<br>
                    • ➕ <strong>Add items:</strong> "Add 1 samosa"<br>
                    • ➖ <strong>Remove items:</strong> "Remove pizza"<br>
                    • ✅ <strong>Complete order:</strong> "That's all"<br>
                    • 📦 <strong>Track orders:</strong> "Track order 123"<br><br>
                    <em>This is a demo version - try placing an order!</em>
                </div>
            </div>
            
            <div class="menu-section">
                <div class="menu-title">📋 Our Delicious Menu</div>
                <div class="menu-items">
                    <div class="menu-item"><span>🥘 Pav Bhaji</span><span><strong>$2.50</strong></span></div>
                    <div class="menu-item"><span>🍛 Chole Bhature</span><span><strong>$3.00</strong></span></div>
                    <div class="menu-item"><span>🍕 Pizza</span><span><strong>$8.50</strong></span></div>
                    <div class="menu-item"><span>🥤 Mango Lassi</span><span><strong>$2.00</strong></span></div>
                    <div class="menu-item"><span>🥞 Masala Dosa</span><span><strong>$4.00</strong></span></div>
                    <div class="menu-item"><span>🍚 Biryani</span><span><strong>$6.50</strong></span></div>
                    <div class="menu-item"><span>🥙 Vada Pav</span><span><strong>$1.50</strong></span></div>
                    <div class="menu-item"><span>🥟 Samosa</span><span><strong>$1.00</strong></span></div>
                    <div class="menu-item"><span>🥘 Idli</span><span><strong>$2.50</strong></span></div>
                    <div class="menu-item"><span>🍰 Dhokla</span><span><strong>$2.00</strong></span></div>
                </div>
                
                <div class="menu-title" style="margin-top: 20px;">🚀 Quick Orders</div>
                <div class="quick-orders">
                    <button class="quick-order-btn" onclick="quickOrder('I want 2 pizza and 1 mango lassi')">🍕 2 Pizza + Lassi</button>
                    <button class="quick-order-btn" onclick="quickOrder('I want 1 biryani and 2 samosa')">🍚 Biryani + Samosa</button>
                    <button class="quick-order-btn" onclick="quickOrder('I want 3 vada pav')">🥙 3 Vada Pav</button>
                    <button class="quick-order-btn" onclick="quickOrder('Track order 101')">📦 Track Order</button>
                </div>
            </div>
        </div>
        
        <div class="typing-indicator" id="typing">
            🤖 Chef is preparing your response...
        </div>
        
        <div class="chat-input-container">
            <form class="chat-input-form" onsubmit="sendMessage(event)">
                <input type="text" class="chat-input" id="messageInput" 
                       placeholder="Type your order here... (e.g., 'I want 2 pizza and 1 biryani')" required>
                <button type="submit" class="send-button">Send 🚀</button>
            </form>
        </div>
    </div>

    <script>
        let currentOrder = {};
        let sessionId = 'demo-session-' + Math.random().toString(36).substr(2, 9);
        
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
            document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
        }
        
        function hideTyping() {
            document.getElementById('typing').style.display = 'none';
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
            
            // Simulate processing delay
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            // Process message with demo logic
            const response = processMessage(message);
            addMessage(response);
            
            hideTyping();
        }
        
        function processMessage(message) {
            const lowerMsg = message.toLowerCase();
            
            // Track order
            if (lowerMsg.includes('track') && lowerMsg.includes('order')) {
                const orderNum = Math.floor(Math.random() * 200) + 100;
                const statuses = ['in progress', 'preparing', 'ready for pickup', 'delivered'];
                const status = statuses[Math.floor(Math.random() * statuses.length)];
                return `📦 Order #${orderNum} status: <strong>${status}</strong><br>Expected delivery: 25-30 minutes`;
            }
            
            // Complete order
            if (lowerMsg.includes('complete') || lowerMsg.includes("that's all") || lowerMsg.includes('place order')) {
                if (Object.keys(currentOrder).length === 0) {
                    return "🤔 You don't have any items in your order yet. Would you like to add something?";
                }
                
                const orderNum = Math.floor(Math.random() * 1000) + 100;
                const total = calculateTotal(currentOrder);
                const orderStr = formatOrder(currentOrder);
                
                currentOrder = {}; // Clear order
                
                return `🎉 <strong>Order Placed Successfully!</strong><br><br>
                        📋 <strong>Order #${orderNum}</strong><br>
                        ${orderStr}<br>
                        💰 <strong>Total: $${total.toFixed(2)}</strong><br><br>
                        🕐 Estimated delivery: 25-30 minutes<br>
                        💳 Pay on delivery`;
            }
            
            // Remove items
            if (lowerMsg.includes('remove')) {
                const items = extractFoodItems(message);
                if (items.length === 0) {
                    return "🤔 Which item would you like to remove from your order?";
                }
                
                let removed = [];
                let notFound = [];
                
                items.forEach(item => {
                    if (currentOrder[item]) {
                        removed.push(item);
                        delete currentOrder[item];
                    } else {
                        notFound.push(item);
                    }
                });
                
                let response = "";
                if (removed.length > 0) {
                    response += `✅ Removed: ${removed.join(', ')}<br>`;
                }
                if (notFound.length > 0) {
                    response += `❌ Not in order: ${notFound.join(', ')}<br>`;
                }
                
                if (Object.keys(currentOrder).length === 0) {
                    response += "🛒 Your order is now empty.";
                } else {
                    response += `<br>🛒 Current order: ${formatOrder(currentOrder)}`;
                }
                
                return response;
            }
            
            // Add items (default)
            const items = extractFoodItems(message);
            const quantities = extractQuantities(message);
            
            if (items.length === 0) {
                return `🤔 I didn't catch which food items you'd like. Try saying something like:<br>
                        • "I want 2 pizza and 1 biryani"<br>
                        • "Add 3 samosa to my order"<br>
                        • "I'd like some vada pav"`;
            }
            
            // Add items to order
            for (let i = 0; i < items.length; i++) {
                const item = items[i];
                const qty = quantities[i] || 1;
                currentOrder[item] = (currentOrder[item] || 0) + qty;
            }
            
            const orderStr = formatOrder(currentOrder);
            return `✅ <strong>Added to your order!</strong><br><br>
                    🛒 Current order: ${orderStr}<br><br>
                    Would you like to add anything else or shall I place this order?`;
        }
        
        function extractFoodItems(message) {
            const items = [];
            const menuItems = Object.keys({
                'pav bhaji': 1, 'chole bhature': 1, 'pizza': 1, 'mango lassi': 1, 
                'masala dosa': 1, 'biryani': 1, 'vada pav': 1, 'samosa': 1, 'idli': 1, 'dhokla': 1
            });
            
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
        
        function formatOrder(order) {
            return Object.entries(order)
                .map(([item, qty]) => `${qty} ${item}`)
                .join(', ');
        }
        
        function calculateTotal(order) {
            const prices = {
                'pav bhaji': 2.50, 'chole bhature': 3.00, 'pizza': 8.50, 'mango lassi': 2.00,
                'masala dosa': 4.00, 'biryani': 6.50, 'vada pav': 1.50, 'samosa': 1.00,
                'idli': 2.50, 'dhokla': 2.00
            };
            
            return Object.entries(order).reduce((total, [item, qty]) => {
                return total + (prices[item] || 0) * qty;
            }, 0);
        }
        
        function quickOrder(orderText) {
            document.getElementById('messageInput').value = orderText;
        }
        
        // Welcome sequence
        setTimeout(() => {
            addMessage("👋 Try one of the quick order buttons below, or type your own order!");
        }, 2000);
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html_content)

@app.post("/webhook")
async def demo_webhook(request: Request):
    """Demo webhook endpoint"""
    try:
        payload = await request.json()
        
        # Simple demo response
        return JSONResponse(content={
            "fulfillmentText": "This is a demo response from Pandeyji Eatery! 🍽️"
        })
    except Exception as e:
        return JSONResponse(content={
            "fulfillmentText": "Demo mode active - API is working! 🚀"
        })

@app.get("/api")
async def api_info():
    """API information"""
    return {
        "name": "Pandeyji Eatery Demo",
        "version": "1.0.0",
        "status": "running",
        "mode": "demo",
        "features": [
            "Interactive web interface",
            "Order management",
            "Menu display",
            "Demo responses"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("🍽️ Starting Pandeyji Eatery Demo...")
    print("🌐 Open your browser and go to: http://localhost:8000")
    print("📖 API docs available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
