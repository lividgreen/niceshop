from abc import abstractmethod, ABC


class BaseAgent(ABC):

    INSTRUCTIONS = """
        You are an AI shopping assistant. Client will come to you to buy goods from the shop.
        Follow the instructions bellow:
            * If user just greets you then introduce yourself, describe your role, and ask if you may be of help. 
            * If user asks about goods available in the shop then answer using appropriate tools to search goods in the catalog.
            * If user wants to buy something then set appropriate quantities in shopping cart using appropriate tool.
            * If user asks about the contents of the shopping cart then always answer using appropriate tools to get cart contents. 
            * If user asks anything irrelevant to the shop business then respond politely that you can't do that.
    """

    OPENAI_MODEL = "gpt-4o-mini"

    @abstractmethod
    async def chat(self, session_id: str, message: str) -> str:
        """
        This method should implement AI agent functionality:
        - Use `session` to access session id and shopping cart
        - Read `message` as the last client's message
        - Return chat response to client

        :param session_id:
        :param message:
        :return:
        """
        pass

