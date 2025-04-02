from aiohttp import web
from langchain.globals import set_verbose, set_debug

from src.agents import BaseAgent
from src.agents.langchain.agent import LangChainAgent
from src.agents.llamaindex.agent import LlamaIndexAgent
from src.shop.catalog import DummyCatalog
from src.shop.session import SessionStorage
from dotenv import load_dotenv

load_dotenv()

AGENT_IMPL = 'llamaindex'

catalog = DummyCatalog()
session_storage = SessionStorage()

def create_agent(agent_impl: str) -> BaseAgent:
    match agent_impl:
        case 'langchain':
            set_verbose(True)
            set_debug(True)
            return LangChainAgent(catalog, session_storage)
        case 'llamaindex':
            return LlamaIndexAgent(catalog, session_storage)
        case _:
            raise ValueError(f'Unknown agent implementation: {agent_impl}')

agent = create_agent(AGENT_IMPL)

routes = web.RouteTableDef()

@routes.get('/')
async def main(request: web.Request) -> web.Response:
    with open('resources/main.html', 'r') as f:
        return web.Response(text=f.read(), content_type='text/html')

@routes.post('/api/auth')
async def create_session(request):
    session = session_storage.create_session()
    return web.Response(text=session)

@routes.post('/api/chat')
async def chat(request):
    session_id = request.headers.get('Session-Id')
    if not session_id:
        return web.Response(status=403, text="Not authenticated")
    client_message = await request.text()
    response_text = await agent.chat(session_id, client_message)
    return web.Response(text=response_text)

@routes.get('/api/checkout')
async def checkout(request):
    session_id = request.headers.get('Session-Id')
    if not session_id:
        return web.Response(status=403, text="Not authenticated")    
    session = session_storage.get_session(session_id)
    return web.Response(text=f"You are going to purchase: {session.get_shopping_cart()}")

app = web.Application()
app.add_routes(routes)

if __name__ == '__main__':
    web.run_app(app)