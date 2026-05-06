import discord
from discord.ext import commands
from discord import app_commands

class Membership(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="멤버십", description="한율 님의 구독 티어 및 혜택을 확인합니다.")
    async def slash_membership(self, interaction: discord.Interaction):
        # ❄️ 눈과 얼음 컨셉에 맞춘 하늘색(0x87CEFA) 컬러 적용
        embed = discord.Embed(
            title="❄️ 율곰이네 멤버십(구독) 개편 안내 ❄️",
            description="**\"26년에도 행복한 율이가 되겠습니다 :> 화이팅하자아아아!!!!!!!!\"**\n\n한율 님을 더 가까이서 응원할 수 있는 멤버십 혜택입니다! 🐻‍❄️💙",
            color=0x87CEFA 
        )
        
        # ⛄ 눈오리 티어
        embed.add_field(
            name="⛄ 눈오리 (3,000원)", 
            value="• 저챗 다시보기 무료 시청\n• 구독자 전용 커뮤니티 이용 가능", 
            inline=False
        )
        
        # 🥈 은오리 티어
        embed.add_field(
            name="🥈 은오리 (13,000원)", 
            value="*(눈오리 혜택 기본 포함)*\n• 모든 다시보기 10코인 할인\n• 티켓방 무료 입장 (RP, 반캠 등)", 
            inline=False
        )
        
        # 🥇 금오리 티어
        embed.add_field(
            name="🥇 금오리 (50,000원)", 
            value="*(눈오리, 은오리 혜택 기본 포함)*\n• 닉네임이 포함된 보이스\n• 모든 다시보기 무료 제공 (2월 업로드부터, 스트릿 구독 형식)\n• 버츄얼 체키", 
            inline=False
        )


        
        # 👇 방금 복사하신 디스코드 이미지 링크를 아래 따옴표 안에 넣어주세요!
        embed.set_image(url="https://cdn.rplay.live/kr/community/68b00e18461659179fe6fbce/images/697e30e19403e77cf9a8a385-0?sign=1778689626-37561b7ca70e0a3a875d0e7d7d3c046e-0-317dc883a20e745536958ed47efc3cab") 
        
        embed.set_footer(text="오리봇 • 율곰이네 멤버십 안내")

        # 공지용이므로 모두가 볼 수 있게 전송합니다.
        await interaction.response.send_message(embed=embed, ephemeral=True)

# 봇이 모듈을 인식하게 하는 필수 코드
async def setup(bot):
    await bot.add_cog(Membership(bot))