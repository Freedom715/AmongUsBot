import io
import os
from random import randint, choice

import discord
import pymorphy2
import requests
from discord.ext import commands

from analize import analyze_image_dog
from config import settings
from data import db_session
from data.__all_models import *
from data.game import Game
from data.users import User
from pic_function import *

db_session.global_init("db/AmongAss.sqlite")

bot = commands.Bot(command_prefix=settings['prefix'])
morph = pymorphy2.MorphAnalyzer()


def check_rating():
    session = db_session.create_session()
    for user in session.query(User):
        user.rating = (user.impostor_win + user.crew_win) * 2 - user.failed_game
    session.commit()


def output_list(res):
    session = db_session.create_session()
    res = sorted(res, key=lambda x: (x[1], x[0]), reverse=True)
    result = ""
    for i in range(1, 1 + len(res)):
        idx = session.query(User).filter(User.discord_id == res[i - 1][0]).first().id
        name = session.query(Names).filter(Names.owner_id == idx).all()
        name = name[randint(0, len(name) - 1)].name if len(name) > 1 else name[0].name
        result += name.title() + ": " + str(res[i - 1][1]) + "\n"
    return result


def save_image(path, url, incr=True):
    files = os.listdir(path="/".join(path.split("/")[:-1]))
    response = requests.get(url)
    if response.status_code == 200:
        if incr:
            out = open(path + str(len(files) + 1) + ".jpg", "wb")
        else:
            out = open(path, "wb")
        out.write(response.content)
        out.close()
        return path + str(len(files) + 1) + ".jpg"


def get_my_files(content):
    f = io.BytesIO(content)
    my_file = discord.File(f)
    return my_file


