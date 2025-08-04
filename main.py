import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import json
import os
import random
import asyncio
import yt_dlp
import requests
from typing import Optional
import re
import string
import datetime
from discord.ui import View, Select
import pytz

tz_wib = pytz.timezone("Asia/Jakarta")

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='zep ', intents=intents, help_command=None)

    async def setup_hook(self):
        await self.tree.sync(guild=None)
        # # GUILD_ID=1346560094325968957
        # await self.tree.sync(guild=discord.Object(id=GUILD_ID))

bot = MyBot()

levels_file = "level.json"
user_levels = {}
if os.path.exists(levels_file):
    with open(levels_file, "r") as f:
        user_levels = json.load(f)
else:
    user_levels = {}

level_config_file = "level_config.json"
server_config = {}
if os.path.exists(level_config_file):
    with open(level_config_file, "r") as f:
        server_config = json.load(f)
else:
    server_config = {}

def save_levels():
    with open(levels_file, "w") as f:
        json.dump(user_levels, f, indent=4)

def save_config():
    with open(level_config_file, "w") as f:
        json.dump(server_config, f, indent=4)

@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.listening, name="Akhdaan The Great | /help")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    bot.loop.create_task(party_reminder_checker())
    print(f"Masuk sebagai {bot.user.name} - {bot.user.id}")


badwords = [
    'anjing', 'babi', 'kontol', 'memek', 'monyet', 'goblok',
    'tolol', 'bangsat', 'asu', 'jancok', 'sialan', 'kampret',
    'tai', 'ngentot', 'setan', 'bego', 'brengsek', 'bangke',
    'shit', 'fuck', 'damn'
]

khodam_list = [
    'PESUT MAHAKAM', 'UGET UGET BOYOLALI', 'AKBAR KESEIMBANGAN',
    'SUKI SERIKAT', 'EKO MAGELANGAN', 'UJANG MAHATHIR', 'BONDAN ENCENG GONDOK',
    'ASEP ASAM MANIS', 'NABIL ASPAL KERAS'
]

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.lower()
    if any(re.search(rf"\b{re.escape(word)}\b", content) for word in badwords):
        await message.channel.send(f"{message.author.mention} jangan gunakan kata kasar di sini!")
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        return
    
    guild_id = str(message.guild.id)
    user_id = str(message.author.id)

    if guild_id not in server_config:
        server_config[guild_id] = {"leveling_enabled": True, "level_channel": None}
        save_config()

    config = server_config[guild_id]
    if not config["leveling_enabled"]:
        return
    if user_id not in user_levels:
        user_levels[user_id] = {"xp": 0, "level": 1}

    gained_xp = random.randint(5, 10)
    user_levels[user_id]["xp"] += gained_xp
    xp = user_levels[user_id]["xp"]
    level = user_levels[user_id]["level"]
    next_level_xp = level * 100

    if xp >= next_level_xp:
        user_levels[user_id]["level"] += 1
        target_channel = message.channel
        if config["level_channel"]:
            ch = bot.get_channel(int(config["level_channel"]))
            if ch:
                target_channel = ch

        await target_channel.send(
            f"🎉 Selamat {message.author.mention}, kamu naik ke **Level {user_levels[user_id]['level']}**!"
        )
    save_levels()
    await bot.process_commands(message)

@bot.tree.command(name="hello", description="Menyapa pengguna")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Halo {interaction.user.mention}!\nGunakan `/help` untuk daftar perintah.')

