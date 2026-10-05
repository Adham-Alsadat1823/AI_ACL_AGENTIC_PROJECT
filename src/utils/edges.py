from dotenv import load_dotenv
from langchain.messages import AIMessage
from .state import GenerateAnalystsState, InterviewState
from typing import Literal
from langgraph.graph import END

load_dotenv()

# conditional edges
def should_continue(state: GenerateAnalystsState) -> Literal[END, "create_analysts"]:
    """Return the next node to execute"""
    feedback = state.get("human_analysts_feedback", None)

    if feedback is None:
        return END

    elif feedback.lower() in ["okay", "perfect", "continue"]:
        return END
        
    else:
        return "create_analysts"

def routes_messages(state: InterviewState, name: str = "expert"):
    """route between question and answer"""

    # get messages
    messages = state["messages"]
    max_num_turns = state.get("max_num_turns", 2)

    # check the number of expert answers
    num_responses = len([message for message in messages if isinstance(message, AIMessage) and message.name == name])

    if num_responses >= max_num_turns:
        return "save_interview"

    return "ask_question"