class AmongAssGame():
    def __init__(self):
        self.game = Game(0, 0, "", "")

    def get_crew(self):
        session = db_session.create_session()
        players_name = list(
            map(lambda x: session.query(Names).filter(Names.owner_id == int(x)).first().name,
                self.game.crew.split(", ")))
        return ", ".join(players_name)

    def get_imposters(self):
        session = db_session.create_session()
        players_name = list(
            map(lambda x: session.query(Names).filter(Names.owner_id == int(x)).first().name,
                self.game.imposters.split(", ")))
        return ", ".join(players_name)

    async def start_game(self, message):
        session = db_session.create_session()
        players = []
        for member in message.guild.members:
            print(member)
        for member in message.author.voice.channel.members:
            crew = session.query(User).filter(User.discord_id == str(member)).first()
            if crew:
                players.append(crew)
            else:
                await message.send("Я не знаю такого человека - ", member)
        players_name = list(
            map(lambda x: session.query(Names).filter(Names.owner_id == x.id).first(),
                players))
        players_name = [x.name for x in players_name]
        print(players_name)
        print(players)
        self.game.crew = ", ".join(list(map(lambda x: str(x.id), players)))
        session.commit()
        await message.channel.send(f"В список игроков внесены {len(players_name)}: " + ", ".join(
            players_name))
        return self

    async def entry_to_imposters(self, message, MembersId):
        session = db_session.create_session()
        msg = message.content.lower().split(": ")[1]
        imposters_id, imposters = [], []
        for user_id in msg.split():
            discord_id = MembersId[user_id[1:-1].strip("@").strip("!")]
            imposters.append(
                session.query(User).filter(User.discord_id == discord_id).first())
        imposters_id = list(map(lambda x: str(x.id), imposters))
        imposters = list(
            map(lambda x: session.query(Names).filter(Names.owner_id == x.id).first().name,
                imposters))
        crew, res = self.game.crew.split(", "), self.game.crew.split(", ")
        for player in crew:
            if player in imposters_id:
                res.remove(player)
                self.game.crew = ", ".join(res)
        self.game.imposters = ', '.join(imposters_id)
        self.game.numb_of_crew = len(self.game.crew.split(", "))
        self.game.numb_of_imposters = len(imposters)
        session.commit()
        await message.channel.send(
            f"в список импосторов внесены {self.game.numb_of_imposters}: " + self.get_imposters())

    async def win_func(self, message):
        msg = message.content.lower()
        session = db_session.create_session()
        fin_word = ""
        for word in msg.split():
            if "импостер" in word:
                for idx in self.game.imposters.split(", "):
                    session.query(User).filter(User.id == int(idx)).first().impostor_win += 1
                for name in self.game.crew.split(", "):
                    session.query(User).filter(User.id == int(name)).first().failed_game += 1
                fin_word = "импостеров"
            elif "экипаж" in word:
                for name in self.game.crew.split(", "):
                    session.query(User).filter(User.id == int(name)).first().crew_win += 1
                for name in self.game.imposters.split(", "):
                    session.query(User).filter(User.id == int(name)).first().failed_game += 1
                fin_word = "экипаж"
        if fin_word:
            session.commit()
            await message.channel.send(f"поздравляю {fin_word} с победой")

    async def profile(self, message, guild, roles_id):
        def check_role_id(role_id):
            for role in author.roles:
                if role.id == role_id:
                    return True, role
            return False

        session = db_session.create_session()
        author = message.author
        res = None
        for user in session.query(User):
            if user.discord_id == str(author):
                res = user
        names = [y.name for y in session.query(Names).filter(Names.owner_id == res.id)]
        session.commit()
        await message.channel.send("Ники: " + ', '.join(names))
        await message.channel.send(str(res))
        user = res
        roles = ""
        if 40 >= user.impostor_win > 20 and not check_role_id(
                roles_id["убийца II ранга"]):
            await author.remove_roles(guild.get_role(roles_id["убийца I ранга"]))
            await author.add_roles(guild.get_role(roles_id["убийца II ранга"]))
            roles = 'Вам выдан "Убийца II ранга".'
        elif 60 >= user.impostor_win > 40 and not check_role_id(
                roles_id["убийца III ранга"]):
            await author.remove_roles(guild.get_role(roles_id["убийца II ранга"]))
            await author.add_roles(guild.get_role(roles_id["убийца III ранга"]))
            roles = 'Вам выдан "Убийца III ранга".'
        elif 40 >= user.crew_win > 20 and not check_role_id(
                roles_id["детектив II ранга"]):
            await author.remove_roles(guild.get_role(roles_id["детектив I ранга"]))
            await author.add_roles(guild.get_role(roles_id["детектив II ранга"]))
            roles = 'Вам выдан "Детектив II ранга".'
        elif 60 >= user.crew_win > 40 and not check_role_id(
                roles_id["детектив III ранга"]):
            await author.remove_roles(guild.get_role(roles_id["детектив II ранга"]))
            await author.add_roles(guild.get_role(roles_id["детектив III ранга"]))
            roles = 'Вам выдан "Детектив III ранга".'
        await message.channel.send(", ".join(
            [y.name for y in author.roles[1:]]) + "\n" + roles)


