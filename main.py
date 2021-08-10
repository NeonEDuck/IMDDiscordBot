from threading import Thread
from flask import Flask, jsonify
import discord
from discord.ext import commands
from discord_slash import SlashCommand
from variable import TOKEN
import init
import error_handler
import app

bot = commands.Bot(command_prefix='/')
slash = SlashCommand(bot, sync_commands=True)
extensions = ['cogs.vote']

@slash.slash(name='ping')
async def _ping(ctx):
    await ctx.send(f'Pong! ({bot.latency*1000}ms)')

if __name__ == '__main__':
    init.setup()
    error_handler.setup(bot)
    server = Thread(target=app.run)
    server.start()

    for ext in extensions:
        bot.load_extension(ext)

    bot.run(TOKEN)