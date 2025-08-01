import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
import random
import asyncio
import yt_dlp
import requests
from typing import Optional
import re
import string
import datetime

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
        # await self.tree.sync(guild=None)
        GUILD_ID=1346560094325968957
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))

bot = MyBot()

@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.listening, name="Akhdaan The Great | /help")
    await bot.change_presence(status=discord.Status.online, activity=activity)
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
    await bot.process_commands(message)

@bot.tree.command(name="hello", description="Menyapa pengguna")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Halo {interaction.user.mention}!\nGunakan `/help` untuk daftar perintah.')

@bot.tree.command(name="help", description="Menampilkan daftar perintah")
async def help_command(interaction: discord.Interaction):
    help_message = (
        "**—— Perintah Dasar ——**\n\n"
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
        "/addqueue - `Menambahkan lagu ke antrian **Under Development**`\n"\
        "/queue - `Melihat daftar lagu dalam antrian **Under Development**`\n"
        "/ask - `Tanya apapun melalui Zep dengan AI`\n"
        "/rename - `Mengubah nama panggilan (nickname) anggota di server`\n\n"
        "**—— Perintah Moderasi ——**\n\n"
        "/kick - `Mengeluarkan user dari server`\n"
        "/ban - `Banned user dari server`\n"
        "/unban - `Unban user dari server`\n\n"
        "**—— Permainaan ——**\n\n"
        "/khodam - `Menampilkan khodam`\n"
        "/anonymous - `Kirim pesan anonim (hanya terlihat oleh pengirim)`\n"
        "/create-party - `Membuat party untuk bermain game **Under Development**`\n"
        "/join-party - `Bergabung ke party sesuai id **Under Development**`\n"
        "/level - `Menampilkan level user`\n\n"
    )
    await interaction.response.send_message(help_message, ephemeral=True)

@bot.tree.command(name="info", description="Menampilkan informasi bot")
async def info(interaction: discord.Interaction):
    info_message = (
        f"**Nama Bot:** `{bot.user.name}`\n"
        f"**ID Bot:** `{bot.user.id}`\n"
        f"**Jumlah Server:** `{len(bot.guilds)}`\n"
        f"**Jumlah Anggota:** `{sum(g.member_count for g in bot.guilds)}`\n"
        f"**Prefix :** `/`\n"
        f"**Versi:** `1.0.2`\n"
        f"**Pengembang:** `Akhdaan The Great`\n"
    )
    await interaction.response.send_message(info_message)

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
    embed = discord.Embed(title="Polling", description=pertanyaan, color=discord.Color.green())
    message = await interaction.channel.send(embed=embed)
    await message.add_reaction("👍")
    await message.add_reaction("👎")
    await interaction.response.send_message("Polling berhasil dikirim!", ephemeral=True)

@bot.tree.command(name="anonymous", description="Kirim pesan anonim ke seseorang")
@app_commands.describe(member="Target penerima pesan anonim", pesan="Isi pesan yang ingin dikirim")
async def anonymous(interaction: discord.Interaction, member: discord.Member, pesan: str):
    try:
        embed = discord.Embed(
            title="Ding Dong! Ada pesan anonim untukmu!",
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

@bot.tree.command(name="level", description="Menampilkan level pengguna")
async def level(interaction: discord.Interaction):
    await interaction.response.send_message("Fitur level belum tersedia. Silakan tunggu pembaruan selanjutnya.")

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

@bot.tree.command(name="addqueue", description="Menambahkan lagu ke antrian")
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

def generate_party_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

@bot.tree.command(name="create-party", description="Membuat party baru")
@app_commands.describe(
    max_members="Jumlah anggota maksimal",
    jobs="Daftar job, pisahkan dengan koma (contoh: Tank,Healer,DPS,DPS)",
    start_time="Waktu mulai (format: YYYY-MM-DD HH:MM)"
)
async def create_party(interaction: discord.Interaction, max_members: int, jobs: str, start_time: str):
    party_id = generate_party_id()
    job_list = [j.strip() for j in jobs.split(",")]

    if max_members != len(job_list):
        await interaction.response.send_message("Jumlah job harus sama dengan jumlah anggota maksimal.", ephemeral=True)
        return

    embed = discord.Embed(title=f"Party {party_id}", color=discord.Color.green())
    embed.add_field(name="Jumlah Anggota", value=f"{len(job_list)}/{max_members}", inline=False)
    embed.add_field(name="Job Slots", value="\n".join([f"{j}: ❌ Kosong" for j in job_list]), inline=False)
    embed.add_field(name="Waktu Mulai", value=start_time, inline=False)
    embed.set_footer(text="Gunakan /join-party <id> <job> untuk bergabung")

    msg = await interaction.channel.send(embed=embed)

    parties[party_id] = {
        "creator": interaction.user.id,
        "max_members": max_members,
        "jobs": job_list,
        "members": {},
        "start_time": start_time,
        "message": msg
    }

    await interaction.response.send_message(f"Party {party_id} berhasil dibuat!", ephemeral=True)

@bot.tree.command(name="join-party", description="Bergabung ke party yang tersedia")
@app_commands.describe(party_id="ID Party yang ingin diikuti", job="Job yang ingin diisi")
async def join_party(interaction: discord.Interaction, party_id: str, job: str):
    if party_id not in parties:
        await interaction.response.send_message("Party tidak ditemukan.", ephemeral=True)
        return

    party = parties[party_id]

    if job not in party["jobs"]:
        await interaction.response.send_message("Job tidak valid untuk party ini.", ephemeral=True)
        return

    if job in party["members"].values():
        await interaction.response.send_message("Job ini sudah diambil pemain lain.", ephemeral=True)
        return

    party["members"][interaction.user.id] = job
    updated_jobs = ""
    for j in party["jobs"]:
        member = [m for m, jb in party["members"].items() if jb == j]
        if member:
            user_name = await bot.fetch_user(member[0])
            updated_jobs += f"{j}: {user_name.name}\n"
        else:
            updated_jobs += f"{j}: Kosong\n"
    embed = discord.Embed(title=f"Party {party_id}", color=discord.Color.green())
    embed.add_field(name="Jumlah Anggota", value=f"{len(party['members'])}/{party['max_members']}", inline=False)
    embed.add_field(name="Job Slots", value=updated_jobs, inline=False)
    embed.add_field(name="Waktu Mulai", value=party["start_time"], inline=False)
    embed.set_footer(text="Gunakan /join-party <id> <job> untuk bergabung")
    await party["message"].edit(embed=embed)
    await interaction.response.send_message(f"Kamu berhasil bergabung ke Party {party_id} sebagai {job}!", ephemeral=True)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)