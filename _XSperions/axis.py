import discord
from discord.ext import commands
import asyncio
import os, json
import pymongo
from pymongo import MongoClient
from random import randint

#----------------------------------------------+
#                Connections                   |
#----------------------------------------------+
bot_token = str(os.environ.get("bot_token"))
db_token = str(os.environ.get("db_token"))
prefix = "/"

client = commands.Bot(prefix)
client.remove_command("help")
cluster = MongoClient(db_token)
db = cluster["test"]

#----------------------------------------------+
#                  Variables                   |
#----------------------------------------------+
from functions import owner_ids
from emojis import Emojis
emj = Emojis()

#----------------------------------------------+
#                  Functions                   |
#----------------------------------------------+
from functions import display_perms, vis_aliases, error_msg

#----------------------------------------------+
#                    Events                    |
#----------------------------------------------+
@client.event
async def on_ready():
    print(
        f"Bot user: {client.user}\n"
        f"ID: {client.user.id}"
    )

#----------------------------------------------+
#                  Commands                    |
#----------------------------------------------+
@commands.cooldown(1, 1, commands.BucketType.user)
@client.command()
async def test(ctx, *, text=""):
    reply = discord.Embed(
        description=text,
        color=ctx.author.color
    )
    reply.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
    reply.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
    await ctx.send(embed=reply)

#----------------------------------------------+
#                   Errors                     |
#----------------------------------------------+
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        
        def TimeExpand(time):
            if time//60 > 0:
                return str(time//60)+'мин. '+str(time%60)+' сек.'
            elif time > 0:
                return str(time)+' сек.'
            else:
                return f"0.1 сек."
        
        cool_notify = discord.Embed(
                title='⏳ Подождите немного',
                description = f"Осталось {TimeExpand(int(error.retry_after))}"
            )
        await ctx.send(embed=cool_notify)
    
    elif isinstance(error, commands.MissingPermissions):
        if ctx.author.id not in owner_ids:
            reply = discord.Embed(
                title="❌ Недостаточно прав",
                description=f"Необходимые права:\n{display_perms(error.missing_perms)}",
                color=discord.Color.dark_red()
            )
            reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=reply)
        else:
            try:
                await ctx.reinvoke()
            except Exception as e:
                await on_command_error(ctx, e)
    
    elif isinstance(error, commands.MissingRequiredArgument):
        p = ctx.prefix
        cmd = ctx.command
        reply = discord.Embed(
            title=f"🗃 О команде `{cmd.name}`",
            description=(
                f"**Описание:** {cmd.help}\n"
                f"**Использование:** `{p}{cmd.name} {cmd.brief}`\n"
                f"**Пример:** `{p}{cmd.name} {cmd.usage}`\n\n"
                f"{vis_aliases(cmd.aliases)}"
            )
        )
        reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=reply)
    
    elif isinstance(error, commands.BadArgument):
        kw, search, rest = str(error).split(maxsplit=2)
        del rest
        reply = discord.Embed(
            title=f"{emj.cross} | Неверный аргумент",
            description=f"По запросу {search} {error_msg(kw)}. Увы.",
            color=discord.Color.dark_red()
        )
        reply.set_footer(text=str(ctx.author), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=reply)

    else:
        print(error)

#----------------------------------------------+
#                  Loading Cogs                |
#----------------------------------------------+
for file_name in os.listdir("./cogs"):
    if file_name.endswith(".py"):
        client.load_extension(f"cogs.{file_name[:-3]}")

# Running all the stuff
client.run(bot_token)