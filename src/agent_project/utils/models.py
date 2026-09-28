from langchain_openrouter import ChatOpenRouter
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenRouter(
    model = "qwen/qwen3.8-27b:free",
    api_key = os.getenv("OPENROUTER_API_KEY"),
    temperature = 0.0
)

