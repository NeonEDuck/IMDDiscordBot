import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import (
    get_all_commands,
    get_guild_command_permissions,
    update_single_command_permissions,
    generate_permissions,
    create_option
)
from discord_slash.context import SlashContext
from typing import Union, List, Tuple, Dict, Any
from variable import TOKEN
from data_manager import DataManager as data

class Permission(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await self.update_permission()

    @commands.Cog.listener()
    async def on_guild_join(self, guild) -> None:
        await self.update_permission(guild=guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild) -> None:
        data.delete_permission(guild.id)
        await self.update_permission(guild=guild)

    permission_edit_kwargs = {
        'base': 'permission',
        'name': 'edit',
        'description': '編輯指令的權限。',
        'base_default_permission': False,
        'options': [
            create_option(
                name='role',
                description='指定身分組。',
                option_type=8,
                required=True
            ),
            create_option(
                name='command',
                description='指令名稱。(只能設定父指令的權限，如"/vote add"，只能設定父指令/vote，而子指令/vote add會隨之套用)',
                option_type=3,
                required=True
            ),
            create_option(
                name='allow',
                description='是否給予權限。',
                option_type=5,
                required=True
            )
        ]
    }
    @cog_ext.cog_subcommand(**permission_edit_kwargs)
    async def _permission_edit(self, ctx:SlashContext, command:str, role:discord.role.Role, allow:bool) -> None:
        command = command.split(' ')[0].strip('/')
        result:List[dict] = await get_all_commands(self.bot.user.id, TOKEN)

        command_id = next((item['id'] for item in result if item['name'] == command), None)

        if command_id is None:
            raise KeyError('permission', f'/{command}指令不存在')

        perm_info = data.get_permission(ctx.guild_id) or {}

        perm_info[command_id] = perm_info.get(command_id, [])
        
        if allow:
            if str(role.id) not in perm_info[command_id]:
                perm_info[command_id].append(str(role.id))
        else:
            if str(role.id) in perm_info[command_id]:
                perm_info[command_id].remove(str(role.id))

        data.set_permission(perm_info, ctx.guild_id)

        try:
            await self.update_permission(command_id=command_id, guild=ctx.guild)
        except:
            raise KeyError('permission', f'/{command}指令不存在')

        await ctx.send(content=f"已更新/{command}指令的權限", hidden=True)

    permission_get_kwargs = {
        'base': 'permission',
        'name': 'list',
        'description': '顯示所有指令權限清單。'
    }
    @cog_ext.cog_subcommand(**permission_get_kwargs)
    async def _permission_list(self, ctx:SlashContext) -> None:
        perm_info = data.get_permission(ctx.guild_id) or {}

        for command, role_ids in perm_info.items():
            embed = discord.Embed(title='指令權限清單')
            embed.add_field(name=f'/{command}', value=' '.join([f'<@&{role_id}>' for role_id in role_ids]), inline=False)

        await ctx.send(embed=embed, hidden=True)

    async def update_permission(self, command:str=None, command_id:Union[str, int]=None, guild=None):
        if not command_id:
            result:List[dict] = await get_all_commands(self.bot.user.id, TOKEN)

            command_ids = [ item['id'] for item in result if not command or item['name'] == command ]
        else:
            command_ids = [command_id]
        
        if command_ids:
            guilds = [guild] if guild else [guild for guild in self.bot.guilds]
            for guild in guilds:
                for command_id in command_ids:
                    perm_info = data.get_permission(guild.id) or {}
                    await update_single_command_permissions(
                        self.bot.user.id,
                        TOKEN,
                        guild.id,
                        command_id,
                        generate_permissions(
                            [int(role_id) for role_id in perm_info.get(command_id, [])],
                            [guild.owner.id]
                        )
                    )
        else:
            raise KeyError

def setup(bot:commands.Bot) -> None:
    bot.add_cog( Permission(bot) )