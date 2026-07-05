"""Provider-agnostic LLM initialization.

app/config.py has already decided which of ANTHROPIC_API_KEY / OPENAI_API_KEY is in
play, so all this module does is hand langchain's `init_chat_model` the
provider:model pair.
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
