from objects import Analyst
from typing_extensions import TypedDict, NotRequired
from typing import Optional, List

# state
class GenerateAnalystsState(TypedDict):
    topic: str # Research topic
    max_analysts: int # number of analysts
    human_analysts_feedback: NotRequired[Optional[str]] # Human feedback for what is generated
    analysts: NotRequired[List[Analyst]] # List of all our analysts
