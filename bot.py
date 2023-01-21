import discord
import config
from discord.ext import commands
import constants
import asyncio
import sys

# TODO
# [X] verify secret phrase is from user and in a dm
# [X] detect abort to end game
# [X] add time limit to secret phrase
# [X] add time limit to recieving a guess
# [X] length of phrase 
# 


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

ABORT = "abort"
lock = asyncio.Lock()
is_alive_ = False

@bot.event
async def on_ready():
    print(f'logged in as {bot.user}')

@bot.command()
async def hangman(ctx):
    global is_alive_
    if is_alive_:
        await ctx.send("another game is going on right now.")
        return
    is_alive_ = True

    async with lock:
        author = ctx.author.name
        await ctx.send(f"Getting the secret phrase from {author}")
        await ctx.author.send("Reply with your secret phrase (length < 40): ")
        # get phrase
        def check(msg):
            return 1 < len(msg.content.strip()) < 40  and msg.author == ctx.author and str(msg.channel.type) == "private"
        try:
            reply = await bot.wait_for('message', check=check, timeout=25.0)
        except asyncio.TimeoutError:
            await ctx.send(f'{author} took too long, game ending.')
            return

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
            def check(msg):
                return len(msg.content) == 1 or msg.content in {phrase, ABORT}
            try:
                guess = await bot.wait_for('message', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send('Nobody took a guess. Imma just end this game.')
                return
            author = guess.author.name
            guess = guess.content.lower().strip()

            if guess == phrase:
                gamewon = True
                break
            elif guess == ABORT and author == ctx.author.name:
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
                await ctx.send("already guessed, try again")
        if len(missing_letters) == 0 or gamewon:
            await ctx.send(f"Lucky guess. The phrase was indeed `{phrase}`.")
        elif wrong_guesses == 6:
            await ctx.send(f"bruh. the phrase was `{phrase}`")
        elif safety_word:
            await ctx.send(f"game aborted. the phrase was `{phrase}`")
        is_alive_ = False


def convert(s):
    """
    convert list of characters into string 
    """
    result = ""
    for c in s:
        result += c
    return result

bot.run(config.token)