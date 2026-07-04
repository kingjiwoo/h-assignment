"""Provider-agnostic LLM 초기화.

ANTHROPIC_API_KEY / OPENAI_API_KEY 중 존재하는 쪽을 app/config.py가 이미 판별해두었으므로,
여기서는 langchain의 init_chat_model에 provider:model 형식으로 넘기기만 한다.
"""

from functools import lru_cache

from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel

from app.config import settings


@lru_cache(maxsize=1)
def get_chat_model() -> BaseChatModel:
    settings.require_llm_key()
    return init_chat_model(
        model=settings.llm_model,
        model_provider=settings.llm_provider,
        temperature=0,
    )
