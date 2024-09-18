import requests
import json
import dotenv, os

dotenv.load_dotenv()

# Define the API endpoint and your API key
API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = os.getenv('OPENAI_API')

# Set up the headers for the request
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def send_message(message):
    # Define the payload for the request
    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ]
    }

    # Send the request to the API
    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

    # Parse the response
    if response.status_code == 200:
        response_data = response.json()
        return response_data['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code}, {response.text}"

def main():
    print("Chat with ChatGPT! Type 'exit' to end the conversation.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        response = send_message(user_input)
        print(f"ChatGPT: {response}")

if __name__ == "__main__":
    main()