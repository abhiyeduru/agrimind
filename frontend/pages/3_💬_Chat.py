import streamlit as st
import requests

st.set_page_config(page_title="Chat - AgriMind.AI", page_icon="💬")

st.title("💬 Chat with AgriMind")
st.write("""
Have a farming question? Ask our AI assistant for expert advice on:
- Crop management
- Disease prevention
- Best farming practices
- Soil health
- And more!
""")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Language selection
language = st.selectbox("Select Language", ["en", "hi", "te"], index=0)

# Chat input
if prompt := st.chat_input("Ask your farming question..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    "http://localhost:8000/chat",
                    json={
                        "message": prompt,
                        "user_id": "demo_user",
                        "language": language
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result['response']
                    st.markdown(answer)
                    # Add assistant's response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error("Failed to get response. Please try again.")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Make sure the backend server is running at http://localhost:8000")

# Clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.experimental_rerun()

# Help section
with st.expander("💡 Tips for better answers"):
    st.write("""
    1. Be specific in your questions
    2. Include relevant details like crop type, region, or season
    3. Ask one question at a time
    4. Provide context about your farming situation
    """)

# Display some example questions
with st.expander("📝 Example Questions"):
    st.write("""
    - "What are the best practices for growing tomatoes?"
    - "How can I improve soil fertility naturally?"
    - "What could cause yellow leaves in my rice crop?"
    - "When is the best time to plant wheat in North India?"
    - "How much water does cotton need during flowering stage?"
    """)