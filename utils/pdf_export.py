"""
ProposalOS PDF Export
Converts generated Markdown proposals into consultant-grade PDF documents
using WeasyPrint with an HTML/CSS template.
Red/gold brand system throughout.
"""

from datetime import datetime
from io import BytesIO
import os
import re
from weasyprint import HTML


# ── Template Path ────────────────────────────────────
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "proposal_template.html")


# ── Markdown to HTML Parser ──────────────────────────

def parse_markdown_to_html(proposal_text):
    """
    Parses Markdown proposal text into HTML blocks for the template.
    Stops parsing when it hits the Follow-Up Message section.
    
    Returns a string of HTML.
    """
    lines = proposal_text.strip().split("\n")
    html_blocks = []
    current_bullets = []
    skip_section = False

    def flush_bullets():
        nonlocal current_bullets
        if current_bullets:
            items = "\n".join(
                f"<li>{clean_inline_markdown(item)}</li>"
                for item in current_bullets
            )
            html_blocks.append(f'<ul class="bullet-list">\n{items}\n</ul>')
            current_bullets = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            flush_bullets()
            continue

        # Stop at Follow-Up Message — not included in PDF
        if stripped.startswith("## Follow-Up Message") or stripped.startswith("## Follow-Up"):
            flush_bullets()
            skip_section = True
            break

        # Section headers: ## Header
        if stripped.startswith("## "):
            flush_bullets()
            title = stripped.replace("## ", "").strip()
            html_blocks.append(f"""
<div class="section-block">
  <div class="section-top-rule"></div>
  <div class="section-title">{title}</div>
  <div class="section-bottom-rule"></div>
</div>""")
            continue

        # Sub-headers: ### Header
        if stripped.startswith("### "):
            flush_bullets()
            title = stripped.replace("### ", "").strip()
            html_blocks.append(f'<div class="subheader">{title}</div>')
            continue

        # Bullet points: - text or * text
        if stripped.startswith("- ") or stripped.startswith("* "):
            bullet_text = stripped[2:].strip()
            current_bullets.append(bullet_text)
            continue

        # Standalone bold lines: **text**
        if stripped.startswith("**") and stripped.endswith("**"):
            flush_bullets()
            text = stripped[2:-2].strip()
            html_blocks.append(f'<p class="body-bold">{text}</p>')
            continue

        # Regular body text
        flush_bullets()
        html_blocks.append(f'<p class="body-text">{stripped}</p>')

    flush_bullets()
    return "\n".join(html_blocks)


def clean_inline_markdown(text):
    """
    Strips inline Markdown formatting that doesn't translate to PDF.
    Removes **bold** markers — the body-text CSS handles weight.
    Removes *italic* markers.
    """
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    return text


# ── Main Generator ───────────────────────────────────

def generate_pdf(proposal_text, client_name="Client", proposal_type="Business Proposal", sender_name=""):
    """
    Generates a consultant-grade branded PDF from proposal text.
    
    Args:
        proposal_text: Markdown-formatted proposal from the AI
        client_name: Client name for the cover page
        proposal_type: Engagement type for the cover title
        sender_name: Sender firm name for the cover page
    
    Returns:
        bytes: PDF file as bytes for Streamlit's download_button
    """
    content_html = parse_markdown_to_html(proposal_text)

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    html = template.replace("{{PROPOSAL_TYPE}}", proposal_type.upper())
    html = html.replace("{{CLIENT_NAME}}", client_name)
    html = html.replace("{{DATE}}", datetime.now().strftime("%B %d, %Y"))
    html = html.replace("{{CONTENT}}", content_html)

    # Handle sender line — show if provided, hide if not
    if sender_name.strip():
        sender_html = f'<div class="cover-label">Prepared by</div><div class="cover-sender">{sender_name}</div>'
    else:
        sender_html = ""
    html = html.replace("{{SENDER}}", sender_html)

    buf = BytesIO()
    HTML(string=html).write_pdf(buf)
    return buf.getvalue()