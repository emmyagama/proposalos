"""
ProposalOS Prompt Builder
Assembles system and user prompts using the language registry,
calls OpenRouter, and returns structured proposals.
"""

import random
import requests
import streamlit as st
from config.language_registry import LANGUAGE_REGISTRY


def build_system_prompt(industry, proposal_type, tone, sections=None):
    """
    Builds a cleaner, more effective system prompt optimized for Gemini.
    """
    lang = LANGUAGE_REGISTRY.get(industry, LANGUAGE_REGISTRY["Business Services"])

    # Sample fresh language
    problem_terms = random.sample(lang["problem_language"], min(3, len(lang["problem_language"])))
    symptoms = random.sample(lang["operational_symptoms"], min(3, len(lang["operational_symptoms"])))
    solution_terms = random.sample(lang["solution_language"], min(3, len(lang["solution_language"])))
    outcome_terms = random.sample(lang["outcome_language"], min(3, len(lang["outcome_language"])))
    markers = random.sample(lang["value_markers"], min(3, len(lang["value_markers"])))

    # ==================== TONE INSTRUCTIONS ====================
    tone_instructions = {
        "Executive": "Write with sharp, confident, executive presence. Start with a bold, debatable claim. Use short, authoritative sentences. Be direct and high-signal. The first sentence of the Executive Summary MUST be a thematic, memorable statement about business value — not about what the client is doing wrong. Pattern: '[Business truth].' Then the second sentence introduces the client's specific situation.",
        
        "Formal": "Use professional, grammatically perfect language. No contractions. No sentence fragments. Clear, structured, and objective.",
        
        "Persuasive": "Frame problems as missed opportunities. Emphasize tangible benefits and outcomes. Use confident, action-oriented language.",
        
        "Technical": "Be precise and evidence-based. Tie every claim to observable operational effects. Define terms clearly. Avoid fluff and metaphors.",
        
        "Concise": "Be extremely brief and high-signal. Cut every unnecessary word. Maximum clarity with minimal text."
    }

    tone_instruction = tone_instructions.get(tone, tone_instructions["Executive"])

    # Default sections
    if sections is None:
        sections = [
            "Executive Summary", "Understanding Your Situation", "Proposed Solution",
            "Scope of Work", "Timeline", "Investment & Value Justification",
            "Next Steps", "Follow-Up Message"
        ]

    section_templates = {
        "Executive Summary": "2-3 paragraphs. Open with sender credibility. State the core problem and proposed outcome. Punchy close.",
        "Understanding Your Situation": "2-3 paragraphs. Open by linking to the core recommendation. Describe what's happening using concrete symptoms. Show what's at stake. Use the symptom language. Include one expert observation about the type of problem being addressed; the observation should - explain why the problem commonly occurs, explain what organizations often misdiagnose, explain why the proposed methodology is appropriate; the observation must be based on general consulting experience. Do not invent facts about the client. Every observation should support a specific argument for change.",
        "Proposed Solution": "Open by restating the recommendation. Then structure as three supporting arguments: what we'll do, how we'll do it, what you'll receive. Each argument should connect to a specific problem from the previous section. Be specific about deliverables. Avoid stacked jargon.",
        "Scope of Work": "Bulleted list. Clear boundaries — what's included and what's not. Short phrases.",
        "Timeline": "Phased breakdown with durations. Link phases to deliverables.",
        "Investment & Value Justification": "Frame cost as investment. Connect to outcomes. Reference the cost of inaction. Each value claim should tie back to an argument made in the Solution section. For diagnostic engagements, DO NOT promise business outcomes; Promise:, clarity, prioritization, risk visibility, decision support",
        "Next Steps": "One specific, low-friction action. One sentence.",
        "Follow-Up Message": f"Three sentences maximum. Sentence 1: Reference the attached proposal. Sentence 2: One-line value reminder. Sentence 3: Specific next step with date. Include [Client Name] and [Date] placeholders. Sound like a person following up, not a summary of the proposal.",
    }

    selected_blocks = [f"## {s}\n{section_templates[s]}" for s in sections if s in section_templates]
    section_format_block = "\n\n".join(selected_blocks)

    # ==================== MAIN SYSTEM PROMPT ====================
    system_prompt = f"""You are a seasoned {industry} consultant writing high-quality MBB-style proposals.

    **PROPOSAL TYPE**: {proposal_type}

HIGHEST PRIORITY RULES (Never violate these):
- Write like an experienced human consultant — natural, confident, and professional.
- Never use these words: synergy, leverage, optimize, ecosystem, paradigm, we believe, we think.
- Do not invent numerical results, percentages, multipliers, salary figures, or historical facts. If citing an industry statistic, attribute it to its source or say "industry research suggests".
- Every section MUST open with a positive, forward-looking statement about what is possible — not a critique of what the client is failing at."
- PYRAMID STRUCTURE - Lead with the conclusion, then support it. The Executive Summary states the single core recommendation. Every subsequent section opens with a sentence that ties back to that recommendation. Group supporting arguments in sets of three where natural. When presenting data or observations, explicitly state which argument they support — do not leave evidence floating without context.
- Anchor the opening with the sender's real credentials.
- Any claim about the client's current operations must be attributed to one of (use no more than two of these across the entire proposal): 
  • preliminary scoping conversations,
  • public information,
  • From initial discussions,
  • Our early read suggests,
  • Pending deeper analysis,
  • Initial indicators point to, or
  • We'll validate this during the diagnostic phase.

**PROHIBITED** (Strictly avoid):
- Opening devices: "Consider a typical scenario", "Picture this", "Imagine", "Let's be clear", "The hard truth is"
- Sentence structure: The pattern "X is not Y; it is Z" or "not X but Y"
- Adverbs: silently, simply, literally, virtually
- Negative comments about client's talent, people, or culture (e.g. high turnover, poor hires, skill gaps) unless the client explicitly stated it in the input
- Vague phrases: "marketing spend is wasted", "impacts the bottom line", "creates friction", "leads to inefficiency" — unless immediately followed by a specific mechanism (e.g. "...by [specific mechanism]")

**HYPOTHESIS REQUIREMENT** (Mandatory - include exactly ONE):
You must include exactly one clear hypothesis statement in either the Executive Summary or Proposed Solution section.

Use the format that best matches the proposal type:
- If "Diagnostic" or "Assessment" appears in proposal type: 
  "Our hypothesis is that [specific cause of the problem]. We will test this by [measurable method]."
- If "Solution", "Implementation", or "Transformation" appears: 
  "Our hypothesis is that [our solution] will produce [specific measurable outcome] within [timeframe]. We will track this by [measurement method]."
- If "Strategy" or "Advisory" appears (and no diagnostic): 
  "Our hypothesis is that [strategic bet] will outperform [alternative] by [specific metric]. We will validate this through [method]."
- Default (if unclear): Use the Diagnostic format.

The hypothesis must be specific and falsifiable. Avoid generic statements like "we can help you grow" or "clarity matters."

**TONE**: {tone_instruction}

**LANGUAGE STYLE**:
- Use these problem/symptom words naturally: {', '.join(problem_terms + symptoms)}
- Use these solution/outcome words: {', '.join(solution_terms + outcome_terms)}
- Value indicators: {', '.join(markers)}

**WRITING GUIDELINES**:
- Vary sentence rhythm. After every long or complex sentence (20+ words), follow with a short one (under 10 words). Avoid three long sentences in a row. Avoid three short sentences in a row.
- Keep the specific but highly concrete. Do not write like this: 'We need to optimize our digital ecosystem to enhance stakeholder engagement.' Write like this instead: 'We need to speed up our website to get more newsletter signups.'
- Downgrade corporate jargon into plain English.
- Match language density to the section (punchy in Executive Summary, more detailed in Solution).

**OUTPUT FORMAT**:
Generate **only** the sections below. Use markdown headers exactly as shown. Do not add extra sections.

{section_format_block}

**FINAL CHECK** before outputting:
- Exactly one hypothesis included in Executive Summary or Proposed Solution
- Understanding Your Situation contains one concrete example with specific actors and behaviors
- No prohibited vague phrases without specific mechanism, openings, adverbs, or talent criticism
- No un-attributed operational claims
- Natural, professional tone

Now generate the proposal following all instructions above."""
    
    return system_prompt

