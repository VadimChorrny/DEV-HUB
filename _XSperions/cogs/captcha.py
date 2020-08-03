import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import os, datetime
from random import sample, choice, randint
from PIL import Image, ImageFont, ImageDraw

#----------------------------------------------+
#                  Cluster                     |
#----------------------------------------------+
from pymongo import MongoClient
db_token = str(os.environ.get("db_token"))
cluster = MongoClient(db_token)
db = cluster["curon"]

#----------------------------------------------+
#                 Variables                    |
#----------------------------------------------+
from emojis import Emojis
emj = Emojis()
captcha_native = "captcha_files"
captcha_buffer = "captchas"
plate_side = 256
gap = 16
num = 6

#----------------------------------------------+
#                 Functions                    |
#----------------------------------------------+
async def try_add_role(member, role_or_id):
    role = None
    if isinstance(role_or_id, int):
        role = member.guild.get_role(role_or_id)
    elif isinstance(role_or_id, discord.Role):
        role = role_or_id
    del role_or_id
    if role is not None and role not in member.roles:
        try:
            await member.add_roles(role)
        except Exception:
            pass


class Component:
    def __init__(self, _dir):
        self.image = Image.open(_dir).convert("RGBA")
    
    def transform(self, index):
        sq_side = min(*self.image.size)
        self.image = self.image.crop((0, 0, sq_side, sq_side))
        self.image = self.image.resize((plate_side, plate_side))

        digit = Image.new("RGBA", (plate_side, plate_side))
        draw = ImageDraw.Draw(digit)
        size = plate_side // 2
        luc = (plate_side // 2 - 3 * size // 8, plate_side // 2 - 2 * size // 3)
        font = ImageFont.truetype("fonts/arial.ttf", size=size)
        draw.text(luc, f"{index + 1}", fill=(0, 0, 0, 200), font=font)

        self.image = Image.alpha_composite(self.image, digit)


class CAPTCHA_gen:
    def __init__(self):
        self.id = None
        self.dirs = None
        self.index = None
        self.answer = None
        self.plates = None

    def generate(self):
        now = datetime.datetime.now()
        self.id = f"{now.second}{now.microsecond}"
        self.dirs = [f"{captcha_native}/{el}" for el in sample(os.listdir(captcha_native), num)]
        self.index = randint(0, num - 1)
        self.answer = self.dirs[self.index].rsplit("/", maxsplit=1)[1]
        self.dirs = [f"{folder}/{choice(os.listdir(folder))}" for folder in self.dirs]
        self.plates = Image.new("RGBA", (plate_side * 3 + gap * 2, plate_side * 2 + gap))

        for i, d in enumerate(self.dirs):
            peace = Component(d)
            peace.transform(i)
            ulc = (i % 3 * (plate_side + gap), i // 3 * (plate_side + gap))
            self.plates.paste(peace.image, ulc)

    async def send(self, channel, content=None):
        fname = f"{self.id}.png"
        _dir = f"{captcha_buffer}/{fname}"
        self.plates.save(_dir, "PNG")
        _file = discord.File(_dir, fname)

        try:
            emb = discord.Embed(
                title=f"{emj.refresh} | reCAPTCHA",
                description=f"Пожалуйста, выберите одно изображение, на котором есть **{self.answer}**",
                color=discord.Color.blurple()
            )
            emb.set_image(url=f"attachment://{_file.filename}")
            emb.set_footer(text="Чтобы выбрать изображение, нажмите реакцию с цифрой, которая совпадает с цифрой на изображении.")
            msg = await channel.send(content=content, embed=emb, file=_file)
            del _file
            os.remove(_dir)
            return msg
        except Exception:
            del _file
            os.remove(_dir)
            return None

    def get_verified_role(self, guil_or_id):
        if not isinstance(guil_or_id, int):
            guil_or_id = guil_or_id.id
        collection = db["captcha_config"]
        result = collection.find_one(
            {"_id": guil_or_id},
            projection={"verified_role": True}
        )
        if result is None:
            result = {}
        return result.get("verified_role")


class captcha(commands.Cog):
    def __init__(self, client):
        self.client = client

    #----------------------------------------------+
    #                   Events                     |
    #----------------------------------------------+
    @commands.Cog.listener()
    async def on_ready(self):
        print(f">> captcha cog is loaded")
    
    @commands.Cog.listener()
    async def on_member_join(self):
        pass

    #----------------------------------------------+
    #                  Commands                    |
    #----------------------------------------------+
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command()
    async def verify(self, ctx):
        if not isinstance(ctx.author, discord.Member):
            reply = discord.Embed(
                title=f"{emj.cross} | reCAPTCHA",
                description="Нам важно знать, на каком сервере Вы проходите верификацию. Напишите команду на нужном сервере.",
                color=discord.Color.dark_red()
            )
            reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=reply)

        else:
            msg = None
            CAPTCHA = CAPTCHA_gen()
            vrole_id = CAPTCHA.get_verified_role(ctx.guild.id)
            if vrole_id is None:
                vrole = None
            else:
                vrole = ctx.guild.get_role(vrole_id)
            del vrole_id

            if vrole is None:
                reply = discord.Embed(
                    title=f"{emj.cross} | reCAPTCHA",
                    description="Администрацией не настроена роль верификации, её прохождение невозможно.",
                    color=discord.Color.dark_red()
                )
                reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
                await ctx.send(embed=reply)
            
            elif vrole in ctx.author.roles:
                reply = discord.Embed(
                    title=f"{emj.cross} | reCAPTCHA",
                    description="Вы уже верифицированы.",
                    color=discord.Color.dark_red()
                )
                reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
                await ctx.send(embed=reply)
            
            else:
                async with ctx.channel.typing():
                    CAPTCHA.generate()
                    msg = await CAPTCHA.send(ctx.author)
                    if msg is None:
                        msg = await CAPTCHA.send(ctx.channel, f"{ctx.author.mention}, не могу отправить лично Вам:")
                    else:
                        await ctx.send(f"{ctx.author.mention}, я отправил тест Вам в личных сообщениях.")
            
            if msg is not None:
                channel = msg.channel
                buttons = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]
                for button in buttons:
                    await msg.add_reaction(button)
                
                try:
                    reaction, user = await self.client.wait_for(
                        "reaction_add",
                        check=lambda r, u: r.message.id == msg.id and r.emoji in buttons and u.id == ctx.author.id,
                        timeout=30
                    )
                except asyncio.TimeoutError:
                    reply = discord.Embed(
                        title=f"{emj.refresh} | reCAPTCHA",
                        description=f"Время ожидания истекло. Напишите `{ctx.prefix}verify`, чтобы начать заново.",
                        color=discord.Color.blurple()
                    )
                    try:
                        await channel.send(embed=reply)
                    except Exception:
                        pass
                else:
                    del user
                    ind = buttons.index(reaction.emoji)
                    if ind == CAPTCHA.index:
                        await try_add_role(ctx.author, vrole)
                        reply = discord.Embed(
                            title=f"{emj.tick} | reCAPTCHA",
                            description="Верификация пройдена! Теперь Вы можете зайти на сервер, желаем хорошо провести время!",
                            color=discord.Color.green()
                        )
                        reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
                        await channel.send(embed=reply)
                    else:
                        reply = discord.Embed(
                            title=f"{emj.cross} | reCAPTCHA",
                            description=f"Верификация не пройдена. Чтобы попробовать снова, напишите `{ctx.prefix}verify`",
                            color=discord.Color.dark_red()
                        )
                        reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
                        await channel.send(embed=reply)
                
                await msg.delete()

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.command(
        aliases=["verified-role", "vr"],
        help="настраивает роль, которая будет даваться при верификации",
        brief="Роль",
        usage="@Участник")
    async def verified_role(self, ctx, *, role: discord.Role):
        collection = db["captcha_config"]
        collection.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'verified_role': role.id}},
            upsert=True
        )
        reply = discord.Embed(
            title=f"{emj.tick} | reCAPTCHA | Роль",
            description=f"Роль для прошедших верификацию настроена как **<@&{role.id}>**",
            color=discord.Color.green()
        )
        reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=reply)
    
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.command(aliases=["delete-verified-role", "dvr", "delete-vr"])
    async def delete_verified_role(self, ctx):
        collection = db["captcha_config"]
        collection.update_one(
            {'_id': ctx.guild.id},
            {'$unset': {'verified_role': ""}}
        )
        reply = discord.Embed(
            title=f"{emj.refresh} | reCAPTCHA | Роль",
            description=f"Роль для прошедших верификацию теперь отсутствует.",
            color=discord.Color.blurple()
        )
        reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=reply)

    #----------------------------------------------+
    #                   Errors                     |
    #----------------------------------------------+


def setup(client):
    client.add_cog(captcha(client))