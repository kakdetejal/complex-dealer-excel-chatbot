# Excel AI Chatbot
# Overview

This project is an AI-powered chatbot that allows users to interact with complex Excel files using natural language. It can extract insights, perform calculations, and present results in a conversational format.

The system is designed to handle semi-structured Excel data, automatically clean and process it, and provide accurate answers using a hybrid approach combining rule-based logic and AI.

# Key Features
- Query Excel data using natural language
- Supports monthly analysis (sales, revenue, P&L, etc.)
- Performs calculations (sum, average, max, min)
- Conversational interface with chat history
-  Handles follow-up questions (basic context awareness)
-  LLM fallback for ambiguous or unsupported queries
- Proper formatting for financial outputs (currency, monthly breakdown)

# Tech Stack
Python
Pandas – Data processing
Streamlit – UI / Chat interface
OpenAI GPT (gpt-4o-mini) – LLM fallback
Regex & Rule-based NLP – Query understanding

# How It Works
- Excel Parsing
- Dynamically detects headers and cleans messy Excel sheets
- Converts data into structured Pandas DataFrames
- Query Understanding
- Cleans user input (removes symbols, normalizes text)
- Detects intent (sum, average, max, etc.)
- Maps business terms (e.g., “P&L” → “Total Revenue”)
- Data Retrieval
- Uses keyword-based scoring to find the most relevant row
- Extracts monthly values and performs calculations
- Response Generation
- Formats results into readable output (e.g., monthly breakdown, currency)
- Falls back to GPT if structured data cannot answer the query
- Conversational Interface
- Maintains chat history
- Supports follow-up queries using previous context

# Key Design Decision

Initially, embeddings and vector databases were explored for semantic search. However, since the data is primarily structured and numeric, a rule-based retrieval system using Pandas provided higher accuracy and better performance. The LLM is used only as a fallback for flexibility.

## Conclusion

This project demonstrates how to build a practical AI system that combines:

- Structured data processing
- Lightweight NLP
- LLM integration

to create an efficient and user-friendly data assistant.
