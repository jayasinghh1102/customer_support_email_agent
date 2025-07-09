from typing import List, Dict, Any
import email
from langgraph.graph import StateGraph, END

from .llm_integration import classify_email_intent, draft_response
from .email_client import send_email, get_email_body
from .knowledge_base import get_knowledge_base

# Agent State Definition
class AgentState(Dict[str, Any]):
    """Represents the state of our agent's workflow."""
    email_message: email.message.Message = None
    email_body: str = None
    classification: str = None
    knowledge_context: str = None
    response: str = None
    log: List[str] = []

# Agent Nodes
def fetch_email_node(state: AgentState):
    print("\n--- Node: Process Email ---")
    state['log'].append("Processing fetched email...")
    email_msg = state['email_message']
    if email_msg:
        state['email_body'] = get_email_body(email_msg)
        state['log'].append("Successfully extracted email body.")
    else:
        state['log'].append("ERROR: No email message found in state.")
    return state

def classify_email_node(state: AgentState):
    print("\n--- Node: Classify Email ---")
    classification = classify_email_intent(state['email_body'])
    state['classification'] = classification
    state['log'].append(f"Email classified as: {classification}")
    return state

def retrieve_knowledge_node(state: AgentState):
    print("\n--- Node: Retrieve Knowledge ---")
    vectorstore = get_knowledge_base()
    docs = vectorstore.similarity_search(state['email_body'])
    
    context = "\n---\n".join([doc.page_content for doc in docs])
    state['knowledge_context'] = context
    state['log'].append("Retrieved knowledge from vector store.")
    return state

def draft_response_node(state: AgentState):
    print("\n--- Node: Draft Response ---")
    response = draft_response(state['email_body'], state['knowledge_context'])
    state['response'] = response
    state['log'].append("Drafted email response.")
    return state

def send_response_node(state: AgentState):
    print("\n--- Node: Send Response ---")
    email_msg = state['email_message']
    to_address = email.utils.parseaddr(email_msg['From'])[1]
    subject = email_msg['Subject']
    
    send_email(to_address, subject, state['response'])
    state['log'].append("Sent email response.")
    return state

def log_escalation_node(state: AgentState):
    print("\n--- Node: Log Escalation ---")
    email_subject = state['email_message']['Subject']
    from_address = state['email_message']['From']
    escalation_log = (
        f"ESCALATION NEEDED: Email from '{from_address}' with subject: '{email_subject}'. "
        f"Reason: Classified as '{state['classification']}'."
    )
    print(f"\n\n{'='*20}\n{escalation_log}\n{'='*20}\n")
    state['log'].append(escalation_log)
    return state

# --- Conditional Edge Logic ---
def should_auto_respond(state: AgentState):
    print("\n--- Conditional Edge: Should Auto-Respond? ---")
    if "auto_respondable" in state['classification']:
        print("Decision: Yes, auto-respond.")
        return "yes"
    else:
        print("Decision: No, escalate.")
        return "no"

# Graph Assembly 
def create_agent_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("fetch_email", fetch_email_node)
    workflow.add_node("classify_email", classify_email_node)
    workflow.add_node("retrieve_knowledge", retrieve_knowledge_node)
    workflow.add_node("draft_response", draft_response_node)
    workflow.add_node("send_response", send_response_node)
    workflow.add_node("log_escalation", log_escalation_node)

    workflow.set_entry_point("fetch_email")
    workflow.add_edge("fetch_email", "classify_email")
    workflow.add_conditional_edges(
        "classify_email",
        should_auto_respond,
        {"yes": "retrieve_knowledge", "no": "log_escalation"}
    )
    workflow.add_edge("retrieve_knowledge", "draft_response")
    workflow.add_edge("draft_response", "send_response")
    workflow.add_edge("send_response", END)
    workflow.add_edge("log_escalation", END)

    return workflow.compile()
