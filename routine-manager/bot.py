from dotenv import load_dotenv
import os
import discord

load_dotenv()
TOKEN = os.getenv("TOKEN")


bot = discord.Client(intents=discord.Intents())

@bot.event
async def on_ready():
	guild_count = 0

	for guild in bot.guilds:
		print(f"- {guild.id} (name: {guild.name})")

		guild_count = guild_count + 1

	print("Bot is in " + str(guild_count) + " guilds.")

@bot.event
async def on_message(message):
	if message.content == "hello":
		await message.channel.send("hey dirtbag")

bot.run(TOKEN)
