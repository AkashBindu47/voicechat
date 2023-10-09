import speech_recognition as sr
import openai
import streamlit as st
import requests

openai.api_key=st.secrets["OPENAI_API_KEY"]

# Create a speech recognizer object
r = sr.Recognizer()
#message_history =  StreamlitChatMessageHistory(key="chat_messages") 
conversation = [{'role' :  'system', 'content' : 'You are a helpful and friendly assistant.'},]


def chatgpt(user_input, conversation=conversation, temperature=0.5):
    conversation.append({"role": "user","content": user_input})
    messages_input = conversation.copy()
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=temperature,
        messages=messages_input,
    )
    chat_response = completion['choices'][0]['message']['content']
    conversation.append({"role": "assistant", "content": chat_response})
    return chat_response


def text_to_speech(text, voice_id="UDD8B7Y7NOuOD8CW9cLw", api_key=st.secrets["ELEVENLABS"]):
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
    headers = {
        'Accept': 'audio/mpeg',
        'xi-api-key': api_key,
        'Content-Type': 'application/json'
    }
    data = {
        'text': text,
        'model_id': 'eleven_monolingual_v1',
        'voice_settings': {
            'stability': 0.6,
            'similarity_boost': 0.85
        }
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        with open('output.mp3', 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        # audio = AudioSegment.from_mp3()
        st.audio('output.mp3')
  
    else:
        print('Error:', response.text)
        
def main():
    # Start recording audio
    if st.button("Start Speech Recognition"):
        with sr.Microphone() as source:
            st.write("Say something...")
            r = sr.Recognizer()
            audio = r.listen(source)
            st.write("Done!")

            # Use the Google Web Speech API to recognize speech
            try:
                text = r.recognize_google(audio)
                st.write("User: " + text)
                response = chatgpt(user_input=text)
                text_to_speech(text=response)
                st.write("Assistant: " + response)
            except sr.UnknownValueError:
                st.write("Sorry, I could not understand your audio.")
            except sr.RequestError as e:
                st.write(f"Sorry, an error occurred: {e}")
                
    # # Transcribe the audio using OpenAI
    # transcription = openai.Audio.transcribe("whisper-1", audio.get_wav_data())

    # # Streamlit UI
    # st.title("Speech to Text")

    # # Display the transcription
    # st.write(transcription)

if __name__ == "__main__":
    main()