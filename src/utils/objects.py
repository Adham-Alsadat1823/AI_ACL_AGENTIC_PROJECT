from pydantic import BaseModel, Field
from typing import List

# creating our object analyst
class Analyst(BaseModel):
    name: str = Field(description="The name of the analyst")
    affiliation: str = Field(description="The primary affiliation of the analyst")
    role: str = Field(description="The role of the analyst in the context of the topic")
    description: str = Field(description="Description of the analyst focus, concerns, and motivations")

    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nAffiliation: {self.affiliation}\nRole: {self.role}\nDescription: {self.description}"

class Perspectives(BaseModel):
    analysts: List[Analyst] = Field(description="Comprehensive list of analysts with the roles and affiliations")
    