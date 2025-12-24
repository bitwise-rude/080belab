from dotenv import load_dotenv
import os
from discord.ext import commands
from datetime import datetime, timedelta
import discord
import json

load_dotenv()
TOKEN = os.getenv("TOKEN")

DEFAULT_ROOM = "C303"
CURRENT_SEASON = "winter"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Persistent storage file
STORAGE_FILE = "routine_data.json"

# State management - will be loaded from file
schedule_data = {}  # {date_str: {cancellations, rescheduled, added, room, notice, is_holiday}}

# ---------------- ROUTINE DATA ----------------
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

# ---------------- STORAGE FUNCTIONS ----------------
def load_data():
    """Load schedule data from file"""
    global schedule_data
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r') as f:
                schedule_data = json.load(f)
        else:
            schedule_data = {}
    except Exception as e:
        print(f"Error loading data: {e}")
        schedule_data = {}

def save_data():
    """Save schedule data to file"""
    try:
        with open(STORAGE_FILE, 'w') as f:
            json.dump(schedule_data, f, indent=2)
    except Exception as e:
        print(f"Error saving data: {e}")

def get_tomorrow_data():
    """Get or create data for tomorrow"""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    if tomorrow not in schedule_data:
        schedule_data[tomorrow] = {
            "cancellations": [],
            "rescheduled": {},
            "added": [],
            "room": None,
            "notice": None,
            "is_holiday": False,
            "holiday_reason": None
        }
    return tomorrow, schedule_data[tomorrow]

def get_date_data(date_str):
    """Get data for specific date"""
    if date_str not in schedule_data:
        schedule_data[date_str] = {
            "cancellations": [],
            "rescheduled": {},
            "added": [],
            "room": None,
            "notice": None,
            "is_holiday": False,
            "holiday_reason": None
        }
    return schedule_data[date_str]

# ---------------- EVENTS ----------------
@bot.event
async def on_ready():
    load_data()
    print(f"✅ Logged in as {bot.user}")

# ---------------- COMMANDS ----------------
@bot.command()
async def test(ctx):
    """Preview tomorrow's routine WITHOUT @everyone mention (for testing)"""
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    day_name = tomorrow.strftime("%A")
    
    data = get_date_data(tomorrow_str)
    
    # Check if it's a holiday
    if data["is_holiday"]:
        embed = discord.Embed(
            title=f"🎉 Holiday - {day_name}, {tomorrow.strftime('%B %d')}",
            description=data["holiday_reason"] or "No classes scheduled",
            color=discord.Color.gold()
        )
        embed.set_footer(text="B.E. Electrical • Winter Routine • TEST MODE")
        await ctx.send(embed=embed)
        return
    
    # Get routine data
    routine_data = ROUTINES[CURRENT_SEASON].get(day_name.lower())
    
    if not routine_data:
        await ctx.send(f"❌ No classes scheduled for {day_name}")
        return
    
    room = data["room"] or DEFAULT_ROOM
    
    embed = discord.Embed(
        title=f"📘 Tomorrow's Routine ({day_name}, {tomorrow.strftime('%b %d')}) - PREVIEW",
        description=f"🏫 **Room:** {room}",
        color=discord.Color.orange()
    )
    
    # Theory classes
    embed.add_field(name="📖 Theory (Same for A & B)", value="\u200b", inline=False)
    for time, subject in routine_data["theory"]:
        if subject in data["cancellations"]:
            embed.add_field(name=time, value=f"❌ ~~{subject}~~", inline=False)
        elif subject in data["rescheduled"]:
            new_time, new_name = data["rescheduled"][subject]
            embed.add_field(name=time, value=f"🔄 ~~{subject}~~ → Moved to {new_time}", inline=False)
        else:
            embed.add_field(name=time, value=subject, inline=False)
    
    # Show rescheduled classes at their new time
    for original, (new_time, new_name) in data["rescheduled"].items():
        embed.add_field(name=f"🔄 {new_time}", value=f"{new_name} (Rescheduled)", inline=False)
    
    # Practical classes
    if routine_data["practical"]:
        embed.add_field(name="🧪 Practical", value="\u200b", inline=False)
        for group, classes in routine_data["practical"].items():
            for time, subject in classes:
                label = f"{time} — Group {group}"
                if subject in data["cancellations"]:
                    embed.add_field(name=label, value=f"❌ ~~{subject}~~", inline=False)
                elif subject in data["rescheduled"]:
                    new_time, new_name = data["rescheduled"][subject]
                    embed.add_field(name=label, value=f"🔄 ~~{subject}~~ → Moved to {new_time}", inline=False)
                else:
                    embed.add_field(name=label, value=subject, inline=False)
    
    # Added classes
    if data["added"]:
        embed.add_field(name="➕ Extra Classes", value="\u200b", inline=False)
        for time, subject in data["added"]:
            embed.add_field(name=time, value=f"🆕 {subject}", inline=False)
    
    # Notice
    if data["notice"]:
        embed.add_field(name="📢 Notice", value=data["notice"], inline=False)
    
    embed.set_footer(text="B.E. Electrical • Winter Routine • TEST MODE (No @everyone)")
    
    await ctx.send(embed=embed)


