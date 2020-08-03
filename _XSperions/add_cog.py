#----------------------------------------------+
#                Enter Cog name                |
#----------------------------------------------+
COG_NAME = "captcha"

#----------------------------------------------+
#                Cog template                  |
#----------------------------------------------+
cog_template = f"""import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio

#----------------------------------------------+
#                 Functions                    |
#----------------------------------------------+

class {COG_NAME}(commands.Cog):
    def __init__(self, client):
        self.client = client

    #----------------------------------------------+
    #                   Events                     |
    #----------------------------------------------+
    @commands.Cog.listener()
    async def on_ready(self):
        print(f">> {COG_NAME} cog is loaded")

    #----------------------------------------------+
    #                  Commands                    |
    #----------------------------------------------+


    #----------------------------------------------+
    #                   Errors                     |
    #----------------------------------------------+


def setup(client):
    client.add_cog({COG_NAME}(client))"""

import os
if "cogs" not in os.listdir("."):
    print("No [cogs] folder in current directory")
elif f"{COG_NAME}.py" in os.listdir("cogs"):
    print(f"[{COG_NAME}.py] already exists")
else:
    with open(f"cogs/{COG_NAME}.py", "w", encoding="utf8") as _file:
        _file.write(cog_template)
    print("Cog is deployed")