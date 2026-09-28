from langchain_openrouter import ChatOpenRouter
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenRouter(
    model="nvidia/nemotron-3-ultra-550b-a55b:free",
    temperature=0.0
)