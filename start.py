from config import *
import sqlite3
import logging
from datetime import datetime, timedelta
from decimal import Decimal
import random
import string
import time
import threading
import psutil
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
import asyncio
from aiogram import executor
import aiosqlite
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import asyncio 
import math
import requests
import aiohttp
import threading
import asyncio
import os
from termcolor import colored
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import ReportRequest
import random
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors import SessionPasswordNeededError
from telethon.errors import PhoneCodeInvalidError, PhoneNumberInvalidError, FloodWaitError
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeExpiredError, PhoneCodeInvalidError, FloodWaitError
from telethon.tl.types import Channel, Chat, InputPeerChannel, InputPeerChat
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.types import InputReportReasonOther, InputReportReasonSpam, Channel, Chat

def create_database(): 
    conn = sqlite3.connect('') 
    cursor = conn.cursor() 

    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS users ( 
            id INTEGER PRIMARY KEY, 
            user_id INTEGER UNIQUE, 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            timeout DATETIME,
            white_list TEXT
        ) 
    ''')
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS api ( 
            api_id 28904446,
            api_hash 1cc79a619e9d62cfaab48dc521c66821,
            session 894
        ) 
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS promocodes (
            id INTEGER PRIMARY KEY,
            code TEXT UNIQUE NOT NULL,
            days_subscription INTEGER NOT NULL,
            max_activations INTEGER NOT NULL,
            activations_count INTEGER DEFAULT 0,
            used_by TEXT  
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id INTEGER PRIMARY KEY,
            expiration_date DATETIME
        );
    ''')
    
    conn.commit()
    
create_database()

# ....... хз

bot = Bot(token=api_token)
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


async def check_user(user_id):
    conn = sqlite3.connect('/home/container/database.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            return True
        else:
            cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
            conn.commit()
            await bot.send_message(
                log_chat_id,
                f'<b>👤 Зарегистрирован новый <a href="tg:/openmessage?user_id={user_id}">пользователь</a></b>\nID: <code>{user_id}</code>',
                parse_mode='HTML'
            )
            return False
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        return False
    finally:
        conn.close()


async def check_subcribe_status(id):
	conn = sqlite3.connect('/home/container/database.db')
	cursor = conn.cursor()
	cursor.execute("SELECT expiration_date FROM subscriptions WHERE user_id=?", (id, ))
	
	subscription = cursor.fetchone()
	chat = await bot.get_chat(id)
	cursor.execute("SELECT white_list FROM users WHERE user_id = ?", (id, ))
	white = cursor.fetchone()[0]
	if white:
		white = "Присутствует"
	else:
		white = "Отсутствует"
		
	name = chat.full_name
	username = chat.username
	if username:
		username = f"/ @{username}"
	else:
		username = ""
		
	if subscription:
		expiration_date = subscription[0]
		date = datetime.strptime(expiration_date, '%Y-%m-%d %H:%M:%S.%f')
		current_date = datetime.now()
		if current_date <= date:
			status = f"<b>📱 Ваш профиль\n\n🗣 Имя: {name}\n🗄 Данные: id {id} {username}\n💎  Подписка до: {date}\n🎲 Вайт-лист: {white}</b>"
		else:
			status = f"<b>📱 Ваш профиль\n\n🗣 Имя: {name}\n🗄 Данные: id {id} {username}\n💎  Подписка: Истекла\n🎲 Вайт-лист: {white}</b>"
	else:
		status = f"<b>📱 Ваш профиль\n\n🗣 Имя: {name}\n🗄 Данные: id {id} {username}\n💎  Подписка: Отсутствует\n🎲 Вайт-лист: {white}</b>"
		
	return status


async def subscribe_check(id):
	conn = sqlite3.connect('/home/container/database.db')
	cursor = conn.cursor()
	cursor.execute("SELECT expiration_date FROM subscriptions WHERE user_id=?", (id, ))
	subscription = cursor.fetchone()
	if subscription:
		return True
	else:
		return False


@dp.message_handler(commands=['start'])
async def home(message: types.Message):
	if message.chat.type != types.ChatType.PRIVATE:
		return 
		
	markup = types.InlineKeyboardMarkup(row_width=2)
	markup.add(types.InlineKeyboardButton(f"💸 Купить", callback_data=f"buy"))
	markup.add(types.InlineKeyboardButton(f"☃️ Профиль", callback_data=f"profile"))
	
	button = types.InlineKeyboardMarkup(row_width=2)
	
	profile = types.InlineKeyboardButton(text="☃️ Профиль", callback_data="profile")
	
	owner = types.InlineKeyboardButton(text="✨ Правила сноса", url="https://telegra.ph/Rukovodstvo-po-vilonetbot-11-19")
	
	channel = types.InlineKeyboardButton(text="❄️ Канал", url="https://t.me/+5oL9vt-N6TM1MmRi")
	
	botnet = types.InlineKeyboardButton(text="🎅 Репорт", callback_data="botnet")
	button.add(profile, owner, channel, botnet)
	await check_user(message.from_user.id)
	

	if await subscribe_check(message.from_user.id):
		with open('banner.png', 'rb') as banner1:
			await bot.send_photo(
            chat_id=message.from_user.id,
            photo=banner1,
            caption='<b>Приветствуем вас в Meta BotNet! ❄️</b>',            
            reply_markup=button,
            parse_mode='HTML'
        )
	else:
		with open('banner.png', 'rb') as banner2:
			await bot.send_photo(
            chat_id=message.from_user.id,
            photo=banner2,
            caption='<b>🍾 У вас отсутствует подписка! Приобретите её по кнопке ниже.</b>',            
            reply_markup=markup,
            parse_mode='HTML'
        )
		
		
@dp.callback_query_handler(lambda call: call.data == 'profile')
async def profile(call: types.CallbackQuery):
	text = await check_subcribe_status(call.from_user.id)
	check = await subscribe_check(call.from_user.id)
	markup = types.InlineKeyboardMarkup(row_width=1)
	if check:
		markup.add(types.InlineKeyboardButton(f"💰 Продлить Подписку", callback_data=f"buy"))
		
	markup.add(types.InlineKeyboardButton(f"📮 Промокод", callback_data=f"promo"))
		
	markup.add(types.InlineKeyboardButton(f"Меню", callback_data=f"back"))
	
	await bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=text,
            reply_markup=markup,
            parse_mode="HTML"
        )
        
        
