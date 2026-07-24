import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
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

# --- MINI WEB SERVER AGAR RENDER TIDAK TIMEOUT ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

def run_server():
    # Render otomatis memberikan port melalui environment variable 'PORT'
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Jalankan web server di background thread secara otomatis saat bot dinyalakan
threading.Thread(target=run_server, daemon=True).start()
# -----------------------------------------------

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

if __name__ == "__main__":
    if DISCORD_BOT_TOKEN:
        bot.run(DISCORD_BOT_TOKEN)
    else:
        print("Error: DISCORD_BOT_TOKEN tidak ditemukan!")
