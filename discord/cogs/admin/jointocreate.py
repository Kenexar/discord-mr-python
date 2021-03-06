from cogs.etc.presets import fillup
from nextcord.ext import commands
from nextcord.ext.commands import has_permissions


class JoinToCreate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.jtc_channel: dict = fillup(5)
        self.jtc_category: dict = fillup(6)

        self.jtc_current_channel = []

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Todo:
        #  Restart resitense
        guild_has_jtc = self.jtc_channel.get(member.guild.id)

        if guild_has_jtc:
            try:
                if after.channel.id in guild_has_jtc:
                    guild = self.bot.get_guild(member.guild.id)
                    category = self.bot.get_channel(self.jtc_category[member.guild.id][0])

                    channel = await guild.create_voice_channel(name=f'{member.name}\'s Voice',
                                                               category=category)

                    self.jtc_current_channel.append(channel.id)
                    await self.channel_creator(channel, member)
            except AttributeError:
                pass
        try:
            if before.channel.id in self.jtc_current_channel and guild_has_jtc:
                channel = self.bot.get_channel(before.channel.id)

                if not await self.count_member_in_voice(channel):
                    self.jtc_current_channel.remove(channel.id)
                    await channel.delete()
        except AttributeError:
            pass

    async def count_member_in_voice(self, channel):
        user_in_voice = []
        for member in channel.members:
            user_in_voice.append(member.id)
        return user_in_voice

    async def channel_creator(self, channel, member):
        await channel.edit(sync_permissions=True)
        await member.move_to(channel=channel)

    @commands.group(no_pm=True)
    @has_permissions(administrator=True)
    async def jtc(self, ctx):
        pass

    @jtc.command()
    async def set(self, ctx, channel: str):
        if not channel.isdigit():
            return await ctx.send('Um einen Channel zu setzten, gebe bitte eine ChannelId an')

        cur = self.bot.dbBase.cursor()
        ch = self.bot.get_channel(int(channel))
        channel_ids = [(ch.id, 5), (ch.category.id, 6)]

        for i in channel_ids:
            cur.execute("insert into dcbots.serverchannel(server_id, channel_id, channel_type) values (%s, %s, %s);",
                        (ctx.message.guild.id,) + i)
        self.bot.dbBase.commit()
        cur.close()

        self.jtc_channel: dict = fillup(5)
        self.jtc_category: dict = fillup(6)
        await ctx.send(f'Channel: <#{ch.id}> wurde als JTC gesetzt!')


def setup(bot):
    bot.add_cog(JoinToCreate(bot))
