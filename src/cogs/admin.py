import json
import nextcord

from datetime import datetime
from itertools import cycle

from nextcord.ext import commands
from nextcord.ext import tasks
from nextcord.ext.commands import CommandNotFound

from cogs.etc.embeds import user_info
from cogs.etc.embeds import help_site
from cogs.etc.config import cur_db, DBBASE
from cogs.etc.config import DBESSENT
from cogs.etc.config import cur, dbSun
from cogs.etc.config import fetch_whitelist, status_query

from cogs.etc.presets import Preset


# todo:
#   get, del, add, clear
#       getVehicleTrunk
#		delUser
#       delVehicles
#       delWeapon
#       clearInventory
#       clearVehicleTrunk
#       clearUserMoney
#       addUserMoney


class Admin(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.whitelist = fetch_whitelist()

		self.whitelist_options = ['add', 'remove', 'list']
		self.GET_OPTIONS = [
			f'user', f'u',
			f'vehicletrunk', f'vh', 'Null']

		self.DEL_OPTIONS = [
			f'user', f'u',
			f'veh', f'vehicle',
			f'weapons', 'Null']

		self.CLEAR_OPTIONS = [
			f'inv',
			f'vehtrunk', f'veht',
			f'usermoney', f'um']

		self.ADD_OPTIONS = [f'um', f'usermoney']

	@commands.Cog.listener()
	async def on_ready(self):
		print(f'Ready at {datetime.now().strftime("%H:%M:%S")}')


	@commands.Cog.listener()
	async def on_command_error(self, ctx,
									error):  # Function doing intense computing!
		if isinstance(error, CommandNotFound):
			return await ctx.send("Command/API not found.")
		raise error

	@commands.Command
	async def get(self, ctx, *args):
		if Preset.get_perm(ctx.message.author.id) <= 2:
			return await ctx.send('You are not Authorized to use the Get function!')
		cur.execute(DBESSENT)

		parsed = Preset.parser(rounds=2, toparse=args, option=self.GET_OPTIONS)
		if parsed[0] in self.GET_OPTIONS[0:2]:
			cur.execute(
				"SELECT identifier, `accounts`, `group`, inventory, job, job_grade, loadout, firstname, lastname, phone_number FROM users WHERE identifier=%s", (parsed[1],))

			fetcher = cur.fetchone()

			try:
				money = json.loads(fetcher[1])
			except TypeError:
				return await ctx.send(f'{parsed[1]} is not an Valid id!')

			inventory = json.loads(fetcher[3])
			weapons = json.loads(fetcher[6])

			license_ = fetcher[0]

			weapons_list = []

			for i in weapons:
				weapons_list.append(f'{i.replace("WEAPON_", "").title()} - {weapons[i]["ammo"]}/255')

			cur.execute("SELECT owner FROM owned_vehicles WHERE owner=%s", (parsed[1],))

			fetcher2 = cur.fetchall()
			veh = 0

			for i in fetcher2:
				veh += 1

			user = {
				'username': 'clx',
				'license': license_,
				'job': fetcher[4],
				'job_grade': fetcher[5],
				'cash': money.get('money'),
				'bank': money.get('bank'),
				'bm': money.get('black_money'),
				'veh': veh,
				'weapons': weapons_list,
				'inv': inventory,
				'firstname': fetcher[7],
				'lastname': fetcher[8],
				'phone_number': fetcher[9]
			}

			await ctx.send(embed=user_info(user=user))
		elif parsed[0] in self.GET_OPTIONS[2:4]:
			pass
		elif parsed[0] == 'Null':
			pass

	@commands.command()
	async def delete(self, ctx, *args):
		pass

	@commands.command()
	async def add(self, ctx, *args):
		pass

	@commands.command()
	async def clear(self, ctx, *args):
		pass

	@commands.Command
	async def einreise(self, ctx, *args):
		if not ctx.message.author.id in self.whitelist:
			return


		if Preset.get_perm(ctx.message.author.id) >= 4:
			cur.execute(DBESSENT)
			if not args:
				return await ctx.send(embed=help_site('einreise'))

			if args[0]:
				try:
					cur.execute("DELETE FROM users WHERE identifier=%s", (args[0].strip('license:'),))
					dbSun.commit()
					await ctx.send('User got deleted from the Db')
				except Exception:
					return await ctx.send('Nothing happens, Contact an dev or try it again.\n**Maybe it was an invalid id!**')
		return await ctx.send('You are not Authorized to manage the Whitelist')

	@commands.Command
	async def whitelist(self, ctx, *args):
		if not ctx.message.author.id in self.whitelist:
			return await ctx.send('You are not Authorized to manage the Whitelist')
		cur_db.execute(DBBASE)

		id = ctx.message.author.id

		if not Preset.get_perm(id) == 5:
			return await ctx.send('You are not Authorized to manage the Whitelist')
		
		if not args:
			return await ctx.send(embed=help_site('whitelist'))

		if args[0] == 'add':
			return await ctx.send(Preset.whitelist('add', args[1].strip('<!@ >'), args[2] if args[2].isdigit() else 0))
		elif args[0] == 'remove':
			return await ctx.send(Preset.whitelist('remove', args[1].strip('<!@ >')))
		elif args[0] == 'list':
			return await ctx.send(embed=Preset.whitelist('list'))
		return await ctx.send('The argument is not valid!')

	@commands.Command
	async def help(self, ctx):
		await ctx.send(embed=help_site())


def setup(bot):
	bot.add_cog(Admin(bot))
