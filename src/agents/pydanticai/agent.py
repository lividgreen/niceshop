from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage

from src.agents import BaseAgent
from src.shop.catalog import Catalog
from src.shop.entities import ItemQuantity, ShoppingCart, CatalogResult, CatalogFetchParams, CatalogSearchParams
from src.shop.session import SessionStorage

@dataclass
class Session:
    session_id: str

class HistoryStorage:
    def __init__(self):
        self.histories: dict[str, list[ModelMessage]] = {}
    def get(self, session_id) -> list[ModelMessage]:
        if session_id not in self.histories:
            self.histories[session_id] = []
        return self.histories[session_id]
    def add_new(self, session_id, messages: list[ModelMessage]):
        self.histories[session_id].extend(messages)

class PydanticAIAgent(BaseAgent):
    def __init__(self, catalog: Catalog, session_storage: SessionStorage):
        self.history_storage = HistoryStorage()

        shopping_assistant = Agent(
            model='openai:gpt-4o-mini',
            system_prompt=self.INSTRUCTIONS,
            deps_type=Session
        )
        self.shopping_assistant = shopping_assistant

        @shopping_assistant.tool_plain
        async def catalog_search(
                params: CatalogSearchParams
        ) -> CatalogResult:
            """Search for items in the catalog by textual query"""
            return catalog.search(params)

        @shopping_assistant.tool_plain
        async def catalog_fetch(
                params: CatalogFetchParams
        ) -> CatalogResult:
            """Fetch items from the catalog"""
            return catalog.fetch(params)

        @shopping_assistant.tool
        async def list_shopping_cart(ctx: RunContext[Session]) -> ShoppingCart:
            """List contents of the shopping cart"""
            session_id = ctx.deps.session_id
            session = session_storage.get_session(session_id)
            return session.get_shopping_cart()

        @shopping_assistant.tool
        async def set_item_quantity(ctx: RunContext[Session], ic: ItemQuantity, ) -> None:
            """Set quantity of specified item in the shopping cart"""
            session_id = ctx.deps.session_id
            session = session_storage.get_session(session_id)
            session.set_item_quantity(ic)

    async def chat(self, session_id: str, message: str) -> str:
        history = self.history_storage.get(session_id)
        response = await self.shopping_assistant.run(
            message,
            deps=Session(session_id=session_id),
            message_history=history
        )
        self.history_storage.add_new(session_id, response.new_messages())
        return response.data