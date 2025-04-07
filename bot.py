import telebot
import openai
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_API_TOKEN)
openai.api_key = OPENAI_API_KEY

def ask_openai(message_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": message_text}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return None

def search_google(query):
    try:
        url = f"https://serpapi.com/search.json?q={query}&api_key={SERPAPI_API_KEY}"
        response = requests.get(url)
        data = response.json()
        results = []
        for result in data.get('organic_results', [])[:2]:  # Limit 2 links
            title = result.get('title')
            link = result.get('link')
            if title and link:
                results.append(f"{title}: {link}")
        return results
    except Exception as e:
        print(f"Search Error: {e}")
        return []

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.chat.type in ["group", "supergroup"]:
        if "@YourBotName" in message.text:
            user_text = message.text.replace("@YourBotName", "").strip()
            reply = ask_openai(user_text)
            if not reply or "saya hanya sebuah program komputer" in reply.lower():
                search_results = search_google(user_text)
                if search_results:
                    reply = "\n".join(search_results)
                else:
                    reply = "Maaf, saya tidak menemukan informasi yang relevan."
            bot.reply_to(message, reply)

bot.polling()
