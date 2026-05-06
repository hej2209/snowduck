import discord
from discord.ext import commands
from discord import app_commands

class Links(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="링크", description="한율 님의 모든 링크를 나만 보이게 확인합니다.")
    async def slash_link(self, interaction: discord.Interaction):
        embed = discord.Embed(
        title="🔗 한율 님 공식 링크 모음",
        description="한율 님의 모든 공식 채널과 안내 페이지입니다!",
        color=0x8A2BE2
    )
        embed.add_field(name="📺 알플레이", value="[바로가기](https://rplay.live/creatorhome/68b00e18461659179fe6fbce?page=contents)", inline=True)
    	embed.add_field(name="🟢 치지직", value="[바로가기](https://chzzk.naver.com/edd22e44e7b2fd551cebccd09163c938)", inline=True)
    	embed.add_field(name="▶️ 유튜브", value="[바로가기](https://www.youtube.com/@hanYul_owo)", inline=True)
    	embed.add_field(name="🐦 X (트위터)", value="[바로가기](https://x.com/hanyul_lustia_?s=21)", inline=True)
    	embed.add_field(name="🎵 멜로밍", value="[바로가기](https://meloming.com/channel/hanyul)", inline=True)
    	embed.add_field(name="💌 마슈마로", value="[바로가기](https://marshmallow-qa.com/olp7sqjuz9bfn48?t=JHPPUQ)", inline=True)
    	embed.add_field(name="📖 방송 사용법", value="[노션 바로가기](https://gigantic-uncle-c53.notion.site/1d3f84e0ed0780a1b791fa9b72f2ef7c)", inline=False)
        embed.set_thumbnail(url="https://pb2.rplay.live/pics/a2554f33fcb348be72d1db644d7bcdde")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Links(bot))