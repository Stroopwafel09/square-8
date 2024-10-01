import os
from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

class Moderation(commands.Cog, name="moderation"):
    def init(self, bot) -> None:
        self.bot = bot

@app_commands.command(name="kick", description="Kick a user out of the server.")
@app_commands.checks.has_permissions(kick_members=True)
@app_commands.describe(user="The user that should be kicked.", reason="The reason why the user should be kicked.")
async def kick(self, interaction: discord.Interaction, user: discord.User, *, reason: str = "Not specified") -> None:
    """Kick a user out of the server."""
    member = interaction.guild.get_member(user.id) or await interaction.guild.fetch_member(user.id)
    if member.guild_permissions.administrator:
        embed = discord.Embed(description="User has administrator permissions.", color=0xE02B2B)
        await interaction.response.send_message(embed=embed)
    else:
        try:
            embed = discord.Embed(description=f"**{member}** was kicked by **{interaction.user}**!", color=0xBEBEFE)
            embed.add_field(name="Reason:", value=reason)
            await interaction.response.send_message(embed=embed)
            try:
                await member.send(f"You were kicked by **{interaction.user}** from **{interaction.guild.name}**!\nReason: {reason}")
            except:
                pass
            await member.kick(reason=reason)
        except Exception:
            embed = discord.Embed(description="An error occurred while trying to kick the user. Make sure my role is above the role of the user you want to kick.", color=0xE02B2B)
            await interaction.response.send_message(embed=embed)


@app_commands.command(name="nick", description="Change the nickname of a user on a server.")
@app_commands.checks.has_permissions(manage_nicknames=True)
@app_commands.describe(user="The user that should have a new nickname.", nickname="The new nickname that should be set.")
async def nick(self, interaction: discord.Interaction, user: discord.User, *, nickname: str = None) -> None:
    """Change the nickname of a user on a server."""
    member = interaction.guild.get_member(user.id) or await interaction.guild.fetch_member(user.id)
    try:
        await member.edit(nick=nickname)
        embed = discord.Embed(description=f"**{member}'s** new nickname is **{nickname}**!", color=0xBEBEFE)
        await interaction.response.send_message(embed=embed)
    except Exception:
        embed = discord.Embed(description="An error occurred while trying to change the nickname of the user. Make sure my role is above the role of the user you want to change the nickname.", color=0xE02B2B)
        await interaction.response.send_message(embed=embed)


@app_commands.command(name="ban", description="Bans a user from the server.")
@app_commands.checks.has_permissions(ban_members=True)
@app_commands.describe(user="The user that should be banned.", reason="The reason why the user should be banned.")
async def ban(self, interaction: discord.Interaction, user: discord.User, *, reason: str = "Not specified") -> None:
    """Bans a user from the server."""
    member = interaction.guild.get_member(user.id) or await interaction.guild.fetch_member(user.id)
    try:
        if member.guild_permissions.administrator:
            embed = discord.Embed(description="User has administrator permissions.", color=0xE02B2B)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(description=f"**{member}** was banned by **{interaction.user}**!", color=0xBEBEFE)
            embed.add_field(name="Reason:", value=reason)
            await interaction.response.send_message(embed=embed)
            try:
                await member.send(f"You were banned by **{interaction.user}** from **{interaction.guild.name}**!\nReason: {reason}")
            except:
                pass
            await member.ban(reason=reason)
    except Exception:
        embed = discord.Embed(title="Error!", description="An error occurred while trying to ban the user. Make sure my role is above the role of the user you want to ban.", color=0xE02B2B)
        await interaction.response.send_message(embed=embed)


@app_commands.group(name="warning", description="Manage warnings of a user on a server.", invoke_without_command=True)
@app_commands.checks.has_permissions(manage_messages=True)
async def warning(self, interaction: discord.Interaction) -> None:
    """Manage warnings of a user on a server."""
    embed = discord.Embed(description="Please specify a subcommand.\n\n**Subcommands:**\n`add` - Add a warning to a user.\n`remove` - Remove a warning from a user.\n`list` - List all warnings of a user.", color=0xE02B2B)
    await interaction.response.send_message(embed=embed)


@warning.command(name="add", description="Adds a warning to a user in the server.")
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(user="The user that should be warned.", reason="The reason why the user should be warned.")
async def warning_add(self, interaction: discord.Interaction, user: discord.User, *, reason: str = "Not specified") -> None:
    """Warns a user in their private messages."""
    member = interaction.guild.get_member(user.id) or await interaction.guild.fetch_member(user.id)
    total = await self.bot.database.add_warn(user.id, interaction.guild.id, interaction.user.id, reason)
    embed = discord.Embed(description=f"**{member}** was warned by **{interaction.user}**!\nTotal warns for this user: {total}", color=0xBEBEFE)
    embed.add_field(name="Reason:", value=reason)
    await interaction.response.send_message(embed=embed)
    try:
        await member.send(f"You were warned by **{interaction.user}** in **{interaction.guild.name}**!\nReason: {reason}")
    except:
        await interaction.followup.send(f"{member.mention}, you were warned by **{interaction.user}**!\nReason: {reason}")


