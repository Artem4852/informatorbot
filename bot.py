import logging, os, dotenv, json
import datetime
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, LinkPreviewOptions
from telegram.ext import CommandHandler, MessageHandler, CallbackContext, ConversationHandler, ApplicationBuilder
import random, pytz

dotenv.load_dotenv()
token = os.getenv("TELEGRAM_TOKEN")

from fetch import Fetcher
from ai import send_message

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def get_user_data():
    with open("userdata.json", "r") as f:
        data = json.load(f)
    return data

def save_user_data(data):
    with open("userdata.json", "w") as f:
        json.dump(data, f)

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привіт! Нема часу переглядати новини? Тисни /news, і я зроблю тобі скорочену версію по всім телеграм каналам, що тебе цікавлять!")

async def news(update: Update, context: CallbackContext):
    chat_id = str(update.message.chat_id)
    userdata = get_user_data()
    if chat_id not in userdata:
        userdata[chat_id] = {
            "last_update": None,
            "channels": []
        }
        await update.message.reply_text("Ти ще не додав жодного каналу. Додай канал командою /add_channel.")
        save_user_data(userdata)
        return

    viewing_message = await update.message.reply_text(f"Переглядаю {', '.join(userdata[chat_id]['channels'])}...")
    fetcher = Fetcher()
    await fetcher.start()
    from_date = userdata[chat_id]["last_update"]
    if from_date:
        from_date = datetime.datetime.fromtimestamp(int(from_date), tz=pytz.UTC)
    else:
        from_date = datetime.datetime.now(tz=pytz.UTC) - datetime.timedelta(hours=8)
    userdata[chat_id]["last_update"] = datetime.datetime.now().timestamp()

    messages = []
    for channel in userdata[chat_id]["channels"]:
        messages += await fetcher.get_messages(channel, from_date=from_date)
    messages = sorted(messages, key=lambda x: x.date)
    await fetcher.disconnect()

    print(len(messages))

    # output = """Ваші новини 🐈\n\n"""

    # processed = 0

    # output_message = None

    # existing_summaries = []

    # for message in messages:
    #     processed += 1
    #     summary = send_message(f"{message.text}. Previous summaries: ```{', '.join(existing_summaries)}```.")
        # print(f"Summarize this news message in 1-2 sentences: {message.text}. Previous summaries: ```{', '.join(existing_summaries)}```. If anything similar was already summarized, output `SKIP` and only that.")
        # print(summary)
        # if summary == "SKIP":
        #     print(f"Skipping {message.link}")
        #     continue
        # existing_summaries.append(summary)

        # summary = "- " + summary
        # summary += f" [Детальніше]({message.link})."
        # output += summary + "\n\n"

        # if processed == 5:
        #     await viewing_message.edit_text(f"Йой, які цікаві новиноньки 😮")
        # elif processed == 10:
        #     await viewing_message.edit_text(f"Так багатооооо...")
        # elif processed == 20:
        #     await viewing_message.edit_text(f"Ще трішки (але це не точно)...")
        # elif processed == 50:
        #     await viewing_message.edit_text(f"Та тут читати не перечитати...")

        # if processed == 1:
        #     output_message = await update.message.reply_text(output, parse_mode="Markdown", link_preview_options=LinkPreviewOptions(is_disabled=True, url=None))
        # else:
        #     try:
        #         await output_message.edit_text(output, parse_mode="Markdown", link_preview_options=LinkPreviewOptions(is_disabled=True, url=None))
        #     except:
        #         output = output.split("\n\n")[-2]
        #         output_message = await update.message.reply_text(output, parse_mode="Markdown", link_preview_options=LinkPreviewOptions(is_disabled=True, url=None))

    if messages:
        merged = "Summarize these news messages in 1-2 sentences: \n\n" + "\n\n".join([f"{message.text} | LINK THAT SHOULD BE PROVIDED IN `Детальніше` - {message.link}" for message in messages])
        # print(merged)
        output = send_message(merged)
        print(output)
        output = "Ваші новини 🐈\n\n" + output.replace("#", "")
        await update.message.reply_text(output, parse_mode="Markdown", link_preview_options=LinkPreviewOptions(is_disabled=True, url=None), reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton('/news')]], resize_keyboard=True, one_time_keyboard=True))

    else:
        await update.message.reply_text("Хм, нічого цікавенького. Спробуйте пізніше. 😴", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton('/news')]], resize_keyboard=True, one_time_keyboard=True))

    await viewing_message.delete()

    save_user_data(userdata)

