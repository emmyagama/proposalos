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
        
        "Concise": "One page maximum (400 - 500 words). Be extremely brief and high-signal. Cut every unnecessary word. Maximum clarity with minimal text."
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
        "Proposed Solution": "Open by restating the recommendation. Then structure as three supporting arguments using the headers: what we'll do, how we'll do it, what you'll receive. Each argument should connect to a specific problem from the previous section. For the How we'll do it and What you'll receive sections, break the details down into a clean, bulleted list. Ensure the deliverables are highly specific, tangible, and free of stacked jargon. Do not merge these sections into standard text paragraphs",
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

def build_user_prompt(sender_name, sender_credentials, client_name, client_problem, deliverables, budget_range, timeline, mined_brief=""):
    """
    Builds the user context prompt. If mined_brief contains an RFP, it takes priority.
    """
    credential_line = f"Sender credentials: {sender_credentials}" if sender_credentials.strip() else "Sender credentials: Experienced consulting firm"
    
    # Check if we have substantial RFP content (more than just a few words)
    has_rfp = mined_brief and len(mined_brief.strip()) > 200

    # Debug - remove after testing
    if mined_brief:
        print(f"📄 Mined brief length: {len(mined_brief)} chars")
        if len(mined_brief) < 500:
            print(f"⚠️ WARNING: Mined brief seems short! Content: {mined_brief[:200]}")
    
    if has_rfp:
        # RFP MODE - The uploaded document is the primary source
        user_prompt = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║  OFFICIAL CLIENT DOCUMENT / REQUEST FOR PROPOSAL (RFP)                     ║
║  THIS IS THE AUTHORITATIVE SOURCE - FOLLOW IT EXACTLY                      ║
╚════════════════════════════════════════════════════════════════════════════╝

{mined_brief}

╔════════════════════════════════════════════════════════════════════════════╗
║  WHO IS RESPONDING (Your firm identity)                                    ║
╚════════════════════════════════════════════════════════════════════════════╝

Sender: {sender_name if sender_name else 'Consulting Firm'}
{credential_line}
Client: {client_name if client_name else 'Client Organization'}

╔════════════════════════════════════════════════════════════════════════════╗
║  CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE EXACTLY                     ║
╚════════════════════════════════════════════════════════════════════════════╝

1. IGNORE the "Manual Problem Description" below - the RFP above is the REAL requirement
2. Extract ALL requirements from the RFP: timeline, budget, audience, deliverables, scope
3. Do NOT change the program duration - use exactly what the RFP specifies
4. Do NOT change the target audience - use exactly who the RFP is for
5. Use the client's terminology and vocabulary from the RFP
6. Address EVERY work package and deliverable listed in the RFP

╔════════════════════════════════════════════════════════════════════════════╗
║  MANUAL INPUT - IGNORE IF CONTRADICTS THE RFP ABOVE                        ║
╚════════════════════════════════════════════════════════════════════════════╝

