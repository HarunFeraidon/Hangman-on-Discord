import discord
import config
from discord.ext import commands
import constants
import asyncio

# TODO
# [X] verify secret phrase is from user and in a dm
# [X] detect abort to end game
# [] add time limit to secret phrase
# [] add time limit to recieving a guess
# 


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'logged in as {bot.user}')

@bot.command()
async def hangman(ctx):
    author = ctx.author
    await ctx.send(f"Getting the secret phrase from {author}")
    await ctx.author.send("Reply with your secret phrase: ")
    # get phrase
    def check(msg):
        return msg.author == ctx.author and str(msg.channel.type) == "private"
    try:
        reply = await bot.wait_for('message', check=check, timeout=15.0)
    except asyncio.TimeoutError:
        await ctx.send('Took too long, game ending.')

    phrase = reply.content.lower().strip()
    guessed_letters = set([])
    missing_letters = {} 
    censored_phrase = []
    # build censored phrase and dict of missing letters 
    for idx, letter in enumerate(phrase):
        if(letter != " "):
            censored_phrase += "-"
            missing_letters.setdefault(letter,[]).append(idx)
        else:
            censored_phrase += " "
    
    await ctx.send(f' {author} has picked a phrase: {convert(censored_phrase)}')
    
    # loop until game wins or game loses
    wrong_guesses=0
    gamewon = False
    safety_word = False
    while len(missing_letters) and wrong_guesses < 6:
        guess = await bot.wait_for('message')
        guess_author = guess.author
        guess = guess.content.lower().strip()
        if guess == phrase:
            gamewon = True
            break
        elif guess == "abort" and guess_author == ctx.author:
            safety_word = True
            break
        if guess not in guessed_letters:
            guessed_letters.add(guess)
            if guess in missing_letters:
                locations = missing_letters.get(guess)
                for index in locations:
                    censored_phrase[index] = guess
                missing_letters.pop(guess)
            else:
                wrong_guesses+=1
            await ctx.send(f"```{constants.HANGMANPICS[wrong_guesses]}```\n{convert(censored_phrase)}")
        else:
            await ctx.send("already guessed, please try again")
    if len(missing_letters) == 0 or gamewon:
        await ctx.send(f"congrats, u won! the phrase was `{phrase}`")
    elif wrong_guesses == 6:
        await ctx.send(f"bruh. the phrase was `{phrase}`")
    elif safety_word:
        await ctx.send(f"game aborted. the phrase was `{phrase}`")


def convert(s):
    """
    convert list of characters into string 
    """
    result = ""
    for c in s:
        result += c
    return result

bot.run(config.token)