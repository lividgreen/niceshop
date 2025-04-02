import uuid

from src.shop.entities import ShoppingCart, ItemQuantity


class ShopSession:
    def __init__(self, session_id):
        self.id = session_id
        self._shopping_cart = ShoppingCart()

    def get_shopping_cart(self):
        return self._shopping_cart

    def set_item_quantity(self, item_quantity: ItemQuantity):
        self._shopping_cart.items[item_quantity.item_code] = item_quantity.quantity
        if self._shopping_cart.items[item_quantity.item_code] == 0:
            del self._shopping_cart.items[item_quantity.item_code]

class SessionStorage:
    def __init__(self):
        self.sessions: dict[str, ShopSession] = {}

    def create_session(self) -> str:
        session_id = uuid.uuid4().hex
        session = ShopSession(session_id)
        self.sessions[session_id] = session
        return session_id

    def get_session(self, session_id):
        return self.sessions[session_id]