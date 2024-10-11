import datetime
import pytz
import os
import json
import random

from helper.config import api_id, api_hash, api_phone
from helper.messages import messages
from telethon import events, TelegramClient, functions
from telethon.tl.types import DocumentAttributeAudio
from mutagen import File
from helper.voice import voice_files, music_files

from module.utils.Colors import Colors


def user_in_reputation(user_id):
    reputation_data = load_reputation()
    user_id = str(user_id)
    return user_id in reputation_data['users']

def load_reputation():
    if os.path.exists('files/reputation.json'):
        try:
            with open('files/reputation.json', 'r') as f:
                data = json.load(f)
                return data
        except (json.JSONDecodeError, ValueError):
            return {"users": {}}
    return {"users": {}}

def save_reputation(data):
    with open('files/reputation.json', 'w') as f:
        json.dump(data, f, indent=4)

reputation_data = load_reputation()

def update_reputation(user_id, username, change_value):
    reputation_data = load_reputation()
    user_id = str(user_id)

    if user_id not in reputation_data['users']:
        reputation_data['users'][user_id] = {'username': username, 'reputation': 0}

    reputation_data['users'][user_id]['reputation'] = max(0, reputation_data['users'][user_id]['reputation'] + change_value)

    save_reputation(reputation_data)

def add_user_to_reputation(user_id, username):
    reputation_data = load_reputation()
    user_id = str(user_id)

    if user_id not in reputation_data['users']:
        reputation_data['users'][user_id] = {'username': username, 'reputation': 0}
        save_reputation(reputation_data)
        return True
    return False


def add_user_to_immunity(user_id, username):
    immunity_data = load_immunity()
    user_id = str(user_id)

    if user_id in immunity_data['users']:
        if immunity_data['users'][user_id]['immunity'] == 'off':
            immunity_data['users'][user_id]['immunity'] = 'on'
            save_immunity(immunity_data)
            return False
        return True

    immunity_data['users'][user_id] = {'username': username, 'immunity': 'on'}
    save_immunity(immunity_data)
    return False

def load_bull():
    if os.path.exists('files/bull.json'):
        try:
            with open('files/bull.json', 'r') as f:
                data = json.load(f)
                return data
        except (json.JSONDecodeError, ValueError):
            return {"users": {}}
    return {"users": {}}

def save_bull(data):
    with open('files/bull.json', 'w') as f:
        json.dump(data, f, indent=4)

def add_user_to_bull(user_id, username):
    bull_data = load_bull()
    user_id = str(user_id)

    if user_id in bull_data['users']:
        if bull_data['users'][user_id]['bulling'] == 'off':
            bull_data['users'][user_id]['bulling'] = 'on'
            save_bull(bull_data)
            return False
        return True

    bull_data['users'][user_id] = {'username': username, 'bulling': 'on'}
    save_immunity(bull_data)
    return False

def user_in_bull(user_id):
    bull_data = load_bull()
    user_id = str(user_id)

    if user_id in bull_data['users']:
        return bull_data['users'][user_id].get('bulling') == 'on'
    else:
        return False

def update_bull(user_id, username, change_value):
    bull_data = load_bull()
    user_id = str(user_id)

    if user_id not in bull_data['users']:
        bull_data['users'][user_id] = {'username': username, 'bulling': 'off'}

    bull_data['users'][user_id]['bulling'] = change_value

    save_bull(bull_data)
def load_immunity():
    if os.path.exists('files/immunity.json'):
        try:
            with open('files/immunity.json', 'r') as f:
                data = json.load(f)
                return data
        except (json.JSONDecodeError, ValueError):
            return {"users": {}}
    return {"users": {}}

def save_immunity(data):
    with open('files/immunity.json', 'w') as f:
        json.dump(data, f, indent=4)

def user_in_immunity(user_id):
    immunity_data = load_immunity()
    user_id = str(user_id)

    if user_id in immunity_data['users']:
        return immunity_data['users'][user_id].get('immunity') == 'on'
    else:
        return False

