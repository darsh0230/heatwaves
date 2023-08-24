from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

import pymongo
import asyncio

BOT_TOKEN = "6442773979:AAEhZBu1_1qUxrubsZY0w0WP1YaKE5Kyz34"
LOCATIONS = ['Bengaluru', 'Coimbatore', 'Goa', "Manali", "Ladakh"]
LOCATIONS_LATLONG = {
  "Bengaluru": { "latidude": 77.23, "longitude": 71.23 },
  "Coimbatore": { "latidude": 77.23, "longitude": 71.23 },
  "Goa": { "latidude": 77.23, "longitude": 71.23 },
  "Manali": { "latidude": 77.23, "longitude": 71.23 },
  "Ladakh": { "latidude": 77.23, "longitude": 71.23 }
}

# MONGODB __________
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["heatwaves"]
collection = mydb["teleUsers"]

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # print(update)
    # print(update.effective_chat.id)
    collection.find_one_and_update({"chatId": update.effective_chat.id},
                                        {"$set": 
                                            {
                                                "chatId": update.effective_chat.id,
                                            }
                                        },
                                        upsert=True)
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


def build_keyboard(options):
    keyboard = []
    for option in options:
        keyboard.append([KeyboardButton(option)])
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

async def select_area(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = build_keyboard(LOCATIONS)
    await update.message.reply_text(
        'Please select an option:',
        reply_markup=keyboard
    )

async def process_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text in LOCATIONS:
        collection.find_one_and_update({"chatId": update.effective_chat.id},
                                        {"$set": 
                                            {
                                                "location": update.message.text,
                                                "latitude":LOCATIONS_LATLONG.get(update.message.text).get("latitude"),
                                                "longitude":LOCATIONS_LATLONG.get(update.message.text).get("longitude")
                                            }
                                        })
        await update.message.reply_text("Okie got your location")
    else:
        await update.message.reply_text("Need any Help?")


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", hello))
app.add_handler(CommandHandler("location", select_area))
app.add_handler(MessageHandler(filters.ALL, process_text))
app.run_polling()

# from telegram import Bot
# bot = Bot(token="6442773979:AAEhZBu1_1qUxrubsZY0w0WP1YaKE5Kyz34")
# async def send_message_bot():
#     await bot.send_message(chat_id="2068727565", text="mesdcsage_text")

# asyncio.run(send_message_bot())