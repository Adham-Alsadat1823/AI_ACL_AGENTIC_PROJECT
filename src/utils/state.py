from .objects import Analyst
from typing_extensions import TypedDict, NotRequired
from typing import Optional, List, Annotated
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from .objects import Analyst

# state
class GenerateAnalystsState(TypedDict):
    topic: str # Research topic
    max_analysts: int # number of analysts
    human_analysts_feedback: NotRequired[Optional[str]] # Human feedback for what is generated
    analysts: NotRequired[List[Analyst]] # List of all our analysts

class InterviewState(MessagesState):
    max_num_turns: int # Number turns of conversation
    context: Annotated[List, add_messages] # Source of docs
    analyst: Analyst # My analyst
    interview: str # interview transcript
    sections: List[str] # Final key we duplicate in outer state for Send() api
    
class ResearchGraphState(TypedDict):
    topic: str # Research topic
    max_analysts: int # number of analysts
    human_analysts_feedback: NotRequired[Optional[str]] # Human feedback for what is generated
    analysts: NotRequired[List[Analyst]] # List of all our analysts
    sections: Annotated[List, add_messages] # send() API key
    introduction: str # introduction to final report
    content: str # content of final report
    conclusion: str # conclusion of final report
    final_report: str # final report



