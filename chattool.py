from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, FSInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.client.bot import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.types import BotCommand, ReactionTypeEmoji
from aiogram.filters import Command
from PIL import Image
import random

import logging
import json
import os

# Завантажуємо конфіг
with open('config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)

if 'ADMINS' not in config:
    config['ADMINS'] = []
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)

TOKEN = config['TOKEN']
CHAT_TITLE = config.get('CHAT_TITLE', '')

# Ініціалізуємо бота і диспетчера
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='Markdown'))
dp = Dispatcher()
router = Router()

logging.basicConfig(level=logging.INFO)

# Обробник команди /start
@router.message(Command(commands=['start']))
async def start_command_handler(message: Message):
    await message.answer("🛡 Привіт. Я допоможу тобі позбутися ноунеймів і окремих індивідуумів у чаті. Не забудь дати мені права адміністратора\nЩе вивчай /help")

# Обробник команди /help
@router.message(Command(commands=['help']))
async def help_command_handler(message: Message):
    await message.answer(
        "⚙️ Список команд:"
        "\n\n/start — запустити бота"
        "\n/help — це повідомлення"

        "\n/id [chat] [replay] — показує id"
        "\n/bluetext — синій текст для мавп"
        "\n/roulet — список розіграшів, теж для мавп"
        "\n\\*/kb [text] [replay] [one] — клава для спаму. one - одноразово"
        "\n\\*/ckb — закриває активні клави"
        "\n/pic — зробити авою"
        "\n\\*/picset — змінити пнг"
        "\n/topic — додати в назву чата"
        "\n\\*/topicset — змінити назву чата. Потрібен рестарт бота"
        "\n/pin — розхуярити кремль"
        "\n\n\\* — команди для адмінів бота (не чата)"
    )

# Обробник команди /id
@router.message(Command(commands=['id']))
async def id_command_handler(message: Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        await message.answer(f"ID юзера: `{user_id}`")
    elif "chat" in message.text:
        chat_id = message.chat.id
        await message.answer(f"ID чату: `{chat_id}`")
    else:
        user_id = message.from_user.id
        await message.answer(f"Твій ID: `{user_id}`")

# Обробник команди /roulet
@router.message(Command(commands=['roulet']))
async def roulet_command_handler(message: Message):
    await message.answer(
        "🚀 *Про розіграші:*"
        "\n_Введи команду та отримай шанс виграти приз. У кожної команди свій приз і свої шанси. Не забудь додати мене в груповий чат (розіграші працюють тільки там) і видати права адміністратора, інакше я не зможу працювати😢_"
        "\n\n🥳 *Список розіграшів:*"
        "\n*/yadebil*"
        "\n*Приз:* _можливість закріплювати повідомлення_"
        "\n*Шанс:* _10%_"
        "\n*/yagandone*"
        "\n*Приз:* _можливість отримати адміністратора_"
        "\n*Шанс:* _5%_"
        "\n*/yapedarasik*"
        "\n*Приз:* _можливість отримати творця_"
        "\n*Шанс:* _1%_"
    )

kick_roulet_commands = ['/yadebil', '/yagandone', '/yapedarasik']

@router.message(lambda message: message.text is not None and any(word in message.text.lower() for word in kick_roulet_commands))
async def kick_user(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    try:
        await bot.ban_chat_member(chat_id, user_id)
        await bot.unban_chat_member(chat_id, user_id)
        await message.answer("😢 *На жаль, ти не виграв*\n_Спробуй ще раз_")
    except TelegramBadRequest as e:
        if 'not enough rights' in str(e).lower():
            await message.answer("⚠️ Щось не так. Можливо, у мене немає прав адміна")
        else:
            await message.answer(f"Чортила, ти вже адмін")

# # Обробник команди /bluetext
# @router.message(Command(commands=['bluetext']))
# async def bluetext_command_handler(message: Message):
#     await message.answer("/BLUE /TEXT\n/MUST /CLICK\n/I /AM /A /STUPID /ANIMAL /THAT /ISS /ATTRACTED /TO /COLORS")

# kick_words = [
#     "слава россии", "/kekmi", "/blue", "/text", "/must", "/click", "/i", "/am", "/stupid", "/animal", "/that", "/iss", "/attracted", "/colors"
# ]

# @router.message(lambda message: message.text is not None and any(word in message.text.lower() for word in kick_words))
# async def kick_words_handler(message: Message):
#     user_id = message.from_user.id
#     chat_id = message.chat.id
#     try:
#         await bot.ban_chat_member(chat_id, user_id)
#         await bot.unban_chat_member(chat_id, user_id)
#         await message.answer("🫵😂")
#     except TelegramBadRequest:
#         return

# Обробник команди /kb
@router.message(Command(commands=['kb']))
async def kb_handler(message: Message):
    if message.from_user.id not in config['ADMINS']: 
        return

    args = message.text.split()[1:]
    one_time_keyboard = 'one' in args

    if one_time_keyboard:
        args.remove('one')

    if args:
        button_text = ' '.join(args)
    elif message.reply_to_message:
        button_text = message.reply_to_message.text
    else:
        await message.answer("Текст..?")
        return

    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=button_text)]], resize_keyboard=False, one_time_keyboard=one_time_keyboard, input_field_placeholder=button_text)
    
    await message.answer("🆒", reply_markup=keyboard)

