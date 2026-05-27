from __future__ import annotations
from abc import ABC


class BaseAgent(ABC):
    def __init__(self):
        ...
    
    def step(self, dt: int, context):
        ...