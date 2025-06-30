import os
import shutil
from telethon import TelegramClient
from telethon.errors import AuthKeyDuplicatedError  # Импортируем ошибку
import asyncio
from colorama import Fore, Style, init

# Инициализация colorama
init(autoreset=True)

api_id = '20401021'
api_hash = '7fa6c7f62816334c230cebf77c565c3d'

async def check_session(session_file):
    client = TelegramClient(session_file, api_id, api_hash)
    try:
        await client.connect()
        
        # Пытаемся авторизовать пользователя
        is_authorized = await asyncio.wait_for(client.is_user_authorized(), timeout=3)
        
        await client.disconnect()
        return is_authorized
    except AuthKeyDuplicatedError:  # Обрабатываем ошибку AuthKeyDuplicatedError
        print(f"{Fore.YELLOW}Сессия {session_file} нерабочая из-за использования авторизационного ключа в разных IP!{Style.RESET_ALL}")
        await client.disconnect()
        return False
    except asyncio.TimeoutError:  # Обработка таймаута
        print(f"{Fore.YELLOW}Сессия {session_file} не отвечает!{Style.RESET_ALL}")
        await client.disconnect()
        return False
    except Exception as e:  # Обрабатываем все другие ошибки
        print(f"{Fore.RED}Ошибка при проверке сессии {session_file}: {e}{Style.RESET_ALL}")
        await client.disconnect()
        return False

async def main():
    session_dir = 'sessions'
    unwork_dir = 'unworks'
    
    if not os.path.exists(unwork_dir):
        os.makedirs(unwork_dir)

    session_files = [f for f in os.listdir(session_dir) if f.endswith('.session')]
    
    if not session_files:
        print("Нет доступных сессий. Пожалуйста, создайте аккаунт сначала.")
        return
    
    semaphore = asyncio.Semaphore(100)  # Установите лимит параллельных задач

    async def limited_check(session_file):
        async with semaphore:
            return await check_session(os.path.join(session_dir, session_file))

    tasks = [limited_check(session_file) for session_file in session_files]
    results = await asyncio.gather(*tasks)

    for session_file, result in zip(session_files, results):
        if result:
            print(f"{Fore.GREEN}Сессия {session_file} работает!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Сессия {session_file} не работает!{Style.RESET_ALL}")
            shutil.move(os.path.join(session_dir, session_file), os.path.join(unwork_dir, session_file))

if __name__ == '__main__':
    asyncio.run(main())