# Обробник команди /ckb
@router.message(Command(commands=['ckb']))
async def ckb_handler(message: Message):
    if message.from_user.id not in config['ADMINS']:
        return

    keyboard = ReplyKeyboardRemove()
    await message.answer("🆒", reply_markup=keyboard)

# Обробник команди /pic
@router.message(Command(commands=['pic']))
async def set_chat_photo_handler(message: Message):

    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.answer("⚠️ Тільки фото. Не файлом. В реплай")
        return

    photo = message.reply_to_message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    original_image_path = 'original_photo.png'
    with open(original_image_path, 'wb') as f:
        f.write(downloaded_file.read())

    original_image = Image.open(original_image_path)
    overlay_image = Image.open('mn.png')

    fixed_overlay_size = (150, 150)
    overlay_image = overlay_image.resize(fixed_overlay_size, Image.LANCZOS)

    original_width, original_height = original_image.size

    if original_width < 512 or original_height < 512:
        aspect_ratio = original_width / original_height
        if aspect_ratio > 1:
            new_width = max(512, original_width)
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = max(512, original_height)
            new_width = int(new_height * aspect_ratio)
        original_image = original_image.resize((new_width, new_height), Image.LANCZOS)

    original_width, original_height = original_image.size
    overlay_width, overlay_height = overlay_image.size
    position = ((original_width - overlay_width) // 2, (original_height - overlay_height) // 2)
    original_image.paste(overlay_image, position, overlay_image if overlay_image.mode == 'RGBA' else None)

    final_image_path = 'final_photo.png'
    original_image.save(final_image_path)

    try:
        input_file = FSInputFile(final_image_path)
        await bot.set_chat_photo(message.chat.id, photo=input_file)
    except TelegramBadRequest as e:
        await message.answer(f"⚠️: `{str(e)}`")

    os.remove(original_image_path)
    os.remove(final_image_path)

# Обробник команди /picset
@router.message(Command(commands=['picset']))
async def set_overlay_photo_handler(message: Message):
    if message.from_user.id not in config['ADMINS']:
        return

    if not message.reply_to_message or not message.reply_to_message.document:
        await message.answer("⚠️ Тільки png. В реплай")
        return

    document = message.reply_to_message.document
    if document.mime_type != 'image/png':
        await message.answer("⚠️ Тільки png. В реплай")
        return

    file_info = await bot.get_file(document.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    with open('mn.png', 'wb') as f:
        f.write(downloaded_file.read())

    await message.answer("🆒")

# Обробник команди /pin
@router.message(Command(commands=['pin']))
async def pin_command_handler(message: Message):
    if message.reply_to_message:
        try:
            await bot.pin_chat_message(chat_id=message.chat.id, message_id=message.reply_to_message.message_id)
        except TelegramBadRequest as e:
            await message.answer(f"⚠️: {e}")
    else:
        await message.answer("Реплай де?")

# Обробник команди /topic
@router.message(Command(commands=['topic']))
async def add_topic_handler(message: Message):
    if not message.reply_to_message:
        await message.answer("Цю команду потрібно використовувати у відповідь на повідомлення.")
        return

    chat_title = config['CHAT_TITLE']
    topic_text = message.reply_to_message.text

    new_chat_title = f"{chat_title} — {topic_text}"
    
    try:
        await bot.set_chat_title(message.chat.id, new_chat_title)
    except Exception as e:
        await message.answer(f"⚠️: {e}")

# Обробник команди /topicset
@router.message(Command(commands=['topicset']))
async def set_topic_title_handler(message: Message):
    if message.from_user.id not in config['ADMINS']:
        return

    if not message.reply_to_message:
        await message.answer("А де реплай?")
        return

    new_chat_title = message.reply_to_message.text
    config['CHAT_TITLE'] = new_chat_title

    with open('config.json', 'w', encoding='utf-8') as file:
        json.dump(config, file, indent=4, ensure_ascii=False)

    try:
        await bot.set_chat_title(message.chat.id, new_chat_title)
    except TelegramBadRequest as e:
        await message.answer(f"⚠️: {e}")

    await message.answer(f"🆒: {new_chat_title}")

# Обробник команди для випадкової реакції
@router.message()
async def random_reaction_handler(message: Message):
    if random.randint(1, 100) <= 5:
        reactions = ["❤️", "👍", "😂", "🔥", "😢", "😍", "👏", "😮", "🤔", "😡", "😎", "🎉", "😴", "🙄", "🤯", "🤩", "😭", "🥺", "👀", "🖤", "💔", "😜", "🥳", "🤪", "😏", "😇", "👋", "✌️", "🙏", "🤝", "💊", "💯"]        
        reaction = random.choice(reactions)
        reaction_object = ReactionTypeEmoji(emoji=reaction)
        try:
            await bot.set_message_reaction(chat_id=message.chat.id, message_id=message.message_id, reaction=[reaction_object])
        except TelegramBadRequest:
            pass

dp.include_router(router)

if __name__ == "__main__":
    import asyncio
    
    async def main():
        commands = [
            BotCommand(command="/id", description="[chat] [replay] — показує id"),
            BotCommand(command="/bluetext", description="- синій текст для мавп"),
            BotCommand(command="/roulet", description="- список розіграшів, теж для мавп"),
            BotCommand(command="/pic", description="- зробити авою"),
            BotCommand(command="/topic", description="- додати в назву чата"),
            BotCommand(command="/pin", description="- розхуярити кремль")
        ]

        await bot.set_my_commands(commands)
        await dp.start_polling(bot)

    asyncio.run(main())