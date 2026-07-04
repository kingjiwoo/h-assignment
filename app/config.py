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
        """LLM을 실제로 호출하기 직전에 키 존재를 검증한다(fail-fast).

        import 시점이 아니라 사용 시점에 검증하므로, 데이터 집계 계층은 키 없이도 테스트/실행할 수 있다.
        """
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise RuntimeError("LLM_PROVIDER=anthropic이지만 ANTHROPIC_API_KEY가 설정되지 않았습니다.")
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise RuntimeError("LLM_PROVIDER=openai이지만 OPENAI_API_KEY가 설정되지 않았습니다.")
        if not self.anthropic_api_key and not self.openai_api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY 또는 OPENAI_API_KEY 중 하나는 반드시 설정되어야 합니다. "
                ".env.example을 참고해 .env를 만드세요."
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
