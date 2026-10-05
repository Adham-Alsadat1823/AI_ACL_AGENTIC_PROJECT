from src.utils.nodes import generate_questions, search_web, search_web2
from src.utils.nodes import save_interview, write_section, generate_answer
from src.utils.edges import routes_messages
from src.utils.state import InterviewState
from langgraph.graph import StateGraph, START, END

builder = StateGraph(InterviewState)

# add nodes
builder.add_node("ask_question", generate_questions)
builder.add_node("search_web", search_web)
builder.add_node("search_web2", search_web2)
builder.add_node("answer_question", generate_answer)
builder.add_node("save_interview", save_interview)
builder.add_node("write_section", write_section)

# add edges
builder.add_edge(START, "ask_question")
builder.add_edge("ask_question", "search_web")
builder.add_edge("ask_question", "search_web2")
builder.add_edge("search_web", "answer_question")
builder.add_edge("search_web2", "answer_question")
builder.add_conditional_edges(
    "answer_question",
    routes_messages,
    {
        "ask_question": "ask_question",
        "save_interview": "save_interview"
    }
)
builder.add_edge("save_interview", "write_section")
builder.add_edge("write_section", END)

graph = builder.compile()