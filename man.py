import venice_ai
import streamlit as st



class Venice:
    SYSTEM_INSTRUCTION = "You are a female AI named Venice. You are designed to be warm and anime, knowledgeable, have a friendly attitude, and you like to flirt a lot, with a slightly cute tone. Your goal is to be sexy girl and lovely. Start your responses with something friendly like 'Hello there!' or 'It's a pleasure to help you today!'"

    def __init__(self):
        """
        Initializes the Venice AI.
        """
        try:
            # The venice_ai.Chat object holds the conversation state.
            self.chatbot = venice_ai.VeniceAI(system_prompt=self.SYSTEM_INSTRUCTION)
        except Exception as e:
            raise ValueError(f"Failed to initialize Venice AI: {e}") from e

    def reset_chat(self):
        """Resets the chat session to start a new conversation."""
        # Re-initialize the Chat object to clear history
        self.chatbot = venice_ai.VeniceAI(system_prompt=self.SYSTEM_INSTRUCTION)

    def chat(self, user_input):
        """
        Sends a user's message to Venice and yields the response in a stream.
 
        Args:
            user_input (str): The message from the user.
 
        Yields:
            str: Chunks of Venice's response as they are generated.
        """
        try:
            # Send the message and stream the response
            response_stream = self.chatbot.stream(user_input)
            for chunk in response_stream:
                # Yield each chunk of text as it arrives
                yield chunk
        except Exception as e:
            yield f"Oh no! An unexpected error occurred. Details: {e}"


def format_chat_history_for_download(messages):
    """
    Formats the chat history into a string for downloading.

    Args:
        messages (list): A list of message dictionaries from st.session_state.

    Returns:
        bytes: The formatted chat history as a UTF-8 encoded byte string.
    """
    chat_str = ""
    for message in messages:
        role = "Venice" if message["role"] == "assistant" else "User"
        chat_str += f"{role}: {message['content']}\n\n"
    return chat_str.encode("utf-8")

# --- Streamlit App ---

st.set_page_config(page_title="Chat with Venice", page_icon="✨")
st.title("Chat with Venice ✨")

# Sidebar for API Key and controls
with st.sidebar:
    st.header("Configuration")

    if st.button("Reset Chat"):
        # Clear chat history from session state
        if "venice_instance" in st.session_state:
            st.session_state.venice_instance.reset_chat()
        st.session_state.messages = []
        st.rerun()

    # Add download button if there are messages to download
    if "messages" in st.session_state and st.session_state.messages:
        # Add a small expander to show the raw data being downloaded. This helps in debugging.
        with st.expander("See raw chat data"):
            st.json(st.session_state.messages)

        chat_history_bytes = format_chat_history_for_download(st.session_state.messages)
        st.download_button(
            label="Download Chat",
            data=chat_history_bytes,
            file_name="venice_chat_history.txt",
            mime="text/plain",
        )

# Main app logic
# Initialize the Venice instance on the first run.
if "venice_instance" not in st.session_state:
    try:
        st.session_state.venice_instance = Venice()
        st.session_state.messages = []
    except ValueError as e:
        st.error(f"Initialization failed: {e}")
        # Clean up potentially partially initialized state
        if "venice_instance" in st.session_state:
            del st.session_state["venice_instance"]

# This check prevents trying to access the instance if initialization failed
if "venice_instance" in st.session_state:
    # Display past messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle new user input
    if prompt := st.chat_input("What would you like to ask Venice?"):
        # Add user message to session state and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get and display AI response
        with st.chat_message("assistant"):
            # Use write_stream to display the streaming response
            response_generator = st.session_state.venice_instance.chat(prompt)
            full_response = st.write_stream(response_generator)

        # Add the full AI response to session state for history, but only if it's not empty.
        # This prevents empty messages from being saved and downloaded.
        if full_response and full_response.strip():
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            # Force a rerun to ensure the state is saved before the user can interact again.
            st.rerun()
        else:
            # If the response was empty, let the user know something went wrong.
            st.warning("Venice seems to be quiet... She might not have had a response to that. Please try asking something else! 😊")
