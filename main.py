import interactions
from OpenaiBeforeFunctions import *
import openai
import discord
from discord.ext import commands

openai.organization = "org-vNmstpCOraNT0PltYS5FPVNy"
openai.api_key = os.environ['APIKEY']
openai.Model.list()

print('ok')

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=",", intents=intents)

bot_guilds = [1061278016166166629, 643109758936809488, 1067096622372229180]
conversation = Conversation()


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    print('Connected to bot: {}'.format(bot.user.name))
    print('Bot ID: {}'.format(bot.user.id))
    await bot.get_channel(748455841157611580).send("ok")

    custom = discord.Activity(type=discord.ActivityType.watching, name="your chats")
    playing = discord.Game("with you!!")
    await bot.change_presence(activity=custom, status=discord.Status.idle)


@bot.event
async def on_message(message):
    if message.author == bot.user or not message.content or message.content.startswith("\\") or message.author.bot:
        return

    text = message.content
    if not text:
        return

    async with message.channel.typing():

        prev_chat = conversation.get_conversation(message.author.id)
        new_chat = prompt(message, prev_chat, text)

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=new_chat.strip(),
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6
        )

        replied_text = response.choices[0].text
        conversation.update_conversation(message.author.id, update_message(new_chat, replied_text))
        # print("\n\nupdated message: ", update_message(new_chat, replied_text))
        # send the response to Discord

        if len(replied_text) >= 2000:
            reply = ''
            for word in replied_text:
                if len(reply) >= 1800:
                    await message.reply(reply)
                    reply = ''
                reply.join(word)
        else:
            await message.reply(f"{response.choices[0].text}")

    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    if member.guild.id in bot_guilds:
        guild = member.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(member.name, overwrites=overwrites)
        await channel.delete()
        await channel.send(welcome(member))


@bot.event
async def on_member_remove(member):
    if member.guild.id in bot_guilds:
        name = member.name.lower()
        for channel in member.guild.channels:
            if channel.name == name:
                await channel.delete()


bot.run(os.environ['TOKEN'])