@bot.command()
async def routine(ctx):
    """Display tomorrow's routine with @everyone mention and clear previous command messages"""
    # Try to delete recent command messages in this channel
    try:
        # Fetch recent messages (up to 100)
        last_everyone_found = False
        messages_to_delete = []
        
        async for message in ctx.channel.history(limit=5):
            # Check if this message has @everyone (previous routine post)
            if "@everyone" in (message.content or ""):
                last_everyone_found = True
                break
            
            # Collect messages to delete (all messages until we hit @everyone)
            messages_to_delete.append(message)
        
        # If @everyone found, delete all messages between
        # If not found, delete only last 10 messages max
        if not last_everyone_found:
            messages_to_delete = messages_to_delete[:10]
        
        # Delete collected messages
        for message in messages_to_delete:
            try:
                await message.delete()
            except:
                pass
    except Exception as e:
        print(f"Error deleting messages: {e}")
    
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    day_name = tomorrow.strftime("%A")
    
    data = get_date_data(tomorrow_str)
    
    # Check if it's a holiday
    if data["is_holiday"]:
        embed = discord.Embed(
            title=f"🎉 Holiday - {day_name}, {tomorrow.strftime('%B %d')}",
            description=data["holiday_reason"] or "No classes scheduled",
            color=discord.Color.gold()
        )
        embed.set_footer(text="B.E. Electrical • Winter Routine")
        await ctx.send("@everyone", embed=embed)
        return
    
    # Get routine data
    routine_data = ROUTINES[CURRENT_SEASON].get(day_name.lower())
    
    if not routine_data:
        await ctx.send(f"@everyone ❌ No classes scheduled for {day_name}")
        return
    
    room = data["room"] or DEFAULT_ROOM
    
    embed = discord.Embed(
        title=f"📘 Tomorrow's Routine ({day_name}, {tomorrow.strftime('%b %d')})",
        description=f"🏫 **Room:** {room}",
        color=discord.Color.blue()
    )
    
    # Theory classes
    embed.add_field(name="📖 Theory (Same for A & B)", value="\u200b", inline=False)
    for time, subject in routine_data["theory"]:
        # Check if cancelled
        if subject in data["cancellations"]:
            embed.add_field(name=time, value=f"❌ ~~{subject}~~", inline=False)
        # Check if rescheduled
        elif subject in data["rescheduled"]:
            new_time, new_name = data["rescheduled"][subject]
            embed.add_field(name=time, value=f"🔄 ~~{subject}~~ → Moved to {new_time}", inline=False)
        else:
            embed.add_field(name=time, value=subject, inline=False)
    
    # Show rescheduled classes at their new time
    for original, (new_time, new_name) in data["rescheduled"].items():
        embed.add_field(name=f"🔄 {new_time}", value=f"{new_name} (Rescheduled)", inline=False)
    
    # Practical classes
    if routine_data["practical"]:
        embed.add_field(name="🧪 Practical", value="\u200b", inline=False)
        for group, classes in routine_data["practical"].items():
            for time, subject in classes:
                label = f"{time} — Group {group}"
                if subject in data["cancellations"]:
                    embed.add_field(name=label, value=f"❌ ~~{subject}~~", inline=False)
                elif subject in data["rescheduled"]:
                    new_time, new_name = data["rescheduled"][subject]
                    embed.add_field(name=label, value=f"🔄 ~~{subject}~~ → Moved to {new_time}", inline=False)
                else:
                    embed.add_field(name=label, value=subject, inline=False)
    
    # Added classes
    if data["added"]:
        embed.add_field(name="➕ Extra Classes", value="\u200b", inline=False)
        for time, subject in data["added"]:
            embed.add_field(name=time, value=f"🆕 {subject}", inline=False)
    
    # Notice
    if data["notice"]:
        embed.add_field(name="📢 Notice", value=data["notice"], inline=False)
    
    embed.set_footer(text="B.E. Electrical • Winter Routine | Use !help for commands")
    
    await ctx.send("@everyone", embed=embed)


