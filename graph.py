from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Define the state (use "messages" plural)
class State(TypedDict):
    messages: Annotated[list, add_messages]  # <-- This should be "messages"

# Set up the AI model (OpenAI GPT)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# Function for the chatbot (generates responses)
def chatbot(state: State):
    # Check if messages is empty to avoid OpenAI error
    if not state["messages"]:  # <-- Matches the key
        # Return a default response if no messages
        from langchain_core.messages import AIMessage
        return {"messages": [AIMessage(content="Hi! I'm here to chat. What can I help with?")]}
    
    # Otherwise, invoke the LLM normally
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# Build the graph (workflow for the AI)
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# Add memory to remember conversations
memory = InMemorySaver()
graph = graph_builder.compile(checkpointer=memory)