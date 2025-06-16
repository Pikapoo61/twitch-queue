from flask import Flask, render_template, request, jsonify
from collections import deque
import threading
import time
import re

app = Flask(__name__)

# In-memory queue to store all incoming orders
order_queue = deque()
# Lock for thread-safe access to the queue
queue_lock = threading.Lock()

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.is_json:
        data = request.get_json()

        # All orders are now processed, so we just get the line items
        # and no longer filter for "live stream".
        line_items = data.get('line_items') or []

        # Safely get the order number
        raw_order_id = data.get('order_number')
        if not raw_order_id:
            raw_order_id = f"{str(int(time.time()))[-5:]}"
        order_id = str(raw_order_id).lstrip('#')

        # Try to get customer name from note attributes (e.g., "Tiktok/Twitch account")
        customer_name = ''
        note_attributes = data.get('note_attributes', [])
        for attr in note_attributes:
            if attr.get('name', '').lower() == 'tiktok/twitch account':
                customer_name = attr.get('value', '').strip()
                break

        # If not found, try the shipping address company name
        if not customer_name:
            shipping_address = data.get('shipping_address') or {}
            customer_name = (shipping_address.get('company') or '').strip()

        # If not found in note attributes, try the general order note
        if not customer_name:
            customer_name = (data.get('note') or '').strip()

        # If still no name, fall back to the customer's first name
        if not customer_name:
            customer_data = data.get('customer') or {}
            customer_name = customer_data.get('first_name', '').strip()
        
        # Final fallback if no name is available at all.
        if not customer_name:
            customer_name = 'Someone'
        
        products = []
        for item in line_items:
            product_name = item.get('name') or 'Unknown Product'
            # Clean the product name for display
            # First, remove "live stream" case-insensitively
            display_name = re.sub(r'live stream', '', product_name, flags=re.IGNORECASE)
            # Then, remove any trailing stuff like " - " or "(test product)" if it's there
            display_name = re.sub(r'\s*\(test product\)', '', display_name, flags=re.IGNORECASE)
            display_name = re.sub(r'\s*-\s*$', '', display_name).strip()
            products.append(f"{item.get('quantity')}x {display_name}")

        with queue_lock:
            # Add the new order to the queue
            order_data = {
                "id": order_id,
                "customer_name": customer_name,
                "products": products,
            }
            order_queue.append(order_data)
            
        print(f"Order added to queue: #{order_id}. Queue size: {len(order_queue)}")
        
        return jsonify({"status": "success", "message": "Order received"}), 200
    return jsonify({"status": "error", "message": "Invalid request"}), 400

@app.route('/overlay')
def overlay():
    return render_template('overlay.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/orders', methods=['GET'])
def get_orders():
    with queue_lock:
        return jsonify(list(order_queue))

@app.route('/api/delete-order/<order_id>', methods=['DELETE'])
def delete_order(order_id):
    global order_queue
    with queue_lock:
        initial_length = len(order_queue)
        order_queue = deque([order for order in order_queue if order['id'] != order_id])
        if len(order_queue) < initial_length:
            print(f"Order #{order_id} deleted by admin. Queue size: {len(order_queue)}")
            return jsonify({"status": "success", "message": f"Order #{order_id} deleted."}), 200
        else:
            return jsonify({"status": "error", "message": "Order not found."}), 404

@app.route('/api/next-order', methods=['POST'])
def next_order():
    with queue_lock:
        if order_queue:
            order_queue.popleft()
    # Return the new list of orders
    return get_orders()

if __name__ == '__main__':
    app.run(debug=True) 