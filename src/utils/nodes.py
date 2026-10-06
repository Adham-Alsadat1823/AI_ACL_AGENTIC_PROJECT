from dotenv import load_dotenv
from langchain import messages
from .state import GenerateAnalystsState, InterviewState
from .models import llm
from .objects import Perspectives, Analyst, SearchQuery
from .prompts import analyst_instructions, question_instructions, search_instructions
from .prompts import  answer_instructions, section_writer_instructions
from langchain.messages import SystemMessage, HumanMessage
from langgraph.types import interrupt
from langchain_tavily import TavilySearch
from langchain_core.messages import get_buffer_string

load_dotenv()

# nodes
def create_analysts(state: GenerateAnalystsState) -> GenerateAnalystsState:
    """create analysts"""
    
    topic = state['topic']
    max_analysts = state['max_analysts']
    human_analyst_feedback = state.get('human_analysts_feedback', "")

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

def human_feedback(state: GenerateAnalystsState) -> GenerateAnalystsState:
    """this is where the human gives feedback about the analysts"""

    feedback = interrupt({
        "question": "Are these analysts okay for you?",
        "analysts": [
            analyst.model_dump() if hasattr(analyst, "model_dump") else analyst
            for analyst in state.get('analysts', [])
        ],
        "instructions": """Return feedback to regenerate analysts
        or return empty/okay/perfect/continue to prove and continue the graph."""
    }
    )

    if feedback is None:
        return {"human_analysts_feedback": None}

    if isinstance(feedback, str):
        feedback = feedback.strip()

        if feedback == "":
            return {"human_analysts_feedback": None}

        if feedback.lower() in ["okay", "perfect", "continue"]:
            return {"human_analysts_feedback": None}

        return {"human_analysts_feedback": feedback}
    
    return {"human_analysts_feedback": None}

def generate_questions(state: InterviewState) -> InterviewState:
    """node to generate questions"""

    # get state analyst
    analyst = state['analyst']

    if isinstance(analyst, dict):
        analyst = Analyst.model_validate(analyst)

    messages = state['messages']

    # system message
    system_message = question_instructions.format(
        goals = analyst.persona
        )

    # generate question
    question = llm.invoke(
        [SystemMessage(content = system_message)] + messages
    )

    return {"messages": [question]}

def search_web(state: InterviewState) -> InterviewState:
    """Retrieve docs from the web"""

    # Search query
    structured_llm = llm.with_structured_output(SearchQuery)

    # Search instruction
    system_message = search_instructions
    tavily_search = TavilySearch(max_result=3)

    search_query = structured_llm.invoke([SystemMessage(system_message)] + state["messages"])

    # search
    data = tavily_search.invoke({"query": search_query.search_query})
    search_docs = data.get("results", data)

    # format
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}

def search_web2(state: InterviewState) -> InterviewState:
    """ Retrieve docs from web search """

    # Search query
    structured_llm = llm.with_structured_output(SearchQuery)
    tavily_search = TavilySearch(max_results= 3)
    search_query = structured_llm.invoke([search_instructions]+state['messages'])
    
    # Search
    #search_docs = tavily_search.invoke(search_query.search_query) # updated 1.0
    data = tavily_search.invoke({"query": search_query.search_query})
    search_docs = data.get("results", data)
    

     # Format
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}

def generate_answer(state: InterviewState) -> InterviewState:
    """node to answer a question"""

    # get state
    analyst = state["analyst"]
    context = state["context"]
    messages = state["messages"]

    if isinstance(analyst, dict):
        analyst = Analyst.model_validate(analyst)

    # answer question
    system_message = answer_instructions.format(goals= analyst.persona, context= context)
    answer = llm.invoke([SystemMessage(system_message)] + messages)

    # name the message as coming from the expert
    answer.name = "expert"

    return {"messages": [answer]}

def save_interview(state: InterviewState) -> InterviewState:
    """save interviews"""

    messages = state["messages"]

    interview = get_buffer_string(messages)

    return {"interview": interview}

def write_section(state: InterviewState) -> InterviewState:
    """node to answer a question"""

    # get the state
    interview = state["interview"]
    context = state["context"]
    analyst = state["analyst"]

    if isinstance(analyst, dict):
        analyst = Analyst.model_validate(analyst)

    # system message
    system_message = section_writer_instructions.format(focus=analyst.description)
    section = llm.invoke([system_message], [HumanMessage(f"use this source to write your section: {context}")])

    return {"sections": [section.content]}

def write_report(state: ResearchGraphState):
    # Full set of sections
    sections = state["sections"]
    topic = state["topic"]

    # Concat all sections together
    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])
    
    # Summarize the sections into a final report
    system_message = report_writer_instructions.format(topic=topic, context=formatted_str_sections)    
    report = llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content=f"Write a report based upon these memos.")]) 
    return {"content": report.content}

def write_introduction(state: ResearchGraphState):
    # Full set of sections
    sections = state["sections"]
    topic = state["topic"]

    # Concat all sections together
    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])
    
    # Summarize the sections into a final report
    
    instructions = intro_conclusion_instructions.format(topic=topic, formatted_str_sections=formatted_str_sections)    
    intro = llm.invoke([instructions]+[HumanMessage(content=f"Write the report introduction")]) 
    return {"introduction": intro.content}

def write_conclusion(state: ResearchGraphState):

    # Full set of sections
    sections = state["sections"]
    topic = state["topic"]

    # Concat all sections together
    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])
    
    # Summarize the sections into a final report
    
    instructions = intro_conclusion_instructions.format(topic=topic, formatted_str_sections=formatted_str_sections)    
    conclusion = llm.invoke([instructions]+[HumanMessage(content=f"Write the report conclusion")]) 
    return {"conclusion": conclusion.content}

def finalize_report(state: ResearchGraphState):
    """ The is the "reduce" step where we gather all the sections, combine them, and reflect on them to write the intro/conclusion """
    # Save full final report
    content = state["content"]
    if content.startswith("## Insights"):
        content = content.strip("## Insights")
    if "## Sources" in content:
        try:
            content, sources = content.split("\n## Sources\n")
        except:
            sources = None
    else:
        sources = None

    final_report = state["introduction"] + "\n\n---\n\n" + content + "\n\n---\n\n" + state["conclusion"]
    if sources is not None:
        final_report += "\n\n## Sources\n" + sources
    return {"final_report": final_report}
