# import streamlit as st

# st.set_page_config(page_title="Banking Support Assistant", layout="centered")

# st.title("Banking Support Assistant")
# st.markdown("Start by describing your issue. The assistant will try to resolve it or escalate if needed.")

# # User input
# user_query = st.text_area(
#     "Describe your problem:",
#     placeholder="Example: I cannot log into my online banking account",
#     height=120
# )

# # Submit button
# if st.button("Submit"):
#     if not user_query.strip():
#         st.warning("Please enter a description of your issue.")
#     else:
#         # TEMPORARY PLACEHOLDER (will be replaced by L0 agent)
#         st.subheader("Assistant Response")
#         st.info(
#             "Thanks for your request. "
#             "The system will first search the knowledge base and respond if a solution is found."
#         )

#         st.markdown("**Next steps (mocked):**")
#         st.markdown(
#             "-Knowledge Base search\n"
#             "-Check previous similar issues\n"
#             "-Escalate to L1 if needed"
#         )

# import streamlit as st

# # ---------------------------------------------------
# # Page config
# # ---------------------------------------------------
# st.set_page_config(
#     page_title="Banking Support Assistant",
#     page_icon="🝦",
#     layout="centered"
# )

# # ---------------------------------------------------
# # Custom CSS (light, safe overrides)
# # ---------------------------------------------------
# st.markdown("""
# <style>
# .main {
#     background-color: #F8F9FB;
# }

# .block-container {
#     padding-top: 2rem;
#     padding-bottom: 2rem;
# }

# .issue-box {
#     background-color: #FFFFFF;
#     border-radius: 10px;
#     padding: 1.25rem;
#     border-left: 6px solid #0B5ED7;
# }

# .response-box {
#     background-color: #FFFFFF;
#     border-radius: 10px;
#     padding: 1.25rem;
#     border-left: 6px solid #198754;
# }

# .escalation-box {
#     background-color: #FFF3CD;
#     border-radius: 10px;
#     padding: 1.25rem;
#     border-left: 6px solid #FFC107;
# }

# small {
#     color: #6C757D;
# }
# </style>
# """, unsafe_allow_html=True)

# # ---------------------------------------------------
# # Header
# # ---------------------------------------------------
# st.title("🝦 Banking Support Assistant")
# st.caption(
#     "AI‑powered support assistant. "
#     "Self‑service first (L0), escalation when needed (L1)."
# )

# st.divider()

# # ---------------------------------------------------
# # User Input Section
# # ---------------------------------------------------
# st.subheader("📝 Describe your issue")

# st.markdown(
#     "<small>Please describe your problem in your own words. "
#     "The assistant will first search the knowledge base.</small>",
#     unsafe_allow_html=True
# )

# user_query = st.text_area(
#     label="",
#     placeholder="Example: I cannot log into my online banking account",
#     height=120
# )

# submit = st.button("🚀 Submit request")

# # ---------------------------------------------------
# # Processing Logic (mocked for now)
# # ---------------------------------------------------
# if submit:
#     if not user_query.strip():
#         st.warning("⚠︝ Please enter a description of your issue.")
#     else:
#         # Display user issue
#         st.markdown("### 📌 Your request")
#         st.markdown(
#             f"""
#             <div class="issue-box">
#                 <strong>User description</strong><br/>
#                 {user_query}
#             </div>
#             """,
#             unsafe_allow_html=True
#         )

#         st.divider()

#         # Simulated L0 behavior (placeholder)
#         st.markdown("### 🤖 Assistant response (L0 Agent)")

#         st.markdown(
#             """
#             <div class="response-box">
#                 <strong>Possible resolution found</strong><br/><br/>
#                 ✅ <b>Issue identified:</b> Authentication problem related to login credentials.<br/>
#                 🔧 <b>Recommended actions:</b>
#                 <ul>
#                     <li>Reset your password</li>
#                     <li>Verify keyboard language and Caps Lock</li>
#                     <li>Enable MFA if not already active</li>
#                 </ul>
#                 📊 <b>Confidence:</b> High
#             </div>
#             """,
#             unsafe_allow_html=True
#         )

