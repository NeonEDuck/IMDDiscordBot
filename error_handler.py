import discord
from discord_slash.context import ComponentContext
import json
from data_manager import DataManager as data

def setup(bot):
    
    @bot.event
    async def on_slash_command_error(ctx, ex):
        if ex.args[0] == 'vote':
            await ctx.send(content=ex.args[1], hidden=True)
        else:
            print(ex.with_traceback())

    @bot.event
    async def on_component_callback_error(ctx, ex):
        if ex.args[0] == 'vote':
            await ctx.send(content=ex.args[1], hidden=True)
        else:
            print(ex.with_traceback())