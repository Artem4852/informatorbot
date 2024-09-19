import requests
import json
import dotenv, os

dotenv.load_dotenv()

API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = os.getenv('OPENAI_API')

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

with open("input.txt", "r") as f:
    example_input = f.read()

with open("output.txt", "r") as f:
    example_output = f.read()

def send_message(message):
    payload = {
        "model": "gpt-4o-mini-2024-07-18",
        # "model": "gpt-4o-2024-08-06",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Your task is to summarize messages from a news sources. 1. Stay objective and concise. 2. Respond in UKRAINIAN. 3. Each summarized news message should be 1-2 sentences. 4. If you miss something important, the user will be annoyed which is really bad. If you repeat something that was already summarized, the user will be annoyed which is really bad. Please don't make the user annoyed. 5. Output in bulletpoints, each summary starts with `-`. At the end of each summary you should add link to original message. It should be in format `[Детальніше](link)`. 6. Divide news into categories and name them creatively. For example news about HAMAS and Israel can be titled `Що там на близькому сході?`, news about AI can be titled `Що нового в технологіях?`, and news about enlistment can be called `Мобізілація, мобізілація, мобілізація`. These are just examples, be creative. Use `#` to mark subtitles. 7. Use playful language if piece of info is not serious and stay biased towards Ukraine, ukrainians, common people of Ukraine. THE NEWS MUST NOT BE REPETITIVE. NEWS COME FROM DIFFERENT SOURCES SO DON'T MENTION THE SAME THING TWICE. 8. NO PIECE OF INFORMATION SHOULD BE MISSED OUT, CHECK THE NEWS CAREFULLY."},
            {"role": "user", "content": example_input},
            {"role": "assistant", "content": example_output},
            {"role": "user", "content": message}
        ]
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        response_data = response.json()
        return response_data['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code}, {response.text}"

def main():
    response = send_message("""Summarize this news message in 1-2 sentences: \"Более 50 элитных авто зарегистрировали в Украине с начала этого года, среди которых Ferrari, Maserati и Aston Martin, — ЕП

▪️Уровень первой регистрации таких автомобилей в 2024 году даже выше, чем в соответствующие периоды 2021 года.
▪️Самыми дорогими среди всех стали Rolls-Royce Spectre 2024 года выпуска (440 тыс долл). Все на киевских номерах.
▪️Одна из самых больших коллекций авто у интернет-арбитражника Слобоженко: во время полномасштабной он купил McLaren 720S Spider, стоимостью около $300 тысяч, а в целом имеет почти 20 очень дорогих авто. Недавно он получил подозрение в неуплате налогов и выехал из Украины. 
▪️Ещё один молодой любитель дорогих машин - блогер и инвестор в криптовалюту Харченко. В 22 года имел суперкар Lamborghini Huracan за $280 тысяч и гибридное купе BMW i8 за $100 тысяч.
▪️“Криптомиллиардер“ в 2023 году купил суперкар Bugatti Bolide стоимостью $4,6 млн. До этого он якобы стал владельцем еще более дорогого Bugatti Centodieci, цена которого более $10 млн и которых выпустили всего 10 штук.\"""")
    print(f"Response: {response}")

if __name__ == "__main__":
    main()