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
last_photo = 0
ROLES_ID = {"детектив I ранга": 774184288303448075,
            "детектив II ранга": 774185308912484363,
            "детектив III ранга": 774185310786420738,
            "убийца I ранга": 774185571072868373,
            "убийца II ранга": 774185704217116672,
            "убийца III ранга": 774185839377776680}
ImageFilters = {"случайные пиксели": random_pixels_color,
                "чёрно-белые пиксели": bw_pixels,
                "осветление": prosvet,
                "негатив": negativ,
                "затемнени": zatemn}


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
        name = name[randint(0, len(name) - 1)].name
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
        global last_photo, GAME

        async def send(text=None, file=None):
            await message.channel.send(text, file=file)

        session = db_session.create_session()
        url = ''
        whats_on_photo = ""
        author = message.author
        msg = message.content.lower()
        print(message.content)
        if message.attachments:
            print(message.attachments[0].filename)
        if len(message.attachments) > 0 and "нейросеть" == msg:
            url = message.attachments[0].url
            response = requests.get(url)
            if response.status_code == 200:
                await send(text=f"Ах ты любитель собак, {author}",
                           file=get_my_files(response.content))
        if len(message.attachments) > 0 and "шлю" in msg:
            await send(text=f"Я думаю, что это шлюха на {randint(0, 100)}%")
        elif len(message.attachments) > 0 and "гей" in msg:
            await send(text=f"Я думаю, что это гей на {randint(0, 100)}%")
        elif len(
                message.attachments) > 0 and "обезьяна" in msg and "процентов" in msg:
            await send(text=f"Я думаю, что это обезьяна на {randint(0, 100)}%")
        elif len(
                message.attachments) > 0 and "обезьяна" in msg and "какая" in msg:
            await send(text=f"Я думаю, что это {choice(['шимпанзе', 'гибон', 'пажилой гибон', 'орангутан', 'макака', 'красножопая обезьяна'])}")
        print(author)
        if str(author) != "AmongAss#3527":
            if "кот" == msg or "кошка" == msg:
                whats_on_photo = "cat"
                response = requests.get('https://api.thecatapi.com/v1/images/search')
                json_response = response.json()
                url = json_response[0]['url']
            elif "собака" == msg or "кабель" == msg:
                whats_on_photo = "dog"
                response = requests.get('https://dog.ceo/api/breeds/image/random')
                json_response = response.json()
                url = json_response['message']
            elif "я ем" in msg:
                await send(text="Приятного аппетита " + str(author))
            elif "заткнись" in msg:
                await send(text="Сам заткнись " + str(author))
            elif "начать игру" in msg:
                GAME = Game(0, 0, "", "")
                session.add(GAME)
                session.commit()
                await send(text=GAME.id)
            elif "!мут" == msg:
                for member in message.author.voice.channel.members:
                    print(member)
                    await member.edit(mute=True)
            elif "!анмут" == msg:
                for member in message.author.voice.channel.members:
                    print(member)
                    await member.edit(mute=False)
                await send(text="Говорить можно")
            elif "<@" in msg and len(msg.split()) == 1:
                if "768013620730134528" in message.content:
                    await send(text="Иду, иду", file=discord.File("static/фото/autocalls/ТАНЯ.jpg"))
                elif "710796981764882444" in msg:
                    await send(text="Доделываю тату и иду",
                               file=discord.File("static/фото/autocalls/ЕГОР.jpg"))
                elif "500302418425282560" in msg:
                    await send(text="Я сейчас немного занят, вот вам пока моё фото",
                               file=discord.File(
                                   f"static/фото/autocalls/{randint(1, 4)}.jpg"))
                elif "584385862947569681" in msg:
                    await send(text="Контракты сами себя не выполнят, выполню приду")
                elif "551476310879240193" in msg:
                    await send(text=f"{choice(('Артём', 'Деня'))} сам себя не выгуляет. Скоро приду.")
                elif "322764019721306112" in msg:
                    await send(text=
                        "Зачем я вернулась в кс? **Bomb has been planted** Чёрт, скоро приду.")
                elif "704739275329110028" in msg:
                    await send(text="Зачем кто-то вызвал шлюх?")
                elif "436582679299751938" in msg:
                    await send(text=f"ГЫГЫ ГАГА пошёл нахуй {author}")
                elif "708037859864739890" in msg:
                    await send(text="Доедаю стрипсы из KFC. Мне вкусно, не зовите")
                elif "699592093491920897" in msg:
                    await send(text="Я кропива")
                elif "433700742797459456" in msg:
                    await send(text="Вы хто такие? Я вас не звал, подите на хуй!")
            elif "побед" in msg:
                fin_word = ""
                for word in msg.split():
                    if "импостер" in word:
                        for name in GAME.imposters.split(", "):
                            indx = session.query(Names).filter(Names.name == name).first().owner_id
                            session.query(User).filter(User.id == indx).first().impostor_win += 1
                        for name in GAME.crew.split(", "):
                            indx = session.query(Names).filter(Names.name == name).first().owner_id
                            session.query(User).filter(User.id == indx).first().failed_game += 1
                        fin_word = "импостеров"
                    elif "экипаж" in word:
                        for name in GAME.crew.split(", "):
                            indx = session.query(Names).filter(Names.name == name).first().owner_id
                            session.query(User).filter(User.id == indx).first().crew_win += 1
                        for name in GAME.imposters.split(", "):
                            indx = session.query(Names).filter(Names.name == name).first().owner_id
                            session.query(User).filter(User.id == indx).first().failed_game += 1
                        fin_word = "экипаж"
                if fin_word:
                    session.commit()
                    await send(text=f"поздравляю {fin_word} с победой")
            elif "случайное число" in msg:
                if "от" in msg and "до" in msg:
                    frst_numb = int(msg.split()[-3])
                    secnd_numb = int(msg.split()[-1])
                    await send(text=randint(frst_numb, secnd_numb))
                else:
                    await send(text=randint(0, 100))
            elif "случайное фото" == msg:
                whats_on_photo = "random"
                url = f"https://picsum.photos/{randint(200, 1600)}/{randint(200, 1600)}"
            elif "доброе утро всем" in msg:
                await send(text="Доброе утро @everyone")
            elif "спокойной ночи всем" in msg:
                await send(text="Спокойной ночи @everyone")
            elif "добавить имя -" in msg:
                user = session.query(User).filter(User.discord_id == str(author)).first()
                name = Names(msg.split("- ")[1], user.id)
                session.add(name)
                names = list(session.query(Names).filter(Names.owner_id == user.id).all())
                session.commit()
                await send(text=f"Имена: {', '.join([name.name for name in names])}")
            elif "топ" in msg:
                check_rating()
                if "импостер" in msg:
                    res = [(user.discord_id, user.impostor_win) for user in session.query(User)]
                    result = output_list(res)
                    await send(text=result)
                elif "экипаж" in msg:
                    res = [(user.discord_id, user.crew_win) for user in session.query(User)]
                    result = output_list(res)
                    await send(text=result)
                else:
                    check_rating()
                    res = [(user.discord_id, user.rating) for user in session.query(User)]
                    result = output_list(res)
                    await send(text=result)
            elif "экипажа:" in msg and "член" in msg:
                crew = list(map(lambda x: x.lower(), message.content.split(": ")[1].split(", ")))
                for name in session.query(Names):
                    if name.name in crew:
                        session.query(User).filter(User.id == name.owner_id).first().count_crew += 1
                GAME.crew = ", ".join(crew)
                GAME.numb_of_crew = int(message.content[0])
                session.commit()
                await send(text=
                    f"в список экипажа внесены {GAME.numb_of_crew}: " + GAME.crew)
            elif "экипаж" == msg:
                await send(text=f"список экипажа: " + GAME.crew)
            elif "залп!" == msg:
                await send(text="Пиф-паф")
            elif "обработай фото" in msg:
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
                    filt = list(filter(lambda x: a[0].split()[2:] in x, ImageFilters.keys()))[0]
                    image_filter(name, "result.png", ImageFilters[filt], color=color, numb=numb,
                                 kol_vo=kol_vo, up_or_right=up_or_right, coeff=coeff)
                    await send(file=discord.File("result.png"))
                except Exception as e:
                    return "Упс! не получилось"
            elif "добавь фото" in msg and message.attachments:
                url = message.attachments[0].url
                if "рандом" in msg:
                    save_image(f"static/фото/15/", url)
                    await send(text="Добавлено фото в рандом")
                elif len(message.content.split()) > 2:
                    for name in msg.split()[2:]:
                        name = session.query(Names).filter(
                            Names.name == name).first()
                        save_image(f"static/фото/{name.owner_id}/", url)
                        await send(text=
                            "Добавлено новое фото " + msg.split()[2])
                else:
                    name = session.query(User).filter(User.discord_id == str(author)).first()
                    save_image(f"static/фото/{name.id}/", url)
                    await send(text="Добавлено новое ваше фото")
            elif "покажи фото" in msg and len(message.content.split()) == 2:
                name = session.query(Names).filter(
                    Names.name == msg.split()[1]).first()
                path = f"static/фото/{name.owner_id}/"
                files = os.listdir(path=path)
                await send(
                    file=discord.File(path + str(randint(1, len(files))) + ".jpg"))
            elif "импостер" in msg and (
                    "1" in msg or "2" in msg):
                imposters = message.content.split(": ")[1].split(", ")
                for name in imposters:
                    name = name.lower()
                    if not session.query(Names).filter(Names.name == name):
                        session.commit()
                        await send(text="В БД нет имени " + name)
                    else:
                        n = session.query(Names).filter(Names.name == name).first().owner_id
                        session.query(User).filter(User.id == n).first().count_impostor += 1
                GAME.numb_of_imposters = int(message.content[0])
                GAME.imposters = ", ".join(imposters)
                session.commit()
                await send(text=
                    f"в список импосторов внесены {GAME.numb_of_imposters}: " + GAME.imposters)
            elif "импостеры" == msg:
                await send(text=f"список импосторов: " + GAME.imposters)
            elif "профиль" in msg:
                def check_role_id(role_id):
                    for role in author.roles:
                        if role.id == role_id:
                            return True, role
                    return False

                session = db_session.create_session()
                res = None
                for user in session.query(User):
                    if user.discord_id == str(author):
                        res = user
                names = [y.name for y in session.query(Names).filter(Names.owner_id == res.id)]
                session.commit()
                await send(text="Ники: " + ', '.join(names))
                await send(text=str(res))
                user = res
                roles = ""
                guild = self.get_guild(710796793775915098)
                # bot = guild.get_member(774253134368604190)
                if 40 >= user.impostor_win > 20 and not check_role_id(ROLES_ID["убийца II ранга"]):
                    await author.remove_roles(guild.get_role(ROLES_ID["убийца I ранга"]))
                    await author.add_roles(guild.get_role(ROLES_ID["убийца II ранга"]))
                    roles = 'Вам выдан "Убийца II ранга".'
                elif 60 >= user.impostor_win > 40 and not check_role_id(
                        ROLES_ID["убийца III ранга"]):
                    await author.remove_roles(guild.get_role(ROLES_ID["убийца II ранга"]))
                    await author.add_roles(guild.get_role(ROLES_ID["убийца III ранга"]))
                    roles = 'Вам выдан "Убийца III ранга".'
                elif 40 >= user.crew_win > 20 and not check_role_id(ROLES_ID["детектив II ранга"]):
                    await author.remove_roles(guild.get_role(ROLES_ID["детектив I ранга"]))
                    await author.add_roles(guild.get_role(ROLES_ID["детектив II ранга"]))
                    roles = 'Вам выдан "Детектив II ранга".'
                elif 60 >= user.crew_win > 40 and not check_role_id(ROLES_ID["детектив III ранга"]):
                    await author.remove_roles(guild.get_role(ROLES_ID["детектив II ранга"]))
                    await author.add_roles(guild.get_role(ROLES_ID["детектив III ранга"]))
                    roles = 'Вам выдан "Детектив III ранга".'
                await send(text=
                    ", ".join(
                        [y.name for y in author.roles[1:]]) + "\n" + roles)
            elif "помощь" in msg:
                await send(text=
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
                await send(file=discord.File(path + str(randint(1, len(files))) + ".jpg"))
            elif "пизда" in msg:
                path = f"static/фото/{choice(['1', '2', '3', '5', '7', '9', '10', '11', '12', '13'])}/"
                files = os.listdir(path=path)
                await send(file=discord.File(path + str(randint(1, len(files))) + ".jpg"))
            elif "рандом" in msg:
                path = f"static/фото/{str(randint(1, 14))}/"
                files = os.listdir(path=path)
                await send(file=discord.File(path + str(randint(1, len(files))) + ".jpg"))
            elif "волк" in msg or "ауф" in msg or "☝" in msg:
                path = f"static/фото/волк/"
                files = os.listdir(path=path)
                await send(file=discord.File(path + str(randint(1, len(files))) + ".jpg"))
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
                await send(text=
                    "Хм... Очень похоже на породу " + dct[str(name[0]).split()[0]],
                    file=discord.File(f"static/neuro/{name[0]}.jpg"))
        if url:
            response = requests.get(url)
            if response.status_code == 200:
                if whats_on_photo == "random":
                    await send(file=get_my_files(response.content))
                elif whats_on_photo == "cat":
                    await send(text=f"Ах ты любитель кошек, {message.author}",
                               file=get_my_files(response.content))
                elif whats_on_photo == "dog":
                    await send(text=f"Ах ты любитель собак, {message.author}",
                               file=get_my_files(response.content))


client = AmongAssBot()
client.run(settings['token'])
