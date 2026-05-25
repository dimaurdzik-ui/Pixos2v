from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAdapter(ABC):
    @abstractmethod
    async def execute(self, payload: Dict[str, Any]) -> Any:
        pass
