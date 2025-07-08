import heapq
import uuid
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

@dataclass
class Order:
    """Order data structure"""
    order_id: str
    side: str  # 'buy' or 'sell'
    price: float
    quantity: float
    trader_id: str
    timestamp: datetime
    
    def __post_init__(self):
        if self.side not in ['buy', 'sell']:
            raise ValueError("Side must be 'buy' or 'sell'")
        if self.price <= 0:
            raise ValueError("Price must be positive")
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")

@dataclass
class Trade:
    """Trade data structure"""
    trade_id: str
    buyer_id: str
    seller_id: str
    price: float
    quantity: float
    timestamp: datetime
    buy_order_id: str
    sell_order_id: str

class OrderBook:
    """
    Order Book implementation with price-time priority
    """
    
    def __init__(self):
        # Buy orders: max heap (negative prices for max heap behavior)
        self.buy_orders: List[Tuple[float, datetime, Order]] = []
        # Sell orders: min heap
        self.sell_orders: List[Tuple[float, datetime, Order]] = []
        
        # Order tracking
        self.orders: Dict[str, Order] = {}
        self.trades: List[Trade] = []
        
        # Market statistics
        self.last_price: Optional[float] = None
        self.volume_24h: float = 0.0
        self.high_24h: Optional[float] = None
        self.low_24h: Optional[float] = None
        
    def add_order(self, side: str, price: float, quantity: float, trader_id: str) -> str:
        """
        Add a new order to the book
        
        Args:
            side: 'buy' or 'sell'
            price: Order price
            quantity: Order quantity
            trader_id: Trader identifier
            
        Returns:
            Order ID
        """
        order_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        order = Order(
            order_id=order_id,
            side=side,
            price=price,
            quantity=quantity,
            trader_id=trader_id,
            timestamp=timestamp
        )
        
        self.orders[order_id] = order
        
        if side == 'buy':
            # For buy orders, use negative price for max heap
            heapq.heappush(self.buy_orders, (-price, timestamp, order))
        else:
            # For sell orders, use positive price for min heap
            heapq.heappush(self.sell_orders, (price, timestamp, order))
        
        # Try to match orders
        self._match_orders()
        
        return order_id
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an existing order
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            True if successful, False if order not found
        """
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        
        # Mark order as cancelled (quantity = 0)
        order.quantity = 0
        
        return True
    
    def _match_orders(self):
        """
        Match buy and sell orders
        """
        while self.buy_orders and self.sell_orders:
            # Peek at best orders
            best_buy = self.buy_orders[0]
            best_sell = self.sell_orders[0]
            
            buy_price = -best_buy[0]  # Convert back from negative
            sell_price = best_sell[0]
            
            buy_order = best_buy[2]
            sell_order = best_sell[2]
            
            # Skip cancelled orders
            if buy_order.quantity == 0:
                heapq.heappop(self.buy_orders)
                continue
            if sell_order.quantity == 0:
                heapq.heappop(self.sell_orders)
                continue
            
            # Check if orders can be matched
            if buy_price >= sell_price:
                # Execute trade
                trade_price = sell_price  # Price improvement for buyer
                trade_quantity = min(buy_order.quantity, sell_order.quantity)
                
                # Create trade record
                trade = Trade(
                    trade_id=str(uuid.uuid4()),
                    buyer_id=buy_order.trader_id,
                    seller_id=sell_order.trader_id,
                    price=trade_price,
                    quantity=trade_quantity,
                    timestamp=datetime.now(),
                    buy_order_id=buy_order.order_id,
                    sell_order_id=sell_order.order_id
                )
                
                self.trades.append(trade)
                
                # Update market statistics
                self.last_price = trade_price
                self.volume_24h += trade_quantity
                
                if self.high_24h is None or trade_price > self.high_24h:
                    self.high_24h = trade_price
                if self.low_24h is None or trade_price < self.low_24h:
                    self.low_24h = trade_price
                
                # Update order quantities
                buy_order.quantity -= trade_quantity
                sell_order.quantity -= trade_quantity
                
                # Remove fully filled orders
                if buy_order.quantity == 0:
                    heapq.heappop(self.buy_orders)
                if sell_order.quantity == 0:
                    heapq.heappop(self.sell_orders)
                
            else:
                # No more matches possible
                break
    
    def get_order_book(self, depth: int = 20) -> Tuple[List[Dict], List[Dict]]:
        """
        Get current order book state
        
        Args:
            depth: Number of price levels to return
            
        Returns:
            Tuple of (bids, asks) lists
        """
        # Clean up cancelled orders and get active orders
        active_buys = []
        active_sells = []
        
        # Process buy orders
        temp_buys = []
        while self.buy_orders:
            order_data = heapq.heappop(self.buy_orders)
            if order_data[2].quantity > 0:
                temp_buys.append(order_data)
        
        # Restore buy orders
        for order_data in temp_buys:
            heapq.heappush(self.buy_orders, order_data)
            active_buys.append(order_data)
        
        # Process sell orders
        temp_sells = []
        while self.sell_orders:
            order_data = heapq.heappop(self.sell_orders)
            if order_data[2].quantity > 0:
                temp_sells.append(order_data)
        
        # Restore sell orders
        for order_data in temp_sells:
            heapq.heappush(self.sell_orders, order_data)
            active_sells.append(order_data)
        
        # Group by price level
        bids = self._group_by_price(active_buys, 'buy')[:depth]
        asks = self._group_by_price(active_sells, 'sell')[:depth]
        
        return bids, asks
    
    def _group_by_price(self, orders: List[Tuple], side: str) -> List[Dict]:
        """
        Group orders by price level
        """
        price_levels = {}
        
        for order_data in orders:
            if side == 'buy':
                price = -order_data[0]  # Convert back from negative
            else:
                price = order_data[0]
            
            order = order_data[2]
            
            if price not in price_levels:
                price_levels[price] = {
                    'price': price,
                    'quantity': 0,
                    'orders': 0
                }
            
            price_levels[price]['quantity'] += order.quantity
            price_levels[price]['orders'] += 1
        
        # Sort by price
        if side == 'buy':
            # Bids: highest price first
            sorted_levels = sorted(price_levels.values(), key=lambda x: x['price'], reverse=True)
        else:
            # Asks: lowest price first
            sorted_levels = sorted(price_levels.values(), key=lambda x: x['price'])
        
        return sorted_levels
    
    def get_recent_trades(self, limit: int = 50) -> List[Dict]:
        """
        Get recent trades
        
        Args:
            limit: Maximum number of trades to return
            
        Returns:
            List of trade dictionaries
        """
        recent_trades = self.trades[-limit:] if len(self.trades) > limit else self.trades
        return [asdict(trade) for trade in reversed(recent_trades)]
    
    def get_market_stats(self) -> Dict:
        """
        Get market statistics
        
        Returns:
            Dictionary with market statistics
        """
        return {
            'last_price': self.last_price,
            'volume_24h': self.volume_24h,
            'high_24h': self.high_24h,
            'low_24h': self.low_24h,
            'total_trades': len(self.trades),
            'active_orders': len([o for o in self.orders.values() if o.quantity > 0])
        }