@dp.callback_query_handler(lambda call: call.data == 'buy')
async def buy(call: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()
    subscription_options = [
        ("💊 3 дня - 2$", "buy_3"),
        ("💊 7 дней - 4$", "buy_7"),
        ("💊 31 день - 8$", "buy_31"),
        ("💊 Навсегда - 20$", "lifetime"),
        ("Назад", "back")
    ]
    for option_text, callback_data in subscription_options:
        markup.add(types.InlineKeyboardButton(option_text, callback_data=callback_data))
    
    await bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption="<b>💎 Оплата через @send\n⌛️ Выберите срок подписки:</b>",
        reply_markup=markup,
        parse_mode="HTML"
    )
    
    
    
@dp.callback_query_handler(lambda call: call.data == 'back')
async def back_to_main(call: types.CallbackQuery, state: FSMContext):
    check = await subscribe_check(call.from_user.id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton(f"💸 Купить", callback_data=f"buy"))
    markup.add(types.InlineKeyboardButton(f"☃️ Профиль", callback_data=f"profile"))
    
    button = types.InlineKeyboardMarkup(row_width=2)
    
    profile = types.InlineKeyboardButton(text="☃️ Профиль", callback_data="profile")
    owner = types.InlineKeyboardButton(text="✨ Правила сноса", url="https://telegra.ph/Rukovodstvo-po-vilonetbot-11-19")
    channel = types.InlineKeyboardButton(text="❄️ Канал", url="https://t.me/+5oL9vt-N6TM1MmRi")
    botnet = types.InlineKeyboardButton(text="🎅 Репорт", callback_data="botnet")
    button.add(profile, owner, channel, botnet)
    
    if check:
        await bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=f"<b>Приветствуем вас в KillerSnoser! ❄️</b>",
            reply_markup=button,
            parse_mode="HTML"
        )
    else:
        await bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=f"<b>🥀 У вас отсутствует подписка! Приобретите её по кнопке ниже.</b>",
            reply_markup=markup,
            parse_mode="HTML"
        )
		
	
   

async def generate_payment_link(payment_system, amount):
    api_url = "https://pay.crypt.bot/api/createInvoice"
    headers = {"Crypto-Pay-API-Token": Crypto_Pay_API_Token}
    data = {
        "asset": payment_system,
        "amount": float(amount)
    }

    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        json_data = response.json()
        invoice = json_data.get("result")
        payment_link = invoice.get("pay_url")
        invoice_id = invoice.get("invoice_id")
        return payment_link, invoice_id
    else:
        return None, None

