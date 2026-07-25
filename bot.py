import os
import requests
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

# URL API Website Flask kamu di PythonAnywhere
FLASK_API_URL = "https://akihito.pythonanywhere.com/api/add-ticket" 

# Token rahasia yang otomatis dibaca dari Environment Variables Render
BOT_SECRET_TOKEN = os.getenv("BOT_SECRET_TOKEN")

RANK_ROLE_MAPPING = {
    1: "1529594788817535068",
}

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Mensinkronkan slash command ke Discord agar muncul di server
        await self.tree.sync()
        print("Slash commands berhasil disinkronkan!")

bot = MyBot()

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

# --- SLASH COMMAND: /giveticket ---
@bot.tree.command(name="giveticket", description="Berikan 1 tiket gacha ke user secara otomatis ke website")
@app_commands.describe(user="Pilih user Discord yang ingin diberi tiket")
async def giveticket(interaction: discord.Interaction, user: discord.User):
    # Pengaman: Hanya Admin server Discord yang bisa memakai command ini
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Kamu tidak memiliki izin Admin untuk menggunakan perintah ini!", ephemeral=True)
        return

    discord_username = user.name 
    
    headers = {"Authorization": f"Bearer {BOT_SECRET_TOKEN}"}
    payload = {"discord_username": discord_username}

    try:
        response = requests.post(FLASK_API_URL, json=payload, headers=headers, timeout=5)
        res_data = response.json()
        
        if response.status_code == 200 and res_data.get("success"):
            await interaction.response.send_message(f"✅ Berhasil! {res_data.get('message')} (Target: {user.mention})")
        else:
            error_msg = res_data.get('error', 'Terjadi kesalahan tidak dikenal.')
            await interaction.response.send_message(f"❌ Gagal memberikan tiket: {error_msg}", ephemeral=True)
            
    except requests.exceptions.ConnectionError:
        await interaction.response.send_message("❌ Gagal terhubung ke server website Flask. Periksa koneksi PythonAnywhere!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Terjadi error: {e}", ephemeral=True)

# --- WEB SERVER SEDERHANA UNTUK RENDER & UPTIMEROBOT ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is active and running!")
    
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

if __name__ == "__main__":
    if DISCORD_BOT_TOKEN:
        # Menjalankan web server mini di background agar Render mendeteksi port terbuka & UptimeRobot bisa melakukan ping
        server_thread = threading.Thread(target=run_web_server, daemon=True)
        server_thread.start()
        print("Web server pendukung UptimeRobot berhasil dijalankan!")

        bot.run(DISCORD_BOT_TOKEN)
    else:
        print("Error: DISCORD_BOT_TOKEN tidak ditemukan di Environment Variables!")
