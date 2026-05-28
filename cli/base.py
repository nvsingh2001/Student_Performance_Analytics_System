from abc import ABC, abstractmethod

class Command(ABC):
    """Abstract base class for all CLI commands."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The name displayed in the interactive menu."""
        pass

    @abstractmethod
    def execute(self) -> None:
        """The action to perform when the command is selected."""
        pass
