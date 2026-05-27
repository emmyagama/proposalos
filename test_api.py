"""
Temporary API test. Run with: streamlit run test_api.py
"""
import streamlit as st
from engine.prompt_builder import generate_proposal

st.title("API Test")

if st.button("Test Generation"):
    with st.spinner("Calling OpenRouter..."):
        result = generate_proposal(
            industry="Strategy Consulting",
            proposal_type="Strategy Advisory",
            tone="Executive",
            business_name="Sterling Consulting",
            client_problem="Losing deals to newer firms, pricing under pressure, no clear strategic narrative.",
            deliverables="Strategic audit, competitive positioning map, growth roadmap",
            budget_range="₦5,000,000 - ₦10,000,000",
            timeline="3 months"
        )
    st.markdown("### Result")
    st.markdown(result)