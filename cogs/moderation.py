python
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
    async def kick(self, interaction: discord.Interaction, user: discord.User, , reason: str = "Not specified") -> None:
        """Kick a user out of the server."""
        member = interaction.guild.get_member(user.id) or await interaction.guild.fetch_member(user.id)
        if member.guild_permissions.administrator:
            embed = discord.Embed(description="User has administrator permissions.", color=0xE02B2B)
            await interaction.response.send_message(embed=embed)
        else:
            try:
                embed = discord.Embed(description=f"{member} was kicked by {interaction.user}!", color=0xBEBEFE)
                embed.add_field(name="Reason:", value=reason)
                await interaction.response.send_message(embed=embed)
                try:
                    await member.send(f"You were kicked by {interaction.user} from {interaction.guild.name}!\nReason: {reason}")
                except:
                    pass
                await member.kick(reason=reason)
            except:
                embed = discord.Embed(description="An error occurred while trying to kick the user. Make sure my role is above the role of the user you want to kick.", color=0xE02B2B)
                await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nick", description="Change the nickname of a user on a server.")
    @app_commands.checks.has_permissions(manage_nicknames=True)
    @app_commands.describe(user="The user that should have a new nickname.", nickname="The new nickname that should be set.")
    async def nick(self, interaction: discord.Interaction, user: discord.User, , nickname: str = None) -> None:
        """Change the nickname of a user on a server."""
        member = interaction.guild.get_member(user.id) or await interaction.guild.fetch_member(user.id)
        try:
            await member.edit(nick=nickname)
            embed = discord.Embed(description=f"{member}'s new nickname is {nickname}!", color=0xBEBEFE)
            await interaction.response.send_message(embed=embed)
        except:
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
                embed = discord.Embed(description=f"{member} was banned by {interaction.user}!", color=0xBEBEFE)
                embed.add_field(name="Reason:", value=reason)
                await interaction.response.send_message(embed=embed)
                try:
                    await member.send(f"You were banned by {interaction.user} from {interaction.guild.name}!\nReason: {reason}")
                except:
                    pass
                await member.ban(reason=reason)
        except:
            embed = discord.Embed(title="Error!", description="An error occurred while trying to ban the user. Make sure my role is above the role of the user you want to ban.", color=0xE02B2B)
            await interaction.response.send_message(embed=embed)

    # Additional commands (warning, purge, etc.) can be similarly converted to slash commands.

async def setup(bot) -> None:
    await bot.add_cog(Moderation(bot))
