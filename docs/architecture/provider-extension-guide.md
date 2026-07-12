# Provider Extension Guide

## Adding a New LLM Provider
1. Create a new implementation of the LLMProvider abstract base class.
2. Register it in the provider factory in [backend/app/providers/llm/factory.py](backend/app/providers/llm/factory.py).
3. Add any required API key configuration to [backend/app/core/config.py](backend/app/core/config.py).
4. Document the provider in this guide and the README.

### Current providers
- OpenAI: implemented in [backend/app/providers/llm/openai.py](backend/app/providers/llm/openai.py)
- Gemini: implemented in [backend/app/providers/llm/gemini.py](backend/app/providers/llm/gemini.py)
- Grok: implemented in [backend/app/providers/llm/grok.py](backend/app/providers/llm/grok.py)

## Adding a New Database Connector
1. Create a new connector class implementing the DatabaseConnector interface.
2. Register it in the connector factory in [backend/app/services/connection_service.py](backend/app/services/connection_service.py).
3. Add the required DSN or configuration settings to [backend/app/core/config.py](backend/app/core/config.py).
4. Add tests for connection validation and schema inspection.
