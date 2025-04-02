from llama_index.core.tools import FunctionTool, AsyncBaseTool
from llama_index.llms.openai import OpenAI
from llama_index.core.workflow import Context

from src.agents import BaseAgent
from src.agents.llamaindex.workflow import ShoppingAssistantWorkflow
from src.shop.catalog import Catalog
from src.shop.session import SessionStorage
from src.shop.entities import CatalogSearchParams, CatalogFetchParams, ItemQuantity, CatalogResult, ShoppingCart


def _get_tools(catalog: Catalog, session_storage: SessionStorage) -> list[AsyncBaseTool]:
    """Create LlamaIndex function tools for the agent, utilizing Pydantic models for type definitions"""

    async def catalog_search(
            query: str,
            max_results: int = 5
    ) -> CatalogResult:
        """Search for items in the catalog by textual query"""
        return catalog.search(CatalogSearchParams(query=query, max_results=max_results))

    async def catalog_fetch(
            codes: list[str]
    ) -> CatalogResult:
        """Fetch items from the catalog"""
        return catalog.fetch(CatalogFetchParams(codes=codes))

    async def list_shopping_cart(session_id: str) -> ShoppingCart:
        """List contents of the shopping cart"""
        session = session_storage.get_session(session_id)
        return session.get_shopping_cart()

    async def set_item_quantity(item_code: str, quantity: int, session_id: str) -> None:
        """Set quantity of specified item in the shopping cart"""
        session = session_storage.get_session(session_id)
        session.set_item_quantity(ItemQuantity(item_code=item_code, quantity=quantity))

    # Convert functions to LlamaIndex FunctionTools
    tools = [
        FunctionTool.from_defaults(
            async_fn=catalog_search,
            name="catalog_search",
            description="Search for items in the catalog by textual query",
            fn_schema=CatalogSearchParams,
        ),
        FunctionTool.from_defaults(
            async_fn=catalog_fetch,
            name="catalog_fetch",
            description="Fetch items from the catalog by their codes",
            fn_schema=CatalogFetchParams
        ),
        FunctionTool.from_defaults(
            async_fn=list_shopping_cart,
            name="list_shopping_cart",
            description="List contents of the shopping cart"
        ),
        FunctionTool.from_defaults(
            async_fn=set_item_quantity,
            name="set_item_quantity",
            description="Set quantity of specified item in the shopping cart",
            fn_schema=ItemQuantity
        ),
    ]
    return tools


class LlamaIndexAgent(BaseAgent):
    def __init__(self, catalog: Catalog, session_storage: SessionStorage):
        super().__init__()
        self.contexts = {}
        self.workflow = ShoppingAssistantWorkflow(
            llm=OpenAI(model=self.OPENAI_MODEL, temperature=0.7),
            tools=_get_tools(catalog, session_storage),
            system_message=self.INSTRUCTIONS,
            verbose=True
        )

    async def chat(self, session_id: str, message: str) -> str:
        ctx = self.contexts.get(session_id, None)
        if ctx is None:
            ctx = Context(workflow=self.workflow)
            await ctx.set('session_id', session_id)
            self.contexts[session_id] = ctx
        response = await self.workflow.run(ctx=ctx, text=message)
        return response.text