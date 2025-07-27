import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='zep', intents=intents)

@bot.event
async def on_ready():
    print(f'Masuk sebagai {bot.user.name} - {bot.user.id}')

@bot.event
async def on_member_join(member):
    print(f'{member.name} telah bergabung ke server.')

@bot.event
async def on_member_remove(member):
    print(f'{member.name} telah meninggalkan server.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('zep hello'):
        await message.channel.send(f'Halo {message.author.name}!')

    if message.content.startswith('zep help'):
        help_message = (
            "**—— Perintah Dasar ——**\n\n"
            "**zep hello** - `Menyapa pengguna`\n"
            "**zep help** - `Menampilkan daftar perintah`\n"
            "**zep info** - `Menampilkan informasi bot`\n\n"
            "**—— Moderator ——**\n\n"
            "**zep kick** - `Mengeluarkan user (admin only)`\n"
            "**zep ban** - `Banned user (admin only)`\n"
            "**zep unban** - `Unbanned user (admin only)`\n" 
            "**zep clear** - `Menghapus pesan (admin only)`\n\n"
        )
        await message.channel.send(help_message)
    
    if message.content.startswith('zep kick'):
        if message.author.guild_permissions.kick_members:
            user = message.mentions[0] if message.mentions else None
            if user:
                await message.guild.kick(user)
                await message.channel.send(f'{user.name} telah dikeluarkan dari server.')
            else:
                await message.channel.send('Silakan sebutkan pengguna yang ingin dikeluarkan.')
        else:
            await message.channel.send('Anda tidak memiliki izin untuk menggunakan perintah ini.')
    await bot.process_commands(message)

    if message.content.startswith('zep ban'):
        if message.author.guild_permissions.ban_members:
            user = message.mentions[0] if message.mentions else None
            if user:
                await message.guild.ban(user)
                await message.channel.send(f'{user.name} telah dibanned dari server.')
            else:
                await message.channel.send('Silakan sebutkan pengguna yang ingin dibanned.')
        else:
            await message.channel.send('Anda tidak memiliki izin untuk menggunakan perintah ini.')
    
    if message.content.startswith('zep unban'):
        if message.author.guild_permissions.ban_members:
            user_id = message.content.split(' ')[2] if len(message.content.split(' ')) > 2 else None
            if user_id:
                user = await bot.fetch_user(int(user_id))
                await message.guild.unban(user)
                await message.channel.send(f'{user.name} telah diunban dari server.')
            else:
                await message.channel.send('Silakan sebutkan ID pengguna yang ingin diunban.')
        else:
            await message.channel.send('Anda tidak memiliki izin untuk menggunakan perintah ini.')

    if message.content.startswith('zep clear'):
        if message.author.guild_permissions.manage_messages:
            try:
                count = int(message.content.split(' ')[2]) if len(message.content.split(' ')) > 2 else 100
                deleted = await message.channel.purge(limit=count)
                await message.channel.send(f'Dihapus {len(deleted)} pesan.', delete_after=5)
            except ValueError:
                await message.channel.send('Silakan masukkan jumlah pesan yang valid untuk dihapus.')
        else:
            await message.channel.send('Anda tidak memiliki izin untuk menggunakan perintah ini.')

    if message.content.startswith('zep info'):
        info_message = (
            f"**Nama Bot:** `{bot.user.name}`\n"
            f"**ID Bot:** `{bot.user.id}`\n"
            f"**Jumlah Server:** `{len(bot.guilds)}`\n"
            f"**Jumlah Anggota:** `{sum(g.member_count for g in bot.guilds)}`\n"
            f"**Prefix:** `zep`\n"
            f"**Versi:** `1.0.0`\n"
            f"**Pengembang:** `Akhdaan The Great`\n"
        )
        await message.channel.send(info_message)
    
    if "shit" in message.content.lower():
        await message.channel.send("Jangan gunakan kata kasar di sini!") 
        await message.delete()

bot.run(token, log_handler=handler, log_level=logging.DEBUG)