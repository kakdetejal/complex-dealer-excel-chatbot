import pandas as pd
import streamlit as st
from excel_parser import load_all_sheets
from query_handler import detect_intent, handle_calculation
from llm import generate_answer
import re

st.set_page_config(page_title="Chat with your AI Assistant", page_icon=":robot:")
st.title("Chat with your AI Assistant :robot:")

file_path = "data/Complex Dealer Input.xlsx"

# Load data once
if "sheets" not in st.session_state:
    st.session_state.sheets = load_all_sheets(file_path)
    st.success("Data loaded successfully!")

sheets = st.session_state.sheets

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

#  Follow-up memory
if "last_query" not in st.session_state:
    st.session_state.last_query = ""

#  Sidebar
with st.sidebar:
    st.title("💬 Chat History")

    for i, chat in enumerate(st.session_state.chat_history[::-1]):
        if st.button(chat["question"], key=f"chat_{i}"):
            st.session_state.selected_chat = chat

#  Show selected chat
if "selected_chat" in st.session_state and st.session_state.selected_chat:
    st.subheader("📌 Selected Conversation")
    st.write("**Q:**", st.session_state.selected_chat["question"])
    st.write("**A:**", st.session_state.selected_chat["answer"])

#  Input
query = st.text_input("Ask your question")

if query:

    # FOLLOW-UP HANDLING (SMART FIX)
    if st.session_state.last_query:
        if len(query.split()) <= 3:
            full_query = st.session_state.last_query + " " + query
        else:
            full_query = query
    else:
        full_query = query

    st.session_state.last_query = full_query

    clean_query = re.sub(r"[^\w\s]", "", full_query.lower())

    intent = detect_intent(clean_query)

    result_found = False
    final_answer = ""

    st.chat_message("user").write(query)

    # LOOP ALL SHEETS
    for sheet_name, df in sheets.items():

        result = handle_calculation(df, clean_query, intent)

        if result is not None:

            st.chat_message("assistant").write(f"📄 Sheet: {sheet_name}")

            if isinstance(result, pd.Series):

                month_map = {
                    "jan": "January", "feb": "February", "mar": "March",
                    "apr": "April", "may": "May", "jun": "June",
                    "jul": "July", "aug": "August", "sep": "September",
                    "oct": "October", "nov": "November", "dec": "December"
                }

                output_lines = []

                for col, val in result.items():

                    col_lower = str(col).lower()

                    if not any(m in col_lower for m in month_map):
                        continue

                    try:
                        num = float(val)
                        month = next((month_map[m] for m in month_map if m in col_lower), col)

                        line = f"{month}: ${num:,.2f}"

                        st.chat_message("assistant").write(line)
                        output_lines.append(line)

                    except:
                        continue

                if not output_lines:
                    final_answer = "No numeric data found."
                    st.chat_message("assistant").write(final_answer)
                else:
                    final_answer = "\n".join(output_lines)

            else:
                final_answer = f"${float(result):,.2f}"
                st.chat_message("assistant").write(final_answer)

            result_found = True
            break

    # FALLBACK → LLM
    if not result_found:

        context = []

        for sheet_name, df in sheets.items():
            context.append(f"Sheet: {sheet_name}")
            context.append(df.head(10).to_string())

        answer = generate_answer(context, query)

        if "data not available" in answer.lower():
            final_answer = "No relevant information found."
        else:
            final_answer = answer

        st.chat_message("assistant").write(final_answer)

    # Save chat
    st.session_state.chat_history.append({
        "question": query,
        "answer": final_answer
    })