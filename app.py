import streamlit as st
from typing import Generator
from groq import Groq
import utils_app

st.set_page_config(page_icon=":llama:", layout="wide",
                   page_title="Llamma 3 demo")


def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )


icon(":llama:")
st.header("Llama3 Chatbot", divider="blue", anchor=False)


client = Groq(
    api_key=st.secrets["GROQ_API_KEY"],
)

# Initialize chat history and selected model
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

# Define model details
models = {
    "llama3-70b-8192": {"name": "LLaMA3-70b-8192", "tokens": 8192, "developer": "Meta"},
    "llama3-8b-8192": {"name": "LLaMA3-8b-8192", "tokens": 8192, "developer": "Meta"},
}

st.sidebar.subheader("Configuration")
model_option = st.sidebar.selectbox(
    "Choose a model:",
    options=list(models.keys()),
    format_func=lambda x: models[x]["name"],
    index=0   # Default to Llama 70b
)

# Detect model change and clear chat history if model has changed
if st.session_state.selected_model != model_option:
    st.session_state.messages = []
    st.session_state.selected_model = model_option



# Display chat messages from history on app rerun
for message in st.session_state.messages:
    avatar = '🤖' if message["role"] == "assistant" else '😎'
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    """Yield chat response content from the Groq API response."""
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


if prompt := st.chat_input("Enter your prompt here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar='😎'):
        st.markdown(prompt)

    # Fetch response from Groq API
    try:
        chat_completion = client.chat.completions.create(
            model=model_option,
            messages=[
                {
                    "role": m["role"],
                    "content": m["content"]
                }
                for m in st.session_state.messages
            ],
            stream=True
        )

        # Use the generator function with st.write_stream
        with st.chat_message("assistant", avatar="🤖"):
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_responses_generator)
    except Exception as e:
        st.error(e, icon="🚨")

    # Append the full response to session_state.messages
    if isinstance(full_response, str):
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
    else:
        # Handle the case where full_response is not a string
        combined_response = "\n".join(str(item) for item in full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": combined_response})
        
if len(st.session_state.messages):
    try:
        mens= st.session_state.messages[-2]["content"]
        output = utils_app.query({"inputs": mens,})
        result = utils_app.get_label_score(output)
        res = list(result)[0]
        warn_message = """
                        Hello! I hope you're doing okay. I've noticed some signs of stress in our conversation — it's completely okay to feel this way. 
                        If you're feeling overwhelmed, please remember to take care of yourself. Help is available if you need it, and you're not alone. 
                        You can reach out to someone at these numbers: XXXXX. Also, if you're curious about how I can detect signs of stress, feel free to explore our methods here:
                        https://github.com/fjmoyao/depression_detection. Your well-being matters to us!
                        """
        warn_message_esp = """
                            ¡Hola! Espero que te encuentres bien. He notado algunos signos de estrés en nuestra conversación — es completamente normal sentirse así. 
                            Si te sientes abrumado, por favor recuerda cuidarte. Hay ayuda disponible si la necesitas y no estás solo. Puedes comunicarte con alguien en estos números: XXXXX. 
                            Además, si tienes curiosidad sobre cómo puedo detectar signos de estrés, no dudes en explorar nuestros métodos aquí:
                            https://github.com/fjmoyao/depression_detection. ¡Tu bienestar es importante para nosotros!"""
        if res== "1":
            st.warning(warn_message)
    except:
        print("Error")
        #st.warning("Error")