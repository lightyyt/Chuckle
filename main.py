import discord, os
from dotenv import load_dotenv
from ai import *
from bot_payload import *
import re
load_dotenv() # Load Environment Variables

intents = discord.Intents.all() # Setup Intents
bot = discord.Bot(intents=intents) # Setup Bot

add = []


@bot.event
async def on_ready():
    _app = []
    for e in filter:
        print(e,end=", ")
        if "*" in e:
            n_el=e.replace("*","\\*")
            _app.append(n_el)
            print(n_el,end=", ")
    for e in _app:
        filter.append(e)
    print(f"\n[READY] {bot.user}")
    await bot.change_presence(activity=discord.CustomActivity(name='Hi, I am Chuckle!' ,emoji=':joy:'))

@bot.slash_command(name="hello_chuckle", description="Say hello to Chuckle's AI", guild_ids = [os.getenv("GUILD")])
async def hello(ctx: discord.ApplicationContext):
    await ctx.defer()
    response = chat(ctx.user.id, "Hello, Chuckle!", ctx.user.display_name)
    await ctx.respond(response["info"]+response["chat"]+warning)

@bot.slash_command(name="ask_chuckle", description="Talk to Chuckle's AI", guild_ids = [os.getenv("GUILD")])
async def ask(ctx, message: str):
    await ctx.defer()
    response = chat(ctx.user.id, message, ctx.user.display_name)
    await ctx.respond(response["info"]+response["chat"]+warning)

@bot.slash_command(name="get_sessions", description="Get your Sessions", guild_ids = [os.getenv("GUILD")])
async def get_sessions(ctx):
    try:
        if ctx.user.id not in sessions and current_sessions[ctx.user.id] == -1:
            await ctx.respond(f"You are currently in the **global** session!", ephemeral=True)
            return
    except: pass # Ignore exceptions
    if ctx.user.id not in sessions:
        await ctx.respond("You don't have any current sessions!", ephemeral=True)
        return
    
    if len(sessions[ctx.user.id]) == 0:
        await ctx.respond("You don't have any sessions created!", ephemeral=True)
        return
    
    if ctx.user.id not in current_sessions:
        await ctx.respond(f"You have **{len(sessions[ctx.user.id])}** sessions, but are currently in **no** session!", ephemeral=True)
        return

    if current_sessions[ctx.user.id] == -1:
        await ctx.respond(f"You have **{len(sessions[ctx.user.id])}** sessions, but are currently in the **global** session!", ephemeral=True)
        return
    
    await ctx.respond(f"You have **{len(sessions[ctx.user.id])}** sessions, and are currently in the **{current_sessions[ctx.user.id]}** session!", ephemeral=True)

@bot.slash_command(name="make_session", description="Make a new private Session", guild_ids = [os.getenv("GUILD")])
async def mk_session(ctx):
    sid = create_session(ctx.user.id)
    await ctx.respond("Your new Session is #"+str(sid), ephemeral=True)

@bot.slash_command(name="change_session", description="Change to a different Session (-1 == global)", guild_ids = [os.getenv("GUILD")])
async def change_session(ctx, id: int):
    nid = set_session(ctx.user.id, id)
    if nid == -1000:
        await ctx.respond("Invalid Session ID!", ephemeral=True)
    elif nid == -1:
        await ctx.respond("You are now in the **global** Session!", ephemeral=True)
    else:
        await ctx.respond(f"You are now in session **{nid}**!", ephemeral=True)


