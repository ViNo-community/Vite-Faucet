# Import discord.py. Allows access to Discord's API.
import discord

# Import the os,time module.
import os
import time

# Import load_dotenv function from dotenv module.
from dotenv import load_dotenv

# Import commands from the discord.ext module.
from discord.ext import commands

import send_vite

# Loads the .env file that resides on the same level as the script.
load_dotenv()

# Grab the API token from the .env file.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

assert DISCORD_TOKEN is not None, 'environment variable[DISCORD_TOKEN] must be set'

bot = commands.Bot(command_prefix="!")

limits = {}


@bot.command(
    # Adds this value to the $help ping message.
    help=
    "Uses come crazy logic to determine if pong is actually the correct value or not.",
    # Adds this value to the $help message.
    brief="Prints pong back to the channel.")
async def ping(ctx):
    # Sends a message to the channel using the Context object.
    await ctx.reply("pong")


# Command $print. This takes an in a list of arguments from the user and simply prints the values back to the channel.


@bot.command(
    # Adds this value to the $help print message.
    help="!send vite_xxxx",
    # Adds this value to the $help message.
    brief="get test vite token from faucet bot.")
async def send(ctx, *args):
    response = ""

    if len(args) != 1:
        await ctx.reply("error vite address")
        return
    vite_address = args[0]

    if vite_address in limits:
        if limits[vite_address] > int(time.time()):
            await ctx.reply("You are greylisted for another" +
                            str(int((limits[vite_address] - time.time()) /
                                    60)) + " minutes.")
            return
    limits[vite_address] = time.time() + 60 * 60

    # Loops through the list of arguments that the user inputs.
    blockHash = send_vite.sendVite(vite_address)
    # Sends a message to the channel using the Context object.
    await ctx.reply(blockHash)


if not DISCORD_TOKEN.isspace():
    bot.run(DISCORD_TOKEN)
else:
    print("discord token not exists")
