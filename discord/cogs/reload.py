import asyncio
import os
from nextcord.ext import tasks
from datetime import datetime, timedelta

import nextcord
from cogs.etc.embeds import help_site
from nextcord.ext import commands
from nextcord.ext.commands import CommandNotFound

names = ['__init__.py', 'playground.py', 'gtarp_stuff.py']


async def current_cog_modules(unloaded: list) -> list:
    current_modules = []
    for f in os.listdir('cogs'):
        if f.endswith(".py") and f not in names:
            if f not in unloaded:
                current_modules.append('cogs.' + f[:-3])
    return current_modules


class Reload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.unloaded_modules = []

    @commands.Command
    async def stop(self, ctx, cog_module=None):
        if not ctx.author.id == self.bot.authorid:
            return CommandNotFound()

        print(self.unloaded_modules)

        if not cog_module:
            return await ctx.send(embed=await help_site('admin-unload'))

        if cog_module not in await current_cog_modules(self.unloaded_modules):
            return await ctx.send('The giving module is already unloaded!')

        self.unloaded_modules.append(cog_module)

        self.bot.unload_extension(cog_module)
        await ctx.send(f'{cog_module} successfully unloaded')

    @commands.Command
    async def start(self, ctx, cog_module=None):
        if not ctx.author.id == self.bot.authorid:
            return CommandNotFound()

        if not cog_module:
            return await ctx.send(embed=help_site('admin-load'))

        if cog_module not in await current_cog_modules(self.unloaded_modules):
            return await ctx.send('The giving module is already loaded!')

        self.unloaded_modules.remove(cog_module)

        self.bot.load_extension(cog_module)
        await ctx.send(f'{cog_module} successfully loaded')

    @commands.Command
    async def reload(self, ctx, cog_module=None):
        if not ctx.author.id == self.bot.authorid:
            return CommandNotFound()

        if not cog_module:
            return await ctx.send(embed=help_site('admin-reload'))

        if cog_module in self.unloaded_modules:
            return await ctx.send('The giving module is not Loaded!')

        self.bot.unload_extension(cog_module)
        await asyncio.sleep(1)

        self.bot.load_extension(cog_module)
        await ctx.send(f'{cog_module} Reloaded!')

    @commands.Command
    async def listmodules(self, ctx):
        if not ctx.author.id == self.bot.authorid:
            return CommandNotFound()

        embed = nextcord.Embed(title='All Cogs that are loaded are listed here!',
                               color=self.bot.embed_st,
                               timestamp=self.bot.current_timestamp)

        unloaded = '\n'.join(
            self.unloaded_modules) if self.unloaded_modules else 'All modules running down da street, i here AH AH AH AH '

        embed.add_field(name='Loaded Modules', value='\n'.join(await current_cog_modules(self.unloaded_modules)),
                        inline=False)
        embed.add_field(name='Unloaded Modules', value=unloaded, inline=False)

        embed.add_field(name=f'To reload cog modules, write `{self.bot.prefix}reload (cog_module)`',
                        value=f'Example: `{self.bot.prefix}reload cogs.casino`',
                        inline=False)

        await ctx.send(embed=embed)


class AutoModuleReloader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.changed_modules = []

        self.module_reload_auto_filler.start()

    @tasks.loop(minutes=4, seconds=30)
    async def module_reload_auto_filler(self):
        await self.module_reload_list_updater()

    @commands.group()
    async def modulereload(self, ctx):
        if ctx.author.id != self.bot.authorid:
            raise CommandNotFound

    async def module_reload_list_updater(self):
        now = datetime.now()
        ago = now - timedelta(minutes=5)
        for root, dirs, files in os.walk('cogs/'):
            for fname in files:
                path = os.path.join(root, fname)
                st = os.stat(path)

                if '__pycache__' in str(path) or 'logs' in str(path):
                    continue

                mtime = datetime.fromtimestamp(st.st_mtime)
                module_name = path[:-3].replace('/', '.')
                if mtime > ago and module_name not in self.changed_modules:
                    self.changed_modules.append(module_name)

    @modulereload.command()
    async def reload(self, ctx):
        if ctx.author.id != self.bot.authorid:
            raise CommandNotFound

        for module in self.changed_modules:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
            self.changed_modules.remove(module)

        await ctx.send('Reload was successfully')

    @modulereload.command()
    async def list(self, ctx):
        if ctx.author.id != self.bot.authorid:
            raise CommandNotFound

        return await ctx.send(embed=nextcord.Embed(
            title='List of all Modules that received a change since the last Reload',
            description='\n'.join(self.changed_modules) if self.changed_modules else 'Its empty, no reload needed!',
            color=self.bot.embed_st,
            timestamp=self.bot.current_timestamp))


def setup(bot):
    bot.add_cog(Reload(bot))
    bot.add_cog(AutoModuleReloader(bot))
