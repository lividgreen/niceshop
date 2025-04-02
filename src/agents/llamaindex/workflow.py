import asyncio

from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.llms.function_calling import FunctionCallingLLM
from llama_index.core.llms.llm import ToolSelection
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import AsyncBaseTool
from llama_index.core.workflow import Workflow, StartEvent, step, Event, Context, StopEvent


class ClientMessage(StartEvent):
    text: str

class LLMCallEvent(Event):
    messages: list[ChatMessage]

class ToolCallEvent(Event):
    tool_calls: list[ToolSelection]

class LLMResponseEvent(StopEvent):
    text: str

class ShoppingAssistantWorkflow(Workflow):
    def __init__(self, *args, llm: FunctionCallingLLM, tools: list[AsyncBaseTool], system_message: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = llm
        self.tools_by_name = {tool.metadata.get_name(): tool for tool in tools}
        self.system_message = system_message

    @step
    async def chat(self, ctx: Context, ev: ClientMessage) -> LLMCallEvent:
        history = await ctx.get("history", default=None)
        if not history:
            history = ChatMemoryBuffer.from_defaults(
                llm=self.llm,
                chat_history=[ChatMessage(role=MessageRole.SYSTEM, content=self.system_message)]
            )
        history.put(ChatMessage(role=MessageRole.USER, content=ev.text))
        await ctx.set("history", history)
        return LLMCallEvent(messages=history.get())

    @step
    async def call_llm(
            self, ctx: Context, ev: LLMCallEvent
    ) -> ToolCallEvent | LLMResponseEvent:
        response = await self.llm.achat_with_tools(list(self.tools_by_name.values()), messages=ev.messages)

        history = await ctx.get("history")
        history.put(response.message)
        await ctx.set("history", history)

        # get tool calls
        tool_calls = self.llm.get_tool_calls_from_response(
            response, error_on_no_tool_call=False
        )

        if not tool_calls:
            return LLMResponseEvent(text=response.message.content)
        else:
            return ToolCallEvent(tool_calls=tool_calls)

    @step
    async def call_tools(self, ctx: Context, ev: ToolCallEvent) -> LLMCallEvent:
        session_id = await ctx.get("session_id")

        async def call_tool(tool_call: ToolSelection) -> ChatMessage:
            tool = self.tools_by_name.get(tool_call.tool_name)
            additional_kwargs = {
                "tool_call_id": tool_call.tool_id,
                "name": tool.metadata.get_name(),
            }
            if not tool:
                return ChatMessage(
                    role=MessageRole.TOOL,
                    content=f"Tool {tool_call.tool_name} does not exist",
                    additional_kwargs=additional_kwargs,
                )
            else:
                # vvv HARDCODE! vvv
                kwargs = tool_call.tool_kwargs
                if tool.metadata.get_name() in ['list_shopping_cart', 'set_item_quantity']:
                    kwargs['session_id'] = session_id
                # ^^^ HARDCODE! ^^^
                tool_output = await tool.acall(**kwargs)
                return ChatMessage(
                    role=MessageRole.TOOL,
                    content=tool_output.content,
                    additional_kwargs=additional_kwargs
                )

        tool_msgs = await asyncio.gather(*[call_tool(tool_call) for tool_call in ev.tool_calls])

        history = await ctx.get("history")
        for msg in tool_msgs:
            history.put(msg)
        await ctx.set("history", history)

        # update memory
        return LLMCallEvent(messages=history.get())
