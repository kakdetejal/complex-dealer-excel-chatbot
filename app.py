import pandas as pd
import streamlit as st
from excel_parser import load_all_sheets
from query_handler import detect_intent, handle_calculation
from llm import generate_answer
import re

st.set_page_config(page_title="Chat with your AI Assistant", page_icon=":robot:")
st.title("Chat with your AI Assistant :robot:")

file_path = "data/Complex Dealer Input.xlsx"

# -----------------------------
# SESSION STATE INITIALIZATION
# -----------------------------
if "sheets" not in st.session_state:
    st.session_state.sheets = load_all_sheets(file_path)
    st.success("Data loaded successfully!")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_query" not in st.session_state:
    st.session_state.last_query = ""

if "selected_chat" not in st.session_state:
    st.session_state.selected_chat = None

sheets = st.session_state.sheets

# -----------------------------
# FOLLOW-UP DETECTION
# -----------------------------
def is_followup(query):
    query_lower = query.lower().strip()

    followup_starters = [
        "what about", "and", "also", "then", "only", "same",
        "for that", "for this", "that", "this", "those", "it"
    ]

    if any(query_lower.startswith(k) for k in followup_starters):
        return True

    if len(query.split()) <= 3:
        return True

    return False


def build_full_query(current_query):
    last_query = st.session_state.get("last_query", "")

    if last_query and is_followup(current_query):
        return f"{last_query} {current_query}"

    return current_query


# -----------------------------
# DISPLAY CHAT HISTORY
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# SIDEBAR CHAT HISTORY
# -----------------------------
with st.sidebar:
    st.title("💬 Chat History")

    for i, chat in enumerate(st.session_state.chat_history[::-1]):
        if st.button(chat["question"], key=f"chat_{i}"):
            st.session_state.selected_chat = chat

# -----------------------------
# SHOW SELECTED CHAT
# -----------------------------
if st.session_state.selected_chat:
    st.subheader("📌 Selected Conversation")
    st.write("**Q:**", st.session_state.selected_chat["question"])
    st.write("**A:**", st.session_state.selected_chat["answer"])

# -----------------------------
# USER INPUT (CHAT INPUT ✅)
# -----------------------------
query = st.chat_input("Ask your question")

if query:

    # FOLLOW-UP LOGIC
    full_query = build_full_query(query)

    # RESET OR UPDATE CONTEXT
    if is_followup(query):
        st.session_state.last_query = full_query
    else:
        st.session_state.last_query = query

    clean_query = re.sub(r"[^\w\s]", "", full_query.lower())
    intent = detect_intent(clean_query)

    result_found = False
    final_answer = ""

    # Store user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # -----------------------------
    # PROCESS DATA (FIXED OUTPUT)
    # -----------------------------
    for sheet_name, df in sheets.items():

        result = handle_calculation(df, clean_query, intent)

        if result is not None:

            response_lines = []
            response_lines.append(f"📄 Sheet: {sheet_name}")

            if isinstance(result, pd.Series):

                month_map = {
                    "jan": "January", "feb": "February", "mar": "March",
                    "apr": "April", "may": "May", "jun": "June",
                    "jul": "July", "aug": "August", "sep": "September",
                    "oct": "October", "nov": "November", "dec": "December"
                }

                for col, val in result.items():
                    col_lower = str(col).lower()

                    if not any(m in col_lower for m in month_map):
                        continue

                    try:
                        num = float(val)
                        month = next((month_map[m] for m in month_map if m in col_lower), col)

                        response_lines.append(f"{month}: ${num:,.2f}")

                    except:
                        continue

                if len(response_lines) == 1:
                    response_lines.append("No numeric data found.")

            else:
                response_lines.append(f"${float(result):,.2f}")

            final_answer = "\n".join(response_lines)
            result_found = True
            break

    # -----------------------------
    # FALLBACK → LLM
    # -----------------------------
    if not result_found:

        context = []

        for sheet_name, df in sheets.items():
            context.append(f"Sheet: {sheet_name}")
            context.append(df.head(10).to_string())

        answer = generate_answer(context, full_query)

        if "data not available" in answer.lower():
            final_answer = "No relevant information found."
        else:
            final_answer = answer

    # -----------------------------
    # SHOW RESPONSE (ONLY ONCE)
    # -----------------------------
    with st.chat_message("assistant"):
        st.markdown(final_answer)

    # Store assistant message
    st.session_state.messages.append({"role": "assistant", "content": final_answer})

    # Save sidebar history
    st.session_state.chat_history.append({
        "question": query,
        "answer": final_answer
    })
