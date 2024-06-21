import re
from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import (
    BaseChatModel,
)
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.pydantic_v1 import root_validator
from unsloth import FastLanguageModel


class ChatUnsloth(BaseChatModel):
    model_path: str

    def extract_text_between_tags(self, text, start_tag, end_tag):
        start_tag = re.escape(start_tag)
        end_tag = re.escape(end_tag)

        pattern = f"{start_tag}(.*?){end_tag}"

        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return matches[-1]
        else:
            return None

    @root_validator(pre=False, skip_on_failure=True)
    def validate_environment(cls, values: Dict) -> Dict:
        print(values)
        model_path = values["model_path"]
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_path,
            max_seq_length=2048,
            dtype=None,
            load_in_4bit=True,
        )

        from unsloth.chat_templates import get_chat_template

        tokenizer = get_chat_template(
            tokenizer,
            chat_template="chatml",
            mapping={
                "role": "from",
                "content": "value",
                "user": "human",
                "assistant": "gpt",
            },
        )

        FastLanguageModel.for_inference(model)
        values["model"] = model
        values["tokenizer"] = tokenizer
        return values

    def convert_messages(self, messages: List[BaseMessage]):
        result = []
        for message in messages:
            if isinstance(message, HumanMessage):
                result.append({"role": "user", "value": message.content})
            elif isinstance(message, AIMessage):
                result.append({"role": "assistant", "value": message.content})
            elif isinstance(message, SystemMessage):
                result.append({"role": "system", "value": message.content})
        return result

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        messages = self.convert_messages(messages)
        inputs = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,  # Must add for generation
            return_tensors="pt",
        ).to("cuda")
        outputs = self.model.generate(
            input_ids=inputs, max_new_tokens=1024, use_cache=True
        )

        result = self.tokenizer.batch_decode(outputs)[0]
        response = self.extract_text_between_tags(
            result, start_tag="<|im_start|>assistant\n", end_tag="<|im_end|>"
        )
        chat_generation = ChatGeneration(
            message=AIMessage(content=response),
        )
        return ChatResult(generations=[chat_generation])

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model."""
        return "unsloth"