def build_user_prompt(sender_name, sender_credentials, client_name, client_problem, deliverables, budget_range, timeline):
    """
    Builds the user context prompt. Concise, fact-dense, no wasted tokens.
    """
    credential_line = f"Sender credentials: {sender_credentials}" if sender_credentials.strip() else "Sender credentials: Experienced consulting firm"

    user_prompt = f"""Sender: {sender_name if sender_name else 'Consulting Firm'}
{credential_line}
Client: {client_name if client_name else 'Client Organization'}
Problem: {client_problem if client_problem else 'Not specified — infer from industry context'}
Deliverables: {deliverables if deliverables else 'Not specified — propose appropriate deliverables'}
Budget: {budget_range}
Timeline: {timeline}

Generate the complete proposal following all structural rules and format specifications."""
    return user_prompt


import time

def call_gemini(system_prompt, user_prompt, status_ui):
    from google import genai
    from google.genai import types

    models_to_try = ["gemini-3.5-flash", "gemini-2.5-flash"]
    
    try:
        # 1. Initialize client ONCE at the parent level
        client = genai.Client()
        
        # 2. Configure model global token limits and temperature
        config = types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=8000,
            top_p=0.8,
        )

        for model_name in models_to_try:
            # Dynamically update UI based on which model is spinning up
            if model_name == "gemini-3.5-flash":
                status_ui.markdown(
                    '<div style="text-align:center;padding:2rem 0;">'
                    '<p style="font-size:1.1rem;color:#1a1a1a;margin-bottom:0.5rem;">Structuring your proposal...</p>'
                    '<p style="font-size:0.85rem;color:#8b8b8b;">Building an executive narrative</p>'
                    '</div>',
                    unsafe_allow_html=True,
                )
            elif model_name == "gemini-2.5-flash":
                status_ui.markdown(
                    '<div style="text-align:center;padding:2rem 0;">'
                    '<p style="font-size:1.1rem;color:#d97706;margin-bottom:0.5rem;">Optimizing structural alignment...</p>'
                    '<p style="font-size:0.85rem;color:#8b8b8b;">Ensuring consulting-grade quality (Second Pass)</p>'
                    '</div>',
                    unsafe_allow_html=True,
                )

            for attempt in range(2): 
                try:
                    # 3. Force system/user instructions structural separation explicitly inside contents
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[
                            {"role": "system", "parts": [{"text": system_prompt}]},
                            {"role": "user", "parts": [{"text": user_prompt}]}
                        ],
                        config=config
                    )
                    return response.text

                except Exception as e:
                    if "503" in str(e):
                        if attempt == 0:
                            time.sleep(2)
                            continue
                        break  # Step down to 2.5 Flash
                    return f"API Error: {str(e)[:300]}"

        return "API Error: All Gemini engine lines are heavily loaded right now."
    except Exception as e:
        return f"Initialization Error: {str(e)[:300]}"

def generate_proposal(industry, proposal_type, tone, sender_name, sender_credentials,
                      client_name, client_problem, deliverables, budget_range, timeline, sections, status_ui):
    """
    Main orchestrator. Builds prompts, calls Gemini, returns proposal text.
    """
    # 1. Pass data to build the system prompt
    system_prompt = build_system_prompt(industry, proposal_type, tone, sections)
    
    # 2. Pass data to build the user prompt
    user_prompt = build_user_prompt(sender_name, sender_credentials, client_name, client_problem, deliverables, budget_range, timeline)
    
    # 3. Pass prompts and the status_ui object down to the network call
    proposal = call_gemini(system_prompt, user_prompt, status_ui)
    
    return proposal