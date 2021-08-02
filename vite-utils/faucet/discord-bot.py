# Import discord.py. Allows access to Discord's API.
import discord
from question import Question

# Import the os,time,random module.
import os
import time
import random

# Import load_dotenv function from dotenv module.
from dotenv import load_dotenv

# Import commands from the discord.ext module.
from discord.ext import commands

import send_vite

# Loads the .env file that resides on the same level as the script.
load_dotenv()

# Grab the API token from the .env file.
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GREYLIST_TIMEOUT = os.getenv('GREYLIST_TIMEOUT')

print("DISCORD TOKEN is ", DISCORD_TOKEN)
print("TIMEOUT IS ", GREYLIST_TIMEOUT)

assert DISCORD_TOKEN is not None, 'environment variable[DISCORD_TOKEN] must be set'

bot = commands.Bot(command_prefix="!")

limits = {}

questions = []

# Example of how to make a new Question
question1 = Question("What is the capital of Russia?", ["Moscow","St Louis","New York City","Omsk"])
print(question1.get_question())
print(question1.get_anwers())

# Load questions from questions.txt file
# into Questions list
f = open("questions.txt", "r")
while True:
    question = f.readline().strip()
    answers = [f.readline().strip(),
              f.readline().strip(),
              f.readline().strip(),
              f.readline().strip()]
    if(not f.readline()): 
        print("Exit")
        break
    questions.append(Question(question,answers))

# Randomly shuffle questions
random.shuffle(questions)

# Show questions
for q in questions:
    question = q.get_question()
    answers = q.get_anwers()
    random.shuffle(answers)
    print(question)
    i = 1
    for answer in answers:
        print(str(i) + ") " + answer)
        i = i + 1

@bot.command(
    help="!ping",
    brief="Plays ping-pong with bot.")
async def ping(ctx):
    await ctx.reply("I am a stupid piece of shit robot.")

@bot.command(
    help="!question <vite address>",
    brief="Displays a randomly chosen question.")
async def question(ctx, *args):

    # Validate that address is correct
    if len(args) != 1:
        await ctx.reply("Incorrect vite address. Use: !question <vite address>")
        return
    vite_address = args[0]
    if(vite_address.startswith("vite") == False):
        await ctx.reply("Please only use vite addresses.")
        return

    # Check if this address is grey-listed
    if vite_address in limits:
        if limits[vite_address] > int(time.time()):
            await ctx.reply("You are greylisted for another" +
                            str(int((limits[vite_address] - time.time()) /
                                    GREYLIST_TIMEOUT)) + " minutes.")
            return
    limits[vite_address] = time.time() + 60 * GREYLIST_TIMEOUT

    # Grab a random trivia question 
    index = random.randint(0,len(questions))
    q = questions[index]
    # Print out question as multiple-choice
    question = q.get_question()
    answers = q.get_anwers()
    random.shuffle(answers)
    response = question + "\n"
    i = 1
    for answer in answers:
        response = str(i) + ") " + answer + "\n"
        i = i + 1
    await ctx.reply(response)

if not DISCORD_TOKEN.isspace():
    bot.run(DISCORD_TOKEN)
else:
    print("discord token not exists")
