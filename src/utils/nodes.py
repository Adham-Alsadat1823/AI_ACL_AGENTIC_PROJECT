from dotenv import load_dotenv
from state import GenerateAnalystsState
from models import llm
from objects import Analyst, Perspectives
from prompts import analyst_instructions
from langchain.messages import SystemMessage, HumanMessage

load_dotenv()

# nodes
def create_analysts(state: GenerateAnalystsState) -> GenerateAnalystsState:
    """create analysts"""
    
    topic = state['topic']
    max_analysts = state['max_analysts']
    human_analyst_feedback = state['human_analysts_feedback']

    # Enforce structured output
    structured_llm = llm.with_structured_output(
            schema= Perspectives
    )

    # System_message
    system_message = analyst_instructions.format(topic = topic,
                                                 human_analyst_feedback = human_analyst_feedback,
                                                 max_analysts = max_analysts)

    # Generate analysts
    analysts = structured_llm.invoke(
        [SystemMessage(content = system_message)] + [HumanMessage(content = "please generate the set of analysts.")]
    )

    return {"analysts": analysts.analysts}

    