async def add_channel(update: Update, context: CallbackContext):
    chat_id = str(update.message.chat_id)
    userdata = get_user_data()
    if chat_id not in userdata:
        await update.message.reply_text("Спочатку введи /news.")
        return

    await update.message.reply_text("Перешли мені посилання на канал. Приклад: https://t.me/itc_channel.")
    return 0

async def receive_channel(update: Update, context: CallbackContext):
    chat_id = str(update.message.chat_id)
    userdata = get_user_data()

    channel_link = update.message.text
    channel_name = channel_link.split("/")[-1]

    if channel_name in userdata[chat_id]["channels"]:
        await update.message.reply_text("Цей канал вже додано.")
        return ConversationHandler.END

    fetcher = Fetcher()
    try:
        await fetcher.start()
        if not await fetcher.channel_exists(channel_name):
            await update.message.reply_text("Здається такого каналу не існує.")
            return ConversationHandler.END
    except:
        await update.message.reply_text("Здається щось пішло не так. Спробуйте ще раз.")
        return ConversationHandler.END
    await fetcher.disconnect()

    userdata[chat_id]["channels"].append(channel_name)
    await update.message.reply_text(f"Канал [{channel_name}]({channel_link}) додано.", parse_mode="Markdown")

    save_user_data(userdata)

    return ConversationHandler.END

async def list_channels(update: Update, context: CallbackContext):
    chat_id = str(update.message.chat_id)
    userdata = get_user_data()
    if chat_id not in userdata:
        userdata[chat_id] = {
            "last_update": None,
            "channels": []
        }
    save_user_data(userdata)

    channels = userdata[chat_id]["channels"]
    if not channels:
        await update.message.reply_text("Ви ще не додали жодного каналу. Додайте канал командою /add_channel.")
        return

    channels = [f"- https://t.me/{channel}" for channel in channels]
    channels = "\n".join(channels)

    await update.message.reply_text(f"Ваші канали: \n{channels}", link_preview_options=LinkPreviewOptions(is_disabled=True, url=None))

async def remove_channel(update: Update, context: CallbackContext):
    chat_id = str(update.message.chat_id)
    userdata = get_user_data()
    if chat_id not in userdata:
        userdata[chat_id] = {
            "last_update": None,
            "channels": []
        }
    save_user_data(userdata)

    buttons = [KeyboardButton(channel) for channel in userdata[chat_id]["channels"]]
    grouped_buttons = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]

    markup = ReplyKeyboardMarkup(keyboard=grouped_buttons, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Який канал видаляємо?", reply_markup=markup)
    return 0

async def receive_remove_channel(update: Update, context: CallbackContext):
    chat_id = str(update.message.chat_id)
    userdata = get_user_data()

    channel_name = update.message.text
    if channel_name not in userdata[chat_id]["channels"]:
        await update.message.reply_text("Цього каналу немає у списку.", reply_markup=None)
        return ConversationHandler.END

    userdata[chat_id]["channels"].remove(channel_name)
    await update.message.reply_text(f"Канал {channel_name} видалено.")
    save_user_data(userdata)

    return ConversationHandler.END

def main():
    global scraper
    application = ApplicationBuilder().token(token).build()

    add_channel_handler = ConversationHandler(
        entry_points=[CommandHandler('add_channel', add_channel)],
        states={
            0: [MessageHandler(None, receive_channel)]
        },
        fallbacks=[]
    )

    remove_channel_handler = ConversationHandler(
        entry_points=[CommandHandler('remove_channel', remove_channel)],
        states={
            0: [MessageHandler(None, receive_remove_channel)]
        },
        fallbacks=[]
    )
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('news', news))
    application.add_handler(CommandHandler('list_channels', list_channels))
    application.add_handler(remove_channel_handler)
    application.add_handler(add_channel_handler)
    application.run_polling(poll_interval=1)

if __name__ == '__main__':
    main()