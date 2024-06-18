import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# Bot token obtained from BotFather
TOKEN = "7130679796:AAEIeBydpWUaZhv2MfSxvPwrbW5PoaNIYqY"
# Your channel username (without the @)
CHANNEL_USERNAME = "ifioktestchannel"
 
# All handlers should be attached to the Dispatcher
dp = Dispatcher()

# Define image URL for the pinned message
PINNED_IMAGE_URL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSf5VupGZQVAv7kdcR2Yu3RsIEMReTZs11VcT_dI13OhneMRJf6Kh9Y75A&s=10"

# Define button labels for the keyboard
BUTTONS = ["Launch Game", "View Points", "Referrals"]

# Define your web app URL
WEB_APP_URL = "https://gigbot-swart.vercel.app/"

# Create reply keyboard with buttons
keyboard_buttons = [
    KeyboardButton(text="Launch Game", web_app=WebAppInfo(url=WEB_APP_URL)),
    KeyboardButton(text="View Points"),
    KeyboardButton(text="Referrals")
]
keyboard = ReplyKeyboardMarkup(keyboard=[[button] for button in keyboard_buttons], resize_keyboard=True)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command and checks if the user is a member of the channel
    """
    bot = message.bot
    user_id = message.from_user.id
    
    # Check if user is a member of the channel
    member = await bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
    
    if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        # User is a member of the channel
        await message.answer_photo(photo=PINNED_IMAGE_URL, caption="Snake Airdrop Bot")
        await message.answer(f"Hello, {html.bold(message.from_user.full_name)}! Use the menu below to interact with the bot.", reply_markup=keyboard)
    else:
        # User is not a member of the channel
        await message.answer("You must join our channel first! Please join the channel and then restart the bot.")
        await message.answer(f"Join our channel: https://t.me/{CHANNEL_USERNAME}")

@dp.message(lambda message: message.text == "View Points")
async def view_points_handler(message: Message) -> None:
    """
    This handler responds to the 'View Points' command
    """
    await message.answer("Your current points are: 0")

@dp.message(lambda message: message.text == "Referrals")
async def referrals_handler(message: Message) -> None:
    """
    This handler responds to the 'Referrals' command
    """
    await message.answer("You have referred: 0 users")

@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward received messages back to the sender

    By default, the message handler will handle all message types (like text, photo, sticker, etc.)
    """
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")

async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # And then run events dispatching
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
