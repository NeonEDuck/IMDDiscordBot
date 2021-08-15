import discord
from discord.ext import commands, tasks
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow
from discord_slash.context import SlashContext, ComponentContext
from typing import Union, List, Tuple, Dict, Any
from datetime import datetime, timedelta
from utils import get_bit_positions
from data_manager import DataManager as data

class Vote(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        self.vote_closer.start()

    @tasks.loop(seconds=1.0)
    async def vote_closer(self) -> None:
        if self.bot.is_ready():
            for guild_id, title in data.vote_all_keys():
                vote_info:dict = data.get_vote(title, guild_id)
                if vote_info['closed'] or vote_info['close_date'] == None:
                    continue

                if (datetime.utcnow()+timedelta(hours=8)) > datetime.strptime(vote_info['close_date'], '%Y/%m/%d %H:%M'):
                    vote_info['closed'] = True
                    vote_info['forced'] = False
                    data.set_vote(title, vote_info, guild_id)
                    await self.vote_update(self.bot, title, guild_id)
    
    vote_add_kwargs = {
        'base': 'vote',
        'name': 'add',
        'description': '新增一個投票。',
        'base_default_permission': False,
        'options': [
            create_option(
                name='title',
                description='投票標題。',
                option_type=3,
                required=True
            ),
            create_option(
                name='options',
                description='投票選項，請使用「 | 」分開各個選項。(格式：選項A|選項B)',
                option_type=3,
                required=True
            ),
            create_option(
                name='close_date',
                description='關閉日期。(格式：YYYY/MM/DD HH:MM，預設為無限)',
                option_type=3,
                required=False
            ),
            create_option(
                name='max_votes',
                description='一人最多能投幾票。(預設為1)',
                option_type=4,
                required=False
            ),
            create_option(
                name='show_members',
                description='是否在投票選項上顯示成員的選擇。(預設為False)',
                option_type=5,
                required=False
            )
        ]
    }
    @cog_ext.cog_subcommand(**vote_add_kwargs)
    async def _vote_add(self, ctx:SlashContext, title:str, options:str, **kwargs:Dict[str, Union[str, int, bool]]) -> None:
        vote_info:dict = data.get_vote(title, ctx.guild_id)

        close_date:str      = kwargs.get('close_date')
        max_votes:int       = kwargs.get('max_votes', 1)
        show_members:bool   = kwargs.get('show_members', False)

        if vote_info:
            raise ValueError('vote', f'投票「{title}」」已經存在!')
        else:
            if close_date:
                try:
                    datetime.strptime(close_date, '%Y/%m/%d %H:%M')
                except:
                    raise ValueError('vote', 'close_date格式錯誤。(格式：YYYY/MM/DD HH:MM)')

            if max_votes <= 0:
                raise ValueError('vote', 'max_votes必須為大於等於1的值')

            vote_info:dict = {
                'options': [x.strip() for x in options.split('|')],
                'close_date': close_date,
                'max_votes': max_votes,
                'show_members': show_members,
                'closed': False,
                'forced': False,
                'voted': {}
            }

            select = make_select(title, vote_info)
            
            vote_msg = await ctx.send(embed=make_embed(title, vote_info), components=[select])

            vote_info['vote_msgs'] = [str(vote_msg.id)]

            data.set_vote(title, vote_info, ctx.guild_id)

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
    async def _vote_remove(self, ctx:SlashContext, title:str) -> None:
        vote_info:dict = data.get_vote(title, ctx.guild_id)

        if vote_info:
            for msg_id in vote_info['vote_msgs']:
                msg = await ctx.channel.fetch_message(msg_id)
                if msg:
                    await msg.delete()

            data.delete_vote(title, ctx.guild_id)
            await ctx.send(f'以成功將投票「{title}」刪除!', hidden=True)
        else:
            raise KeyError('vote', f'投票「{title}」並不存在!')

    vote_edit_kwargs = {
        'base': 'vote',
        'name': 'edit',
        'description': '編輯指定投票的設定。',
        'options': [
            create_option(
                name='title',
                description='投票標題。',
                option_type=3,
                required=True
            ),
            create_option(
                name='new_title',
                description='新投票標題。',
                option_type=3,
                required=False
            ),
            create_option(
                name='options',
                description='投票選項，請使用「 | 」分開各個選項，使用「 : 」分開索引與名字。(格式：0:選項A|2:選項C)',
                option_type=3,
                required=False
            ),
            create_option(
                name='close_date',
                description='關閉日期。(格式：YYYY/MM/DD HH:MM)',
                option_type=3,
                required=False
            ),
            create_option(
                name='max_votes',
                description='一人最多能投幾票。',
                option_type=4,
                required=False
            ),
            create_option(
                name='show_members',
                description='是否在投票選項上顯示成員的選擇。',
                option_type=5,
                required=False
            )
        ]
    }
    @cog_ext.cog_subcommand(**vote_edit_kwargs)
    async def _vote_edit(self, ctx:SlashContext, title:str, **kwargs:Dict[str, Union[str, int, bool]]) -> None:
        vote_info:dict = data.get_vote(title, ctx.guild_id)

        new_title:str       = kwargs.get('new_title')
        options:str         = kwargs.get('options')
        close_date:str      = kwargs.get('close_date')
        max_votes:int       = kwargs.get('max_votes')
        show_members:bool   = kwargs.get('show_members')

        if not vote_info:
            raise KeyError('vote', f'投票「{title}」並不存在!')
        else:
            if options is not None:
                try:
                    options_list:List[Tuple[int, str]] = sorted([(int(i), name) for i, name in [opt.split(':') for opt in options.split('|')]], key=lambda x:x[0])
                except Exception as ex:
                    raise ValueError('vote', 'options格式錯誤。(格式：0:選項A|2:選項C)')
                for i, name in options_list:
                    if i >= len(vote_info['options']):
                        vote_info['options'].append(name)
                    else:
                        vote_info['options'][i] = name
            if close_date is not None:
                try:
                    datetime.strptime(close_date, '%Y/%m/%d %H:%M')
                except:
                    raise ValueError('vote', 'close_date格式錯誤。(格式：YYYY/MM/DD HH:MM)')
                vote_info['close_date'] = close_date
            if max_votes is not None:
                if max_votes > 0:
                    vote_info['max_votes'] = max_votes
                else:
                    raise ValueError('vote', 'max_votes必須為大於等於1的值')
            if show_members is not None:
                vote_info['show_members'] = show_members

            if new_title is not None:
                if not new_title:
                    raise ValueError('vote', 'new_title不得為空值')
                if data.get_vote(new_title, ctx.guild_id):
                    raise ValueError('vote', f'投票「{new_title}」已經存在，無法取代!')
                data.set_vote(new_title, vote_info, ctx.guild_id)
                data.delete_vote(title, ctx.guild_id)
                await self.vote_update(ctx, new_title, ctx.guild_id)
                await ctx.send(f'以成功編輯投票「{new_title}」!', hidden=True)
            else:
                data.set_vote(title, vote_info, ctx.guild_id)
                await self.vote_update(ctx, title, ctx.guild_id)
                await ctx.send(f'以成功編輯投票「{title}」!', hidden=True)

    vote_close_kwargs = {
        'base': 'vote',
        'name': 'close',
        'description': '關閉指定投票。',
        'options': [
            create_option(
                name='title',
                description='投票標題。',
                option_type=3,
                required=True
            )
        ]
    }
    @cog_ext.cog_subcommand(**vote_close_kwargs)
    async def _vote_close(self, ctx:SlashContext, title:str, close_date:str=None) -> None:
        vote_info:dict = data.get_vote(title, ctx.guild_id)

        if vote_info:
            vote_info['closed'] = True
            vote_info['forced'] = True

            data.set_vote(title, vote_info, ctx.guild_id)
            await self.vote_update(ctx, title, ctx.guild_id)
            await ctx.send(f'以將投票「{title}」關閉!', hidden=True)
        else:
            raise KeyError('vote', f'投票「{title}」並不存在!')

    vote_open_kwargs = {
        'base': 'vote',
        'name': 'open',
        'description': '重新開啟指定投票。',
        'options': [
            create_option(
                name='title',
                description='投票標題。',
                option_type=3,
                required=True
            ),
            create_option(
                name='close_date',
                description='關閉日期。(格式：YYYY/MM/DD HH:MM，預設為原本設定日期)',
                option_type=3,
                required=False
            )
        ]
    }
    @cog_ext.cog_subcommand(**vote_open_kwargs)
    async def _vote_open(self, ctx:SlashContext, title:str, close_date:str=None) -> None:
        vote_info:dict = data.get_vote(title, ctx.guild_id)

        if vote_info:
            vote_info['closed'] = False
            vote_info['forced'] = True
            if close_date:
                try:
                    datetime.strptime(close_date, '%Y/%m/%d %H:%M')
                except:
                    raise ValueError('vote', 'close_date格式錯誤。(格式：YYYY/MM/DD HH:MM)')
                vote_info['close_date'] = close_date
            elif vote_info['close_date'] and (datetime.utcnow()+timedelta(hours=8)) > datetime.strptime(vote_info['close_date'], '%Y/%m/%d %H:%M'):
                vote_info['close_date'] = None

            data.set_vote(title, vote_info, ctx.guild_id)
            await self.vote_update(ctx, title, ctx.guild_id)
            await ctx.send(f'以將投票「{title}」開啟!', hidden=True)
        else:
            raise KeyError('vote', f'投票「{title}」並不存在!')

    vote_show_list_kwargs = {
        'base': 'vote',
        'subcommand_group': 'show',
        'name': 'list',
        'description': '以條件篩選並顯示投票。',
        'options': [
            create_option(
                name='state',
                description='投票狀態。(預設為全部)',
                option_type=3,
                required=False,
                choices=[
                  create_choice(
                    name='全部',
                    value='all'
                  ),
                  create_choice(
                    name='開啟',
                    value='open'
                  ),
                  create_choice(
                    name='關閉',
                    value='close'
                  )
                ]
            )
        ]
    }
    @cog_ext.cog_subcommand(**vote_show_list_kwargs)
    async def _vote_show_list(self, ctx:SlashContext, state:str='all') -> None:
        matchs:List[str] = []
        for title in data.vote_keys(ctx.guild_id):
            vote_info:dict = data.get_vote(title, ctx.guild_id)
            if (vote_info['closed'] and state == 'open') or (not vote_info['closed'] and state == 'close'):
                continue
            
            matchs.append(title)
        
        await ctx.send('符合條件的投票：\n'+'\n'.join([title for title in matchs]) if matchs else '沒有符合條件的投票:(', hidden=True)

    vote_show_result_kwargs = {
        'base': 'vote',
        'subcommand_group': 'show',
        'name': 'result',
        'description': '顯示指定投票結果。',
        'options': [
            create_option(
                name='title',
                description='投票標題。',
                option_type=3,
                required=True
            )
        ]
    }
    @cog_ext.cog_subcommand(**vote_show_result_kwargs)
    async def _vote_show_result(self, ctx:SlashContext, title:str) -> None:
        vote_info:dict = data.get_vote(title, ctx.guild_id)

        if vote_info:
            embed=discord.Embed(title=f'「{title}」', color=0x07A0C3)
            embed.set_author(name='投票結果')
            for i, opt in enumerate(vote_info['options']):
                voted_members:List[str] = [ member_id for member_id, votes in vote_info['voted'].items() if 2**i in get_bit_positions(votes) ]

                if not voted_members:
                    continue
                
                embed.add_field(name=opt, value=' '.join([f'<@{member_id}>' for member_id in voted_members]), inline=False)

            await ctx.send(embed=embed, hidden=True)
        else:
            raise KeyError('vote', f'投票「{title}」並不存在!')

    vote_jumpto_kwargs = {
        'base': 'vote',
        'name': 'jumpto',
        'description': '傳送至指定投票。',
        'options': [
            create_option(
                name='title',
                description='投票標題。',
                option_type=3,
                required=True
            ),
            create_option(
                name='public',
                description='是否公開至聊天室。(預設為False)',
                option_type=5,
                required=False
            )
        ]
    }
    @cog_ext.cog_subcommand(**vote_jumpto_kwargs)
    async def _vote_jumpto(self, ctx:SlashContext, title:str, public:bool=False) -> None:
        vote_info:dict = data.get_vote(title, ctx.guild_id)

        if vote_info:
            for channel in await ctx.guild.fetch_channels():
                for msg_id in vote_info['vote_msgs'][::-1]:
                    try:
                        msg = await channel.fetch_message(msg_id)
                        await ctx.send(f'[點此跳至投票「{title}」]({msg.jump_url})', hidden=not public)
                        break
                    except:
                        pass
                else:
                    continue
                break
            else:
                raise KeyError('vote', f'投票「{title}」並不存在!')
        else:
            raise KeyError('vote', f'投票「{title}」並不存在!')

    vote_notify_kwargs = {
        'base': 'vote',
        'name': 'notify',
        'description': '列出還沒有投票的成員',
        'options': [
            create_option(
                name='title',
                description='投票標題。',
                option_type=3,
                required=True
            ),
            create_option(
                name='public',
                description='是否公開至聊天室。(預設為False)',
                option_type=5,
                required=False
            )
        ]
    }
    @cog_ext.cog_subcommand(**vote_notify_kwargs)
    async def _vote_notify(self, ctx:SlashContext, title:str, public:bool=False) -> None:
        vote_info:dict = data.get_vote(title, ctx.guild_id)

        if vote_info:
            member_ids:str = ' '.join([ f'<@{member.id}>' for member in ctx.guild.members if str(member.id) not in vote_info['voted'] and member != self.bot.user ])
            if member_ids:
                await ctx.send(f'還沒有投「{title}」的成員有：\n{member_ids}', hidden=not public)
            else:
                await ctx.send('全部成員已經都投過此投票!', hidden=True)
        else:
            raise KeyError('vote', f'投票「{title}」並不存在!')

    async def vote_update(self, ctx:Union[commands.Bot, SlashContext, ComponentContext], title:str, guild_id:Union[str, int]) -> None:
        vote_info:dict = data.get_vote(title, guild_id)

        if vote_info:
            embed = make_embed(title, vote_info)
            select = make_select(title, vote_info)

            if ctx is None or type(ctx) == commands.Bot:
                # search in guilds

                tmp_msg_id_list:List[str] = vote_info['vote_msgs']
                for guild in ctx.guilds:
                    for channel in await guild.fetch_channels():
                        if not tmp_msg_id_list:
                            break
                        edited_msg_id_list:List[str] = []
                        for msg_id in tmp_msg_id_list:
                            try:
                                msg = await channel.fetch_message(msg_id)
                                await msg.edit(embed=embed, components=[select])
                                edited_msg_id_list.append(msg_id)
                            except:
                                pass
                        tmp_msg_id_list = [ msg_id for msg_id in tmp_msg_id_list if msg_id not in edited_msg_id_list ]
                    else:
                        continue
                    break
            else:
                # search in channel

                if type(ctx) == ComponentContext:
                    ctx = ctx.origin_message

                for msg_id in vote_info['vote_msgs']:
                    try:
                        msg = await ctx.channel.fetch_message(msg_id)
                        await msg.edit(embed=embed, components=[select])
                    except:
                        pass
        else:
            raise KeyError('vote', f'投票「{title}」並不存在!')


    @cog_ext.cog_component()
    async def vote_select(self, ctx:ComponentContext) -> None:
        for title in data.vote_keys(ctx.guild_id):
            vote_info:dict = data.get_vote(title, ctx.guild_id)
            if str(ctx.origin_message_id) in vote_info['vote_msgs']:
                if vote_info['closed']:
                    raise PermissionError('vote', '投票失敗，投票「{title}」已經結束了！')

                vote_info['voted'][str(ctx.author_id)] = sum(2**int(i) for i in ctx.selected_options)

                data.set_vote(title, vote_info, ctx.guild_id)
                await self.vote_update(ctx, title, ctx.guild_id)
                await ctx.send(content=f"投票成功！\n你投給了：{', '.join([ vote_info['options'][int(i)] for i in ctx.selected_options ])}", hidden=True)
                break
        else:
            raise KeyError('vote', f'投票失敗，投票「{title}」並不存在!')

def make_embed(title:str, vote_info:dict) -> discord.Embed:
    date_text = ''
    if vote_info['closed']:
        if vote_info['forced']:
            if vote_info['close_date']:
                date_text += f"```diff\n- 以被手動截止，原截止日期：{vote_info['close_date']} -\n```"
            else:
                date_text += f"```diff\n- 以被手動截止 -\n```"
        else:
            if vote_info['close_date']:
                date_text += f"```diff\n- 以於{vote_info['close_date']}截止 -\n```"
            else:
                date_text += f"```diff\n- 以截止 -\n```"
    else:
        if vote_info['forced']:
            if vote_info['close_date']:
                date_text += f"```yaml\n- 已重新開啟，截止至{vote_info['close_date']} -\n```"
            else:
                date_text += f"```yaml\n- 已重新開啟，無截止日期 -\n```"
        else:
            if vote_info['close_date']:
                date_text += f"```yaml\n- 截止至{vote_info['close_date']} -\n```"
            else:
                date_text += f"```yaml\n- 無截止日期 -\n```"

    embed=discord.Embed(
        title=f'「{title}」',
        color=0xD64933 if vote_info['closed'] else 0x20B05C
    )
    embed.set_author(name='投票')
    for i, opt in enumerate(vote_info['options']):
        voted_members:List[str] = [ member_id for member_id, votes in vote_info['voted'].items() if 2**i in get_bit_positions(votes) ]
        value = f"票數：{len(voted_members):3}"
        if vote_info['show_members']:
            value += '\n' + ' '.join([ f'<@{member_id}>' for member_id in voted_members ])
        if i == len(vote_info['options'])-1:
            value += f'\n{date_text}'

        embed.add_field(name=opt, value=value, inline=False)
    embed.set_footer(text='≡'*43 + '\n' + ('投票已結束' if vote_info['closed'] else '點擊下面選單以投票'))
    return embed

def make_select(title:str, vote_info:dict) -> dict:
    select = create_actionrow(create_select(
        options=[create_select_option(opt, value=str(i)) for i, opt in enumerate(vote_info['options'])],
        custom_id='vote_select',
        placeholder='選擇1個選項' if vote_info['max_votes'] == 1 else f"選擇最多{vote_info['max_votes']}個選項",
        min_values=1,
        max_values=vote_info['max_votes'],
        disabled=vote_info['closed'],
    ))
    return select

def setup(bot:commands.Bot) -> None:
    bot.add_cog( Vote(bot) )