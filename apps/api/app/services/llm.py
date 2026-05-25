import litellm
from typing import List, Dict, Any
from apps.api.app.core.config import settings

# Configure LiteLLM
if settings.OPENAI_API_KEY:
    import os
    os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

class LLMService:
    @staticmethod
    async def generate_completion(
        messages: List[Dict[str, str]], 
        model: str = "gpt-4o-mini",
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Wrapper around litellm.acompletion to handle generation and cost tracking.
        """
        response = await litellm.acompletion(
            model=model,
            messages=messages,
            temperature=temperature
        )
        
        # Calculate cost
        cost = litellm.completion_cost(completion_response=response)
        
        return {
            "content": response.choices[0].message.content,
            "cost_in_usd": cost,
            "usage": response.usage.model_dump() if response.usage else {}
        }
