from langgraph.graph import StateGraph, START, END
from src.answering_question import interview_builder
from src.utils.edges import initiate_all_interviews
import src.utils.nodes as nodes
from src.utils.state import ResearchGraphState

# Add nodes and edges
deep_agent_builder = StateGraph(ResearchGraphState)

deep_agent_builder.add_node("create_analysts", nodes.create_analysts)
deep_agent_builder.add_node("human_feedback", nodes.human_feedback)
deep_agent_builder.add_node("conduct_interview", interview_builder.compile())
deep_agent_builder.add_node("write_report", nodes.write_report)
deep_agent_builder.add_node("write_introduction", nodes.write_introduction)
deep_agent_builder.add_node("write_conclusion", nodes.write_conclusion)
deep_agent_builder.add_node("finalize_report", nodes.finalize_report)


deep_agent_builder.add_edge(START, "create_analysts")
deep_agent_builder.add_edge("create_analysts", "human_feedback")
deep_agent_builder.add_conditional_edges(
    "human_feedback",
    init_all_interviews,
    {
        "create_analysts": "create_analysts",
        "conduct_interview": "conduct_interview"
    }
)
deep_agent_builder.add_edge("conduct_interview", "write_report")
deep_agent_builder.add_edge("conduct_interview", "write_introduction")
deep_agent_builder.add_edge("conduct_interview", "write_conclusion")
deep_agent_builder.add_edge("write_report", "finalize_report")
deep_agent_builder.add_edge("write_introduction", "finalize_report")
deep_agent_builder.add_edge("finalize_report", END)

graph = deep_agent_builder.compile()
