import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import (
    get_all_commands,
    get_guild_command_permissions,
    update_single_command_permissions,
    generate_permissions,
    create_option,
    create_choice
)
from discord_slash.context import SlashContext
from typing import Union, Optional, List, Tuple, Dict, Any
from variable import TOKEN
from data_manager import DataManager as data

class Permission(commands.Cog):
    """權限模組

    這是一個包含所有關於權限的指令、行程的模組。
    """
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """機器人開啟時，上傳權限

        機器人開啟時，會將權限設回預設，所以需要一開始就上傳到discord上。
        """
        await self.update_permission()

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """加入伺服器時，上傳權限

        如果機器人重新加入以前的伺服器，該伺服器權限可能會還是以前的設定，所以需要將預設權限上傳到discord上。
        """
        await self.update_permission(guild=guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """離開伺服器時，從資料庫刪除權限

        離開伺服器時，將權限設為預設，以防未來重新加入時權限還在。
        """
        data.delete_permission(guild.id)

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
                name='base_command',
                description='指令名稱。(只能設定父指令的權限，如"/vote add"，只能設定父指令/vote，而子指令/vote add會隨之套用)',
                option_type=3,
                required=True
            ),
            create_option(
                name='allow',
                description='是否給予權限。',
                option_type=3,
                required=True,
                choices=[
                    create_choice(
                        name='True',
                        value='true'
                    ),
                    create_choice(
                        name='False',
                        value='false'
                    ),
                    create_choice(
                        name='Default',
                        value='default'
                    )
                ]
            )
        ]
    }
    @cog_ext.cog_subcommand(**permission_edit_kwargs)
    async def _permission_edit(self, ctx: SlashContext, base_command: str, role: discord.role.Role, allow: str) -> None:
        """權限編輯指令

        /permission edit <base_command> <role> <allow (true|false|default)>
        編輯一個身份組是否能使用某一系列指令的權限。
        """
        base_command = base_command.strip().split(' ')[0].strip('/')
        result: List[Dict[str, Any]] = await get_all_commands(self.bot.user.id, TOKEN)

        command_id: Optional[str]
        default_permission: bool
        command_id, default_permission = next(((str(item['id']), item['default_permission']) for item in result if item['name'] == base_command), (None, False))

        if command_id is None:
            raise KeyError('permission', f'/{base_command}指令不存在！')

        perm_info: Dict[str, Any] = data.get_permission(ctx.guild_id) or {}

        perm_info[command_id] = perm_info.get(command_id, [])

        if allow == 'default' or default_permission == (allow == 'true'):
            if str(role.id) in perm_info[command_id]:
                perm_info[command_id].remove(str(role.id))
        else:
            if str(role.id) not in perm_info[command_id]:
                perm_info[command_id].append(str(role.id))

        data.set_permission(perm_info, ctx.guild_id)

        try:
            await self.update_permission(command=(command_id, default_permission), guild=ctx.guild)
        except:
            raise KeyError('permission', f'/{base_command}指令不存在！')

        await ctx.send(content=f"已更新/{base_command}指令的權限！", hidden=True)

    permission_get_kwargs = {
        'base': 'permission',
        'name': 'list',
        'description': '顯示所有指令權限清單。'
    }
    @cog_ext.cog_subcommand(**permission_get_kwargs)
    async def _permission_list(self, ctx: SlashContext) -> None:
        """權限清單指令

        /permission list
        顯示一個所有父指令的權限清單。
        """
        result: List[Dict[str, Any]] = await get_all_commands(self.bot.user.id, TOKEN)
        command_list: List[Tuple[str, str, bool]] = [ (str(item['id']), item['name'], item['default_permission']) for item in result ]
        perm_info: Dict[str, Any] = data.get_permission(ctx.guild_id) or {}
        embed: discord.Embed = discord.Embed(title='指令權限清單')
        print(command_list)
        for command_id, base_command, default_permission in command_list:
            role_string: str
            role_ids: List[str]
            if role_ids := perm_info.get(command_id, []):
                role_string = ' '.join([ '@everyone' if role_id == str(ctx.guild_id) else f'<@&{role_id}>' for role_id in role_ids])
            else:
                role_string = '無身份組。'
            embed.add_field(name=f'/{base_command}．預設：{":o:" if default_permission else ":x:"}', value=f'權限設為{":o:" if not default_permission else ":x:"}：\n'+role_string, inline=False)

        await ctx.send(embed=embed, hidden=True)

    async def update_permission(self, command: Tuple[str, bool]=None, guild: discord.Guild=None) -> None:
        """更新權限

        將權限上傳到discord。
        """
        command_list: List[Tuple[str, bool]]
        if not command:
            result: List[Dict[str, Any]] = await get_all_commands(self.bot.user.id, TOKEN)

            command_list = [ (item['id'], item['default_permission']) for item in result if not command or item['name'] == command ]
        else:
            command_list = [command]

        if command_list:
            guilds = [guild] if guild else [guild for guild in self.bot.guilds]
            for guild in guilds:
                for command_id, default_permission in command_list:
                    perm_info: Dict[str, Any] = data.get_permission(guild.id) or {}
                    await update_single_command_permissions(
                        self.bot.user.id,
                        TOKEN,
                        guild.id,
                        command_id,
                        generate_permissions(
                            [int(role_id) for role_id in perm_info.get(command_id, []) if not default_permission],
                            [guild.owner.id],
                            [int(role_id) for role_id in perm_info.get(command_id, []) if default_permission]
                        )
                    )
        else:
            raise KeyError

def setup(bot: commands.Bot) -> None:
    """設置權限模組

    將權限模組加入機器人。
    """
    bot.add_cog( Permission(bot) )