#         # Simulated escalation indicator
#         st.markdown("### ⬆︝ Escalation status")

#         st.markdown(
#             """
#             <div class="escalation-box">
#                 ⚠︝ <b>Escalation condition met</b><br/><br/>
#                 This issue matches known patterns but requires technical verification.<br/>
#                 The case would be escalated to <b>L1 Technical Support</b> with full context if unresolved.
#             </div>
#             """,
#             unsafe_allow_html=True
#         )

#         st.divider()

#         st.caption(
#             "🔒 Your request is processed securely. "
#             "No sensitive data is stored in the interface."
#         )
import sys
from pathlib import Path

# Add project root to Python path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

import streamlit as st
from multi_agent.l0.l0_agent import L0Agent
from azure_chat_llm import AzureChatLLM

# ---------------------------------------------------
# Page config
# ---------------------------------------------------
st.set_page_config(
    page_title="Banking Support Assistant",
    page_icon="🝦",
    layout="centered"
)

# ---------------------------------------------------
# Custom CSS
# ---------------------------------------------------
st.markdown("""
<style>
.response-box {
    background-color: #FFFFFF;
    border-radius: 10px;
    padding: 1.25rem;
    border-left: 6px solid #198754;
}
.escalation-box {
    background-color: #FFF3CD;
    border-radius: 10px;
    padding: 1.25rem;
    border-left: 6px solid #FFC107;
}
.issue-box {
    background-color: #FFFFFF;
    border-radius: 10px;
    padding: 1.25rem;
    border-left: 6px solid #0B5ED7;
}
small { color: #6C757D; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Initialize L0 Agent (cached)
# ---------------------------------------------------
@st.cache_resource
def init_l0_agent():
    llm = AzureChatLLM()
    return L0Agent(
        llm=llm,
        kb_path="knowledge_base/it_support_kb.md"
    )

l0_agent = init_l0_agent()

# ---------------------------------------------------
# Header
# ---------------------------------------------------
st.title("🝦 Banking Support Assistant")
st.caption(
    "AI-powered self‑service support (L0). "
    "Issues are escalated to technical support (L1) when needed."
)

st.divider()

# ---------------------------------------------------
# User Input
# ---------------------------------------------------
st.subheader("📝 Describe your issue")

user_query = st.text_area(
    label="",
    placeholder="Example: I cannot log into my online banking account",
    height=120
)

submit = st.button("🚀 Submit request")

# ---------------------------------------------------
# L0 Processing & Visualization
# ---------------------------------------------------
if submit:
    if not user_query.strip():
        st.warning("⚠︝ Please enter a description of your issue.")
    else:
        # --- Show user query ---
        st.markdown("### 📌 Your request")
        st.markdown(
            f"<div class='issue-box'>{user_query}</div>",
            unsafe_allow_html=True
        )

        st.divider()

        # --- Call L0 Agent ---
        with st.spinner("🤖 L0 Agent is analyzing your request..."):
            l0_result = l0_agent.handle(user_query)

        decision = l0_result["decision"]

        # ---------------------------------------------------
        # L0 Answer Case
        # ---------------------------------------------------
        if decision == "answer":
            st.markdown("Issue resolved by L0 Agent")

            st.markdown(
                f"""
                <div class="response-box">
                    <strong>Proposed solution</strong><br/><br/>
                    {l0_result["response"]}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.success("This issue was resolved using the knowledge base.")

        # ---------------------------------------------------
        # L0 Escalation Case
        # ---------------------------------------------------
        else:
            st.markdown("Escalation to Technical Support (L1)")

            st.markdown(
                """
                <div class="escalation-box">
                    <strong>Escalation required</strong><br/><br/>
                    The assistant could not confidently resolve this issue using
                    known solutions and previous cases.<br/><br/>
                    Your request is ready to be escalated to L1 technical support
                    with full context.
                </div>
                """,
                unsafe_allow_html=True
            )

            # Optional transparency
            with st.expander("Why was this escalated?"):
                st.write(l0_result["reason"])
                st.write("Memory matches:", l0_result["memory_matches"])

        st.divider()
        st.caption("Your request has been processed securely.")