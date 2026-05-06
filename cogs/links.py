import discord
from discord.ext import commands
from discord import app_commands

class Links(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="링크", description="한율 님의 모든 링크를 나만 보이게 확인합니다.")
    async def slash_link(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🔗 한율 님 공식 링크", color=0x8A2BE2)
        embed.add_field(name="📺 알플레이", value="[바로가기](https://rplay.live/creatorhome/68b00e18461659179fe6fbce?page=contents)", inline=True)
        embed.add_field(name="🟢 치지직", value="[바로가기](https://chzzk.naver.com/edd22e44e7b2fd551cebccd09163c938)", inline=True)
        embed.add_field(name="▶️ 유튜브", value="[바로가기](https://www.youtube.com/@hanYul_owo)", inline=True)
        embed.set_thumbnail(url="https://pb2.rplay.live/pics/a2554f33fcb348be72d1db644d7bcdde")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Links(bot))