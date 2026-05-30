"""
ProposalOS Prompt Builder
Assembles system and user prompts using the language registry,
calls OpenRouter, and returns structured proposals.
"""

import random
import requests
import streamlit as st
from config.language_registry import LANGUAGE_REGISTRY

import random

def build_system_prompt(industry, proposal_type, tone, sections=None):
    """
    Builds a system prompt optimized for natural, human-sounding output.
    Retains dynamic section toggling for Screen 4 compatibility and 
    uses high-actionability style directives for Gemini 3.5 Flash.
    """
    lang = LANGUAGE_REGISTRY.get(industry, LANGUAGE_REGISTRY["Business Services"])

    # Sample from registry to keep prompt fresh across generations
    problem_terms = random.sample(lang["problem_language"], min(3, len(lang["problem_language"])))
    symptoms = random.sample(lang["operational_symptoms"], min(3, len(lang["operational_symptoms"])))
    solution_terms = random.sample(lang["solution_language"], min(3, len(lang["solution_language"])))
    outcome_terms = random.sample(lang["outcome_language"], min(3, len(lang["outcome_language"])))
    markers = random.sample(lang["value_markers"], min(3, len(lang["value_markers"])))

    # High-impact tone instruction mapping
    tone_instructions = {
        "Executive": "Confident and direct. Short sentences for key claims. Longer sentences for context. Lead with outcomes.",
        "Formal": "Structured and precise. Professional register without stiffness. Vary sentence length naturally.",
        "Persuasive": "Conviction without hype. Lead with value. Frame problems as opportunities. Use concrete examples.",
        "Technical": "Analytical depth with accessible language. Use precise terms but explain them through observable symptoms.",
        "Concise": "One page maximum. Bullet-heavy. Every sentence must earn its place. No explanatory prose. Critical details only.",
    }
    tone_instruction = tone_instructions.get(tone, tone_instructions['Executive'])

    # Maintain the dynamic section list fallback for Screen 4
    if sections is None:
        sections = [
            "Executive Summary", "Understanding Your Situation",
            "Proposed Solution", "Scope of Work", "Timeline",
            "Investment & Value Justification", "Next Steps", "Follow-Up Message"
        ]

    # Clean, distinct modular section definitions
    section_templates = {
        "Executive Summary": "2-3 paragraphs. Open with sender credibility. State the core problem and proposed outcome. Punchy close.",
        "Understanding Your Situation": "2-3 paragraphs. Describe what's happening using concrete symptoms. Show what's at stake. Use the symptom language. Include one specific scenario or observation.",
        "Proposed Solution": "Structured as: What we'll do, How we'll do it, What you'll receive. Be specific about deliverables. Avoid stacked jargon.",
        "Scope of Work": "Bulleted list. Clear boundaries — what's included and what's not. Short phrases.",
        "Timeline": "Phased breakdown with durations. Link phases to deliverables.",
        "Investment & Value Justification": "Frame cost as investment. Connect to outcomes. Reference the cost of inaction. Do not include a specific price unless provided.",
        "Next Steps": "One specific, low-friction action. One sentence.",
        "Follow-Up Message": f"A short, natural follow-up the sender can use after delivering the proposal. Match the {tone} tone. Include placeholders like [Client Name] and [Date]. Sound like a person, not a template.",
    }

    # Dynamically build only the user's checked sections
    selected_blocks = []
    for s in sections:
        if s in section_templates:
            selected_blocks.append(f"## {s}\n{section_templates[s]}")

    section_format_block = "\n\n".join(selected_blocks)

    # Combined master prompt string
    system_prompt = f"""You are a {industry} professional writing a corporate business proposal. {tone_instruction}

INDUSTRY LANGUAGE DESCRIPTIONS:
- Problems: {', '.join(problem_terms)}
- Observable symptoms: {', '.join(symptoms)}
- Solutions: {', '.join(solution_terms)}
- Outcomes: {', '.join(outcome_terms)}
- Value indicators: {', '.join(markers)}

PROPOSAL TYPE: {proposal_type}

HUMAN WRITING RULES (mandatory style overrides):
- SENTENCE VARIANCE: Purposely alternate your syntax. Mix short, hard-hitting declarative sentences (under 8 words) with longer, multi-clause strategic context sentences. Avoid uniform sentence length.
- LOCAL REALISM: Never use placeholder statements or abstract filler. Pick exactly one or two explicit operational realities from the symptoms list and write a deep, 2-sentence diagnostic scenario showing what that breakdown looks like on the operational floor.
- STRATEGIC REGISTERS: Match your linguistic density to the document stage. Keep the Executive Summary punchy and outcome-obsessed; switch the Problem Framing into objective, operational terminology; ensure the Solution reads with architectural confidence.
- APPLIED JARGON REVERSION: Actively downgrade common AI business clichés to direct English phrases (e.g., replace "optimize visibility" with "make it easier to track"; replace "leverage synergy" with "work together across departments").

STRUCTURAL RULES:
1. CREDIBILITY BLOCK: Open by anchoring in the sender's specific credentials. Reference the sender by name. One sentence. Do not fabricate client names or case studies.
2. COST OF INACTION: Before solutions, show what the client loses by maintaining the status quo. Use specific observable symptoms, not abstract risk categories.
3. STRUCTURED OFFER: Present the solution with clear deliverables and approach. Be specific about what changes and how.
4. IMMEDIATE VALUE: Link the investment to near-term observable outcomes. Reference value indicators.
5. LOW-RISK NEXT STEP: End with a contained, specific next action. One sentence.

OUTPUT FORMAT — generate exactly these sections with markdown headers (##):
Only generate the sections listed below. Do not add extra sections.

{section_format_block}

CONSTRAINTS:
- Do not invent numerical results, percentages, case studies, or historical facts.
- Do not fabricate client names, project references, or past engagements.
- If context is missing, state reasonable assumptions explicitly.
- No marketing fluff. No buzzwords without substance. No emojis.
- Output must be complete and formatted entirely in Markdown text.
"""
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
    import time

    models_to_try = ["gemini-3.5-flash", "gemini-2.5-flash"]
    
    try:
        # 1. Initialize client ONCE at the parent level
        client = genai.Client()
        
        # 2. Configure model global token limits and temperature
        config = types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=8000,
            top_p=0.9,
        )

        for model_name in models_to_try:
            # Dynamically update UI based on which model is spinning up
            if model_name == "gemini-3.5-flash":
                status_ui.markdown(
                    '<div style="text-align:center;padding:2rem 0;">'
                    '<p style="font-size:1.1rem;color:#1a1a1a;margin-bottom:0.5rem;">Structuring your proposal...</p>'
                    '<p style="font-size:0.85rem;color:#8b8b8b;">Building an executive narrative with Gemini 3.5</p>'
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