@bot.slash_command(name="clear_global", description="Reset Global Session Chat", guild_ids = [os.getenv("GUILD")])
async def clear_global(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("HEY! This is my chat >.< I like it! Leave me alone :(")
        return
    reset_global_session()
    await ctx.respond("Cleared Session `global`!")

@bot.slash_command(name="dbg_sessions", description="DEBUG: Get all Current Sessions", guild_ids = [os.getenv("GUILD")])
async def dbg_sessions(ctx):
    out = ""
    for i in current_sessions:
        out+="<@"+str(i)+">"
        out+=":"
        out+=str(current_sessions[i])+"\n"
    await ctx.respond(out)

@bot.slash_command(name="add_filter", description="Add a word to the filter", guild_ids = [os.getenv("GUILD")])
async def add_filter(ctx, filtered_word: str):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("HEY! Leave my filtered words alone >.< meanie!")
        return
    filter.append(filtered_word)
    print("[ADD_FILTER]"+ctx.user.name+"> /add_filter filtered_word: "+filtered_word)
    await ctx.respond(f"Now filtering: ||{filtered_word}||")

class RebootButton(discord.ui.View):
    @discord.ui.button(label="Yes! Reboot!", style=discord.ButtonStyle.danger)
    async def reb(this, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Rebooting...", view=None)
        print(interaction.user.name + " rebooted Chuckle!")
        exit(0)

@bot.slash_command(name="reboot", description="Reboot Chuckle", guild_ids = [os.getenv("GUILD")])
async def reboot(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("HEY! I WON'T LET YOU REBOOT ME!")
        return
    view = RebootButton()
    await ctx.respond("Are you SURE you want to reboot me?\nThis will clear everything, including:\n- Every Conversation\n- Selected Features\n- Added Filtering rules (via add_filter)",ephemeral=True, view=view)

"""
@bot.slash_command(name="filter", description="Toggle Filter", guild_ids = [os.getenv("GUILD")])
async def filter_toggle(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("HEY! Leave my filter alone! >.<")
        return
    features["filter"] = not features["filter"]
    if features["filter"]:
        await ctx.respond("Filter was ENABLED :D")
    else:
        await ctx.respond("Filter was DISABLED >.<")
"""
@bot.slash_command(name="feature", description="Set Feature value", guild_ids = [os.getenv("GUILD")])
async def feature_toggle(ctx, feature: str):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("HEY! Leave my features alone >.< it hurts!")
        return
    features[feature] = not features[feature]
    if features[feature]:
        await ctx.respond(feature + " was Enabled!")
    else:
        await ctx.respond(feature + " was Disabled!")

@bot.slash_command(name="features",description="List Feature values", guild_idx=[os.getenv("GUILD")])
async def get_features(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("HEY! I'm not gonna tell you my features! Stop >.<")
        return
    out = ""
    for feature in features:
        out += feature
        out += " is "
        out += "enabled" if features[feature] else "disabled"
        out += "\n"
    await ctx.respond(out)

@bot.event
async def on_message(message):
    # Avoid responding to the bot itself
    if message.author.bot:
        return

    # Check for "hey chuckle" followed by optional comma or space (case-insensitive)
    lower = message.content.lower()
    if lower.startswith("hey chuckle ") or lower.startswith("hey chuckle, ") or lower.startswith("hey, chuckle ") or lower.startswith("chuckle") or lower.startswith("ch.") or lower.startswith("ch>") or message.channel.name.startswith("chuckle-ai"):
        async with message.channel.typing():
            m = message.content
            if lower.startswith("ch.") or lower.startswith("ch>"):
                m = m[3:] #Removes first 3 characters (ch. or ch>)
            response = chat(message.author.id, m, message.author.display_name, False)
            sid = f"({current_sessions[message.author.id]})"
            print(message.author.display_name + " (@"+message.author.name + sid + ")> " + message.content)
            print("> "+response["unf"])
            await message.reply(response["info"]+response["chat"]+warning, mention_author=False)
    elif lower.startswith("hey chuckle!") or lower.startswith("hey, chuckle!") or lower.startswith("hey chuckle.") or lower.startswith("hey, chuckle."):
        async with message.channel.typing():
            response = chat(message.author.id, "Hey Chuckle!", message.author.display_name, False)
            sid = f"({current_sessions[message.author.id]})"
            print(message.author.display_name + " (@"+message.author.name + sid + ")> " + message.content)
            print("> "+response["unf"])
            await message.reply(response["info"]+response["chat"]+warning, mention_author=False)
    #await bot.process_commands(message)

bot.run(os.getenv('TOKEN')) # run the bot with the token