def update_immunity(user_id, username, change_value):
    immunity_data = load_immunity()
    user_id = str(user_id)

    if user_id not in immunity_data['users']:
        immunity_data['users'][user_id] = {'username': username, 'immunity': 'off'}

    immunity_data['users'][user_id]['immunity'] = change_value

    save_immunity(immunity_data)

client = TelegramClient('bullingbot', api_id, api_hash)

@client.on(events.NewMessage(pattern='.voice'))
@client.on(events.NewMessage(pattern='.v'))
async def send_voice(event):
    args = event.message.text.split()

    if len(args) < 2 or not args[1].isdigit():
        await event.edit('Введите число от **1** до **25** для выбора музыки.', parse_mode='Markdown')
        return

    voice_number = int(args[1])

    if voice_number not in voice_files:
        await event.edit('Музыка не найдена! Введите число от **1** до **25**.', parse_mode='Markdown')
        return

    voice_file_path = voice_files[voice_number]

    if not os.path.exists(voice_file_path):
        await event.edit('Файл не найден! Пожалуйста, проверьте наличие файла.')
        return

    try:
        audio = File(voice_file_path)
        duration = int(audio.info.length)
        file = await client.upload_file(voice_file_path)

        await client.send_file(
            event.chat_id,
            file,
            voice=True,
            attributes=[DocumentAttributeAudio(voice=True, duration=duration)],
            reply_to=event.message.reply_to_msg_id,
            caption=''
        )

        await client.delete_messages(event.chat_id, event.message.id)
    except Exception as e:
        await event.edit(f'Не удалось отправить голосовое сообщение! Ошибка: {str(e)}')


@client.on(events.NewMessage(pattern='.setstatus'))
async def set_status(event):
    args = event.message.text.split()

    if len(args) < 2:
        await event.respond('Введите новое описание')
        return

    status = ' '.join(args[1:])

    try:
        await client(functions.account.UpdateProfileRequest(about=status))
        await event.respond(f'**Успешно!** Ваш новый статус: `{status}`', parse_mode='Markdown')
    except Exception as e:
        await event.respond(f'Ошибка при обновлении статуса: {str(e)}')


async def send_music(event, artist, track_number):
    if artist not in music_files:
        await event.edit("Введите: **.m guf** / **.m dtf** / **.m obladaet**")
        return

    tracks = music_files[artist]

    if not track_number or not track_number.isdigit() or int(track_number) not in tracks:
        max_num = len(tracks)
        await event.edit(f'Введите число от **1** до **{max_num}**: **.m {artist} {max_num}**', parse_mode='Markdown')
        return

    track_path = tracks[int(track_number)]

    if not os.path.exists(track_path):
        await event.edit('Файл не найден!')
        return

    try:
        file = await client.upload_file(track_path)
        await client.send_file(event.chat_id, file, voice=False, attributes=[
            DocumentAttributeAudio(duration=180, voice=True)
        ])
        await client.delete_messages(event.chat_id, event.message.id)
    except Exception as e:
        await event.edit(f'Не удалось отправить музыку! Ошибка: {str(e)}')

@client.on(events.NewMessage(pattern='.music'))
@client.on(events.NewMessage(pattern='.m'))
async def sendmusic(event):
    args = event.message.text.split()

    if len(args) < 2:
        await event.edit('Введите: **.m guf** / **.m dtf** / **.m obladaet**', parse_mode='Markdown')
        return

    artist = args[1].lower()
    track_number = args[2] if len(args) > 2 else None

    await send_music(event, artist, track_number)

