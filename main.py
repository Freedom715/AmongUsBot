import io

import discord
import requests
from discord.ext import commands
from data import db_session
from data.__all_models import *
from data.game import Game
from data.users import User
from config import settings

db_session.global_init("db/AmongAss.sqlite")

bot = commands.Bot(command_prefix=settings['prefix'])
session = db_session.create_session()
GAME = Game(0, 0, "", "")
session.add(GAME)
session.commit()


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
        elif "импостер" in message.content.lower() and (
                "1" in message.content.lower() or "2" in message.content.lower()):
            imposters = message.content.split(": ")[1].split(", ")
            for name in imposters:
                name = name.lower()
                if not session.query(Names).filter(Names.name == name):
                    session.commit()
                    await message.channel.send("В БД нет имени " + name)
            GAME.imposters = ", ".join(imposters)
            session.commit()
            await message.channel.send(f"в список импосторов внесены: " + ", ".join(imposters))
        elif "импостер" in message.content.lower():
            imposters = session.query(Game).first().imposters
            session.commit()
            await message.channel.send(f"список импосторов: " + imposters)
        elif "профиль" in message.content.lower():
            session = db_session.create_session()
            for owner in session.query(Names):
                print(owner.discord_id)
                if owner.discord_id == message.author:
                    session.commit()
                    await message.channel.send(owner.name)
        if url:
            response = requests.get(url)
            if response.status_code == 200:
                await message.channel.send(f"И тебе привет, {message.author}",
                                           files=get_my_files(response.content))
        session.commit()


client = AmongAssBot()
client.run(settings['token'])
