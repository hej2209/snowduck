import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone # 👈 시간 계산을 위해 timezone 추가

class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="프로필", description="유저의 상세 프로필과 활동 정보를 확인합니다.")
    async def profile(self, interaction: discord.Interaction, user: discord.Member = None):
        target_user = user or interaction.user
        
        # 🚨 [핵심 버그 수정] 슬래시 명령어로 넘어온 빈껍데기 정보 대신, 
        # 서버(guild) 캐시에서 '실시간 상태'가 포함된 꽉 찬 유저 정보를 다시 꺼내옵니다.
        cached_user = interaction.guild.get_member(target_user.id) or target_user
        
        # 📅 시간 및 +일수 계산 로직
        now = datetime.now(timezone.utc) # 디스코드 시간과 맞추기 위해 UTC 기준 현재 시간 
        
        joined_at_str = target_user.joined_at.strftime("%Y년 %m월 %d일")
        created_at_str = target_user.created_at.strftime("%Y년 %m월 %d일")
        
        # 현재 시간에서 가입일/생성일을 뺀 뒤, 일(days) 단위만 가져옵니다.
        joined_days = (now - target_user.joined_at).days
        created_days = (now - target_user.created_at).days
        
        embed_color = target_user.color if target_user.color.value != 0 else discord.Color.blue()

        # 🟢 상태를 한글 이모지로 변환 (cached_user 기준)
        status_str = str(cached_user.status)
        if status_str == 'online':
            status_kr = '🟢 온라인'
        elif status_str == 'idle':
            status_kr = '🌙 자리비움'
        elif status_str == 'dnd':
            status_kr = '⛔ 방해금지'
        else:
            status_kr = '⚪ 오프라인'

        # 📋 임베드 생성
        embed = discord.Embed(
            title=f"💳 {target_user.display_name}님의 프로필",
            description=f"**현재 상태:** {status_kr}",
            color=embed_color
        )

        if target_user.avatar:
            embed.set_thumbnail(url=target_user.avatar.url)

        # ✨ +일수 표시 적용 (줄바꿈으로 깔끔하게 배치)
        embed.add_field(name="📅 서버 가입일", value=f"`{joined_at_str}`\n**(+{joined_days}일)**", inline=True)
        embed.add_field(name="🚀 계정 생성일", value=f"`{created_at_str}`\n**(+{created_days}일)**", inline=True)
        
        embed.add_field(
            name="✨ 특별 활동 (Coming Soon)", 
            value="> 연동된 데이터가 없습니다. 추후 업데이트 예정입니다.", 
            inline=False
        )

        embed.set_footer(text=f"User ID: {target_user.id}")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(ProfileCog(bot))