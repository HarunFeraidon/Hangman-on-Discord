import discord
import discord.ext.commands as commands
from discord.ext.commands import Cog, command
import pytest
import pytest_asyncio
import discord.ext.test as dpytest


from hangman_game import hangman


@pytest_asyncio.fixture
async def bot():
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    b = commands.Bot(command_prefix="!",
                     intents=intents)
    await b._async_setup_hook()  # setup the loop
    await b.add_cog(Misc())

    dpytest.configure(b)
    return b

@pytest.mark.asyncio
async def test_hangman(bot):
    await dpytest.message("!hangman")
    assert dpytest.verify().message().contains().content("Getting the secret phrase from ")


# @pytest.mark.asyncio
# async def test_echo(bot):
#     await dpytest.message("!echo Hello world")
#     assert dpytest.verify().message().contains().content("Hello")