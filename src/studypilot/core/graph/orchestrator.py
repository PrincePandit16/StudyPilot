from typing import Annotated, List, Optional, TypedDict
from langgraph.graph import StateGraph, END
from src.studypilot.core.llm.provider import get_llm_provider
from src.studypilot.core.config import settings
from src.studypilot.services.embedding_service import embedding_service
from sqlalchemy.orm import Session

# --- State Definition ---

class AgentState(TypedDict):
    """
    The shared state across the StudyPilot LangGraph.
    """
    user_id: str
    conversation_id: str
    document_ids: List[str]
    user_message: str
    intent: Optional[str]
    retrieved_chunks: List[str]  # Content of chunks, not full objects to keep state lean
    generated_content: Optional[str]
    citations: List[str]
    retry_count: int
    quality_passed: bool
    error_code: Optional[str]
    db_session: Optional[Session] # Allow passing session for DB operations

# --- Node Implementations ---

async def load_context(state: AgentState):
    print("--- LOADING CONTEXT ---")
    # In a real scenario, we might load conversation history here
    return state

async def validate_request(state: AgentState):
    print("--- VALIDATING REQUEST ---")
    if not state.get("user_id") or not state.get("user_message"):
        return {**state, "error_code": "MISSING_INPUT"}
    return state

async def classify_intent(state: AgentState):
    print("--- CLASSIFYING INTENT ---")
    llm = get_llm_provider()
    categories = ["rag", "summary", "quiz", "flashcards", "study_plan"]

    intent = await llm.classify(
        text=state["user_message"],
        categories=categories,
        system_prompt="You are an intent classifier for a study assistant. Classify the user request into one of the provided categories."
    )

    # Clean up response just in case LLM adds punctuation
    intent = intent.strip().lower().replace(".", "")
    if intent not in categories:
        intent = "rag" # Default

    return {**state, "intent": intent}

async def retrieve_context(state: AgentState):
    print("--- RETRIEVING CONTEXT ---")
    from src.studypilot.repositories.document_repository import DocumentRepository

    session = state.get("db_session")
    if not session:
        return {**state, "error_code": "DB_SESSION_MISSING"}

    repo = DocumentRepository(session)
    query_emb = embedding_service.generate_embedding(state["user_message"])

    # Search for similar chunks
    results = repo.search_similar_chunks(
        user_id=state["user_id"],
        query_embedding=query_emb,
        document_ids=state.get("document_ids"),
        limit=settings.TOP_K
    )

    chunks = [chunk.content for chunk, dist in results]
    return {**state, "retrieved_chunks": chunks}

async def generate_answer(state: AgentState):
    print("--- GENERATING ANSWER ---")
    llm = get_llm_provider()

    context = "\n\n".join(state["retrieved_chunks"])
    prompt = f"""Use the following context to answer the user's question.
If the answer is not in the context, say that you don't know.
Provide citations as [1], [2] etc. based on the order of context chunks.

Context:
{context}

Question: {state['user_message']}
"""

    answer = await llm.generate(
        prompt=prompt,
        system_prompt="You are a grounded study assistant. Only answer based on the provided context."
    )

    # Simple citation extraction mock (in reality, we'd use a better parser)
    citations = [f"Chunk {i+1}" for i in range(len(state["retrieved_chunks"]))]

    return {**state, "generated_content": answer, "citations": citations, "retry_count": state.get("retry_count", 0) + 1}

async def verify_answer(state: AgentState):
    print("--- VERIFYING ANSWER ---")
    llm = get_llm_provider()

    context = "\n\n".join(state["retrieved_chunks"])
    prompt = f"""Check if the following answer is fully supported by the context.
If it is, respond with 'YES'. If it contains hallucinations or unsupported info, respond with 'NO'.

Context: {context}
Answer: {state['generated_content']}
"""

    verdict = await llm.generate(
        prompt=prompt,
        system_prompt="You are a quality auditor. Respond only with YES or NO."
    )

    passed = "YES" in verdict.upper()
    return {**state, "quality_passed": passed}

async def generate_summary(state: AgentState):
    print("--- GENERATING SUMMARY ---")
    llm = get_llm_provider()

    # If we have document_ids, we might want to retrieve all chunks from those docs
    context = "\n\n".join(state.get("retrieved_chunks", []))
    if not context:
        from src.studypilot.repositories.document_repository import DocumentRepository
        session = state.get("db_session")
        if session:
            repo = DocumentRepository(session)
            query_emb = embedding_service.generate_embedding("summarize these documents")
            results = repo.search_similar_chunks(state["user_id"], query_emb, state.get("document_ids"))
            context = "\n\n".join([c.content for c, d in results])

    prompt = f"Summarize the following content concisely:\n\n{context}"
    summary = await llm.generate(prompt, system_prompt="You are an expert summarizer.")

    return {**state, "generated_content": summary}