@bot.command()
async def cancel(ctx, *, search_term: str):
    """Cancel a class for tomorrow. Usage: !cancel electric (searches lazily)"""
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    day_name = tomorrow.strftime("%A").lower()
    
    data = get_date_data(tomorrow_str)
    routine_data = ROUTINES[CURRENT_SEASON].get(day_name)
    
    if not routine_data:
        await ctx.send("❌ No classes scheduled for tomorrow")
        return
    
    # Collect all subjects
    all_subjects = []
    for _, subject in routine_data["theory"]:
        all_subjects.append(subject)
    if routine_data["practical"]:
        for classes in routine_data["practical"].values():
            for _, subject in classes:
                if subject not in all_subjects:
                    all_subjects.append(subject)
    
    # Find matching subjects (case-insensitive partial match)
    search_lower = search_term.lower()
    matches = [s for s in all_subjects if search_lower in s.lower()]
    
    if not matches:
        await ctx.send(f"❌ No class found matching '{search_term}'")
        return
    
    if len(matches) == 1:
        subject = matches[0]
        if subject not in data["cancellations"]:
            data["cancellations"].append(subject)
            save_data()
            await ctx.send(f"✅ Cancelled **{subject}** for tomorrow ({tomorrow.strftime('%A, %b %d')})")
        else:
            await ctx.send(f"⚠️ **{subject}** is already cancelled for tomorrow")
    else:
        # Multiple matches - show options
        matches_list = "\n".join([f"{i+1}. {s}" for i, s in enumerate(matches)])
        await ctx.send(f"🔍 Multiple matches found for '{search_term}':\n{matches_list}\n\nPlease be more specific!")


@bot.command()
async def cancelall(ctx):
    """Cancel all classes for tomorrow"""
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    day_name = tomorrow.strftime("%A").lower()
    
    data = get_date_data(tomorrow_str)
    routine_data = ROUTINES[CURRENT_SEASON].get(day_name)
    
    if not routine_data:
        await ctx.send("❌ No classes scheduled for tomorrow")
        return
    
    count = 0
    for _, subject in routine_data["theory"]:
        if subject not in data["cancellations"]:
            data["cancellations"].append(subject)
            count += 1
    
    if routine_data["practical"]:
        for classes in routine_data["practical"].values():
            for _, subject in classes:
                if subject not in data["cancellations"]:
                    data["cancellations"].append(subject)
                    count += 1
    
    save_data()
    await ctx.send(f"✅ Cancelled all {count} classes for tomorrow ({tomorrow.strftime('%A, %b %d')})")


@bot.command()
async def uncancel(ctx, *, search_term: str):
    """Restore a cancelled class for tomorrow. Usage: !uncancel electric"""
    tomorrow_str, data = get_tomorrow_data()
    
    if not data["cancellations"]:
        await ctx.send("⚠️ No classes are cancelled for tomorrow")
        return
    
    # Find matching cancelled subjects
    search_lower = search_term.lower()
    matches = [s for s in data["cancellations"] if search_lower in s.lower()]
    
    if not matches:
        await ctx.send(f"❌ No cancelled class found matching '{search_term}'")
        return
    
    if len(matches) == 1:
        subject = matches[0]
        data["cancellations"].remove(subject)
        save_data()
        
        tomorrow = datetime.now() + timedelta(days=1)
        await ctx.send(f"✅ Restored **{subject}** for tomorrow ({tomorrow.strftime('%A, %b %d')})")
    else:
        matches_list = "\n".join([f"{i+1}. {s}" for i, s in enumerate(matches)])
        await ctx.send(f"🔍 Multiple matches found:\n{matches_list}\n\nPlease be more specific!")