async def get_invoice_status(invoice_id):
    api_url = f"https://pay.crypt.bot/api/getInvoices?invoice_ids={invoice_id}"
    headers = {"Crypto-Pay-API-Token": Crypto_Pay_API_Token}

    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        json_data = response.json()
        if json_data.get("ok"):
            invoices = json_data.get("result")
            if invoices and 'items' in invoices and invoices['items']:
                status = invoices['items'][0]['status']
                payment_link = invoices['items'][0]['pay_url']
                amount = Decimal(invoices['items'][0]['amount'])
                value = invoices['items'][0]['asset']
                return status, payment_link, amount, value

    return None, None, None, None

async def get_exchange_rates():
    api_url = "https://pay.crypt.bot/api/getExchangeRates"
    headers = {"Crypto-Pay-API-Token": Crypto_Pay_API_Token}

    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        json_data = response.json()
        if json_data.get("ok"):
            return json_data["result"]
    return []

async def convert_to_crypto(amount, asset):
    rates = await get_exchange_rates()
    rate = None
    for exchange_rate in rates:
        if exchange_rate["source"] == asset and exchange_rate["target"] == 'USD':
            rate = Decimal(str(exchange_rate["rate"]))
            break

    if rate is None:
        raise Exception(f"<b>🎲 Не удалось найти курс обмена для {asset}</b>", parse_mode="HTML")

    amount = Decimal(str(amount))
    return amount / rate 
    
    
@dp.callback_query_handler(lambda call: call.data.startswith('buy_'))
async def subscription_duration_selected(call: types.CallbackQuery):
    duration = call.data
    markup = types.InlineKeyboardMarkup()
    currency_options = [
        ("💵 USDT", "currency_USDT_" + duration),
        ("💎 TON", "currency_TON_" + duration),
        ("💰 NOT", "currency_NOT_" + duration),
        ("🪙 BTC", "currency_BTC_" + duration),
        ("💶 ETH", "currency_ETH_" + duration),
        ("Назад", "buy")
    ]
    for option_text, callback_data in currency_options:
        markup.add(types.InlineKeyboardButton(option_text, callback_data=callback_data))
    
    await bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption="<b>💸  Выберите валюту для оплаты:</b>",
        reply_markup=markup,
        parse_mode="HTML"
    )
    
@dp.callback_query_handler(lambda call: call.data.startswith('currency_'))
async def currency_selected(call: types.CallbackQuery):
    parts = call.data.split('_')
    currency = parts[1]
    duration_parts = parts[2:]
    duration = "_".join(duration_parts)

    amount = get_amount_by_duration(duration.replace('buy_', ''))

    try:
        converted_amount = await convert_to_crypto(amount, currency)
        payment_link, invoice_id = await generate_payment_link(currency, converted_amount)
        if payment_link and invoice_id:
            markup = types.InlineKeyboardMarkup()
            oplata = types.InlineKeyboardButton("💰  Оплатить", url=f"{payment_link}")
            check_payment_button = types.InlineKeyboardButton("💸  Проверить оплату", callback_data=f"check_payment:{call.from_user.id}:{invoice_id}")
            markup.add(oplata, check_payment_button)
            
            await bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=f"<b>💸  Счет для оплаты:</b>\n{payment_link}",
                reply_markup=markup,
                parse_mode="HTML"
            )
        else:
            await bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption="<b>❌  Не удалось создать счет для оплаты. Пожалуйста, попробуйте позже.</b>",
                parse_mode="HTML"
            )
    except Exception as e:
        await bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=str(e)
        )

def get_amount_by_duration(duration):
    prices = {
        '3': 2,
        '7': 4,
        '31': 8,
        'lifetime': 20
    }
    return prices.get(duration, 0)
    
  
