from typing import Any, Dict, List, Union

from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult

# https://python.langchain.com/v0.1/docs/modules/callbacks/
class LogHandler(BaseCallbackHandler):
    """Base callback handler that can be used to handle callbacks from langchain."""
    def __init__(
        self, context: str
    ):
        self.context = context

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        """Run when LLM starts running."""
        print(f"\n{self.context} LLM started: {prompts}\n{serialized}\n{kwargs}\n")

    def on_chat_model_start(
        self,
        serialized: Dict[str, Any],
        messages: List[List[BaseMessage]],
        **kwargs: Any
    ) -> Any:
        """Run when Chat Model starts running."""
        print(f"\n{self.context} Chat Model started: {messages}\n{serialized}\n{kwargs}\n")

    def on_llm_new_token(self, token: str, **kwargs: Any) -> Any:
        """Run on new LLM token. Only available when streaming is enabled."""
        print(f"\n{self.context} New token: {token}\n{kwargs}\n")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        """Run when LLM ends running."""
        print(f"\n{self.context} LLM end: {response}\n{kwargs}\n")

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when LLM errors."""
        print(f"\n{self.context} LLM error: {error}\n{kwargs}\n")

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> Any:
        """Run when chain starts running."""
        print(f"\n{self.context} Chain started: {inputs}\n{serialized}\n{kwargs}\n")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> Any:
        """Run when chain ends running."""
        print(f"\n{self.context} Chain end: {outputs}\n{kwargs}\n")

    def on_chain_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when chain errors."""
        print(f"\n{self.context} Chain error: {error}\n{kwargs}\n")

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> Any:
        """Run when tool starts running."""
        print(f"\n{self.context} Tool started: {input_str}\n{serialized}\n{kwargs}\n")

    def on_tool_end(self, output: Any, **kwargs: Any) -> Any:
        """Run when tool ends running."""
        print(f"\n{self.context} Tool end: {output}\n{kwargs}\n")

    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when tool errors."""
        print(f"\n{self.context} Tool error: {error}\n{kwargs}\n")

    def on_text(self, text: str, **kwargs: Any) -> Any:
        """Run on arbitrary text."""
        print(f"\n{self.context} Text: {text}\n{kwargs}\n")

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Run on agent action."""
        print(f"\n{self.context} Agent action: {action}\n{kwargs}\n")

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """Run on agent end."""
        print(f"\n{self.context} Agent finish: {finish}\n{kwargs}\n")
