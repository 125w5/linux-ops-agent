from __future__ import annotations


class LLMError(RuntimeError):
    pass


class LLMConfigurationError(LLMError):
    pass


class LLMRequestError(LLMError):
    pass


class NeedApiConfig(LLMConfigurationError):
    pass
