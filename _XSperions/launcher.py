from os import environ as e


e["bot_token"] = open("secret/test_bot_token.txt", "r").read()
e["db_token"] = open("secret/db_token.txt", "r").read()


import axis