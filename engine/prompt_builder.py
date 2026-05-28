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
    Builds a compressed system prompt optimized for smaller models.
    Uses instruction-dense language, minimal explanation, tight formatting rules.
    """
    lang = LANGUAGE_REGISTRY.get(industry, LANGUAGE_REGISTRY["Business Services"])

    # Sample from registry to keep prompt fresh across generations
    problem_terms = random.sample(lang["problem_language"], min(3, len(lang["problem_language"])))
    symptoms = random.sample(lang["operational_symptoms"], min(3, len(lang["operational_symptoms"])))
    solution_terms = random.sample(lang["solution_language"], min(3, len(lang["solution_language"])))
    outcome_terms = random.sample(lang["outcome_language"], min(3, len(lang["outcome_language"])))
    markers = random.sample(lang["value_markers"], min(3, len(lang["value_markers"])))

        # Tone instruction mapping with fallback
    tone_instructions = {
        "Executive": "Write with confident authority. Concise sentences. Direct recommendations. No hedging.",
        "Formal": "Write with structured precision. Proper business English. Reserved and professional tone.",
        "Persuasive": "Write with conviction. Lead with value. Frame everything around outcomes and urgency.",
        "Technical": "Write with analytical depth. Use precise terminology. Emphasize methodology and process."
    }
    tone_instruction = tone_instructions.get(tone, "Write with confident authority. Concise sentences. Direct recommendations.")

    # Dynamic section list for OUTPUT FORMAT
    if sections is None:
        sections = [
            "Executive Summary", "Understanding Your Situation",
            "Proposed Solution", "Scope of Work", "Timeline",
            "Investment & Value Justification", "Next Steps", "Follow-Up Message"
        ]

    # Full instructions for each section type
    section_templates = {
        "Executive Summary": "2-3 paragraphs. First paragraph: Anchor in the client's specific situation and industry context — make them feel seen. Do not start with \"This proposal outlines...\" Start with what's at stake for them specifically. Second paragraph: Credibility anchor (methodology, relevant expertise). Third: Immediate value statement — what changes for them if they say yes.",
        "Understanding Your Situation": "2-3 paragraphs. Frame current reality and cost of inaction. Use symptom language.",
        "Proposed Solution": "Structured as: Objectives, Approach, Deliverables. Be specific. No vagueness.",
        "Scope of Work": "Bulleted list. Clear boundaries. What's included and what's not.",
        "Timeline": "Phased breakdown with durations. Link phases to deliverables.",
        "Investment & Value Justification": "Frame cost as investment. Compare the investment against the cost of inaction using concrete logic (e.g., \"If the client loses X deals, the cost of inaction exceeds this investment Y times over\"). Connect to specific outcomes from the value indicators provided. Do not include a specific price unless one was provided.",
        "Next Steps": "Specific, low-friction call to action. Single clear action the client can take today.",
        "Follow-Up Message": f"A follow-up email template the user can send after delivering this proposal. Requirements:\n- Reference one specific insight from the proposal (e.g., a finding from the situation analysis or a specific deliverable)\n- Suggest a concrete next action tied to the proposed engagement (e.g., a diagnostic workshop, a call to discuss a specific deliverable, not a generic \"let's discuss\")\n- Keep it under 150 words\n- Match the {tone} tone\n- Include [Client Name], [Date], [Your Name] placeholders\n- Do not use \"I hope this finds you well\" or similar boilerplate openings",
    }

    # Build only the selected sections
    selected_blocks = []
    for s in sections:
        if s in section_templates:
            selected_blocks.append(f"## {s}\n{section_templates[s]}")

    section_format_block = "\n\n".join(selected_blocks)

    system_prompt = f"""You are a {industry} proposal strategist. {tone_instruction}

INDUSTRY CONTEXT:
- Problem domain: {', '.join(problem_terms)}
- Observable symptoms: {', '.join(symptoms)}
- Solution approaches: {', '.join(solution_terms)}
- Target outcomes: {', '.join(outcome_terms)}
- Value indicators: {', '.join(markers)}

PROPOSAL TYPE: {proposal_type}

STRUCTURAL RULES (mandatory):
1. CREDIBILITY BLOCK: Open with a brief statement anchoring this proposal in the sender's specific credentials provided. If credentials were provided, use them directly. If not, anchor in the sender's firm name and industry expertise. Reference the sender by name. Do not fabricate client names or case studies. Vary your opening sentence across generations. Do not use cliché phrases like "faces a critical juncture," "at a crossroads," or "in today's rapidly changing landscape." Lead with a specific observation about the client's situation.
2. COST OF INACTION: Before presenting solutions, articulate what the client loses by maintaining the status quo. Use the operational symptoms provided. Be specific, not alarmist.
3. STRUCTURED OFFER: Present the solution as a clearly defined scope. Specify deliverables, approach, and format. No vague descriptions.
4. IMMEDIATE VALUE: Link the investment to observable near-term outcomes. Reference the value indicators where relevant.
5. LOW-RISK NEXT STEP: End with a contained, low-friction call to action. Suggest a diagnostic, a call, or a phased first step. Create urgency without pressure.

OUTPUT FORMAT:
Generate exactly these sections with markdown headers (##). Only generate the sections listed below. Do not add extra sections.

{section_format_block}

CONSTRAINTS:
- Do not invent numerical results, percentages, case studies, or historical facts.
- Do not fabricate client names, project references, or past engagements.
- If context is missing, state reasonable assumptions explicitly (e.g., "Assuming a mid-sized team...").
- No marketing fluff. No buzzwords without substance. No emojis.
- Output must be complete, not truncated.
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
        client = genai.Client()
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
            max_output_tokens=8000,
            top_p=0.9,
        )

        for model_name in models_to_try:
            # Dynamically update UI based on which model is spinning up!
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
                    response = client.models.generate_content(
                        model=model_name, contents=user_prompt, config=config
                    )
                    return response.text

                except Exception as e:
                    if "503" in str(e):
                        if attempt == 0:
                            time.sleep(2)
                            continue
                        break # Step down to 2.5 Flash
                    return f"API Error: {str(e)[:300]}"

        return "API Error: All Gemini engine lines are heavily loaded right now."
    except Exception as e:
        return f"Initialization Error: {str(e)[:300]}"

def generate_proposal(industry, proposal_type, tone, sender_name, sender_credentials,
                      client_name, client_problem, deliverables, budget_range, timeline, sections, status_ui):

    system_prompt = build_system_prompt(industry, proposal_type, tone, sections)
    user_prompt = build_user_prompt(sender_name, sender_credentials, client_name, client_problem, deliverables, budget_range, timeline)
    
    # Pass the UI controller down to the network call
    proposal = call_gemini(system_prompt, user_prompt, status_ui)
    return proposal