@dp.callback_query_handler(lambda call: call.data.startswith('check_payment:'))
async def check_payment(call: types.CallbackQuery):
    _, user_id_str, invoice_id_str = call.data.split(':')
    user_id = int(user_id_str)
    invoice_id = invoice_id_str
    
    if user_id == call.from_user.id:
        status, payment_link, amount, value = await get_invoice_status(invoice_id)
        
        if status == "paid":
            duration_days = get_duration_by_amount(amount)
            
            expiration_date = datetime.now() + timedelta(days=duration_days)
            await add_subscription(user_id, expiration_date)
            await bot.send_message(
                log_chat_id,
                f"<b>💸 Была <a href='tg:/openmessage?user_id={user_id}'>куплена</a> подписка\n==========</b>\n"
                f"<b>Покупатель: {user_id}</b>\n"
                f"<b>Количество дней: {duration_days}</b>\n"
                f"<b>Статус:</b> {status}\n"
                f"<b>Ссылка для оплаты:</b> {payment_link}\n"
                f"<b>Цена:</b> {amount} {value}",
                parse_mode="HTML"
            )
            await bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id, 
                caption="<b>✅ Оплата подтверждена! Подписка активирована. Спасибо за покупку.</b>",
                parse_mode="HTML"
            )
            await home(call.message)
        else:
            await bot.answer_callback_query(call.id, "❌ Оплата не найдена. Попробуйте позже!")
    else:
        await bot.answer_callback_query(call.id, "❌ Вы не можете проверить эту оплату.", show_alert=True)

def get_duration_by_amount(amount):
    amount = round(amount, 2)
    if amount <= 2:
        return 3
    elif amount <= 4:
        return 7
    elif amount <= 8:
        return 31
    elif amount <= 20:
        return 365 * 99  
    else:
        return 0
        
        
class MyState(StatesGroup):
	link = State()
	promo = State()
	delete = State()
 
 
        
        
@dp.callback_query_handler(lambda call: call.data == 'promo')
async def handle_inline_button_click2(call: types.CallbackQuery):   

	with open('banner.png', 'rb') as had:
		await bot.send_photo(call.message.chat.id, had, "<b>🎁 Введите промокод в чат:</b>", parse_mode="HTML")
	await MyState.promo.set()
	

def is_user_in_promocode(user_id, promo_code):
    with sqlite3.connect('/home/container/database.db') as conn:
        cursor = conn.cursor()

        user_id_str = str(user_id)

        cursor.execute('''
            SELECT 1
            FROM promocodes
            WHERE code = ?
            AND (
                used_by = ? OR                  -- ID единственный в поле
                used_by LIKE ? OR               -- ID в начале
                used_by LIKE ? OR               -- ID в конце
                used_by LIKE ?                  -- ID в середине
            )
        ''', (
            promo_code,
            user_id_str,
            f'{user_id_str},%',
            f'%,{user_id_str}',
            f'%,{user_id_str},%'
        ))

        result = cursor.fetchone()
        return result is not None










