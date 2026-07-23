import os
import sqlite3
import requests
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

RANK_ROLE_MAPPING = {
    1: "1529594788817535068",
}

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot Discord Berhasil Online Sebagai: {bot.user}")

def get_member_id_by_username(discord_username, guild):
    if not discord_username:
        return None
    clean_input = discord_username.strip().lstrip('@').lower()
    for member in guild.members:
        if (member.name.lower() == clean_input or 
            (member.global_name and member.global_name.lower() == clean_input) or
            str(member).lower() == clean_input):
            return member.id
    return None

# Opsional: Bisa ditambahkan fungsi untuk mengecek database bersama atau Webhook listener jika ingin role otomatis aktif kembali dari server terpisah.
print("Bot Discord Worker siap dijalankan.")

if __name__ == "__main__":
    if DISCORD_BOT_TOKEN:
        bot.run(DISCORD_BOT_TOKEN)
    else:
        print("Error: DISCORD_BOT_TOKEN tidak ditemukan!")