import discord
from discord_slash.context import SlashContext, ComponentContext
import json
from data_manager import DataManager as data
import traceback

def setup(bot):
    
    @bot.event
    async def on_slash_command_error(ctx:SlashContext, ex:Exception) -> None:
        if ex.args and ex.args[0] in ('vote', 'permission'):
            await ctx.send(content=ex.args[1], hidden=True)
        else:
            traceback.print_tb(ex.__traceback__)
            print(ex)

    @bot.event
    async def on_component_callback_error(ctx:ComponentContext, ex:Exception) -> None:
        if ex.args and ex.args[0] in ('vote', 'permission'):
            await ctx.send(content=ex.args[1], hidden=True)
        else:
            traceback.print_tb(ex.__traceback__)
            print(ex)