@bot.tree.command(name="help", description="Menampilkan daftar perintah")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Daftar Perintah Zephry",
        description="Pilih kategori di bawah ini untuk melihat daftar perintah yang tersedia.",
        color=discord.Color.gold()
    )
    select = Select(
        placeholder="Pilih kategori perintah...",
        options=[
            discord.SelectOption(label="Perintah Dasar", description="Perintah umum bot"),
            discord.SelectOption(label="Perintah Moderasi", description="Perintah untuk moderasi server"),
            discord.SelectOption(label="Permainan", description="Perintah untuk hiburan dan permainan")
        ]
    )

    async def select_callback(interaction_select):
        pilihan = select.values[0]
        if pilihan == "Perintah Dasar":
            desc = (
                "/hello - `Menyapa pengguna`\n"
                "/help - `Menampilkan daftar perintah`\n"
                "/info - `Menampilkan informasi bot`\n"
                "/polling - `Membuat polling dengan reaksi`\n"
                "/embed - `Membuat pesan embed`\n"
                "/play - `Memainkan musik dari YouTube`\n"
                "/pause - `Pause musik yang sedang diputar`\n"
                "/resume - `Melanjutkan musik yang dipause`\n"
                "/stop - `Menghentikan musik yang sedang diputar`\n"
                "/leave - `Bot keluar dari voice channel`\n"
                "/addqueue - `Menambahkan lagu ke antrian`\n"
                "/queue - `Melihat daftar lagu dalam antrian`\n"
                "/ask - `Tanya apapun melalui Zep dengan AI`\n"
            )
        elif pilihan == "Perintah Moderasi":
            desc = (
                "/kick - `Mengeluarkan user dari server`\n"
                "/ban - `Banned user dari server`\n"
                "/unban - `Unban user dari server`\n"
                "/rename - `Mengubah nickname anggota`\n"
                "/clear - `Menghapus sejumlah pesan dari channel`\n"
                "/set-level-channel - `Mengatur channel untuk notifikasi level`\n"
                "/enable-leveling - `Aktifkan atau matikan sistem leveling`\n"
            )
        else:
            desc = (
                "/khodam - `Menampilkan khodam`\n"
                "/anonymous - `Kirim pesan anonim`\n"
                "/create-party - `Membuat party untuk bermain game`\n"
                "/join-party - `Bergabung ke party sesuai id`\n"
                "/party - `Menampilkan daftar party aktif`\n"
                "/level - `Menampilkan level user`\n"
                "/leaderboard - `Melihat leaderboard level server`\n"
            )
        embed_new = discord.Embed(
            title=f"{pilihan}",
            description=desc,
            color=discord.Color.gold()
        )
        await interaction_select.response.edit_message(embed=embed_new, view=view)
    select.callback = select_callback
    view = View()
    view.add_item(select)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="info", description="Menampilkan informasi bot")
async def info(interaction: discord.Interaction):
    info_message = discord.Embed(
        title="Informasi Bot",
        description=(
            f"**Nama Bot:** `{bot.user.name}`\n"
            f"**ID Bot:** `{bot.user.id}`\n"
            f"**Jumlah Server:** `{len(bot.guilds)}`\n"
            f"**Jumlah Anggota:** `{sum(g.member_count for g in bot.guilds)}`\n"
            f"**Prefix:** `/`\n"
            f"**Versi:** `1.0.3`\n"
            f"**Pengembang:** `Akhdaan The Great`\n"
        ),
        color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=info_message)

@bot.tree.command(name="khodam", description="Menampilkan khodam secara acak")
@app_commands.describe(member="(Opsional) Pilih user lain")
async def khodam(interaction: discord.Interaction, member: discord.Member = None):
    if member is None:
        member = interaction.user
    elif member == interaction.guild.owner:
        await interaction.response.send_message("Pemilik server terlalu hebat untuk memiliki khodam biasa. Mereka adalah khodam itu sendiri!")
        return
    khodam_choice = random.choice(khodam_list)
    embed = discord.Embed(
        title=f"Khodam {member.name}",
        description=f"**{khodam_choice}** adalah khodam yang cocok untuk {member.name}.",
        color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="polling", description="Membuat polling dengan reaksi 👍 👎")
@app_commands.describe(pertanyaan="Pertanyaan untuk polling")
async def polling(interaction: discord.Interaction, pertanyaan: str):
    embed = discord.Embed(title="Polling", description=pertanyaan, color=discord.Color.gold())
    message = await interaction.channel.send(embed=embed)
    await message.add_reaction("👍")
    await message.add_reaction("👎")
    await interaction.response.send_message("Polling berhasil dikirim!", ephemeral=True)

