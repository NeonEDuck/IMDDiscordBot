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
    
    vote_add_kwargs = {
        'base': 'vote',
        'name': 'add',
        'description': '新增一個投票。',
        'options': [
            create_option(
                name='title',
                description='投票標題。',
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
        ]
    }
    @cog_ext.cog_subcommand(**vote_add_kwargs)
    async def _vote_add(self, ctx, title:str, options:str, end_date:str=None, multi_vote:bool=False):
        with open('data/vote.json', 'r', encoding='utf-8') as f:
            vote = json.loads(f.read())

        if title in vote:
            await ctx.send(f'投票「{title}」已經存在!')
        else:
            if end_date:
                try:
                    datetime.strptime(end_date, '%Y/%m/%d %H:%M')
                except ValueError:
                    await ctx.send(f'時間格式錯誤：YYYY/MM/DD HH:MM')
                    return

            vote[title] = {
                'options': [{"name":x.strip(),"votes":0} for x in options.split('|')],
                'end_date': end_date,
                'multi_vote': multi_vote,
                'voted': {}
            }
            with open('data/vote.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(vote, indent=4, separators=(',', ':')))
            await ctx.send(f'Create a vote {title=}, {options=}, {end_date=}, {multi_vote=}')

    vote_remove_kwargs = {
        'base': 'vote',
        'name': 'remove',
        'description': '刪除指定投票。',
        'options': [
            create_option(
                name='title',
                description='投票標題。',
                option_type=3,
                required=True
            )
        ]
    }
    @cog_ext.cog_subcommand(**vote_remove_kwargs)
    async def _vote_remove(self, ctx, title:str):
        with open('data/vote.json', 'r', encoding='utf-8') as f:
            vote = json.loads(f.read())

        if title in vote:
            del vote[title]
            with open('data/vote.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(vote, indent=4, separators=(',', ':')))
            await ctx.send(f'以成功將投票「{title}」刪除!')
        else:
            await ctx.send(f'投票「{title}」並不存在!')

    vote_edit_title_kwargs = {
        'base': 'vote',
        'subcommand_group': 'edit',
        'name': 'title',
        'description': '編輯指定投票的名字。',
        'options': [
            create_option(
                name='old_title',
                description='舊投票標題。',
                option_type=3,
                required=True
            ),
            create_option(
                name='new_title',
                description='新投票標題。',
                option_type=3,
                required=True
            )
        ]
    }
    @cog_ext.cog_subcommand(**vote_edit_title_kwargs)
    async def _vote_edit_title(self, ctx, old_title:str, new_title:str):
        with open('data/vote.json', 'r', encoding='utf-8') as f:
            vote = json.loads(f.read())

        if not old_title in vote:
            await ctx.send(f'投票「{old_title}」並不存在!')
        elif new_title in vote:
            await ctx.send(f'投票「{new_title}」已經存在，無法取代!')
        else:
            vote[new_title] = vote[old_title]
            del vote[old_title]
            with open('data/vote.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(vote, indent=4, separators=(',', ':')))
            await ctx.send(f'以成功將投票「{old_title}」名字編輯成「{new_title}」!')

    
    vote_edit_option_kwargs = {
        'base': 'vote',
        'subcommand_group': 'edit',
        'name': 'option',
        'description': '編輯指定投票的選項。',
        'options': [
            create_option(
                name='title',
                description='投票標題。',
                option_type=3,
                required=True
            ),
            create_option(
                name='opt_idx',
                description='投票選項索引。(從0開始)',
                option_type=4,
                required=True
            ),
            create_option(
                name='new_name',
                description='選項名字。',
                option_type=3,
                required=True
            )
        ]
    }
    @cog_ext.cog_subcommand(**vote_edit_option_kwargs)
    async def _vote_edit_option(self, ctx, title:str, opt_idx:int, new_name:str):
        with open('data/vote.json', 'r', encoding='utf-8') as f:
            vote = json.loads(f.read())

        if title in vote:
            if opt_idx < 0 or opt_idx >= len(vote[title]["options"]):
                await ctx.send(f'投票「{title}」並沒有第{opt_idx}個選項!')
                return

            vote[title]["options"][opt_idx]["name"] = new_name

            with open('data/vote.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(vote, indent=4, separators=(',', ':')))
            await ctx.send(f'以成功將投票「{title}」選項{opt_idx}編輯成「{new_name}」!')
        else:
            await ctx.send(f'投票「{title}」並不存在!')

def setup(bot):
    bot.add_cog( Vote(bot) )