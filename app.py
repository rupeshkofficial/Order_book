from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import threading
import time
import random
from datetime import datetime
from order_book import OrderBook

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global order book instance
order_book = OrderBook()

# Sample trading pairs
TRADING_PAIRS = ['BTC/USD', 'ETH/USD', 'ADA/USD', 'DOT/USD']
current_pair = 'BTC/USD'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/orderbook/<pair>')
def get_orderbook(pair):
    """Get current order book state"""
    global current_pair
    current_pair = pair
    
    bids, asks = order_book.get_order_book()
    return jsonify({
        'bids': bids,
        'asks': asks,
        'pair': pair,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/add_order', methods=['POST'])
def add_order():
    """Add a new order to the book"""
    data = request.json
    
    try:
        order_id = order_book.add_order(
            side=data['side'],
            price=float(data['price']),
            quantity=float(data['quantity']),
            trader_id=data.get('trader_id', 'anonymous')
        )
        
        # Emit update to all connected clients
        bids, asks = order_book.get_order_book()
        socketio.emit('orderbook_update', {
            'bids': bids,
            'asks': asks,
            'pair': current_pair,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({'success': True, 'order_id': order_id})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/cancel_order', methods=['POST'])
def cancel_order():
    """Cancel an existing order"""
    data = request.json
    
    try:
        success = order_book.cancel_order(data['order_id'])
        
        if success:
            # Emit update to all connected clients
            bids, asks = order_book.get_order_book()
            socketio.emit('orderbook_update', {
                'bids': bids,
                'asks': asks,
                'pair': current_pair,
                'timestamp': datetime.now().isoformat()
            })
            
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/trades')
def get_trades():
    """Get recent trades"""
    trades = order_book.get_recent_trades()
    return jsonify(trades)

@app.route('/api/market_data')
def get_market_data():
    """Get market statistics"""
    stats = order_book.get_market_stats()
    return jsonify(stats)

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    # Send current order book state
    bids, asks = order_book.get_order_book()
    emit('orderbook_update', {
        'bids': bids,
        'asks': asks,
        'pair': current_pair,
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

def simulate_market_activity():
    """Simulate random market orders for demonstration"""
    while True:
        time.sleep(random.uniform(2, 8))  # Random interval between 2-8 seconds
        
        # Generate random order
        side = random.choice(['buy', 'sell'])
        base_price = 45000 if current_pair == 'BTC/USD' else 3000
        price = base_price + random.uniform(-1000, 1000)
        quantity = random.uniform(0.1, 2.0)
        
        try:
            order_book.add_order(
                side=side,
                price=round(price, 2),
                quantity=round(quantity, 4),
                trader_id='market_maker'
            )
            
            # Emit update
            bids, asks = order_book.get_order_book()
            socketio.emit('orderbook_update', {
                'bids': bids,
                'asks': asks,
                'pair': current_pair,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Error in market simulation: {e}")

# Start market simulation in background thread
market_thread = threading.Thread(target=simulate_market_activity, daemon=True)
market_thread.start()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    socketio.run(app, debug=True, host='0.0.0.0', port=port)