import io

import discord
import requests
from discord.ext import commands

from config import settings
from data import db_session
from data.__all_models import *
from data.game import Game
from data.users import User

db_session.global_init("db/AmongAss.sqlite")

bot = commands.Bot(command_prefix=settings['prefix'])


def check_rating():
    session = db_session.create_session()
    for user in session.query(User):
        user.rating = (user.impostor_win + user.crew_win) * 2 - user.failed_game


def get_my_files(content):
    f = io.BytesIO(content)
    my_files = [
        discord.File(f, "tmpcat.jpg"),
    ]
    return my_files


class AmongAssBot(discord.Client):
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        for guild in self.guilds:
            print(
                f'{self.user} подключились к чату:\n'
                f'{guild.name}(id: {guild.id})')

    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(
            f'Привет, {member.name}!'
        )

    async def on_message(self, message):
        global GAME
        session = db_session.create_session()
        url = ''
        author = message.author
        print(message.content)
        print(author)
        if "кот" in message.content.lower():
            response = requests.get('https://api.thecatapi.com/v1/images/search')
            json_response = response.json()
            url = json_response[0]['url']
        elif "собака" in message.content.lower():
            response = requests.get('https://dog.ceo/api/breeds/image/random')
            json_response = response.json()
            url = json_response['message']
        elif "начать игру" in message.content.lower():
            GAME = Game(0, 0, "", "")
            session.add(GAME)
            session.commit()
            await message.channel.send(GAME.id)
        elif "побед" in message.content.lower():
            fin_word = "никого"
            for word in message.content.lower().split():
                if "импостер" in word:
                    for name in GAME.imposters.split(", "):
                        indx = session.query(Names).filter(Names.name == name).first().owner_id
                        session.query(User).filter(User.id == indx).first().imposter_win += 1
                    fin_word = "импостеров"
                elif "экипаж" in word:
                    for name in GAME.crew.split(", "):
                        indx = session.query(Names).filter(Names.name == name).first().owner_id
                        session.query(User).filter(User.id == indx).first().crew_win += 1
                    fin_word = "экипаж"
            await message.channel.send(f"поздравляю {fin_word} с победой")
            session.commit()
        elif "добавить имя -" in message.content.lower():
            user = session.query(User).filter(User.discord_id == str(author)).first()
            name = Names(message.content.lower().split("- ")[1], user.id)
            session.add(name)
            names = list(session.query(Names).filter(Names.owner_id == user.id).all())
            await message.channel.send(f"Имена: {', '.join([name.name for name in names])}")
        elif "топ" in message.content.lower():
            check_rating()
            if "импостер" in message.content.lower():
                res = [(user.discord_id, user.impostor_win) for user in session.query(User)]
                res = sorted(res, key=lambda x: (x[1], x[0]))
                for i in range(1, 1 + len(res)):
                    await message.channel.send(
                        str(i) + ") " + "\t".join((res[i - 1][0], str(res[i - 1][1]))))
            elif "экипаж" in message.content.lower():
                res = [(user.discord_id, user.crew_win) for user in session.query(User)]
                res = sorted(res, key=lambda x: (x[1], x[0]))
                for i in range(1, len(res) + 1):
                    await message.channel.send(
                        str(i) + ") " + "\t".join((res[i - 1][0], str(res[i - 1][1]))))
            else:
                res = [(user.discord_id, user.rating) for user in session.query(User)]
                res = sorted(res, key=lambda x: (x[1], x[0]))
                for i in range(1, 1 + len(res)):
                    await message.channel.send(
                        str(i) + ") " + "\t".join((res[i - 1][0], str(res[i - 1][1]))))

        elif "экипажа:" in message.content.lower() and "член" in message.content.lower():
            crew = list(map(lambda x: x.lower(), message.content.split(": ")[1].split(", ")))
            for name in session.query(Names):
                if name.name in crew:
                    session.query(User).filter(User.id == name.owner_id).first().count_crew += 1
            GAME.crew = ", ".join(crew)
            GAME.numb_of_crew = int(message.content[0])
            session.commit()
            await message.channel.send(
                f"в список экипажа внесены {GAME.numb_of_crew}: " + GAME.crew)
        elif "экипаж" == message.content.lower():
            await message.channel.send(f"список экипажа: " + GAME.crew)
        elif "импостер" in message.content.lower() and (
                "1" in message.content.lower() or "2" in message.content.lower()):
            imposters = message.content.split(": ")[1].split(", ")
            for name in imposters:
                name = name.lower()
                if not session.query(Names).filter(Names.name == name):
                    session.commit()
                    await message.channel.send("В БД нет имени " + name)
                else:
                    n = session.query(Names).filter(Names.name == name).first().owner_id
                    session.query(User).filter(User.id == n).first().count_impostor += 1
            GAME.numb_of_imposters = int(message.content[0])
            GAME.imposters = ", ".join(imposters)
            session.commit()
            await message.channel.send(
                f"в список импосторов внесены {GAME.numb_of_imposters}: " + GAME.imposters)
        elif "импостер" in message.content.lower():
            await message.channel.send(f"список импосторов: " + GAME.imposters)
        elif "профиль" in message.content.lower():
            session = db_session.create_session()
            res = None
            for user in session.query(User):
                print(user.discord_id)
                if user.discord_id == str(author):
                    res = user
            session.commit()
            await message.channel.send(str(res))
        elif "помощь" in message.content.lower():
            await message.channel.send(
                "Привет, я бот по игре AmongUs. Я веду статистику игр для каждого игрока.\n \
Ты можешь посмотреть свой профиль написав в чат 'профиль'. \n \
Также я могу показать тебе топ импостеров, экипажей и просто топ самых лучших игроков. \
Для этого напиши в чат 'топ игроков/топ импостеров/топ экипажа.'\n\
При старте игры напишите в чат 'начать игру', а после напишите мне кто был импостером, а кто членом экипажа\
'1 или 2 импостера: А, Б' и '(число) членов экипажа: А, Б, В'\
и кто выиграл 'победа импостеров/экипажа' или 'победил экипаж/импостеров'\n \
 ")
        elif "конец" in message.content.lower():
            session.commit()
        if url:
            response = requests.get(url)
            if response.status_code == 200:
                await message.channel.send(f"И тебе привет, {message.author}",
                                           files=get_my_files(response.content))


client = AmongAssBot()
client.run(settings['token'])
