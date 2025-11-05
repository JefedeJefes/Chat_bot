from flask import render_template, request, Flask, redirect, url_for
from graph import graph  # Import the AI graph
from langchain_core.messages import HumanMessage, AIMessage  # For converting messages
import json  # For readable printing

app = Flask(__name__)
app.config["SECRET_KEY"] = "arjunvyas"

# Global list for shared chat history (as dicts for easy display)
messages = []

# Add initial bot message to prevent empty list
messages.append({"role": "assistant", "content": "Hi! How may I help you today?"})

@app.route('/', methods=['GET'])
def index():
    # Show the chat page with current history
    return render_template("index.html", messages=messages)

@app.route('/chat', methods=['POST'])
def chat():
    # Get user's message from the form
    user_input = request.form.get('message')
    if not user_input:
        return redirect(url_for('index'))
    
    # Add user's message to history (as dict)
    messages.append({"role": "user", "content": user_input})
    
    # Convert messages to LangChain objects for the graph
    langchain_messages = []
    for msg in messages:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            langchain_messages.append(AIMessage(content=msg["content"]))
    
    print(f"the langchain_output is {langchain_messages}")
    # Set up for AI (shared thread)
    thread_id = "global"
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        # Ask AI for a response using converted messages
        result = graph.invoke({"messages": langchain_messages}, config)
        
        # Debug: Print result and state
        print(f"Graph invoke result: {result}")
        state = graph.get_state(config)
        print("Current Graph State (Readable):")
        print(json.dumps(state.values, indent=2, default=str))
        
        # Stricter check: Ensure result is dict, has 'messages', and it's not None/empty
        if result is None or not isinstance(result, dict) or "messages" not in result or result["messages"] is None or not result["messages"]:
            print("Result is invalid, using fallback.")
            bot_response = "Sorry, I couldn't process that. Try again!"
        else:
            # Safely get bot response
            bot_response = result["messages"][-1].content
            print(f"Bot response: {bot_response}")
    except Exception as e:
        # Catch any errors (e.g., API issues)
        print(f"Error invoking graph: {e}")
        bot_response = "Oops, something went wrong. Please try again."
    
    # Add AI's response to history (as dict)
    messages.append({"role": "assistant", "content": bot_response})
    
    # Show updated chat page
    return render_template("index.html", messages=messages)

if __name__ == '__main__':
    app.run(debug=True)