Manual Problem Description (IGNORE): {client_problem if client_problem else 'Not specified'}
Manual Deliverables (IGNORE if RFP has different ones): {deliverables if deliverables else 'Not specified'}
Manual Budget (USE THE RFP'S BUDGET INSTEAD): {budget_range}
Manual Timeline (USE THE RFP'S TIMELINE INSTEAD): {timeline}

╔════════════════════════════════════════════════════════════════════════════╗
║  YOUR TASK                                                               ║
╚════════════════════════════════════════════════════════════════════════════╝

Write a professional proposal responding DIRECTLY to the RFP at the top of this prompt.
The proposal should be tailored for {client_name}.
"""
    else:
        # NORMAL MODE - No RFP, use manual inputs
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
    import streamlit as st
    import re

    # Correct model names as of June 2026
    # Note: gemini-2.0-flash was discontinued March 31, 2026
    # Note: gemini-3-flash doesn't exist - correct name is gemini-3-flash-preview
    models_to_try = [
        "gemini-3.5-flash",      # Best quality, GA (May 2026)
        "gemini-3-flash-preview", # Preview version, works but not GA
        "gemini-2.5-flash",       # Stable fallback, GA
        "gemini-2.5-flash-lite"   # Lightweight last resort, GA
    ]
    
    # User-friendly status messages - never mention fallback or downgrade
    status_messages = {
        0: {  # gemini-3.5-flash
            "main": "Processing your request...",
            "sub": "Analyzing requirements and structuring content"
        },
        1: {  # gemini-3-flash-preview
            "main": "Still working on your proposal...",
            "sub": "This is taking a bit longer than expected"
        },
        2: {  # gemini-2.5-flash
            "main": "Finalizing your document...",
            "sub": "Almost there, performing quality checks"
        },
        3: {  # gemini-2.5-flash-lite
            "main": "Completing your proposal...",
            "sub": "Just a moment longer"
        }
    }
    
    try:
        client = genai.Client()
        
        for model_idx, model_name in enumerate(models_to_try):
            # Update UI with user-friendly message
            msg = status_messages[model_idx]
            status_ui.markdown(
                f'<div style="text-align:center; padding:2rem 1rem; border-radius:12px; background:#fafaf8; border:1px solid #e8e5e0;">'
                f'<div class="loading-circle" style="border: 3px solid #e8e5e0; border-top: 3px solid #8B7355; border-radius: 50%; width: 24px; height: 24px; margin: 0 auto 1rem auto; animation: spin 1s linear infinite;"></div>'
                f'<p style="font-size:1.1rem; color:#1a1a1a;">{msg["main"]}</p>'
                f'<p style="font-size:0.85rem; color:#8b8b8b;">{msg["sub"]}</p>'
                f'</div>'
                f'<style>@keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}</style>',
                unsafe_allow_html=True,
            )
            
            # Try this model with retries for transient errors
            for attempt in range(2):
                try:
                    config = types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=8000,
                        top_p=0.8,
                        system_instruction=system_prompt,
                    )
                    
                    # Streaming setup for live preview
                    text_placeholder = st.empty()
                    full_response_text = ""
                    word_count = 0
                    
                    response_stream = client.models.generate_content_stream(
                        model=model_name,
                        contents=user_prompt,
                        config=config
                    )
                    
                    for chunk in response_stream:
                        if chunk.text:
                            full_response_text += chunk.text
                            word_count = len(full_response_text.split())
                            
                            # Update word count during generation
                            status_ui.markdown(
                                f'<div style="text-align:center; padding:2rem 1rem; border-radius:12px; background:#fafaf8; border:1px solid #e8e5e0;">'
                                f'<div class="loading-circle" style="border: 3px solid #e8e5e0; border-top: 3px solid #8B7355; border-radius: 50%; width: 24px; height: 24px; margin: 0 auto 1rem auto; animation: spin 1s linear infinite;"></div>'
                                f'<p style="font-size:1.1rem; color:#1a1a1a;">Writing your proposal... {word_count} words</p>'
                                f'<p style="font-size:0.85rem; color:#8b8b8b;">This may take a moment</p>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
                            
                            # Live preview of generated content
                            text_placeholder.markdown(
                                f'<div style="background:#fdfdfc; border:1px solid #e8e5e0; border-radius:10px; padding:2rem; max-height:400px; overflow-y:auto;">'
                                f'{full_response_text}'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                    
                    text_placeholder.empty()
                    return full_response_text
                    
                except Exception as e:
                    error_str = str(e)
                    
                    # Quota exhaustion (429) - move to next model
                    if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                        time.sleep(1)
                        break  # Move to next model
                    
                    # Model not found (404) - move to next model
                    elif "404" in error_str and "not found" in error_str.lower():
                        # This model doesn't exist or isn't supported
                        break  # Silently move to next model
                    
                    # Server overload (503) - retry this model
                    elif "503" in error_str:
                        if attempt == 0:
                            # Parse retry delay if available
                            match = re.search(r'retry in ([\d.]+)', error_str)
                            wait_time = float(match.group(1)) + 1 if match else 3
                            
                            status_ui.markdown(
                                f'<div style="text-align:center; padding:2rem 1rem; border-radius:12px; background:#fafaf8; border:1px solid #e8e5e0;">'
                                f'<div class="loading-circle" style="border: 3px solid #e8e5e0; border-top: 3px solid #8B7355; border-radius: 50%; width: 24px; height: 24px; margin: 0 auto 1rem auto; animation: spin 1s linear infinite;"></div>'
                                f'<p style="font-size:1.1rem; color:#1a1a1a;">High demand, retrying...</p>'
                                f'<p style="font-size:0.85rem; color:#8b8b8b;">Please wait {wait_time:.0f} seconds</p>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
                            time.sleep(wait_time)
                            continue
                        else:
                            break  # Move to next model after 2 retries
                    
                    # Rate limiting (other than 429) - move to next model
                    elif "rate" in error_str.lower() or "quota" in error_str.lower():
                        time.sleep(2)
                        break
                    
                    # Any other error - return it
                    else:
                        return f"Error: {error_str[:300]}"
        
        # All models exhausted - user-friendly message
        status_ui.error(
            "The system is currently under high load. Please try again in a few minutes."
        )
        return None
        
    except Exception as e:
        return f"System Error: {str(e)[:300]}"

def generate_proposal(industry, proposal_type, tone, sender_name, sender_credentials,
                      client_name, client_problem, deliverables, budget_range, timeline, sections, status_ui, mined_brief=""):
    
    system_prompt = build_system_prompt(industry, proposal_type, tone, sections)
    
    # Pass mined_brief into your user prompt compile logic
    user_prompt = build_user_prompt(
        sender_name, sender_credentials, client_name, client_problem, 
        deliverables, budget_range, timeline, mined_brief
    )
    
    # Pass the UI controller down to the network call
    proposal = call_gemini(system_prompt, user_prompt, status_ui)

    return proposal