@warning.command(name="remove", description="Removes a warning from a user in the server.")
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(user="The user that should get their warning removed.", warn_id="The ID of the warning that should be removed.")
async def warning_remove(self, interaction: discord.Interaction, user: discord.User, warn_id: int) -> None:
    """Removes a warning from a user."""
    member = interaction.guild.get_member(user.id) or await interaction.guild.fetch_member(user.id)
    total = await self.bot.database.remove_warn(warn_id, user.id, interaction.guild.id)
    embed = discord.Embed(description=f"I've removed the warning **#{warn_id}** from **{member}**!\nTotal warns for this user: {total}", color=0xBEBEFE)
    await interaction.response.send_message(embed=embed)


@warning.command(name="list", description="Shows the warnings of a user in the server.")
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(user="The user you want to get the warnings of.")
async def warning_list(self, interaction: discord.Interaction, user: discord.User) -> None:
    """Shows the warnings of a user in the server."""
    warnings_list = await self.bot.database.get_warnings(user.id, interaction.guild.id)
    embed = discord.Embed(title=f"Warnings of {user}", color=0xBEBEFE)
    description = ""
    if len(warnings_list) == 0:
        description = "This user has no warnings."
    else:
        for warning in warnings_list:
            description += f"• Warned by <@{warning[2]}>: **{warning[3]}** (<t:{warning[4]}>) - Warn ID #{warning[5]}\n"
    embed.description = description
    await interaction.response.send_message(embed=embed)


@app_commands.command(name="purge", description="Delete a number of messages.")
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(amount="The amount of messages that should be deleted.")
async def purge(self, interaction: discord.Interaction, amount: int) -> None:
    """Delete a number of messages."""
    await interaction.response.send_message("Deleting messages...")  # Acknowledges the interaction
    purged_messages = await interaction.channel.purge(limit=amount + 1)
    embed = discord.Embed(description=f"**{interaction.user}** cleared **{len(purged_messages) - 1}** messages!", color=0xBEBEFE)
    await interaction.followup.send(embed=embed)


@hackban.command(name="hackban", description="Bans a user without the user having to be in the server.")
@app_commands.checks.has_permissions(ban_members=True)
@app_commands.describe(user_id="The user ID that should be banned.", reason="The reason why the user should be banned.")
async def hackban(self, interaction: discord.Interaction, user_id: str, *, reason: str = "Not specified") -> None:
    """Bans a user without the user having to be in the server."""
    try:
        await interaction.guild.ban(discord.Object(id=user_id), reason=reason)
        user = self.bot.get_user(int(user_id)) or await self.bot.fetch_user(int(user_id))
        embed = discord.Embed(
            description=f"**{user}** (ID: {user_id}) was banned by **{interaction.user}**!",
            color=0xBEBEFE,
        )
        embed.add_field(name="Reason:", value=reason)
        await interaction.response.send_message(embed=embed)
    except Exception:
        embed = discord.Embed(
            description="An error occurred while trying to ban the user. Make sure the ID is valid and corresponds to an existing user.",
            color=0xE02B2B,
        )
        await interaction.response.send_message(embed=embed)

@app_commands.command(name="archive", description="Archives in a text file the last messages with a chosen limit of messages.")
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(limit="The limit of messages that should be archived.")
async def archive(self, interaction: discord.Interaction, limit: int = 10) -> None:
    """Archives in a text file the last messages with a chosen limit of messages."""
    log_file = f"{interaction.channel.id}.log"
    with open(log_file, "w", encoding="UTF-8") as f:
        f.write(
            f'Archived messages from: #{interaction.channel} ({interaction.channel.id}) in the guild "{interaction.guild}" ({interaction.guild.id}) at {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n'
        )
        async for message in interaction.channel.history(limit=limit, before=interaction.message):
            attachments = [attachment.url for attachment in message.attachments]
            attachments_text = (
                f"[Attached File{'s' if len(attachments) >= 2 else ''}: {', '.join(attachments)}]"
                if attachments else ""
            )
            f.write(
                f"{message.created_at.strftime('%d.%m.%Y %H:%M:%S')} {message.author} {message.id}: {message.clean_content} {attachments_text}\n"
            )
    file = discord.File(log_file)
    await interaction.response.send_message(file=file)
    os.remove(log_file)


    # Additional commands (warning, purge, etc.) can be similarly converted to slash commands.

async def setup(bot) -> None:
    await bot.add_cog(Moderation(bot))
