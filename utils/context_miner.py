import re
import pypdf

def mine_file_context(uploaded_file, industry, proposal_type):
    """
    Algorithmic Context Miner (No AI tokens used).
    Parses PDFs/TXT briefs and extracts ALL constraint-rich sentences.
    """
    if uploaded_file is None:
        return ""

    # EXPANDED keyword set - includes RFP-specific terms
    target_keywords = {
        # Mandatory/requirement words
        "must", "require", "shall", "mandatory", "required", "must be",
        # Scope words  
        "deliverable", "timeline", "deadline", "milestone", "objective", 
        "scope", "problem", "bottleneck", "work package", "wp",
        # RFP-specific words
        "kpi", "key performance indicator", "evaluation", "criteria",
        "budget", "cap", "capped at", "total budget",
        "team", "composition", "cvs", "qualification", "expert",
        "eligibility", "registered", "legal entity", "years",
        "submission", "deadline", "email", "subject line",
        "technical proposal", "financial proposal", "separate document",
        # Industry/context words from your selection
        "youth", "entrepreneurship", "esg", "incubation", "mentorship",
        "southwest", "south-south", "niger delta", "nigeria"
    }
    
    # Extract structural keywords from user's Screen 1 choices
    for word in re.findall(r'\w+', f"{industry} {proposal_type}".lower()):
        if len(word) > 3:  
            target_keywords.add(word)

    raw_text = ""
    try:
        if uploaded_file.name.endswith('.txt'):
            raw_text = str(uploaded_file.read(), "utf-8")
        elif uploaded_file.name.endswith('.pdf'):
            pdf_reader = pypdf.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    raw_text += text + "\n"

        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', raw_text)
        
        scored_sentences = []
        for sentence in sentences:
            clean_sentence = sentence.strip()
            if len(clean_sentence.split()) < 5:
                continue
                
            score = 0
            lower_sentence = clean_sentence.lower()
            
            for keyword in target_keywords:
                if keyword in lower_sentence:
                    # Higher weight for critical RFP sections
                    if keyword in ["must", "require", "shall", "mandatory", "deadline", "budget", "cap", "kpi", "cvs", "wp", "work package"]:
                        score += 3  # Triple weight for requirements
                    elif keyword in ["deliverable", "timeline", "scope", "evaluation", "criteria", "team", "qualification"]:
                        score += 2  # Double weight for structure
                    else:
                        score += 1
            
            # Boost score for sentences containing numbers (budgets, dates, years)
            if re.search(r'\$\d+', clean_sentence):  # Dollar amounts
                score += 5
            if re.search(r'\d+\s*(years?|months?|weeks?)', clean_sentence, re.IGNORECASE):  # Time periods
                score += 3
            if re.search(r'[0-9]{1,2}%', clean_sentence):  # Percentages (evaluation weights)
                score += 3
            
            if score > 0:
                scored_sentences.append((score, clean_sentence))

        # Sort by highest score
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        
        # INCREASE from 35 to 60 sentences to capture more context
        top_slices = [item[1] for item in scored_sentences[:60]]
        
        # Add a header to help the LLM understand this is an RFP
        extracted_brief = "=== OFFICIAL RFP / CLIENT BRIEF ===\n"
        extracted_brief += "The following are extracted requirements from the client's official document:\n\n"
        extracted_brief += "\n".join(f"- {s}" for s in top_slices)
        extracted_brief += "\n\n=== END OF EXTRACTED REQUIREMENTS ==="
        
        return extracted_brief

    except Exception as e:
        return f"[Context Extraction Note: Limited data captured due to formatting layout - {str(e)[:40]}]"