@client.on(events.NewMessage(pattern='.rp'))
async def rp(event):
    args = event.message.text.split(maxsplit=1)

    if len(args) < 2:
        await event.edit('🚫 Пожалуйста, введите текст для RP после команды. Пример: `.rp [действие]`',
                          parse_mode='Markdown')
        return

    rp = args[1]
    if rp.isdigit():
        await event.edit('Действие не может быть **числом**', parse_mode='Markdown')
        return

    me = await client.get_me()

    if event.is_reply:
        replied_to = await event.get_reply_message()
        if replied_to:
            user_id_other = replied_to.sender_id
            user_id_other_entity = await client.get_entity(user_id_other)
            first_name_other = user_id_other_entity.first_name
            await event.edit(
                f'**[{me.first_name}](tg://user?id={me.id})** `{rp}` **[{first_name_other}](tg://user?id={user_id_other_entity.id})**',
                parse_mode='Markdown')
        else:
            await event.edit('🚫 Не удалось получить информацию о пользователе, на которого вы ответили.')
    else:
        await event.edit('🚫 Нужен реплай для выполнения команды')
@client.on(events.NewMessage(pattern='.rep'))
async def rep(event):
    args = event.message.text.split()

    if len(args) < 2:
        await event.edit("🚫 Укажите действие (add, remove, check, js).")
        return

    command = args[1].lower()

    if command == 'add':
        replied_to = await event.get_reply_message()
        if not replied_to:
            await event.edit("🚫 Нужен реплай")
            return

        try:
            change_value = int(args[2])
        except (IndexError, ValueError):
            await event.edit("🚫 Укажите корректное число для изменения репутации.")
            return

        user_id = replied_to.sender_id

        if not user_in_reputation(user_id):
            await event.edit("🚫 Добавьте пользователя через .rep js")
            return

        username = replied_to.sender.first_name

        update_reputation(user_id, username, change_value)

        await event.edit(f"👍 Репутация **{username}** увеличена на **{change_value}**!", parse_mode="Markdown")

    elif command == 'remove':
        replied_to = await event.get_reply_message()
        if not replied_to:
            await event.edit("🚫 Нужен реплай")
            return

        try:
            change_value = -int(args[2])
        except (IndexError, ValueError):
            await event.edit("🚫 Укажите корректное число для изменения репутации.")
            return

        user_id = replied_to.sender_id

        if not user_in_reputation(user_id):
            await event.edit("🚫 Добавьте пользователя через .rep js")
            return

        username = replied_to.sender.first_name

        update_reputation(user_id, username, change_value)

        await event.edit(f"👎 Репутация **{username}** уменьшена на **{-change_value}**!", parse_mode="Markdown")

    elif command == 'check':
        replied_to = await event.get_reply_message()
        if not replied_to:
            await event.edit("🚫 Нужен реплай")
            return

        user_id = replied_to.sender_id

        if not user_in_reputation(user_id):
            await event.edit("🚫 Добавьте пользователя через .rep js")
            return

        reputation_data = load_reputation()
        user_id_str = str(user_id)

        if user_id_str in reputation_data['users']:
            reputation = reputation_data['users'][user_id_str]['reputation']
            await event.edit(f"ℹ️ Репутация {reputation_data['users'][user_id_str]['username']}: **{reputation}**", parse_mode='Markdown')
        else:
            await event.edit("ℹ️ У этого пользователя пока нет репутации.")

    elif command == 'js':
        replied_to = await event.get_reply_message()
        if not replied_to:
            await event.edit("🚫 Нужен реплай.")
            return

        user_id = replied_to.sender_id
        username = replied_to.sender.first_name

        added = add_user_to_reputation(user_id, username)

        if added:
            await event.edit(f"✅ Пользователь **{username}** добавлен в систему репутации.", parse_mode='Markdown')
        else:
            await event.edit(f"ℹ️ Пользователь **{username}** уже находится в системе репутации.", parse_mode='Markdown')
    else:
        await event.edit("🚫 Неизвестная команда. Используйте: add, remove, check, js.")

