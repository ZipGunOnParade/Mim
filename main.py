import interactions

import os
import json
import re
from thefuzz import fuzz
import io

dirPath = os.path.dirname(os.path.realpath(__file__))

bot = interactions.Client(intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MEMBERS | interactions.Intents.MESSAGE_CONTENT, send_command_tracebacks=False, fetch_members=False)


@interactions.listen()
async def on_startup():
    print("Bot is ready!")
    print("Bot is in:")
    for guild in bot.guilds:
        print(guild.name, guild.id)



class Answer:
    def __init__(self, fp: io.TextIOWrapper):
        self.name = fp.readline()[4:-4]
        self.description = fp.readline()[4:-4]

        self.search_aids = [x.strip() for x in (fp.readline()[4:-4].split(","))]
        self.matchable = " ".join([
            self.name,
            self.description,
            " ".join(self.search_aids)
        ])
        self.body = fp.read()




answers = []

for item in os.scandir(dirPath+"/answers/"):
    if os.path.isfile(f"answers/{item.name}"):
        with open(f"answers/{item.name}", "r", encoding="utf-8") as f:
            answers.append(Answer(f))



@interactions.slash_command(name="mim")
@interactions.slash_option(
    name="answer",
    description="The relevant answer",
    required=True,
    opt_type=interactions.OptionType.STRING,
    autocomplete=True
)
async def mim(ctx: interactions.SlashContext, answer: str):
    for file in answers:
        if file.name == answer.lower():
            await ctx.send(file.body)
            return
        
    await ctx.send("Couldn't find an answer with that name.", ephemeral=True)


@mim.autocomplete("answer")
async def autocomplete(ctx: interactions.AutocompleteContext):
    query = ctx.input_text


    if query == "":
        choices = [{"name": answer.name + " - " + answer.description, "value": answer.name} for answer in answers]
        await ctx.send(choices=choices)
        return

    results = []

    for answer in answers:
        score = fuzz.token_set_ratio(query, answer.matchable)
        results.append((score, answer))

    results.sort(reverse=True, key=lambda x: x[0])

    choices = [{"name": x[1].name + " - " + x[1].description, "value": x[1].name} for x in results]

    await ctx.send(choices=choices)


# Load bot token from config file
with open(dirPath+"/config.json", "r") as f:
    data = json.load(f)
    token = data["token"]

bot.start(token)