@bot.tree.command(name="anonymous", description="Kirim pesan anonim ke seseorang")
@app_commands.describe(member="Target penerima pesan anonim", pesan="Isi pesan yang ingin dikirim")
async def anonymous(interaction: discord.Interaction, member: discord.Member, pesan: str):
    try:
        embed = discord.Embed(
            title="Ding dong! Ada pesan anonim untukmu!",
            description=pesan,
            color=discord.Color.pink()
        )
        embed.set_footer(text="Pesan ini dikirim secara anonim melalui bot.")
        await member.send(embed=embed)
        await interaction.response.send_message(f"Pesan anonim berhasil dikirim ke **{member.name}**.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"Tidak dapat mengirim DM ke {member.name}.", ephemeral=True)

@bot.tree.command(name="embed", description="Membuat embed custom")
@app_commands.describe(title="Judul embed", content="Isi konten embed")
async def embed(interaction: discord.Interaction, title: str, content: str):
    em = discord.Embed(title=title, description=content, color=discord.Color.blue())
    await interaction.response.send_message(embed=em)

@bot.tree.command(name="level", description="Cek level dan XP kamu atau user lain")
@app_commands.describe(user="User yang ingin dicek (opsional)")
async def level(interaction: discord.Interaction, user: discord.User = None):
    target = user or interaction.user
    user_id = str(target.id)

    if user_id not in user_levels:
        await interaction.response.send_message(f"{target.mention} belum memiliki data level.", ephemeral=True)
        return
    data = user_levels[user_id]
    embed = discord.Embed(
            title=f"Level Info",
            description=(
                f"**Level:** {data['level']}\n"
                f"**XP:** {data['xp']} / {data['level'] * 100}"
            ),
            color=discord.Color.blue()
        )
    await interaction.response.send_message(
        content=f"{target.mention}",
        embed=embed,
        ephemeral=False
    )

@bot.tree.command(name="set-level-channel", description="Set channel khusus untuk notifikasi level")
@app_commands.describe(channel="Channel yang ingin dijadikan channel leveling")
@app_commands.checks.has_permissions(administrator=True)
async def set_level_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_id = str(interaction.guild.id)

    if guild_id not in server_config:
        server_config[guild_id] = {"leveling_enabled": True, "level_channel": None}

    server_config[guild_id]["level_channel"] = str(channel.id)
    save_config()
    await interaction.response.send_message(
        f"✅ Channel leveling diatur ke {channel.mention}", ephemeral=True
    )

@bot.tree.command(name="enable-leveling", description="Aktifkan atau matikan sistem leveling di server ini")
@app_commands.checks.has_permissions(administrator=True)
async def toggle_leveling(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)

    if guild_id not in server_config:
        server_config[guild_id] = {"leveling_enabled": True, "level_channel": None}

    server_config[guild_id]["leveling_enabled"] = not server_config[guild_id]["leveling_enabled"]
    state = "✅ AKTIF" if server_config[guild_id]["leveling_enabled"] else "⛔ NONAKTIF"
    save_config()
    await interaction.response.send_message(f"Leveling sekarang: **{state}**", ephemeral=True)

@bot.tree.command(name="leaderboard", description="Melihat leaderboard level server ini")
@app_commands.describe(limit="Jumlah user yang ingin ditampilkan (default 10)")
async def leaderboard(interaction: discord.Interaction, limit: int = 10):
    guild_id = str(interaction.guild.id)
    if guild_id not in server_config or not server_config[guild_id].get("leveling_enabled", True):
        await interaction.response.send_message("Sistem leveling tidak aktif di server ini.", ephemeral=True)
        return
    sorted_users = sorted(user_levels.items(), key=lambda x: (x[1]['level'], x[1]['xp']), reverse=True)
    leaderboard_text = ""
    for i, (user_id, data) in enumerate(sorted_users[:limit], start=1):
        user = await bot.fetch_user(int(user_id))
        leaderboard_text += f"{i}. {user.name} - Level {data['level']} (XP: {data['xp']})\n"
    if not leaderboard_text:
        leaderboard_text = "Tidak ada data level yang tersedia."
    embed = discord.Embed(
        title="Leaderboard Leveling",
        description=leaderboard_text,
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"Menampilkan {len(sorted_users)} user, menampilkan {limit} teratas.")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="clear", description="Menghapus sejumlah pesan dari channel")
@app_commands.describe(amount="Jumlah pesan yang ingin dihapus")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    if amount < 1 or amount > 100:
        await interaction.response.send_message("Jumlah pesan harus antara 1 dan 100.", ephemeral=True)
        return
    deleted = await interaction.channel.purge(limit=amount + 1)
    await interaction.response.send_message(f"Berhasil menghapus {len(deleted) - 1} pesan.", ephemeral=True)

