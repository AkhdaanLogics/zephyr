import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='zep ', intents=intents, help_command=None)


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
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.listening, name="Akhdaan The Great | zep help")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f'Masuk sebagai {bot.user.name} - {bot.user.id}')

@bot.event
async def on_member_join(member):
    print(f'{member.name} telah bergabung ke server.')

@bot.event
async def on_member_remove(member):
    print(f'{member.name} telah keluar dari server.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if any(word in message.content.lower() for word in badwords):
        await message.channel.send(f"{message.author.mention} jangan gunakan kata kasar di sini!") 
        await message.delete()
        return
    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send(f'Halo {ctx.author.mention}!\nGunakan `zep help` untuk daftar perintah.')

@bot.command()
async def help(ctx):
    help_message = (
        "**—— Perintah Dasar ——**\n\n"
        "**zep hello** - `Menyapa pengguna`\n"
        "**zep help** - `Menampilkan daftar perintah`\n"
        "**zep info** - `Menampilkan informasi bot`\n"
        "**zep anonymous** - `Mengirim pesan anonim ke pengguna lain *uji coba*`\n"
        "**zep embed** - `Membuat pesan embed *uji coba*`\n"
        "**zep polling** - `Membuat polling`\n"
        "**zep level** - `Menampilkan level dan XP pengguna *uji coba*`\n\n"
        "**—— Moderator ——**\n\n"
        "**zep kick @user** - `Mengeluarkan user (admin only)`\n"
        "**zep ban @user** - `Banned user (admin only)`\n"
        "**zep unban user_id** - `Unbanned user (admin only)`\n"
        "**zep clear jumlah** - `Menghapus pesan (admin only)`\n"
        "**zep msg @user pesan** - `Mengirim pesan ke DM user (owner only)`\n\n"
        "**—— Games ——**\n\n"
        "**zep khodam** - `Menampilkan khodam`\n"
    )
    await ctx.send(help_message)

@bot.command()
async def info(ctx):
    info_message = (
        f"**Nama Bot:** `{bot.user.name}`\n"
        f"**ID Bot:** `{bot.user.id}`\n"
        f"**Jumlah Server:** `{len(bot.guilds)}`\n"
        f"**Jumlah Anggota:** `{sum(g.member_count for g in bot.guilds)}`\n"
        f"**Prefix:** `zep`\n"
        f"**Versi:** `1.0.0`\n"
        f"**Pengembang:** `Akhdaan The Great`\n"
        f"**Bot Link:** `https://discord.gg/bots/zephyr`\n"
    )
    await ctx.send(info_message)

@bot.command()
async def level(ctx):
    await ctx.send("Fitur level belum tersedia. Silakan tunggu pembaruan selanjutnya.")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None, *, reason="Tanpa alasan"):
    if member is None:
        await ctx.send("Anda harus mention pengguna yang ingin dikeluarkan.\nContoh: `zep kick @user alasan`")
        return
    if member == ctx.author:
        await ctx.send("Anda tidak dapat mengeluarkan diri sendiri.")
    elif member == ctx.guild.owner or member.id == ctx.guild.owner_id:
        await ctx.send("Anda tidak dapat mengeluarkan pemilik server.")
    elif member.top_role >= ctx.author.top_role:
        await ctx.send("Anda tidak dapat mengeluarkan anggota dengan role yang lebih tinggi atau setara.")
    elif member.bot:
        await ctx.send("Anda tidak dapat mengeluarkan bot.")
    elif member.id == bot.user.id:
        await ctx.send("Anda tidak dapat mengeluarkan bot ini.")
    else:
        await member.kick(reason=reason)
        await ctx.send(f'{member.name} telah dikeluarkan dari server.\nAlasan: {reason}')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None, *, reason="Tanpa alasan"):
    if member is None:
        await ctx.send("Anda harus mention pengguna yang ingin dibanned.\nContoh: `zep ban @user alasan`")
        return
    if member == ctx.author:
        await ctx.send("Anda tidak dapat membanned diri sendiri.")
    elif member == ctx.guild.owner or member.id == ctx.guild.owner_id:
        await ctx.send("Anda tidak dapat membanned pemilik server.")
    elif member.top_role >= ctx.author.top_role:
        await ctx.send("Anda tidak dapat membanned anggota dengan role yang lebih tinggi atau setara.")
    elif member.bot:
        await ctx.send("Anda tidak dapat membanned bot.")
    elif member.id == bot.user.id:
        await ctx.send("Anda tidak dapat membanned bot ini.")
    else:
        await ctx.guild.ban(member, reason=reason)
        await ctx.send(f'{member.name} telah dibanned dari server.\nAlasan: {reason}')

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int = None):
    if user_id is None:
        await ctx.send("Anda harus memasukkan ID pengguna yang ingin diunban.\nContoh: `zep unban 1234567890`")
        return
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f'{user.name} telah diunban dari server.')
    except discord.NotFound:
        await ctx.send("Pengguna dengan ID tersebut tidak ditemukan dalam daftar banned.")
    except Exception as e:
        await ctx.send(f"Terjadi kesalahan: {str(e)}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, jumlah: int = 100):
    deleted = await ctx.channel.purge(limit=jumlah)
    await ctx.send(f'Dihapus {len(deleted)} pesan.', delete_after=5)

@bot.command()
async def msg(ctx, member: discord.Member = None, *, message: str = None):
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("Hanya pemilik server yang dapat menggunakan perintah ini.")
        return
    if member is None:
        await ctx.send("Anda harus mention pengguna yang ingin dikirimi DM.\nContoh: `zep send @user Halo, ini pesan pribadi.`")
        return
    if message is None:
        await ctx.send("Anda harus menuliskan isi pesan.\nContoh: `zep send @user Halo, ini pesan pribadi.`")
        return
    try:
        await member.send(message)
        await ctx.send(f'DM berhasil dikirim ke **{member.name}**:\n`{message}`')
    except discord.Forbidden:
        await ctx.send(f'Tidak dapat mengirim DM ke {member.name}. Mungkin mereka menonaktifkan DM dari server ini.')

@bot.command()
async def anonymous(ctx, member: discord.Member = None, *, message: str = None):
    if member is None:
        await ctx.send("Kamu harus mention pengguna yang ingin dikirimi pesan anonim.\nContoh: `zep anonmsg @user isi pesanmu`")
        return
    if message is None:
        await ctx.send("Kamu harus menuliskan isi pesan.\nContoh: `zep anonymous @user isi pesanmu`")
        return
    try:
        embed = discord.Embed(
            title="Ding Dong! ada pesan anonim untukmu!",
            description=message,
            color=discord.Color.pink()
        )
        embed.set_footer(text="Pesan ini dikirim secara anonim melalui bot.")
        await member.send(embed=embed)
        await ctx.send(f'Pesan anonim berhasil dikirim ke **{member.name}**.')
    except discord.Forbidden:
        await ctx.send(f'Tidak dapat mengirim DM ke {member.name}. Mungkin mereka menonaktifkan DM dari server ini.')

@bot.command()
async def embed(ctx, title: str = None, *, content: str = None):
    if title is None or content is None:
        await ctx.send("Kamu harus memberikan judul dan isi konten untuk embed.\nContoh: `zep embed Judul Isi konten`")
        return
    embed = discord.Embed(title=title, description=content, color=discord.Color.blue())
    await ctx.send(embed=embed)

@bot.command()
async def polling(ctx, *, question: str = None):
    if question is None:
        await ctx.send("Kamu harus memberikan pertanyaan untuk polling.\nContoh: `zep polling Apa pendapatmu tentang akhdaan si manusia dermawan?`")
        return
    embed = discord.Embed(title="Polling", description=question, color=discord.Color.green())
    message = await ctx.send(embed=embed)
    await message.add_reaction("👍")
    await message.add_reaction("👎")

@bot.command()
async def khodam(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    elif member == ctx.guild.owner:
        await ctx.send("Pemilik server terlalu hebat untuk memiliki khodam biasa. Mereka adalah khodam itu sendiri!")
        return
    khodam_choice = random.choice(khodam_list)
    embed = discord.Embed(
        title=f"Khodam {member.name}",
        description=f"**{khodam_choice}** adalah khodam yang cocok untuk {member.name}.",
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
