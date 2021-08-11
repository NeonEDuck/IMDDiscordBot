import discord
from discord_slash.context import ComponentContext
import json
from data_manager import DataManager as data

def setup(bot):
    
    # @bot.event
    # async def on_slash_command_error(ctx, ex):
    #     pass

    @bot.event
    async def on_component_callback_error(ctx, ex):
        if str(ctx.custom_id) == 'vote_select':
            if isinstance(ex, KeyError):
                await ctx.send(content=f"投票失敗，此投票不存在！", hidden = True)
            elif isinstance(ex, PermissionError):
                await ctx.send(content=f"投票失敗，此投票已經結束了！", hidden = True)
            else:
                print(ex)