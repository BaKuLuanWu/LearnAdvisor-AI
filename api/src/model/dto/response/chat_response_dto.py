from dataclasses import dataclass


@dataclass
class ChatResponseDTO:
    type:str
    content:str