@bot.command()
async def reschedule(ctx, original_time: str, new_time: str, *, subject_name: str = None):
    """Reschedule a class for tomorrow. Usage: !reschedule "10:15" "14:00" Subject Name"""
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    day_name = tomorrow.strftime("%A").lower()
    
    data = get_date_data(tomorrow_str)
    routine_data = ROUTINES[CURRENT_SEASON].get(day_name)
    
    if not routine_data:
        await ctx.send("❌ No classes scheduled for tomorrow")
        return
    
    # Find the class at original time
    found = False
    for time, subject in routine_data["theory"]:
        if original_time in time or time in original_time:
            data["rescheduled"][subject] = [new_time, subject_name or subject]
            save_data()
            await ctx.send(f"✅ Rescheduled **{subject}** from {time} to {new_time} for tomorrow ({tomorrow.strftime('%A, %b %d')})")
            found = True
            break
    
    if not found and routine_data["practical"]:
        for group, classes in routine_data["practical"].items():
            for time, subject in classes:
                if original_time in time or time in original_time:
                    data["rescheduled"][subject] = [new_time, subject_name or subject]
                    save_data()
                    await ctx.send(f"✅ Rescheduled **{subject}** (Group {group}) from {time} to {new_time} for tomorrow ({tomorrow.strftime('%A, %b %d')})")
                    found = True
                    break
    
    if not found:
        await ctx.send(f"❌ No class found at {original_time}")


@bot.command()
async def addclass(ctx, time: str, *, subject: str):
    """Add an extra class for tomorrow. Usage: !addclass "14:00-15:00" Subject Name"""
    tomorrow_str, data = get_tomorrow_data()
    
    data["added"].append([time, subject])
    save_data()
    
    tomorrow = datetime.now() + timedelta(days=1)
    await ctx.send(f"✅ Added **{subject}** at {time} for tomorrow ({tomorrow.strftime('%A, %b %d')})")


@bot.command()
async def room(ctx, room_name: str):
    """Change room for tomorrow. Usage: !room D204"""
    tomorrow_str, data = get_tomorrow_data()
    
    data["room"] = room_name
    save_data()
    
    tomorrow = datetime.now() + timedelta(days=1)
    await ctx.send(f"✅ Room changed to **{room_name}** for tomorrow ({tomorrow.strftime('%A, %b %d')})")


@bot.command()
async def notice(ctx, *, message: str):
    """Add a notice for tomorrow. Usage: !notice Remember to bring your notebooks"""
    tomorrow_str, data = get_tomorrow_data()
    
    data["notice"] = message
    save_data()
    
    tomorrow = datetime.now() + timedelta(days=1)
    await ctx.send(f"✅ Notice added for tomorrow ({tomorrow.strftime('%A, %b %d')}): {message}")


@bot.command()
async def holiday(ctx, *, reason: str = "Holiday"):
    """Mark tomorrow as a holiday. Usage: !holiday Dashain Festival"""
    tomorrow_str, data = get_tomorrow_data()
    
    data["is_holiday"] = True
    data["holiday_reason"] = reason
    save_data()
    
    tomorrow = datetime.now() + timedelta(days=1)
    await ctx.send(f"✅ Tomorrow ({tomorrow.strftime('%A, %b %d')}) marked as holiday: {reason}")


@bot.command()
async def unholiday(ctx):
    """Remove holiday status from tomorrow"""
    tomorrow_str, data = get_tomorrow_data()
    
    data["is_holiday"] = False
    data["holiday_reason"] = None
    save_data()
    
    tomorrow = datetime.now() + timedelta(days=1)
    await ctx.send(f"✅ Holiday status removed for tomorrow ({tomorrow.strftime('%A, %b %d')})")