@bot.tree.command(name="kick", description="Mengeluarkan anggota dari server")
@app_commands.describe(member="User yang ingin dikeluarkan", reason="Alasan pengeluaran")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Tanpa alasan"):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("Kamu tidak punya izin untuk kick anggota.", ephemeral=True)
        return
    await member.kick(reason=reason)
    await interaction.response.send_message(f"{member.mention} telah dikeluarkan. Alasan: {reason}")

@bot.tree.command(name="ban", description="Banned anggota dari server")
@app_commands.describe(member="User yang ingin dibanned", reason="Alasan banned")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Tanpa alasan"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("Kamu tidak punya izin untuk ban anggota.", ephemeral=True)
        return
    await interaction.guild.ban(user=member, reason=reason)
    await interaction.response.send_message(f"{member.mention} telah dibanned. Alasan: {reason}")

@bot.tree.command(name="unban", description="Unban anggota dari server berdasarkan ID")
@app_commands.describe(user_id="ID pengguna yang ingin di-unban")
async def unban(interaction: discord.Interaction, user_id: str):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("Kamu tidak punya izin untuk unban anggota.", ephemeral=True)
        return
    user = await bot.fetch_user(int(user_id))
    try:
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"{user.name} telah di-unban dari server.")
    except discord.NotFound:
        await interaction.response.send_message("Pengguna tidak ditemukan dalam daftar banned.", ephemeral=True)

@bot.tree.command(name="play", description="Memainkan musik dari YouTube")
@app_commands.describe(query="Judul lagu atau URL YouTube")
async def play(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    voice_channel = interaction.user.voice.channel if interaction.user.voice else None
    if not voice_channel:
        await interaction.followup.send("Kamu harus berada di voice channel dulu.", ephemeral=True)
        return
    if interaction.guild.voice_client is None:
        vc = await voice_channel.connect()
    else:
        vc = interaction.guild.voice_client
    ytdl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }
    try:
        with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            url = info['url']
            title = info.get('title', 'Unknown Title')
        vc.stop()
        vc.play(discord.FFmpegPCMAudio(
            url,
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
        ))
        await interaction.followup.send(f"Sekarang memutar: **{title}**")
    except Exception as e:
        await interaction.followup.send(f"Gagal memutar musik: {str(e)}", ephemeral=True)

queues = {}

def play_next(guild_id, vc):
    if queues[guild_id]:
        url, title = queues[guild_id].pop(0)
        vc.play(
            discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'),
            after=lambda e: play_next(guild_id, vc)
        )

