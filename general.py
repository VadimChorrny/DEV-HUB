import discord
from discord.ext import commands

TOKEN = 'NzM5ODM0MzQ1OTcxNTE1NDY0.XygObQ.eby3KMX6Lw7tONeWn2OJgg_r2wE'
bot = commands.Bot(command_prefix='!')


@bot.command(pass_context=True)  # разрешаем передавать агрументы
async def test(ctx, arg):  # создаем асинхронную фунцию бота
    await ctx.send(arg)  # отправляем обратно аргумент


bot.run(TOKEN)