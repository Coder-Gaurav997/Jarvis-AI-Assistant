from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import pyttsx3
import speech_recognition as sr 

# Load environment variables from the .env file
env_vars = dotenv_values(".env")

# Retrieve specific environment variables for username, assistant name, and API key
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey") 

# Initialize the Groq client using the provided API key
client = Groq(api_key=GroqAPIKey)

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Attempt to load the chat log from a JSON file.
try:
    with open(r"ChatLog.json", "r") as f:
        messages = load(f)  # Load existing messages from the chat log.
except FileNotFoundError:
    messages = []  # Initialize with an empty list if the file doesn't exist.

# Function to get real-time date and time information
def RealTimeInformation():
    current_date_time = datetime.datetime.now()
    return f"Day: {current_date_time.strftime('%A')}, Date: {current_date_time.strftime('%d')}, Month: {current_date_time.strftime('%B')}, Year: {current_date_time.strftime('%Y')}"

# Function to modify the chatbot's response for better formatting.
def AnswerModifier(Answer):
    return '\n'.join(line for line in Answer.split('\n') if line.strip())

# Function to speak the response
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to capture audio and convert it to text
def speech_to_text():
    with sr.Microphone() as source:
        print("\nListening...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        audio = recognizer.listen(source)  # Listen for the first phrase
        try:
            text = recognizer.recognize_google(audio)  # Use Google Speech Recognition
            print(f"\nYou said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None

def ChatBot(Query, real_time_info):
    messages.append({"role": "user", "content": Query})  # Append the user's query to messages

    # Create a completion request to the chatbot API
    completion = client.chat.completions.create(
        model="llama3-70b-8192", 
        messages=[{"role": "system", "content": real_time_info}] + messages,
        max_tokens=1024,
        temperature=0.7,
        top_p=1,
        stream=True,
        stop=None
    )

    Answer = "".join(chunk.choices[0].delta.content for chunk in completion if chunk.choices[0].delta.content)

    messages.append({"role": "assistant", "content": Answer})  # Update messages with the assistant's response
    return AnswerModifier(Answer)  # Return the modified answer

def main():
    real_time_info = RealTimeInformation()  # Get real-time information once
    while True:
        user_input = speech_to_text()  # Capture speech input
        if user_input is None:
            continue  # Skip if no valid input was captured
        if user_input.lower() in ["exit", "quit"]:
            break
        response = ChatBot(user_input, real_time_info)  # Get the chatbot's response
        if response:
            print(f"Chatbot: {response}")
            speak(response)

    # Save the updated messages to the chat log when exiting
    with open(r"ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

# Main loop to interact with the user
speak("Initialising Jarvis...")
print("\nYour AI Assistant - JARVIS")
print("--------------------------")
main()

# Creater: GAURAV PANDEY
# Email: golupandey95207@gmail.com
# DOC(Date of Creation): 15th March, 2025
# Name of AI: JARVIS.