@bot.tree.command(name="add-queue", description="Menambahkan lagu ke antrian")
@app_commands.describe(query="Judul lagu atau URL YouTube")
async def add_queue(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    voice_channel = interaction.user.voice.channel if interaction.user.voice else None
    if not voice_channel:
        await interaction.followup.send("Kamu harus berada di voice channel dulu.", ephemeral=True)
        return
    
    if interaction.guild.voice_client is None:
        vc = await voice_channel.connect()
    else:
        vc = interaction.guild.voice_client

    ytdl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }
    try:
        with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            url = info['url']
            title = info.get('title', 'Unknown Title')
        if interaction.guild.id not in queues:
            queues[interaction.guild.id] = []
        if not vc.is_playing():
            vc.play(
                discord.FFmpegPCMAudio(url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'),
                after=lambda e: play_next(interaction.guild.id, vc)
            )
            await interaction.followup.send(f"Sekarang memutar: **{title}**")
        else:
            queues[interaction.guild.id].append((url, title))
            await interaction.followup.send(f"Lagu **{title}** telah ditambahkan ke antrian.")
    except Exception as e:
        await interaction.followup.send(f"Gagal menambahkan lagu ke antrian: {str(e)}", ephemeral=True)

@bot.tree.command(name="queue", description="Melihat daftar lagu dalam antrian")
async def queue(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    if guild_id not in queues or len(queues[guild_id]) == 0:
        await interaction.response.send_message("Tidak ada lagu dalam antrian saat ini.", ephemeral=True)
        return
    queue_list = ""
    for i, (_, title) in enumerate(queues[guild_id], start=1):
        queue_list += f"{i}. **{title}**\n"

    embed = discord.Embed(
        title="🎶 Antrian Lagu",
        description=queue_list,
        color=discord.Color.blurple()
    )
    embed.set_footer(text=f"Total lagu dalam antrian: {len(queues[guild_id])}")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="pause", description="Pause lagu yang sedang diputar")
async def pause(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await interaction.response.send_message("Musik dipause.")
    else:
        await interaction.response.send_message("Tidak ada musik yang sedang diputar.", ephemeral=True)

@bot.tree.command(name="resume", description="Melanjutkan lagu yang dipause")
async def resume(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_paused():
        vc.resume()
        await interaction.response.send_message("Musik dilanjutkan.")
    else:
        await interaction.response.send_message("Tidak ada musik yang dipause.", ephemeral=True)

@bot.tree.command(name="stop", description="Menghentikan musik yang sedang diputar")
async def stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message("Musik dihentikan.")
    else:
        await interaction.response.send_message("Tidak ada musik yang sedang diputar.", ephemeral=True)

@bot.tree.command(name="leave", description="Bot keluar dari voice channel")
async def leave(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_connected():
        await vc.disconnect()
        await interaction.response.send_message("Bot keluar dari voice channel.")
    else:
        await interaction.response.send_message("Bot tidak sedang berada di voice channel.", ephemeral=True)

def tanya_ai(prompt: str) -> Optional[str]:
    url = "https://api.cohere.ai/v1/chat"
    headers = {
        "Authorization": f"Bearer {os.getenv('COHERE_API_KEY')}",
        "Content-Type": "application/json"
    }

    payload = {
        "message": prompt,
        "chat_history": []
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("text", "Maaf, saya tidak bisa menjawab sekarang.")
    except Exception as e:
        print(f"[COHERE AI ERROR] {e}")
        return "Terjadi kesalahan saat menghubungi Cohere AI."
    
@bot.tree.command(name="ask", description="Tanyakan sesuatu ke AI Zep")
async def ask(interaction: discord.Interaction, pertanyaan: str):
    await interaction.response.defer(thinking=True)
    jawaban = tanya_ai(pertanyaan)
    await interaction.followup.send(f"**Pertanyaan:** {pertanyaan}\n**Jawaban AI:** `{jawaban}`")

@bot.tree.command(name="rename", description="Mengubah nama panggilan (nickname) anggota di server")
@app_commands.describe(member="User yang ingin diubah namanya", new_name="Nama baru yang diinginkan")
async def rename(interaction: discord.Interaction, member: discord.Member, new_name: str):
    if not interaction.user.guild_permissions.manage_nicknames:
        await interaction.response.send_message("Kamu tidak punya izin untuk mengubah nickname anggota.", ephemeral=True)
        return
    if not interaction.guild.me.guild_permissions.manage_nicknames:
        await interaction.response.send_message("Bot tidak memiliki izin untuk mengubah nickname.", ephemeral=True)
        return
    try:
        await member.edit(nick=new_name)
        await interaction.response.send_message(f"Nickname **{member.name}** berhasil diubah menjadi **{new_name}**.")
    except discord.Forbidden:
        await interaction.response.send_message("Tidak bisa mengubah nickname anggota ini karena role bot lebih rendah.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Gagal mengubah nickname: {str(e)}", ephemeral=True)

parties = {}

async def party_reminder_checker():
    await bot.wait_until_ready()
    while not bot.is_closed():
        now = datetime.datetime.now(tz_wib)
        for party_id, party in list(parties.items()):
            try:
                start_time_str = party["start_time"].replace(" WIB", "")
                start_time = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
                start_time = tz_wib.localize(start_time)
                reminder_time = start_time - datetime.timedelta(minutes=15)

                if "reminder_sent" not in party and now >= reminder_time:
                    mentions = " ".join([f"<@{member_id}>" for member_id in party["members"].keys()])
                    if mentions:
                        embed = discord.Embed(
                            title=f"⏰ Reminder Party {party_id}",
                            description=f"15 menit lagi party akan dimulai!\n\nPeserta: {mentions}",
                            color=discord.Color.orange()
                        )
                        await party["message"].channel.send(embed=embed)
                    party["reminder_sent"] = True

                if now >= start_time + datetime.timedelta(hours=1):
                    embed = discord.Embed(
                        title=f"❌ Party {party_id} Berakhir",
                        description="Party ini telah berakhir dan dihapus dari daftar.",
                        color=discord.Color.red()
                    )
                    await party["message"].channel.send(embed=embed)
                    del parties[party_id]
            except Exception as e:
                print(f"[Reminder Error] {e}")
        await asyncio.sleep(60)

def generate_party_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

@bot.tree.command(name="create-party", description="Membuat party baru")
@app_commands.describe(
    party_name="Nama party yang akan dibuat",
    max_members="Jumlah anggota maksimal",
    jobs="Daftar job, pisahkan dengan koma (contoh: Paladin,Priest,Force User,Acrobat)",
    start_time="Waktu mulai (format: YYYY-MM-DD HH:MM)"
)
async def create_party(interaction: discord.Interaction, party_name: str, max_members: int, jobs: str, start_time: str):
    try:
        start_time_obj = tz_wib.localize(datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M"))
        start_time_str = start_time_obj.strftime("%Y-%m-%d %H:%M %Z")
    except ValueError:
        await interaction.response.send_message("❌ Format waktu salah! Gunakan format: `YYYY-MM-DD HH:MM`", ephemeral=True)
        return

    party_id = generate_party_id()
    job_list = [j.strip() for j in jobs.split(",")]

    if max_members != len(job_list):
        await interaction.response.send_message("❌ Jumlah job harus sama dengan jumlah anggota maksimal.", ephemeral=True)
        return

    # Embed Party
    embed = discord.Embed(title=f"🎉 {party_name} (ID: {party_id})", color=discord.Color.green())
    embed.add_field(name="Jumlah Anggota", value=f"0/{max_members}", inline=False)
    embed.add_field(name="Job Slots", value="\n".join([f"{j}: ❌ Kosong" for j in job_list]), inline=False)
    embed.add_field(name="Waktu Mulai", value=start_time_str, inline=False)
    embed.set_footer(text=f"Gunakan /join-party {party_id} untuk bergabung")

    msg = await interaction.channel.send(embed=embed)

    parties[party_id] = {
        "creator": interaction.user.id,
        "party_name": party_name,
        "max_members": max_members,
        "jobs": job_list,
        "members": {},
        "start_time": start_time_str,
        "message": msg
    }

    await interaction.response.send_message(embed=discord.Embed(
        title="✅ Party Berhasil Dibuat",
        description=f"Party **{party_name}** (ID: `{party_id}`) berhasil dibuat dan akan dimulai pada **{start_time_str}**.",
        color=discord.Color.green()
    ), ephemeral=True)

class JobDropdown(discord.ui.View):
    def __init__(self, party_id, jobs):
        super().__init__(timeout=60)
        self.party_id = party_id
        self.selected_job = None
        options = [discord.SelectOption(label=j) for j in jobs]
        self.add_item(JobSelect(self, options))

class JobSelect(discord.ui.Select):
    def __init__(self, parent, options):
        super().__init__(placeholder="Pilih job yang ingin diisi...", options=options)
        self.parent = parent

    async def callback(self, interaction: discord.Interaction):
        self.parent.selected_job = self.values[0]
        await interaction.response.send_message(
            f"✅ Kamu memilih job: **{self.values[0]}**", ephemeral=True
        )
        self.view.stop()

@bot.tree.command(name="join-party", description="Bergabung ke party dengan dropdown job")
@app_commands.describe(party_id="ID Party yang ingin diikuti")
async def join_party(interaction: discord.Interaction, party_id: str):
    if party_id not in parties:
        await interaction.response.send_message("❌ Party tidak ditemukan.", ephemeral=True)
        return

    party = parties[party_id]
    available_jobs = [j for j in party["jobs"] if j not in party["members"].values()]

    if not available_jobs:
        await interaction.response.send_message("⚠️ Semua slot job sudah terisi.", ephemeral=True)
        return

    view = JobDropdown(party_id, available_jobs)
    await interaction.response.send_message("Pilih job yang ingin kamu isi:", view=view, ephemeral=True)
    await view.wait()

    if view.selected_job is None:
        return

    job = view.selected_job

    party["members"][interaction.user.id] = job
    updated_jobs = ""
    for j in party["jobs"]:
        member = [m for m, jb in party["members"].items() if jb == j]
        if member:
            user_name = await bot.fetch_user(member[0])
            updated_jobs += f"{j}: {user_name.mention}\n"
        else:
            updated_jobs += f"{j}: ❌ Kosong\n"
    embed = discord.Embed(title=f"Party {party_id}", color=discord.Color.green())
    embed.add_field(name="Jumlah Anggota", value=f"{len(party['members'])}/{party['max_members']}", inline=False)
    embed.add_field(name="Job Slots", value=updated_jobs, inline=False)
    embed.add_field(name="Waktu Mulai", value=party["start_time"], inline=False)
    embed.set_footer(text="Gunakan /join-party <id> untuk bergabung")
    await party["message"].edit(embed=embed)
    await interaction.followup.send(f"✅ Kamu berhasil bergabung ke Party {party_id} sebagai **{job}**!", ephemeral=True)

@bot.tree.command(name="party", description="Menampilkan semua party aktif")
async def list_party(interaction: discord.Interaction):
    if not parties:
        await interaction.response.send_message(embed=discord.Embed(
            title="Daftar Party Aktif",
            description="Tidak ada party aktif saat ini.",
            color=discord.Color.orange()
        ), ephemeral=True)
        return

    embed = discord.Embed(title="Daftar Party Aktif", color=discord.Color.blurple())

    for party_id, party in parties.items():
        updated_jobs = ""
        for j in party["jobs"]:
            member = [m for m, jb in party["members"].items() if jb == j]
            if member:
                user = await bot.fetch_user(member[0])
                updated_jobs += f"{j}: {user.mention}\n"
            else:
                updated_jobs += f"{j}: ❌ Kosong\n"

        creator_user = await bot.fetch_user(party["creator"])
        embed.add_field(
            name=f"🎮 {party['party_name']} (ID: {party_id})",
            value=(
                f"**Party Leader:** {creator_user.mention}\n"
                f"**Anggota:** {len(party['members'])}/{party['max_members']}\n"
                f"**Jobs:**\n{updated_jobs}"
                f"**Mulai:** {party['start_time']}\n"
                f"Gunakan `/join-party {party_id}` untuk bergabung"
            ),
            inline=False
        )
    await interaction.response.send_message(embed=embed)


bot.run(token, log_handler=handler, log_level=logging.DEBUG)