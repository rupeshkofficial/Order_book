# Interactive Order Book

A real-time, web-based order book implementation built with Python Flask and Socket.IO. This project demonstrates a complete trading order book system with live price matching, order management, and market statistics.

## 🚀 Features

- **Real-time Order Book**: Live bid/ask updates with WebSocket connections
- **Order Management**: Place, match, and cancel orders with price-time priority
- **Market Statistics**: Track volume, high/low prices, and trade history
- **Interactive UI**: Modern, responsive web interface with real-time updates
- **Multiple Trading Pairs**: Support for BTC/USD, ETH/USD, ADA/USD, DOT/USD
- **Trade History**: View recent trades with detailed information
- **Market Simulation**: Automatic market maker for demonstration purposes

## 🛠️ Technology Stack

- **Backend**: Python Flask, Flask-SocketIO
- **Frontend**: HTML5, CSS3, JavaScript, Socket.IO
- **Data Structures**: Heap-based order book for efficient price matching
- **Real-time Communication**: WebSocket for live updates

## 📁 Project Structure

```
order-book/
├── app.py                 # Main Flask application
├── order_book.py          # Core order book logic
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface
└── README.md             # This file
```

## 🔧 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/interactive-order-book.git
   cd interactive-order-book
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open your browser**:
   Navigate to `http://localhost:5000`

## 🎯 How to Use

### Placing Orders
1. Select a trading pair (BTC/USD, ETH/USD, etc.)
2. Choose order side (Buy/Sell)
3. Enter price and quantity
4. Optionally specify trader ID
5. Click Buy or Sell button

### Viewing Order Book
- **Red rows**: Sell orders (asks) - sorted by lowest price first
- **Green rows**: Buy orders (bids) - sorted by highest price first
- **Spread**: Difference between best bid and best ask
- **Click on any row**: Auto-fill order form with that price/quantity

### Market Statistics
- **Last Price**: Most recent trade price
- **24h Volume**: Total trading volume
- **24h High/Low**: Price range for the day
- **Total Trades**: Number of completed trades
- **Active Orders**: Current orders in the book

## 🏗️ Architecture

### Core Components

1. **Order Class**: Represents individual orders with validation
2. **Trade Class**: Records completed trades
3. **OrderBook Class**: Manages order matching and book state
4. **Flask App**: Handles HTTP requests and WebSocket connections

### Order Matching Algorithm

- **Price-Time Priority**: Orders matched by best price first, then by time
- **Buy Orders**: Stored in max-heap (highest price first)
- **Sell Orders**: Stored in min-heap (lowest price first)
- **Automatic Matching**: Orders matched immediately when price conditions are met

### Data Flow

1. User places order via web interface
2. Order sent to Flask backend via API
3. Order added to appropriate heap in OrderBook
4. Matching engine attempts to match orders
5. Updates broadcast to all connected clients via WebSocket
6. UI updates in real-time

## 🔀 API Endpoints

- `GET /`: Main web interface
- `GET /api/orderbook/<pair>`: Get current order book state
- `POST /api/add_order`: Add new order
- `POST /api/cancel_order`: Cancel existing order
- `GET /api/trades`: Get recent trades
- `GET /api/market_data`: Get market statistics

## 🌐 WebSocket Events

- `connect`: Client connected to server
- `disconnect`: Client disconnected from server
- `orderbook_update`: Real-time order book updates

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production with Gunicorn
```bash
gunicorn --worker-class eventlet -w 1 app:app
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "app:app"]
```

## 📊 Features Explained

### Real-time Updates
- WebSocket connection maintains live data feed
- Order book updates instantly when orders are placed/matched
- Connection status indicator shows server connectivity

### Market Simulation
- Background thread generates random market orders
- Demonstrates order matching in action
- Configurable frequency and price ranges

### Order Book Depth
- Configurable depth (default: 20 levels)
- Aggregates orders by price level
- Shows total quantity and number of orders per level

### Trade History
- Records all completed trades
- Shows buyer/seller information
- Timestamp and trade details

## 🔒 Security Considerations

- Input validation on all order parameters
- Rate limiting can be added for production use
- CORS configuration for cross-origin requests
- Error handling for invalid operations

## 🎨 Customization

### Styling
- Modern gradient design with glassmorphism effects
- Responsive layout for mobile devices
- Customizable color scheme in CSS

### Trading Pairs
- Easily add new trading pairs in `TRADING_PAIRS` list
- Separate order books can be maintained per pair
- Base prices configurable in market simulation

### Order Types
- Currently supports market and limit orders
- Can be extended for stop-loss, take-profit orders
- Time-in-force options can be added

## 📈 Performance

- Heap-based order book: O(log n) insertion/deletion
- Efficient price-time matching algorithm
- WebSocket for minimal latency updates
- Optimized for high-frequency trading simulation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📝 License

This project is open source and available under the MIT License.

## 🔮 Future Enhancements

- [ ] Order book visualization charts
- [ ] Advanced order types (stop-loss, iceberg)
- [ ] User authentication and portfolios
- [ ] Historical data and analytics
- [ ] REST API for algorithmic trading
- [ ] Database persistence
- [ ] Load testing and performance optimization
- [ ] Mobile app version

## 💡 Learning Outcomes

This project demonstrates:
- Data structures and algorithms (heaps, priority queues)
- Real-time web applications with WebSockets
- Financial market concepts and order matching
- Modern web development practices
- API design and implementation

Perfect for learning about trading systems, real-time applications, and full-stack development!

---
