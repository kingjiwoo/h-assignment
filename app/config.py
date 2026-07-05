import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm_provider = os.getenv("LLM_PROVIDER") or self._default_provider()
        self.llm_model = os.getenv("LLM_MODEL") or self._default_model()
        self.max_studies = int(os.getenv("MAX_STUDIES", "500"))
        self.ctgov_base_url = "https://clinicaltrials.gov/api/v2"

    def require_llm_key(self) -> None:
        """Validate the LLM key at call time (fail-fast).

        Validated at use time (not import time) so the data/aggregation layers can be
        tested and run without any LLM key configured.
        """
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise RuntimeError("LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY is not set.")
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise RuntimeError("LLM_PROVIDER=openai but OPENAI_API_KEY is not set.")
        if not self.anthropic_api_key and not self.openai_api_key:
            raise RuntimeError(
                "Either ANTHROPIC_API_KEY or OPENAI_API_KEY must be set. "
                "See .env.example and create a .env file."
            )

    def _default_provider(self) -> str:
        if os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        return "anthropic"

    def _default_model(self) -> str:
        return {
            "anthropic": "claude-sonnet-4-5",
            "openai": "gpt-4.1",
        }[self.llm_provider]


settings = Settings()