class AmongAssBot(discord.Client):
    def __init__(self):
        super().__init__()
        session = db_session.create_session()
        self.roles_id = {"детектив I ранга": 774184288303448075,
                         "детектив II ранга": 774185308912484363,
                         "детектив III ранга": 774185310786420738,
                         "убийца I ранга": 774185571072868373,
                         "убийца II ранга": 774185704217116672,
                         "убийца III ранга": 774185839377776680,
                         "пидорас.": 779712216467243009}
        self.game = Game(0, 0, "", "")
        self.last_photo = 0
        self.guild = self.get_guild(710796793775915098)
        self.image_filter = {"случайные пиксели": random_pixels_color,
                             "чёрно-белые пиксели": bw_pixels,
                             "осветление": prosvet,
                             "негатив": negativ,
                             "затемнени": zatemn}
        self.members_id = {str(user.tech_id): user.discord_id for user in
                           session.query(User)}
        session.commit()
        """self.members_id = {"500302418425282560": "svoboda21#7898",
                           "551476310879240193": "arsur2004#4404",
                           "768013620730134528": "Гуки, Гуки, они на деревьях#7659",
                           "584385862947569681": "Until_I_Die#1490",
                           "710796981764882444": "Егорио#9836",
                           "322764019721306112": "Ranmin#3616",
                           "694912358010716290": "Маруся#3591",
                           "704739275329110028": "REscurer5#6678",
                           "710801183593463828": "джоне#2915",
                           "699592093491920897": "Krapiva#5217",
                           "437493349730091018": "ketso#0814",
                           "436582679299751938": "Тимоня#1006",
                           "768521164213059626": "просто Мария Алексеевна#8718",
                           "708037859864739890": "___anion___#2509"}"""
    def _rewrite_members_id(self):
        session = db_session.create_session()
        self.members_id = {str(user.tech_id): user.discord_id for user in
                           session.query(User)}
        session.commit()

    def _get_author(self, author):
        return str(author).split("#")[0]

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

    async def send(self, message, text=None, file=None):
        await message.channel.send(text, file=file)

    async def call_member(self, message):
        try:
            dct_member_calls = {"768013620730134528": ("иду, иду",
                                                       discord.File(
                                                           "static/фото/autocalls/ТАНЯ.jpg")),
                                "710796981764882444": (
                                    "Доделываю тату и иду",
                                    discord.File("static/фото/autocalls/ЕГОР.jpg")),
                                "500302418425282560": (
                                    "Я сейчас немного занят, вот вам пока моё фото",
                                    discord.File(
                                        f"static/фото/autocalls/{randint(1, 4)}.jpg")),
                                "584385862947569681": (
                                    "Контракты сами себя не выполнят, выполню приду", None),
                                "551476310879240193": (
                                    f"{choice(('Артём', 'Деня'))} сам себя не выгуляет. Скоро приду.",
                                    None),
                                "322764019721306112": (
                                    "Зачем я вернулась в кс? **Bomb has been planted** Чёрт, скоро приду.",
                                    None),
                                "704739275329110028": ("Зачем кто-то вызвал шлюх?", None),
                                "436582679299751938": (
                                    f"ГЫГЫ ГАГА пошёл нахуй {self._get_author(message.author)}",
                                    None),
                                "708037859864739890": (
                                    "Доедаю стрипсы из KFC. Мне вкусно, не зовите", None),
                                "699592093491920897": ("Я кропива", None),
                                "433700742797459456": (
                                    "Вы хто такие? Я вас не звал, подите на хуй!", None),
                                "437493349730091018": (
                                    "Я пока не могу, за меня ответит моя секретарша", None),
                                "358582354622545941": ("Ебу поней. Просьба отвалить.", None)}
            member_id = message.content[1:-1].strip("@").strip("!")
            call = dct_member_calls[member_id]
            if call[0] != "" and call[1]:
                await self.send(message, text=call[0], file=call[1])
            elif call[0] != "" and call[1] is None:
                await self.send(message, text=call[0])
            else:
                await self.send(message, file=call[1])
        except Exception as e:
            return "Упс! Что-то пошло не так"

    async def measure(self, message):
        await self.send(message,
                        text=f"Я думаю, что это {' '.join(message.content.split()[3:])} на {randint(0, 100)}%")

    async def show_photo_smb(self, message):
        try:
            session = db_session.create_session()
            name = session.query(Names).filter(
                Names.name == " ".join(message.content.lower().split()[2:])).first()
            if name is None:
                await self.send(message,
                                text=f"Имени {name} не существует. Добавьте его вручную, либо обратитесь к админам")
                return
            path = f"static/фото/{name.owner_id}/"
            files = os.listdir(path=path)
            if len(files) > 0:
                path = path + str(randint(1, len(files))) + ".jpg"
                session.query(User).filter(User.id == name.owner_id).first().count_view += 1
                session.commit()
                await self.send(message, file=discord.File(path))
            else:
                await self.send(message, text="У этого юзера пока нет фото :(")
        except Exception as e:
            path = 'Пшл нх'
            await self.send(message,
                            text=f"Упс! Такого файла {path} не существует. Сообщите об этом админу")

    async def check_fucking_rating(self, message):
        session = db_session.create_session()
        max_fuck = 0
        max_user = None
        guild = self.get_guild(710796793775915098)
        for user in session.query(User):
            if user.go_ahead > max_fuck:
                max_user = user
                max_fuck = user.go_ahead
            print(user.tech_id)
            member = guild.get_member(int(user.tech_id))
            try:
                await member.remove_roles(guild.get_role(self.roles_id["пидорас."]))
            except Exception:
                pass
        if max_user is not None:
            member = guild.get_member(max_user.tech_id)
            await member.add_roles(guild.get_role(779712216467243009))
            await self.send(message, text="Новый пидарас. " + max_user.discord_id)

    async def go_ahead(self, message):
        try:
            session = db_session.create_session()
            name = " ".join(message.content.lower().split()[1:])
            print(name)
            if name != "@everyone":
                discord_id = self.members_id[name[2:-1].strip("!")]
                session.query(User).filter(
                    User.discord_id == discord_id).first().go_ahead += 1
                # await self.check_fucking_rating(message)
            else:
                for user in session.query(User):
                    user.go_ahead += 1
            session.commit()
            await self.send(message, text=f"{self._get_author(message.author)} послал {name}")
        except Exception as e:
            await self.send(message, text=f"Упс! Послать не удалось. " + str(e))

    def check_admin(self, message):
        return list(filter(lambda x: "админ" in x.lower(), map(str, message.author.roles)))

    async def add_user(self, message):
        if self.check_admin(message):
            msg = message.content.split(": ")[1]
            path = "static/фото/"
            numb = str(len(os.listdir(path="/".join(path.split("/")[:-1]))) - 2)
            discord_id, tech_id, first_name = msg.split(", ")
            session = db_session.create_session()
            user = User(discord_id, int(tech_id))
            session.add(user)
            name = Names(first_name, int(numb))
            session.add(name)
            session.commit()
            self._rewrite_members_id()
            path += numb
            os.mkdir(path)
            await self.send(message, text=f"Добро пожаловать в игру <@{tech_id}>")

    async def get_compliment(self, message):
        content = message.content
        if len(content.split()) == 1:
            await self.send(message, text="You're amazing")
        else:
            f = open("static/compliment.txt", "rb")
            compliments = f.readlines()
            print(compliments)
            tech_id = content.split()[1]
            phrase = choice(compliments).decode("utf-8").replace("1", self._get_author(message.author),
                                                                 1).replace("2", tech_id, 1)
            await self.send(message, text=phrase)

    async def on_message(self, message):
        url = ""
        session = db_session.create_session()
        author = message.author
        msg = message.content.lower()
        command = msg.startswith("!")
        whats_on_photo = None
        print(message.content)
        print(author)
        if message.attachments:
            print(message.attachments[0].filename)
        if str(author) != "AmongAss#3527":
            if len(message.attachments) > 0 and "нейросеть" == msg:
                url = message.attachments[0].url
                response = requests.get(url)
                if response.status_code == 200:
                    await self.send(message, text=f"Ах ты любитель собак, {self._get_author(author)}",
                                    file=get_my_files(response.content))
            if "на сколько процентов" in msg and message.attachments:
                await self.measure(message)
            elif message.attachments and "обезьяна" in msg and "какая" in msg:
                await self.send(message,
                                text="Я думаю, что это " + choice(
                                    ['шимпанзе', 'гибон', 'пажилой гибон', 'орангутан', 'макака',
                                     'красножопая обезьяна']))
            if "!кот" == msg or "!кошка" == msg:
                whats_on_photo = "cat"
                response = requests.get('https://api.thecatapi.com/v1/images/search')
                json_response = response.json()
                url = json_response[0]['url']
            elif "!собака" == msg or "1кабель" == msg:
                whats_on_photo = "dog"
                response = requests.get('https://dog.ceo/api/breeds/image/random')
                json_response = response.json()
                url = json_response['message']
            elif "!случайное фото" == msg:
                whats_on_photo = "random"
                url = f"https://picsum.photos/{randint(200, 1600)}/{randint(200, 1600)}"

            elif "доброе утро всем" in msg:
                await self.send(message, text="Доброе утро @everyone")
            elif "спокойной ночи всем" in msg:
                await self.send(message, text="Спокойной ночи @everyone")
            elif msg.startswith("!я") or len(
                    list(filter(lambda x: x in ["ем", "пошел", "пошла", "есть"],
                                msg.split()))) == 3:
                await self.send(message, text="Приятного аппетита " + self._get_author(author))
            elif "заткнись" in msg:
                await self.send(message, text="Сам заткнись " + self._get_author(author))
            elif "<@" in msg and len(msg.split()) == 1:
                await self.call_member(message)
            elif "!случайное число" in msg:
                if "от" in msg and "до" in msg:
                    frst_numb = int(msg.split()[-3])
                    secnd_numb = int(msg.split()[-1])
                    await self.send(message, text=randint(frst_numb, secnd_numb))
                else:
                    await self.send(message, text=randint(0, 100))
            elif "комплимент" in msg and command:
                await self.get_compliment(message)
            elif "!пшлнх" in msg or "!пошелнах" in msg:
                await self.go_ahead(message)
            # функции для игры АмонгАсс
            elif "!мут" == msg:
                for member in author.voice.channel.members:
                    print(member)
                    await member.edit(mute=True)
            elif "!мут" in msg and len(msg.split()) >= 2:
                guild = self.get_guild(710796793775915098)
                for name in msg.split()[1:]:
                    name = name[1:-1].strip("@").strip("!")
                    member = guild.get_member(int(name))
                    print(member)
                    if member:
                        if member.voice:
                            await member.edit(mute=True)
                            await self.send(message, text=f"{self._get_author(author)} замутил <@{name}>")
                        else:
                            await self.send(message, text=f"Увы, <@{name}> не в голосовом канале")
            elif "!анмут" == msg:
                for member in author.voice.channel.members:
                    print(member)
                    await member.edit(mute=False)
                await self.send(message, text="Говорить можно")
            elif "!анмут" in msg and len(msg.split()) >= 2:
                guild = self.get_guild(710796793775915098)
                for name in msg.split()[1:]:
                    name = name[1:-1].strip("@").strip("!")
                    member = guild.get_member(int(name))
                    print(member)
                    if member:
                        if member.voice:
                            await member.edit(mute=False)
                            await self.send(message, text=f"{self._get_author(author)} размутил <@{name}>")
                        else:
                            await self.send(message, text=f"Увы, <@{name}> не в голосовом канале")
            elif "!перенос" in msg.lower():
                for member in author.voice.channel.members:
                    print(member)
                    await member.edit(voice_channel=self.guild.get_channel(710797183653249104))
                    await member.edit(voice_channel=self.guild.get_channel(710796794266648656))
            elif "!начать игру" in msg:
                self.game = AmongAssGame()
                await self.game.start_game(message)
            elif "побед" in msg and command:
                await self.game.win_func(message)
            elif "добавить имя -" in msg and command:
                user = session.query(User).filter(User.discord_id == str(author)).first()
                name = Names(msg.split("- ")[1], user.id)
                session.add(name)
                names = list(session.query(Names).filter(Names.owner_id == user.id).all())
                session.commit()
                await self.send(message, text=f"Имена: {', '.join([name.name for name in names])}")
            if "добавить игрока" in message.content.lower() and command:
                await self.add_user(message)
            elif "топ" in msg and command:
                check_rating()
                if "импостер" in msg:
                    res = [(user.discord_id, user.impostor_win) for user in session.query(User)]
                    result = output_list(res)
                    await self.send(message, text=result)
                elif "экипаж" in msg:
                    res = [(user.discord_id, user.crew_win) for user in session.query(User)]
                    result = output_list(res)
                    await self.send(message, text=result)
                else:
                    check_rating()
                    res = [(user.discord_id, user.rating) for user in session.query(User)]
                    result = output_list(res)
                    await self.send(message, text=result)
            elif "экипажа:" in msg and "член" in msg and command:
                await self.send(message, text=list(self.get_all_members()))
            elif "экипаж" == msg and command:
                await self.send(message, text=f"список экипажа: " + self.game.get_crew())
            elif "импостер" in msg and (
                    "1" in msg or "2" in msg) and command:
                await self.game.entry_to_imposters(message, self.members_id)
            elif "импостеры" == msg and command:
                await self.send(message, text="список импостеров: " + self.game.get_imposters())
            elif "профиль" in msg and command:
                await self.game.profile(message, self.get_guild(710796793775915098), self.roles_id)
            # конец функций для игры АмонгАсс
            elif "статистика" in msg and command:
                user = session.query(User).filter(User.discord_id == str(author)).first()
                await self.send(message,
                                text="Послали {} раз\nПосмотрели фото\
 {} раз\nРандомил {} раз".format(user.go_ahead, user.count_view, user.count_random))
            elif "залп!" == msg:
                await self.send(message, text="Пиф-паф")
            elif "обработай фото" in msg and command:
                try:
                    url = message.attachments[0].url
                    name = save_image("static/change/", url, incr=True)
                    a = message.content.split(", ")
                    color = 'r'
                    numb = 100
                    kol_vo = 1
                    up_or_right = 'up'
                    coeff = 1
                    if "рамка" in msg:
                        numb = int(list(filter(lambda x: "рамка" in x, a))[0].split()[1])
                    if "цвет" in msg:
                        color = list(filter(lambda x: "рамка" in x, a))[0].split()[1]
                    filt = list(filter(lambda x: a[0].split()[2:] in x, self.image_filter.keys()))[0]
                    image_filter(name, "result.png", self.image_filter[filt], color=color, numb=numb,
                                 kol_vo=kol_vo, up_or_right=up_or_right, coeff=coeff)
                    await self.send(message, file=discord.File("result.png"))
                except Exception as e:
                    return "Упс! не получилось"
            elif "добавь фото" in msg and message.attachments and command:
                url = message.attachments[0].url
                if "рандом" in msg:
                    save_image(f"static/фото/random/", url)
                    await self.send(message, text="Добавлено фото в рандом")
                elif "ауф" in msg:
                    save_image(f"static/фото/волк/", url)
                    await self.send(message, text="Все мои волки делают - АУФ:point_up:")
                elif len(message.content.split()) > 2:
                    for name in msg.split()[2:]:
                        discord_id = self.members_id[name[2:-1].strip("!")]
                        user = session.query(User).filter(
                            User.discord_id == discord_id).first()
                        save_image(f"static/фото/{str(user.id)}/", url)
                        await self.send(message, text=
                        "Добавлено новое фото " + msg.split()[2])
                else:
                    name = session.query(User).filter(User.discord_id == str(author)).first()
                    save_image(f"static/фото/{name.id}/", url)
                    await self.send(message, text="Добавлено новое ваше фото")
            elif "покажи фото" in msg and len(message.content.split()) >= 3 and command:
                await self.show_photo_smb(message)
            elif "негр" in msg or "пидорас" in msg:
                await self.send(message, text="БАН")
            elif "помощь" in msg:
                await self.send(message, text=
                "Привет, я бот по игре AmongUs. Я веду статистику игр для каждого игрока.\n \
Ты можешь посмотреть свой профиль написав в чат 'профиль'. \n \
Также я могу показать тебе топ импостеров, экипажей и просто топ самых лучших игроков. \
Для этого напиши в чат 'топ игроков/топ импостеров/топ экипажа.'\n\
При старте игры напишите в чат 'начать игру', а после напишите мне кто был импостером, а кто членом экипажа\
'1 или 2 импостера: А, Б' и '(число) членов экипажа: А, Б, В'\
и кто выиграл 'победа импостеров/экипажа' или 'победил экипаж/импостеров'\n \
Кстати, ты можешь добавить себе игровой ник, чтобы твоё имя не мелькало в списках предателей ;). "
                                )
            elif "хуй" in msg:
                path = f"static/фото/{choice(['4', '6', '8'])}/"
                files = os.listdir(path=path)
                await self.send(message,
                                file=discord.File(path + str(randint(1, len(files))) + ".jpg"))
            elif "пизд" in msg:
                path = f"static/фото/{choice(['1', '2', '3', '5', '9', '12', '13', '14'])}/"
                files = os.listdir(path=path)
                await self.send(message,
                                file=discord.File(path + str(randint(1, len(files))) + ".jpg"))
            elif "рандом" in msg:
                session = db_session.create_session()
                path = f"static/фото/{choice((str(randint(1, len(session.query(User).all()))), 'random'))}/"
                while "7" in path or "10" in path or "11" in path:
                    path = f"static/фото/{choice((str(randint(1, 14)), 'random'))}/"
                files = os.listdir(path=path)
                session.query(User).filter(User.discord_id == str(author)).first().count_random += 1
                session.commit()
                await self.send(message,
                                file=discord.File(path + str(randint(1, len(files))) + ".jpg"))
            elif "настроение" in msg and command:
                session = db_session.create_session()
                path = f"static/фото/{choice((str(randint(1, len(session.query(User).all())))))}/"
                while "7" in path or "10" in path or "11" in path:
                    path = f"static/фото/{choice((str(randint(1, 14)), 'random'))}/"
                files = os.listdir(path=path)
                session.query(User).filter(User.discord_id == str(author)).first().count_random += 1
                session.commit()
                await self.send(message,
                                file=discord.File(path + str(randint(1, len(files))) + ".jpg"))
            elif "волк" in msg or "ауф" in msg or "☝" in msg:
                path = f"static/фото/волк/"
                files = os.listdir(path=path)
                await self.send(message,
                                file=discord.File(path + str(randint(1, len(files))) + ".jpg"))
            elif "похож" in msg:
                dct = {"Abyssinian": "Абиссинский кот", "Bengal": "Бенгальский кот",
                       "Birman": "Бирманская кошка", "Bombay": "Бомбей",
                       "British_Shorthair": "Британская Короткошерстная Кошка",
                       "Egyptian_Mau": "Египетский Мау", "Maine_Coon": "Мейн-кун",
                       "Persian": "Персидский кот", "Ragdoll": "Рэгдолл",
                       "Russian_Blue": "Русская Голубая",
                       "Siamese": "Сиамская кошка", "Sphynx": "Сфинкс",
                       "american_bulldog": "американский бульдог",
                       "american_pit_bull_terrier": "американский питбультерьер",
                       "basset_hound": "Бассет",
                       "beagle": "Бигль", "boxer": "боксер", "chihuahua": "чихуахуа",
                       "english_cocker_spaniel": "английский кокер-спаниель",
                       "english_setter": "английский сеттер",
                       "german_shorthaired": "немецкий курцхаар",
                       "great_pyrenees": "Пиренейская горная собака",
                       "havanese": "Гаванский бишон",
                       "japanese_chin": "Японский Хин", "keeshond": "Кеесхонд",
                       "leonberger": "Леонбергер",
                       "miniature_pinscher": "Миниатюрный пинчер",
                       "newfoundland": "Ньюфауленд", "pomeranian": "Померанский шпиц",
                       "pug": "Мопс", "saint_bernard": "Сенбернар", "samoyed": "Самоед",
                       "scottish_terrier": "Шотландский терьер", "shiba_inu": "Сиба-Ину",
                       "staffordshire_bull_terrier": "Стаффордширский бультерьер",
                       "wheaten_terrier": "Ирландский мягкошёрстный пшеничный терьер",
                       "yorkshire_terrier": "Йоркширский терьер", "bom_bom": "Дед Бом-бом",
                       "bushemi": "Стив Бушеми и его глаза", "goblin": "Дмитрий (Гоблин) Пучков",
                       "leopard": "Леопард", "lion": "Лев", "people": "обычный человек",
                       "pepe": "лягушонок Пепе",
                       "sheldon": "Шелдон Купер (Теория Большого взрыва)",
                       "tiger": "Тигр", "yoda": "малыш Йода (Мандалорец)"}
                url = message.attachments[0].url
                save_image("static/analize.jpg", url, incr=False)
                name = analyze_image_dog("/static/analize.jpg".lstrip("/"))
                await self.send(message, text=
                "Хм... Очень похоже на породу " + dct[str(name[0]).split()[0]],
                                file=discord.File(f"static/neuro/{name[0]}.jpg"))
        if url:
            response = requests.get(url)
            if response.status_code == 200 and whats_on_photo:
                if whats_on_photo == "random":
                    await self.send(message, file=get_my_files(response.content))
                elif whats_on_photo == "cat":
                    await self.send(message, text=f"Ах ты любитель кошек, {self._get_author(message.author)}",
                                    file=get_my_files(response.content))
                elif whats_on_photo == "dog":
                    await self.send(message,
                                    text=f"Ах ты любитель собак, {self._get_author(message.author)}",
                                    file=get_my_files(response.content))


client = AmongAssBot()
client.run(settings['token'])
