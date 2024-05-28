import asyncio
import re

from telethon import TelegramClient, events
import requests

api_id = 'your_id'
api_hash = 'your_hash'

bot_token = 'your_token'

# Функция для обработки запросов пользователя
async def handle_request(event):
    # Получаем текст запроса пользователя
    user_input = event.text.strip()

    # Проверяем, является ли ввод почтовым индексом
    if user_input.isdigit():
        # Запрос по почтовому индексу
        await search_by_postal_code(event, user_input)
    else:
        # Поиск по адресу города
        match = re.match(r'^[a-zA-Z]+(?:[\s-][a-zA-Z]+)*$', user_input)
        if match:
            await search_by_city(event, user_input)
        else:
            message = "🏙️ Пожалуйста, введите корректный почтовый индекс или адрес города."
            await event.respond(message)

# Функция для поиска по почтовому индексу
async def search_by_postal_code(event, user_input):
    # Итерируемся по списку стран для поиска
    for country_code in ['US', 'UK', 'RU', 'FR']:
        # Формируем URL для запроса к API zippopotam для текущей страны
        url = f'https://api.zippopotam.us/{country_code}/{user_input}'

        # Отправляем GET-запрос к API zippopotam
        response = requests.get(url)

        # Проверяем успешность запроса
        if response.status_code == 200:
            # Получаем данные в формате JSON
            data = response.json()

            # Извлекаем необходимые данные
            post_code = data.get('post code')
            country = data.get('country')
            country_abbreviation = data.get('country abbreviation')
            places = data.get('places')

            # Формируем сообщение для пользователя
            message = f"📬 Почтовый индекс: {post_code}\n🌍 Страна: {country} ({country_abbreviation})\n"
            for place in places:
                place_name = place.get('place name')
                state = place.get('state')
                state_abbreviation = place.get('state abbreviation')
                longitude = place.get('longitude')
                latitude = place.get('latitude')
                message += f"🎯 Расположение: {place_name}\n🌁 Область/Штат: {state} ({state_abbreviation})\n📏 Долгота: {longitude}\n📏 Широта: {latitude}\n\n"

            # Отправляем сообщение пользователю
            await event.respond(message)
            return  # Завершаем функцию после первого успешного результата

    # Если почтовый индекс не найден в указанных странах, отправляем сообщение пользователю
    message = "🛑 Почтовый индекс не найден в доступных странах."
    await event.respond(message)

# Функция для поиска по адресу города (только для США)
async def search_by_city(event, user_input):
    # Итерируемся по всем штатам США
    for state_code in ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']:
        # Формируем URL для запроса к API zippopotam для текущего штата и города
        url = f'https://api.zippopotam.us/US/{state_code}/{user_input}'

        # Отправляем GET-запрос к API zippopotam
        response = requests.get(url)

        # Проверяем успешность запроса
        if response.status_code == 200:
            # Получаем данные в формате JSON
            data = response.json()

            # Извлекаем необходимые данные
            country = "United States"  # Форматируем название страны
            place_name = data.get('place name')
            state = data.get('state')
            state_abbreviation = data.get('state abbreviation')
            country_abbreviation = data.get('country abbreviation')
            places = data.get('places')

            # Формируем сообщение для пользователя
            message = f"🌍 Страна: {country}\n🏙️ Город: {place_name}\n🌁 Штат: {state} ({state_abbreviation})\n"
            for place in places:
                place_name = place.get('place name')
                state = place.get('state')
                state_abbreviation = place.get('state abbreviation')
                longitude = place.get('longitude')
                latitude = place.get('latitude')
            message += f"📏 Долгота: {longitude}\n📏 Широта: {latitude}\n\n"
            
            # Отправляем сообщение пользователю
            await event.respond(message)
            return  # Завершаем функцию после первого успешного результата

    # Если город не найден во всех штатах, отправляем сообщение пользователю
    message = "🛑 Город не найден в США."
    await event.respond(message)

# Функция для запуска бота
async def main():
    # Создаем клиента Telegram
    client = TelegramClient('session_name', api_id, api_hash)

    # Ожидаем запросов от пользователей
    @client.on(events.NewMessage)
    async def my_event_handler(event):
        await handle_request(event)

    # Подключаемся к серверам Telegram
    await client.start(bot_token=bot_token)

    # Запускаем бота
    await client.run_until_disconnected()

# Запускаем основную функцию
if __name__ == '__main__':
    asyncio.run(main())

