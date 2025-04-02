from typing import TypedDict
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from src.agents import BaseAgent
from src.shop.catalog import Catalog
from src.shop.entities import ShoppingCart, CatalogSearchParams, CatalogFetchParams, CatalogResult, ItemQuantity
from src.shop.session import SessionStorage
from langgraph.graph.message import MessagesState

class Toolkit:
    @staticmethod
    def get_tools(catalog: Catalog, session_storage: SessionStorage):
        @tool(args_schema=CatalogSearchParams)
        async def catalog_search(
                query: str,
                max_results: int = 5
        ) -> CatalogResult:
            """Search for items in the catalog by textual query"""
            return catalog.search(CatalogSearchParams(query=query, max_results=max_results))

        @tool(args_schema=CatalogFetchParams)
        async def catalog_fetch(
                codes: list[str]
        ) -> CatalogResult:
            """Fetch items from the catalog"""
            return catalog.fetch(CatalogFetchParams(codes=codes))

        @tool
        async def list_shopping_cart(config: RunnableConfig) -> ShoppingCart:
            """List contents of the shopping cart"""
            session_id = config['configurable']['thread_id']
            session = session_storage.get_session(session_id)
            return session.get_shopping_cart()

        @tool(args_schema=ItemQuantity)
        async def set_item_quantity(item_code: str, quantity: int, config: RunnableConfig) -> None:
            """Set quantity of specified item in the shopping cart"""
            session_id = config['configurable']['thread_id']
            session = session_storage.get_session(session_id)
            session.set_item_quantity(ItemQuantity(item_code=item_code, quantity=quantity))
        return [catalog_search, catalog_fetch, list_shopping_cart, set_item_quantity]


class LangChainAgent(BaseAgent):
    def __init__(self, catalog: Catalog, session_storage: SessionStorage):
        super().__init__()

        tools = Toolkit.get_tools(catalog, session_storage)

        llm_with_tools = ChatOpenAI(
            model=self.OPENAI_MODEL,
            temperature=0.7
        ).bind_tools(tools)

        async def llm_call(state: TypedDict) -> dict:
            combined_messages = [SystemMessage(self.INSTRUCTIONS)] + state['messages']
            response = await llm_with_tools.ainvoke(combined_messages)
            return {"messages": [response]}

        memory = MemorySaver()

        graph_builder = StateGraph(MessagesState)
        graph_builder.add_node("tools", ToolNode(tools=tools))
        graph_builder.add_node("chatbot", llm_call)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_conditional_edges("chatbot", tools_condition, ["tools", END])
        graph_builder.add_edge("tools", "chatbot")
        self.graph = graph_builder.compile(checkpointer=memory)

    async def chat(self, session_id: str, message: str) -> str:
        config = {"configurable": {"thread_id": session_id}}
        inputs = {"messages": [HumanMessage(content=message)]}
        response = await self.graph.ainvoke(input=inputs, config=config)
        response_message = response["messages"][-1].content
        return response_message