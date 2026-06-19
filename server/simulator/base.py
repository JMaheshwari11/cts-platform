"""BaseSimulator - abstract base class for all simulation engines."""
from abc import ABC, abstractmethod
import pandas as pd
from simulator.models import SimulationResult


class BaseSimulator(ABC):
    name: str = "BaseSimulator"
    methodology: str = "Override in subclass"

    def __init__(self, df: pd.DataFrame):
        self.df = df

    @abstractmethod
    def run(self, params) -> SimulationResult:
        pass

    def _filter(self, **kwargs) -> pd.DataFrame:
        result = self.df
        for col, val in kwargs.items():
            if val is not None and col in result.columns:
                result = result[result[col] == val]
        return result