async def generate_quiz(state: AgentState):
    print("--- GENERATING QUIZ ---")
    llm = get_llm_provider()

    context = "\n\n".join(state.get("retrieved_chunks", []))
    prompt = f"Generate a 3-question multiple choice quiz based on this content:\n\n{context}"
    quiz = await llm.generate(prompt, system_prompt="You are a pedagogical expert.")

    return {**state, "generated_content": quiz}

async def validate_quiz(state: AgentState):
    print("--- VALIDATING QUIZ ---")
    llm = get_llm_provider()

    prompt = f"Verify that the following quiz is accurate and has correct answers based on general knowledge:\n\n{state['generated_content']}"
    verdict = await llm.generate(prompt, system_prompt="You are a quiz auditor. Respond with 'PASSED' or 'FAILED'.")

    passed = "PASSED" in verdict.upper()
    return {**state, "quality_passed": passed}

async def generate_flashcards(state: AgentState):
    print("--- GENERATING FLASHCARDS ---")
    llm = get_llm_provider()

    context = "\n\n".join(state.get("retrieved_chunks", []))
    prompt = f"Generate 5 front-and-back flashcards based on this content:\n\n{context}"
    cards = await llm.generate(prompt, system_prompt="You are a flashcard generator.")

    return {**state, "generated_content": cards}

async def generate_study_plan(state: AgentState):
    print("--- GENERATING STUDY PLAN ---")
    llm = get_llm_provider()

    context = "\n\n".join(state.get("retrieved_chunks", []))
    prompt = f"Create a structured study plan for a student based on this content:\n\n{context}"
    plan = await llm.generate(prompt, system_prompt="You are an academic advisor.")

    return {**state, "generated_content": plan}

async def persist_result(state: AgentState):
    print("--- PERSISTING RESULT ---")
    return state

async def safe_fallback(state: AgentState):
    print("--- SAFE FALLBACK ---")
    return {**state, "generated_content": "I'm sorry, I couldn't process that request. Please try again or refine your question."}

# --- Routing Logic ---

def route_by_intent(state: AgentState):
    intent = state.get("intent")
    if intent == "rag":
        return "retrieve_context"
    elif intent == "summary":
        return "generate_summary"
    elif intent == "quiz":
        return "generate_quiz"
    elif intent == "flashcards":
        return "generate_flashcards"
    elif intent == "study_plan":
        return "generate_study_plan"
    else:
        return "safe_fallback"

def verify_route(state: AgentState):
    if state.get("quality_passed"):
        return "persist_result"
    if state.get("retry_count", 0) < 3:
        return "generate_answer"
    return "safe_fallback"

# --- Graph Construction ---

def create_studypilot_graph():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("load_context", load_context)
    workflow.add_node("validate_request", validate_request)
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("retrieve_context", retrieve_context)
    workflow.add_node("generate_answer", generate_answer)
    workflow.add_node("verify_answer", verify_answer)
    workflow.add_node("generate_summary", generate_summary)
    workflow.add_node("generate_quiz", generate_quiz)
    workflow.add_node("validate_quiz", validate_quiz)
    workflow.add_node("generate_flashcards", generate_flashcards)
    workflow.add_node("generate_study_plan", generate_study_plan)
    workflow.add_node("persist_result", persist_result)
    workflow.add_node("safe_fallback", safe_fallback)

    # Set Entry Point
    workflow.set_entry_point("validate_request")

    # Edges
    workflow.add_edge("validate_request", "load_context")
    workflow.add_edge("load_context", "classify_intent")

    # Intent Routing
    workflow.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "retrieve_context": "retrieve_context",
            "generate_summary": "generate_summary",
            "generate_quiz": "generate_quiz",
            "generate_flashcards": "generate_flashcards",
            "generate_study_plan": "generate_study_plan",
            "safe_fallback": "safe_fallback"
        }
    )

    # RAG Workflow
    workflow.add_edge("retrieve_context", "generate_answer")
    workflow.add_edge("generate_answer", "verify_answer")
    workflow.add_conditional_edges(
        "verify_answer",
        verify_route,
        {
            "persist_result": "persist_result",
            "generate_answer": "generate_answer",
            "safe_fallback": "safe_fallback"
        }
    )

    # Other Workflows
    workflow.add_edge("generate_summary", "persist_result")
    workflow.add_edge("generate_quiz", "validate_quiz")
    workflow.add_edge("validate_quiz", "persist_result")
    workflow.add_edge("generate_flashcards", "persist_result")
    workflow.add_edge("generate_study_plan", "persist_result")

    workflow.add_edge("safe_fallback", END)
    workflow.add_edge("persist_result", END)

    return workflow.compile()
