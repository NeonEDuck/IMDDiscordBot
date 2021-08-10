import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow
from discord_slash.context import ComponentContext
import json
from datetime import datetime
from data_manager import DataManager as data

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
                description='結束日期。(格式：YYYY/MM/DD HH:MM，預設為無限)',
                option_type=3,
                required=False
            ),
            create_option(
                name='max_votes',
                description='一人最多能投幾票。(預設為1)',
                option_type=4,
                required=False
            )
        ]
    }
    @cog_ext.cog_subcommand(**vote_add_kwargs)
    async def _vote_add(self, ctx, title:str, options:str, end_date:str=None, max_votes:int=1):
        vote = data.get_vote()

        if title in vote:
            await ctx.send(f'投票「{title}」已經存在!')
        else:
            if end_date:
                try:
                    datetime.strptime(end_date, '%Y/%m/%d %H:%M')
                except ValueError:
                    await ctx.send(f'時間格式錯誤：YYYY/MM/DD HH:MM')
                    return

            max_votes = max_votes if max_votes > 0 else 1

            vote[title] = {
                'options': [{"name":x.strip(),"votes":0} for x in options.split('|')],
                'end_date': end_date,
                'max_votes': max_votes,
                'voted': {},
                'ended': False
            }
            
            embed=discord.Embed(title=title, color=0xAB4CEA)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
            embed.set_footer(text=f'點擊下面選單以投票' + '≡'*30)

            select = create_actionrow(create_select(
                options=[create_select_option(opt['name'], value=str(i)) for i, opt in enumerate(vote[title]['options'])],
                custom_id='vote_select',
                placeholder='選擇1個選項' if max_votes == 1 else f'選擇最多{max_votes}個選項',  # the placeholder text to show when no options have been chosen
                min_values=1,  # the minimum number of options a user must select
                max_values=max_votes,  # the maximum number of options a user can select
            ))
            
            vote_msg = await ctx.send(embed=embed, components=[select])

            vote[title]['vote_msgs'] = [vote_msg.id]

            data.set_vote(vote)

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
        vote = data.get_vote()

        if title in vote:
            del vote[title]
            data.set_vote(vote)
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
        vote = data.get_vote()

        if not old_title in vote:
            await ctx.send(f'投票「{old_title}」並不存在!')
        elif new_title in vote:
            await ctx.send(f'投票「{new_title}」已經存在，無法取代!')
        else:
            vote[new_title] = vote[old_title]
            del vote[old_title]
            data.set_vote(vote)
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
        vote = data.get_vote()

        if title in vote:
            if opt_idx < 0 or opt_idx >= len(vote[title]["options"]):
                await ctx.send(f'投票「{title}」並沒有第{opt_idx}個選項!')
                return

            vote[title]["options"][opt_idx]["name"] = new_name

            data.set_vote(vote)
            await ctx.send(f'以成功將投票「{title}」選項{opt_idx}編輯成「{new_name}」!')
        else:
            await ctx.send(f'投票「{title}」並不存在!')

    @cog_ext.cog_component()
    async def vote_select(self, ctx: ComponentContext):
        vote = data.get_vote()
        for k, v in vote.items():
            if ctx.origin_message_id in v['vote_msgs']:
                if v['ended']:
                    raise PermissionError

                if str(ctx.author_id) in v['voted']:
                    for i in v['voted'][str(ctx.author_id)]:
                        v['options'][int(i)]["votes"] -= 1

                v['voted'][str(ctx.author_id)] = ctx.selected_options
                
                for i in v['voted'][str(ctx.author_id)]:
                    v['options'][int(i)]["votes"] += 1

                vote[k] = v

                data.set_vote(vote)
                await ctx.send(content=f"投票成功！", hidden = True)
                break
        else:
            raise KeyError

def setup(bot):
    bot.add_cog( Vote(bot) )