import discord
from discord.ext import commands
from discord import app_commands

class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="규칙", description="율곰이네 서버의 공지사항 및 규칙을 확인합니다.")
    async def slash_rules(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📜 율곰이네 서버 규칙",
            description="다들 공지 한 번씩만 읽어줘요!!\n편하고 즐겁게 놀기 위해 꼭 지켜주세요 🐻‍❄️❄️",
            color=0x8A2BE2 # 한율님 상징 컬러 (보라색 계열, 원하시면 변경 가능)
        )
        
        # 필드 추가 (각 규칙 항목들)
        embed.add_field(
            name="📺 방송 관련", 
            value="방송 시간, 내용 등은 방송 중에만 얘기해주세요!", 
            inline=False
        )
        embed.add_field(
            name="🤫 언급 관련", 
            value="스머가 먼저 말하지 않는 이상, 다른 방송이나 스트리머 언급 금지!", 
            inline=False
        )
        embed.add_field(
            name="💖 한율 사랑 가득히 (필수!)", 
            value="응원 멘트, 따뜻한 말 한마디면 스머 행복지수 +100 🥰", 
            inline=False
        )
        embed.add_field(
            name="💬 채팅 매너", 
            value="도배 / 싸움 / 선 넘는 말 ❌\n스머가 말할 땐 조금만 기다려주기 (채팅 겹침 방지!)", 
            inline=False
        )
        embed.add_field(
            name="🚫 절대 금지 사항", 
            value="정치, 렉카, 군대, 종교, 인종차별 관련 발언은 엄격히 금지됩니다.", 
            inline=False
        )
        embed.add_field(
            name="👮 조치 안내", 
            value="규칙을 어기면 경고나 뮤트 등 조치가 있을 수 있어요! 다들 서로 예쁘게 대해줘요 🫶", 
            inline=False
        )

        # ✅ set_thumbnail 대신 set_image를 사용하면 사진이 크게 밑에 나옵니다!

        embed.set_image(url="https://pb2.rplay.live/pics/a2554f33fcb348be72d1db644d7bcdde")
        
        # ✅ 푸터에는 text만 넣거나, 아주 작은 아이콘을 넣을 때만 icon_url을 씁니다.
        embed.set_footer(text="오리봇 • 율곰이네 공지 시스템")

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Rules(bot))