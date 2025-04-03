from src.agents import BaseAgent
from src.shop.catalog import Catalog
from src.shop.session import SessionStorage


class AtomicAgent(BaseAgent):
    def __init__(self, catalog: Catalog, session_storage: SessionStorage):
        pass
    async def chat(self, session_id: str, message: str) -> str:
        pass