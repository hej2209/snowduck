import discord
from discord.ext import commands
from discord import app_commands

# 1. 빠져있던 클래스 선언 부분을 추가했습니다.
class Links(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    # 2. 명령어 데코레이터와 함수 들여쓰기를 맞췄습니다.
    @app_commands.command(name="링크", description="한율 님의 모든 링크를 나만 보이게 확인합니다.")
    async def slash_link(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🔗 한율 님 공식 링크", color=0x8A2BE2)

        embed.add_field(name="📺 알플레이", value="[바로가기](https://rplay.live/creatorhome/68b00e18461659179fe6fbce?page=contents)", inline=True)
        embed.add_field(name="🟢 치지직", value="[바로가기](https://chzzk.naver.com/edd22e44e7b2fd551cebccd09163c938)", inline=True)
        embed.add_field(name="▶️ 유튜브", value="[바로가기](https://www.youtube.com/@hanYul_owo)", inline=True)
        embed.add_field(name="🐦 X (트위터)", value="[바로가기](https://x.com/hanyul_lustia_?s=21)", inline=True)
        embed.add_field(name="🎵 멜로밍", value="[바로가기](https://meloming.com/channel/hanyul)", inline=True)
        embed.add_field(name="💌 마슈마로", value="[바로가기](https://marshmallow-qa.com/olp7sqjuz9bfn48?t=JHPPUQ)", inline=True)
        embed.add_field(name="📖 방송 사용법", value="[바로가기](https://gigantic-uncle-c53.notion.site/1d3f84e0ed0780a1b791fa9b72f2ef7c)", inline=False)


        # ephemeral=True 덕분에 명령어 쓴 사람한테만 보이게 됩니다!
        await interaction.response.send_message(embed=embed, ephemeral=True)

# 3. 엉켜있던 setup 함수를 클래스 바깥으로 분리했습니다.
async def setup(bot):
    await bot.add_cog(Links(bot))