import discord
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash import cog_ext
import json
from datetime import datetime


class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @cog_ext.cog_subcommand(
        base='vote',
        name='create',
        description='創建一個投票。',
        options=[
            create_option(
                name='name',
                description='投票名字。',
                option_type=3,
                required=True
            ),
            create_option(
                name='options',
                description='投票選項，請使用「 | 」分開各個選項。',
                option_type=3,
                required=True
            ),
            create_option(
                name='end_date',
                description='結束日期。(格式：YYYY/MM/DD HH:MM)',
                option_type=3,
                required=False
            ),
            create_option(
                name='multi_vote',
                description='一人多票。',
                option_type=5,
                required=False
            )
        ])
    async def _vote_create(self, ctx, name:str, options:str, end_date:str=None, multi_vote:bool=False):
        with open('data/vote.json', 'r', encoding='utf-8') as f:
            vote = json.loads(f.read())

        if name in vote:
            await ctx.send(f'投票「{name}」已經存在!')
        else:
            if end_date:
                try:
                    datetime.strptime(end_date, '%Y/%m/%d %H:%M')
                except ValueError:
                    await ctx.send(f'時間格式錯誤：YYYY/MM/DD HH:MM')
                    return

            vote[name] = {
                'options': {x.strip():0 for x in options.split('|')},
                'end_date': end_date,
                'multi_vote': multi_vote,
                'voted': {}
            }
            with open('data/vote.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(vote, indent=4, separators=(',', ':')))
            await ctx.send(f'Create a vote {name=}, {options=}, {end_date=}, {multi_vote=}')

def setup(bot):
    bot.add_cog( Vote(bot) )