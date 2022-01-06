from dataclasses import dataclass

@dataclass(frozen=True)
class Instance:
    address: str
    is_running: bool