@bot.command()
async def changes(ctx):
    """Show all current changes for tomorrow"""
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    
    data = get_date_data(tomorrow_str)
    
    if data["is_holiday"]:
        await ctx.send(f"🎉 Tomorrow is a holiday: {data['holiday_reason']}")
        return
    
    if not any([data["cancellations"], data["rescheduled"], data["added"], data["room"], data["notice"]]):
        await ctx.send(f"📋 No changes for tomorrow ({tomorrow.strftime('%A, %b %d')})")
        return
    
    embed = discord.Embed(
        title=f"📋 Changes for Tomorrow ({tomorrow.strftime('%A, %b %d')})",
        color=discord.Color.orange()
    )
    
    if data["room"]:
        embed.add_field(name="🏫 Room", value=data["room"], inline=False)
    
    if data["cancellations"]:
        cancelled_list = "\n".join([f"❌ {s}" for s in data["cancellations"]])
        embed.add_field(name="Cancelled Classes", value=cancelled_list, inline=False)
    
    if data["rescheduled"]:
        rescheduled_list = "\n".join([f"🔄 {orig} → {new_time}" for orig, (new_time, _) in data["rescheduled"].items()])
        embed.add_field(name="Rescheduled Classes", value=rescheduled_list, inline=False)
    
    if data["added"]:
        added_list = "\n".join([f"➕ {time}: {subj}" for time, subj in data["added"]])
        embed.add_field(name="Extra Classes", value=added_list, inline=False)
    
    if data["notice"]:
        embed.add_field(name="📢 Notice", value=data["notice"], inline=False)
    
    await ctx.send(embed=embed)


@bot.command()
async def reset(ctx):
    """Reset all changes for tomorrow"""
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    
    if tomorrow_str in schedule_data:
        del schedule_data[tomorrow_str]
        save_data()
    
    await ctx.send(f"✅ All changes reset for tomorrow ({tomorrow.strftime('%A, %b %d')}). Routine is back to normal.")


@bot.command()
async def clearall(ctx):
    """Clear ALL stored data (use with caution!)"""
    global schedule_data
    schedule_data = {}
    save_data()
    await ctx.send("✅ All stored data cleared!")


@bot.command(name='?')
async def help_command(ctx):
    """Show all available commands"""
    embed = discord.Embed(
        title="🤖 Routine Bot Commands",
        description="All commands work for **TOMORROW's** schedule",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="📘 !routine",
        value="Post tomorrow's routine with @everyone (cleans up command messages)",
        inline=False
    )
    embed.add_field(
        name="🧪 !test",
        value="Preview tomorrow's routine WITHOUT @everyone (for testing)",
        inline=False
    )
    embed.add_field(
        name="❌ !cancel <search>",
        value="Cancel a class (lazy search)\nExample: `!cancel electric` or `!cancel power`",
        inline=False
    )
    embed.add_field(
        name="❌ !cancelall",
        value="Cancel all classes for tomorrow",
        inline=False
    )
    embed.add_field(
        name="✅ !uncancel <search>",
        value="Restore a cancelled class (lazy search)\nExample: `!uncancel dsp`",
        inline=False
    )
    embed.add_field(
        name="🔄 !reschedule <old_time> <new_time> [subject]",
        value="Reschedule a class\nExample: `!reschedule 10:15 14:00`",
        inline=False
    )
    embed.add_field(
        name="➕ !addclass <time> <subject>",
        value="Add an extra class\nExample: `!addclass 15:00-16:00 Extra Tutorial`",
        inline=False
    )
    embed.add_field(
        name="🏫 !room <room_name>",
        value="Change room for tomorrow\nExample: `!room D204`",
        inline=False
    )
    embed.add_field(
        name="📢 !notice <message>",
        value="Add a notice for tomorrow\nExample: `!notice Bring lab coats`",
        inline=False
    )
    embed.add_field(
        name="🎉 !holiday [reason]",
        value="Mark tomorrow as holiday\nExample: `!holiday Dashain Festival`",
        inline=False
    )
    embed.add_field(
        name="📅 !unholiday",
        value="Remove holiday status from tomorrow",
        inline=False
    )
    embed.add_field(
        name="📋 !changes",
        value="Show all changes for tomorrow",
        inline=False
    )
    embed.add_field(
        name="🔄 !reset",
        value="Reset all changes for tomorrow",
        inline=False
    )
    embed.add_field(
        name="🗑️ !clearall",
        value="Clear ALL stored data (use carefully!)",
        inline=False
    )
    
    embed.set_footer(text="B.E. Electrical • CR Assistant Bot • All changes are saved permanently")
    
    await ctx.send(embed=embed)


# ------------------------------------------------
bot.run(TOKEN)