@dp.message_handler(state=MyState.promo)
async def soso(message: types.Message, state: FSMContext):
    try:
        with sqlite3.connect('/home/container/database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM promocodes WHERE code = ?", (message.text,))
            promocode = cursor.fetchone()
            
            cursor.execute("SELECT expiration_date FROM subscriptions WHERE user_id = ?", (message.from_user.id,))
            expiration_date = cursor.fetchone()

            if expiration_date and expiration_date[0]:
                
                expiration_date = datetime.strptime(expiration_date[0], '%Y-%m-%d %H:%M:%S.%f')
            else:
                expiration_date = datetime.now()

            if promocode is not None:
                already_used = is_user_in_promocode(message.from_user.id, message.text)

                if already_used:
                    await message.reply("<b>❌️ Вы уже использовали данный промокод.</b>", parse_mode="HTML")
                    await home(message)
                    await state.finish()
                    return
                elif promocode[4] >= promocode[3]:
                    await message.reply("<b>❌️ Данный промокод использовали макс. количество раз.</b>", parse_mode="HTML")
                    await home(message)
                    await state.finish()
                    return
                else:
                    
                    new_expiration_date = expiration_date + timedelta(days=promocode[2])
                    
                    new_expiration_date_str = new_expiration_date.strftime('%Y-%m-%d %H:%M:%S.%f')

                    
                    cursor.execute("INSERT OR REPLACE INTO subscriptions (user_id, expiration_date) VALUES (?, ?)", (message.from_user.id, new_expiration_date_str))

                    cursor.execute('''
                        UPDATE promocodes 
                        SET used_by = 
                            CASE 
                                WHEN used_by IS NULL OR used_by = '' THEN ?
                                ELSE used_by || ',' || ? 
                            END,
                            activations_count = activations_count + 1
                        WHERE id = ?
                    ''', (str(message.from_user.id), str(message.from_user.id), promocode[0]))

                    conn.commit()

                    await message.reply(f"<b>✅️ Подписка продлена на {promocode[2]} дней!</b>", parse_mode="HTML")

                    await bot.send_message(
                        log_chat_id,
                        f"🩸 <a href='tg:/openmessage?user_id={message.from_user.id}'>Пользователь</a> ввел промокод <code>{message.text}</code>\n"
                        f"<b>🔔 Дни подписки:</b> <code>{promocode[2]}</code>\n"
                        f"<b>🔔 Осталось активаций:</b> <code>{promocode[3] - (1 + promocode[4])}</code>",
                        parse_mode="HTML"
                    )

                    await home(message)
                    await state.finish()

            else:
                await message.reply("<b>❌️ Неверный промокод.</b>", parse_mode="HTML")
                await home(message)
                await state.finish()

    except sqlite3.Error as e:
        print(f"Ошибка при обработке промокода: {e}")
        await message.reply("<b>❌️ Ошибка при обработке промокода.</b>", parse_mode="HTML")
        await home(message)
        await state.finish()
        
        
        
      
@dp.callback_query_handler(lambda call: call.data == 'botnet')
async def botnet(call: types.CallbackQuery, state: FSMContext):
    if not await subscribe_check(call.from_user.id):
        await state.finish()
        return
    
    await call.message.answer("<b>Отправьте ссылку на нарушение в публичном канале/чате: </b>", parse_mode="HTML")
    await MyState.link.set()
	
session_locks = {}
lock = asyncio.Lock()
	

report_texts = [
"Сообщение содержит спам. Пожалуйста, примите меры."
"Данное сообщение нарушает правила сообщества. Требуется действие."
"Содержимое сообщения не приемлемо и требует удаления."
"Спам. Необходимо удалить."
"Спам. Прошу принять меры незамедлительно."
"Спам. Пожалуйста, примите необходимые меры."
"Этот контент нарушает политику сервиса. Требуется проверка."
"Данный контент нарушает политику Telegram. Прошу обратить внимание."
"Сообщение кажется подозрительным. Рекомендую проверить."
"Прошу удалить это сообщение как спам."
"Нарушение правил сообщества. Необходимо рассмотреть."
"Нарушение правил. Прошу принять меры."
"Это сообщение содержит недопустимый контент. Пожалуйста, удалите."
"Обратите внимание. Данное сообщение может быть мошенническим."
"Сообщение нарушает условия использования сервиса. Требуется действие."
"Пожалуйста, проверьте это сообщение на наличие спама."
"Это сообщение не соответствует стандартам сообщества. Прошу удалить."
"Содержимое сообщения вызывает подозрения. Рекомендую проверить."
"Сообщение содержит оскорбительный контент. Необходимо вмешательство."
]

   
    
    
     
   
    

   
   

	
	

@dp.message_handler(state=MyState.link)
async def links(message: types.Message, state: FSMContext):
    link = str(message.text)
    conn = sqlite3.connect('/home/container/database.db')
    cursor = conn.cursor()
    
    print(f"Получена ссылка от пользователя {message.from_user.id}: {link}")
    
    if not str(link).startswith("https://t.me/") or str(link).startswith("https://t.me/c/"):
        await message.answer("<b>❌️ Введите верную ссылку (публичный чат или канал)</b>", parse_mode="HTML")
        await state.finish()
        await home(message)
        print("Неверная ссылка, возвращаем на главный экран.")
        return
        
    if '/' not in link:
        await message.answer("<b>❌️ Ссылка должна содержать ID сообщения. Например: https://t.me/chat/123456</b>", parse_mode="HTML")
        await state.finish()
        await home(message)
        print("Ссылка не содержит ID сообщения.")
        return
        
    if len(link) > 80:
        await message.answer("<b>❌️ Ваша ссылка слишком длинная!</b>")
        await state.finish()
        await home(message)
        print("Ссылка слишком длинная.")
        return
    
    chat = link.split("/")[-2]
    message_id = link.split("/")[-1]
    
    print(f"Обрабатываем жалобы для чата: {chat}, сообщение ID: {message_id}")
    
    await message.answer("<b>Обрабатываем жалобы...</b>", parse_mode="HTML")    
    await state.finish()
    
    failed_sessions = 0
    successful_sessions = 0
    
    cursor.execute("SELECT white_list FROM users")
    white_list = [row[0] for row in cursor.fetchall()]


    
    
    
    async def send_complaint(client, peer, message_id):
        try:
            await client(ReportRequest(peer, id=[int(message_id)], reason=InputReportReasonSpam(), message=random.choice(report_texts)))
            return True
        except Exception as e:
            print(f"Ошибка при отправке жалобы с сессии {client.session.filename}: {e}")
            nonlocal failed_sessions
            failed_sessions += 1
            return False
    
    async def process_session(session_file):
        nonlocal successful_sessions, failed_sessions
        
        session_path = os.path.join(sessions_folder, session_file)
        
        print(f"Обработка сессии {session_file}")
        
        if not os.path.exists(session_path):
            print(f"Сессия {session_file} не найдена.")
            return
        
        if not session_file.endswith('.session'):
            print(f"Сессия {session_file} не имеет окончания .session.")
            return
        
        if session_file not in session_locks:
            session_locks[session_file] = asyncio.Lock()
        
        async with session_locks[session_file]:
            connected = False
            session2 = session_file.split('.')[0]
            try:
                cursor.execute('SELECT api_id, api_hash FROM api WHERE session = ?', (session2,))
                api = cursor.fetchone()
                api_id = int(api[0])
                api_hash = str(api[1])
            except Exception as e:
                print(f"Ошибка при получении API для сессии {session_file}: {e}")
                failed_sessions += 1
                return
            
            print(f"Подключение сессии {session_file} с API_ID: {api_id}")
            
            client = TelegramClient(session_path, api_id=api_id, api_hash=api_hash, auto_reconnect=True)
            
            try:
                await client.connect()
                if await client.is_user_authorized():
                    connected = True
                    print(f"Сессия {session_file} подключена и авторизована.")
                else:
                    failed_sessions += 1
                    print(f"Сессия {session_file} не авторизована.")
                    return
                    
                try:
                    entity = await client.get_entity(chat)
                    peer = await client.get_input_entity(entity)
                    
                    if isinstance(entity, (Channel, Chat)):
                        try:
                            message_info = await client.get_messages(entity, ids=int(message_id))
                            
                            if message_info:
                                from_id = message_info.sender_id
                                print(f"Сообщение найдено от {from_id}.")
                                
                                if int(from_id) in white_list or int(from_id) in admin :
                                    failed_sessions += 1
                                    print(f"Сообщение от пользователя {from_id} в белом списке, пропускаем.")
                                    return
                                
                                all_sent = True
                                for _ in range(count):
                                    if not await send_complaint(client, peer, message_id):
                                        all_sent = False
                                        
                                if all_sent:
                                    successful_sessions += 1
                                    print(f"Жалоба успешно отправлена с сессии {session_file}.")
                                else:
                                    failed_sessions += 1
                                    print(f"Не удалось отправить жалобу с сессии {session_file}.")
                            else:
                                failed_sessions += 1
                                print(f"Сообщение с ID {message_id} не найдено.")
                                return
                                
                        except Exception as e:
                            failed_sessions += 1
                            print(f"Ошибка при получении сообщения с сессии {session_file}: {e}")
                            
                except Exception as e:
                    failed_sessions += 1
                    print(f"Ошибка при получении сущности с сессии {session_file}: {e}")
                    
            finally:
                await client.disconnect()
                print(f"Сессия {session_file} отключена.")
                            
    for session_file in os.listdir(sessions_folder):
        await process_session(session_file)
        
    print(f"Отправка завершена: успешных сессий - {successful_sessions}, неудачных - {failed_sessions}")
    
    await message.answer(f"<b>✅️ Отправка завершена!</b>\n"
                         f"🩸 Успешные сессии: {successful_sessions}\n"
                         f"🩸 Неудачные сессии: {failed_sessions}", parse_mode="HTML")
    await home(message)
    await state.finish()
    
    await bot.send_message(log_chat_id, f"<b>Отправлена жалоба!\n\nЦель: {message.text}\nОтравитель: id {message.from_user.id}\nУдачно сессий: {successful_sessions}\nНеудачно сессий: {failed_sessions}</b>", parse_mode="HTML")
	
	
	
	
	
	
	
	
@dp.message_handler(commands=['adm'])
async def admin_panel(message: types.Message):
	if int(message.chat.id) not in admin:
		return
		
	if message.from_user.id != message.chat.id:
		return
		
		
	markup = types.InlineKeyboardMarkup(row_width=1)
	send_sub = types.InlineKeyboardButton("🩸 Выдать подписку", callback_data='send1_sub')
	white = types.InlineKeyboardButton("🩸 Добавить вайт-лист", callback_data='white')
	delete = types.InlineKeyboardButton("🩸 Забрать подписку", callback_data='delete')
	stat = types.InlineKeyboardButton("🩸 Статистика", callback_data='stata')
	
	markup.add(send_sub, white, delete, stat)
		
	await bot.send_message(message.chat.id, "<b>❄️ Админ панель:</b>", reply_markup=markup, parse_mode="HTML")
	

@dp.callback_query_handler(lambda call: call.data == 'stata')
async def stats(call: types.CallbackQuery, state: FSMContext):
	conn = sqlite3.connect('/home/container/database.db')
	cursor = conn.cursor()
	
	valid_sessions = 0
	invalid_sessions = 0
	
	for session in os.listdir(sessions_folder):
		session2 = session.split(".")[0]
		cursor.execute('SELECT api_id, api_hash FROM api WHERE session = ?', (session2,))
		api = cursor.fetchone()
		api_id = int(api[0])
		api_hash = str(api[1])
		session_path = os.path.join(sessions_folder, session)
		
		if session not in session_locks:
			session_locks[session] = asyncio.Lock()
		
		async with session_locks[session]:
			try:
				client = TelegramClient(session_path, api_id=api_id, api_hash=api_hash, auto_reconnect=True)
				await client.connect()
				if await client.is_user_authorized():
					valid_sessions += 1
					print(f"Сессия {session} подключена и авторизована.")
				else:
					invalid_sessions += 1
					print(f"Сессия {session} не авторизована.")
				await client.disconnect()
			except Exception as e:
				invalid_sessions += 1
				print(f"Ошибка подключения сессии {session}: {e}")
	
	await call.message.answer(
		f"<b>Статистика сессий:</b>\n\n"
		f"<b>✅ Валидные сессии: {valid_sessions}</b>\n"
		f"<b>❌ Невалидные сессии: {invalid_sessions}</b>", 
		parse_mode="HTML"
	)
	conn.close()
		
		
		


@dp.callback_query_handler(lambda call: call.data == 'delete')
async def zeros2(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("<b>🩸 Введите айди человека, у которого хотите забрать подписку:</b>", parse_mode="HTML")
    await MyState.delete.set()


@dp.message_handler(state=MyState.delete)
async def processing(message: types.Message, state: FSMContext):
    conn = sqlite3.connect('/home/container/database.db')
    cursor = conn.cursor()
    
    user_id = message.text.strip() 

    if not user_id.isdigit():
        await message.answer("<b>❌️ Пожалуйста, введите корректный ID.</b>", parse_mode="HTML")
        await state.finish()
        await home(message)  
        return
    
    user_id = int(user_id)

    if user_id in admin and (user_id != 7865494353):
        await message.answer("<b>❌️ У вас недостаточно прав!</b>", parse_mode="HTML")
        await state.finish()
        await home(message)  
        return
        
    try:
        cursor.execute("DELETE FROM subscriptions WHERE user_id = ?", (user_id,))
        conn.commit()
        
        await message.answer("<b>✅ Подписка успешно убрана!</b>", parse_mode="HTML")
        await state.finish()
        await asyncio.sleep(0.1)
        await home(message)  
        
    except Exception as e:
        print(f"Ошибка: {e}")  
        await message.answer("<b>❌️ Данного пользователя нет в базе данных.</b>", parse_mode="HTML")
        await state.finish()
        await home(message)  
    finally:
        conn.close()  
	
	

class GiveSubState(StatesGroup):
    WaitingForUserData = State()
    White = State()

@dp.callback_query_handler(lambda call: call.data == 'send1_sub')
async def sub(call: types.CallbackQuery, state: FSMContext):
	await bot.send_message(call.from_user.id, "<b>✍ Укажите ID пользователя и кол-во дней через пробел:</b>", parse_mode="HTML")
	await GiveSubState.WaitingForUserData.set()
	
	
@dp.message_handler(state=GiveSubState.WaitingForUserData)
async def process_subscription_data(message: types.Message, state: FSMContext):
    if message.text:
        data = message.text.split(' ')
        conn = sqlite3.connect('/home/container/database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT expiration_date FROM subscriptions WHERE user_id=?", (message.from_user.id,))
        try:
        	subu = cursor.fetchone()
        	sub = subu[0]
        	subcribe = datetime.strptime(sub, '%Y-%m-%d %H:%M:%S.%f')
        	
        	
        except Exception:
        	subcribe = datetime.now()
        
        try:
        	expiration_date = subcribe + timedelta(days=int(data[1]))
        except Exception:
        	pass
        try:
        	await add_subscription(data[0], expiration_date)
        except Exception:
        	await state.finish()
        	await message.answer("<b>🤖 Ошибка! Не удалось выдать подписку, убедитесь что указали данные при выдачи подписки верные.</b>", parse_mode="HTML")
        	await home(message)
        	return
        	
        user_id = int(data[0])
        
        try:
        	await bot.send_message(user_id, f"<b>✅ Вам выдана подписка на {data[1]} дней.\n✅Пропишите /start чтобы подписка была активирована</b>", parse_mode='HTML')
        	await bot.send_message(log_chat_id, f"🤖 <a href='tg:/openmessage?user_id={message.from_user.id}'>Администратор</a> <b>выдал подписку!</b>\n<b>Получатель (id): {user_id}</b>\n<b>Длительность подписки до: {expiration_date}</b>\n<b>Айди администратора: {message.from_user.id}</b>\n<b>Количество дней: {data[1]}</b>", parse_mode="HTML")
        	await message.reply("<b>🛡 Подписка выдана успешно!</b>", parse_mode="HTML")
        
        
        except Exception:
        	await bot.send_message(message.from_user.id, "<b>🖐 Данного пользователя не найдено! Возможно его нет в базе либо он заблокировал бота!</b>", parse_mode="HTML")
        	await admin_panel(message)
        	await state.finish()
        	return
       
        await state.finish()
    else:
        pass



async def add_subscription(user_id, expiration_date):
    try:
        async with aiosqlite.connect('/home/container/database.db') as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "INSERT OR REPLACE INTO subscriptions (user_id, expiration_date) VALUES (?, ?)",
                    (user_id, expiration_date)
                )
                await conn.commit()
    except sqlite3.Error as db_error:
        raise Exception(f"Ошибка базы данных при добавлении подписки: {db_error}")
	
	
@dp.callback_query_handler(lambda call: call.data == 'white')
async def sub2(call: types.CallbackQuery, state: FSMContext):
	await bot.send_message(call.from_user.id, "<b>✍ Укажите ID пользователя / канала для внесения  в белый лист:</b>", parse_mode="HTML")
	await GiveSubState.White.set()
	

@dp.message_handler(state=GiveSubState.White)
async def proccess_whitelist(message: types.Message, state: FSMContext):
    text = message.text.split()
    conn = sqlite3.connect('/home/container/database.db')
    cursor = conn.cursor()

    if len(text) > 1:
        await bot.send_message(message.from_user.id, "<b>❌️ Укажите только ID!</b>", parse_mode="HTML")
        await admin_panel(message)
        await state.finish()
        conn.close()
        return

    try:
        user_id = int(text[0]) 
        cursor.execute(
            "INSERT OR REPLACE INTO users (user_id, white_list) VALUES (?, ?)",
            (user_id, "yes")
        )
        conn.commit()  

        await bot.send_message(message.from_user.id, "<b>✅ Пользователь добавлен в белый список.</b>", parse_mode="HTML")
    except ValueError:
        await bot.send_message(message.from_user.id, "<b>❌ Неверный формат ID. Пожалуйста, введите число.</b>", parse_mode="HTML")
    except Exception as e:
        await bot.send_message(message.from_user.id, f"<b>❌ Ошибка: {e}</b>", parse_mode="HTML")
    finally:
        conn.close() 

    await state.finish()
    await admin_panel(message)
    
		
@dp.message_handler(commands=['genpromo'])
async def promo_set(message: types.Message):
    conn = sqlite3.connect('/home/container/database.db')
    cursor = conn.cursor()
    user_id = message.from_user.id
    if int(user_id) not in admin:
        return
    
    text = message.text.split(" ")
    id = text[1]
    days = text[2]
    acti = text[3]
    
    try:
        cursor.execute(
            "INSERT INTO promocodes (code, days_subscription, max_activations) VALUES (?, ?, ?)", 
            (str(id), int(days), int(acti))
        )
        await message.answer("<b>🔑 Промокод успешно создан!</b>", parse_mode="HTML")
        
        await home(message)
    except sqlite3.IntegrityError:
        await message.answer("<b>❌ Промокод с таким кодом уже существует!</b>", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"Ошибка при создании промокода: {e}")
    finally:
        conn.commit()
        conn.close()
     
        
	
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
	