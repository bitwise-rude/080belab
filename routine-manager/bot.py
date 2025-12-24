from dotenv import load_dotenv
import os
from discord.ext import commands
from datetime import datetime
import discord

load_dotenv()
TOKEN = os.getenv("TOKEN")

DEFAULT_ROOM = "C303"
CURRENT_SEASON = "winter"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

today_cancellations = set()
room_override_once = None

# ---------------- ROUTINE DATA ----------------
# TODO: modify this to be the correct data
ROUTINES = {
    "winter": {
        "sunday": {
            "theory": [
                ("10:15–11:55", "Digital Signal Processing (SPP)"),
                ("11:55–12:45", "Project Engineering & Management (NG)"),
                ("13:35–14:25", "Project Engineering & Management (NG)"),
                ("14:25–15:15", "DSP Application (GGT)")
            ],
            "practical": {
                "A": [("15:15–16:55", "Power Electronics Lab (SA+RS)")],
                "B": []
            }
        },

        "monday": {
            "theory": [
                ("10:15–11:05", "Switchgear & Protection (Akhm)"),
                ("11:05–11:55", "Electric Machine Design (SKR)"),
                ("12:45–14:25", "Engineering Thermodynamics & Heat Transfer (LM)"),
                ("14:25–15:15", "Digital Control System (AD)")
            ],
            "practical": {}
        },

        "tuesday": {
            "theory": [
                ("10:15–11:05", "Switchgear & Protection (Akhm)"),
                ("11:05–12:45", "Digital Control System (AD)")
            ],
            "practical": {
                "A": [("13:35–15:15", "Electric Machine Design A/B (SKR+C)")],
                "B": [("13:35–15:15", "Switchgear & Protection A/B (GDJ+BS)")]
            }
        },

        "wednesday": {
            "theory": [
                ("10:15–11:05", "Engineering Thermodynamics & Heat Transfer (LM)"),
                ("11:05–11:55", "Power Electronics (SA)"),
                ("12:45–13:35", "Digital Signal Processing (SPP)")
            ],
            "practical": {
                "A": [("13:35–15:15", "DSP Application (SPP)")],
                "B": [("13:35–15:15", "Electric Machine Design A/B (SKR+C)")]
            }
        },

        "thursday": {
            "theory": [
                ("10:15–11:05", "Electric Machine Design (SKR)"),
                ("11:05–12:45", "DSP Application (SPP)"),
                ("13:35–14:25", "Switchgear & Protection (Akhm)")
            ],
            "practical": {}
        },

        "friday": {
            "theory": [
                ("10:15–11:05", "Digital Control System (AD)"),
                ("12:45–13:35", "Power Electronics (SA)"),
                ("13:35–14:25", "Project Engineering & Management (NG)")
            ],
            "practical": {}
        }
    }
}

# ---------------- EVENTS ----------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ---------------- COMMANDS ----------------
@bot.command()
async def routine(ctx, *, note: str = None):
    global room_override_once

    today = datetime.now().strftime("%A").lower()
    data = ROUTINES[CURRENT_SEASON].get(today)

    if not data:
        await ctx.send("@everyone ❌ No classes today")
        return

    room = room_override_once or DEFAULT_ROOM

    embed = discord.Embed(
        title=f"📘 Today's Routine ({today.capitalize()})",
        description=f"🏫 **Room:** {room}",
        color=discord.Color.blue()
    )

    embed.add_field(name="📖 Theory (Same for A & B)", value="\u200b", inline=False)
    for time, subject in data["theory"]:
        if subject in today_cancellations:
            embed.add_field(time, f"❌ ~~{subject}~~", inline=False)
        else:
            embed.add_field(time, subject, inline=False)

    if data["practical"]:
        embed.add_field(name="🧪 Practical", value="\u200b", inline=False)
        for group, classes in data["practical"].items():
            for time, subject in classes:
                label = f"{time} — Group {group}"
                if subject in today_cancellations:
                    embed.add_field(label, f"❌ ~~{subject}~~", inline=False)
                else:
                    embed.add_field(label, subject, inline=False)

    if note:
        embed.add_field(name="📢 Notice", value=note, inline=False)

    embed.set_footer(text="B.E. Electrical • Winter Routine")

    await ctx.send("@everyone", embed=embed)

    room_override_once = None


@bot.command()
async def cancel(ctx, *, subject: str):
    today_cancellations.add(subject)
    await ctx.send(f"❌ Cancelled **{subject}** for today")


@bot.command()
async def room(ctx, room: str):
    global room_override_once
    room_override_once = room
    await ctx.send(f"🏫 Room changed to **{room}** (one-time only)")

# ------------------------------------------------
bot.run(TOKEN)
