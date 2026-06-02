def run_local_audit(state):
    """
    Evaluates inputs locally via structural algorithms.
    Costs 0 tokens, adds 0ms latency, and eliminates 429/503 network risks.
    """
    coaching_tips = []
    
    # 1. Evaluate Client Problem Input Depth
    problem_words = len(state.get("client_problem", "").split())
    if problem_words < 12:
        coaching_tips.append("⚠️ **Problem Description is Brief:** Consider specifying *what happens if the client maintains the status quo* to trigger stronger Cost-of-Inaction arguments in the final copy.")
        
    # 2. Evaluate Deliverables Scoping Matrix Complexity
    deliverables_list = state.get("deliverables", [])
    if len(deliverables_list) < 3:
        coaching_tips.append("⚠️ **Expand your scope:** You have selected very few deliverables. Consider adding explicit phases or milestones to provide a more thorough consulting structure.")
        
    # 3. Check for Sender Personal Credibility Elements
    credentials_text = state.get("sender_credentials", "").strip()
    if not credentials_text:
        coaching_tips.append("💡 **Missing Credibility Anchor:** Leaving your credentials blank forces the generator to be generic about you. Add a project highlight or core cert to make the opening unique.")

    return coaching_tips