@client.on(events.NewMessage(pattern='.immunity'))
@client.on(events.NewMessage(pattern='.i'))
async def immunity(event):
    args = event.message.text.split()

    if len(args) < 2:
        await event.edit("🚫 Укажите действие (add, remove, check).")
        return

    command = args[1].lower()

    replied_to = await event.get_reply_message()
    if not replied_to:
        await event.edit("🚫 Нужен реплай.")
        return

    user_id = replied_to.sender_id
    username = replied_to.sender.first_name

    if command == 'add':
        if user_in_immunity(user_id):
            await event.edit(f"ℹ️ Пользователь **{username}** уже имеет иммунитет.", parse_mode='Markdown')
        else:
            update_immunity(user_id, username, 'on')
            await event.edit(f"✅ Пользователь **{username}** получил иммунитет.", parse_mode='Markdown')

    elif command == 'remove':
        if user_in_immunity(user_id):
            update_immunity(user_id, username, 'off')
            await event.edit(f"✅ Пользователь **{username}** лишён иммунитета.", parse_mode='Markdown')
        else:
            await event.edit(f"ℹ️ Пользователь **{username}** и так не имеет иммунитета.", parse_mode='Markdown')

    elif command == 'check':
        immunity_data = load_immunity()
        user_id_str = str(user_id)
        if user_id_str in immunity_data['users']:
            user_info = immunity_data['users'][user_id_str]
            immunity = user_info.get('immunity', 'off')
            await event.edit(f"ℹ️ Иммунитет {user_info['username']}: **{immunity}**", parse_mode='Markdown')
        else:
            await event.edit("ℹ️ Иммунитет пользователя отключен.")
    else:
        await event.edit("🚫 Неверная команда. Используйте: add, remove, check.")

@client.on(events.NewMessage(pattern='.bull'))
async def bull(event):
    args = event.message.text.split()

    if len(args) < 2:
        await event.edit("🚫 Укажите действие (add, remove, check).")
        return

    command = args[1].lower()

    replied_to = await event.get_reply_message()
    if not replied_to:
        await event.edit("🚫 Нужен реплай.")
        return

    user_id = replied_to.sender_id
    username = replied_to.sender.first_name

    if command == 'add':
        added = add_user_to_bull(user_id, username)
        if user_in_immunity(user_id):
            await event.edit("**Дефаю**☠️.", parse_mode='Markdown')
            return
        else:
            if added:
                await event.edit("**Этот бездарь и так дал мне номер своей мамаши**☠️.", parse_mode='Markdown')
            else:
                update_bull(user_id, username, 'on')
                await event.edit("**Дай номер своей мамаши бездарь**☠️.", parse_mode='Markdown')
    elif command == 'remove':
        if user_in_bull(user_id):
            update_bull(user_id, username, 'off')
            await event.edit("**Идешь нахуй шалава ебанная**👿.", parse_mode='Markdown')
        else:
            await event.edit("**Я и так не унижаю этого человека**", parse_mode='Markdown')
    elif command == 'check':
        replied_to = await event.get_reply_message()
        if not replied_to:
            await event.edit("🚫 Нужен реплай")
            return

        user_id = replied_to.sender_id

        bull_data = load_bull()
        user_id_str = str(user_id)

        if user_id_str in bull_data['users']:
            bull = bull_data['users'][user_id_str]['bulling']
            await event.edit(f"Буллинг над {bull_data['users'][user_id_str]['username']}: **{bull}**", parse_mode='Markdown')
        else:
            await event.edit(f"Буллинг над {bull_data['users'][user_id_str]['username']}: **off**", parse_mode='Markdown')

@client.on(events.NewMessage())
async def bulling_auto_messages(event):
    user_id = event.sender_id

    if user_in_bull(user_id):
        message = random.choice(messages)

        await event.reply(f"**{message}**", parse_mode='Markdown')

moscow = pytz.timezone('Europe/Moscow')
current = datetime.datetime.now(moscow)
time = current.strftime('%H:%M:%S')

input(f'{Colors.WHITE}[{Colors.CYAN}INFO{Colors.WHITE}] [{time}] Бот успешно запустился')
client.start()
client.run_until_disconnected()