"""
Create the LLM used by the personal assistant.

This file loads environment variables and builds either an OpenAI
or a Gemini chat model, based on LLM_PROVIDER in the .env file.

Keep it small so beginners can see exactly where the LLM comes from.
"""

import os
from functools import lru_cache
from langchain_core.language_models.chat_models import BaseChatModel
from toolcalling_proj.config.settings import get_settings, Settings
from dotenv import load_dotenv

@lru_cache
def get_llm(temperature: float | None = None)-> BaseChatModel:
    """Return a cached chat model instance based on current settings.

    lru_cache here mirrors the get_settings() pattern from Phase 0/2:
    avoids re-instantiating a client (and re-reading env vars) on every
    call, while still failing loudly at first-use rather than at import
    time if credentials are missing.
    """

    settings = get_settings()
    llm_model = settings.llm_model
    temperature = settings.llm_temperature if temperature is None else temperature

    # temperature=0 keeps answers more consistent for demos/lectures.
    if settings.llm_provider == "openai":
        return _create_openai_llm(settings=settings, llm_model=llm_model, temperature=temperature)

    if settings.llm_provider == "gemini":
        return _create_gemini_llm(settings=settings, llm_model=llm_model, temperature=temperature)

    raise ValueError(
        f'Unknown LLM_PROVIDER: "{settings.llm_provider}". '
        'Use "openai" or "gemini" in your .env file.'
    )


def _create_openai_llm(settings: Settings, llm_model: str, temperature: float) -> BaseChatModel:
    """
    Create a ChatOpenAI client using the OpenAI API key from .env.

    Returns:
        ChatOpenAI: An OpenAI chat model instance.

    Raises:
        ValueError: If OPENAI_API_KEY is missing.
    """
    from langchain_openai import ChatOpenAI

    api_key = settings.openai_api_key
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing. "
            "Add it to your .env file when LLM_PROVIDER=openai."
        )
    try:
        llm = ChatOpenAI(
            model=llm_model,
            api_key=api_key,
            temperature=temperature,
        )
        return llm
    except:
        raise ValueError(
            f"OpenAI does not have access to the provided LLM model: {llm_model}"
        )


def _create_gemini_llm(settings: Settings, llm_model: str, temperature: float) -> BaseChatModel:
    """
    Create a ChatGoogleGenerativeAI client using the Gemini API key from .env.

    Returns:
        ChatGoogleGenerativeAI: A Gemini chat model instance.

    Raises:
        ValueError: If GEMINI_API_KEY is missing.
    """
    from langchain_google_genai import ChatGoogleGenerativeAI

    api_key = settings.gemini_api_key
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. "
            "Add it to your .env file when LLM_PROVIDER=gemini."
        )
    try:
        llm = ChatGoogleGenerativeAI(
            model=llm_model,
            google_api_key=api_key,
            temperature=temperature,
        )
        return llm
    except:
        raise ValueError(
            f"Gemini does not have access to the provided LLM model: {llm_model}"
        )
