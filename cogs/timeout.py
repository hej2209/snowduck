import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta

class TimeoutCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==========================================
    # ⏳ 유저 타임아웃 (채팅/음성 금지) 명령어
    # ==========================================
    @app_commands.command(name="격리", description="[관리자]특정 유저의 채팅과 음성 채널 사용을 일정 시간 동안 차단합니다.")
    @app_commands.describe(
        user="격리할 유저를 선택하세요.",
        duration="격리할 시간을 선택하세요.",
        reason="사유를 적어주세요. (선택사항)"
    )
    # 디스코드 UI 자체 드롭다운 메뉴 생성
    @app_commands.choices(duration=[
        app_commands.Choice(name="⏳ 1분 (가벼운 경고)", value=1),
        app_commands.Choice(name="⏳ 10분 (진정하고 오세요)", value=10),
        app_commands.Choice(name="⏳ 1시간 (국밥 한 그릇 먹고 오세요)", value=60),
        app_commands.Choice(name="⏳ 1일 (내일 뵙겠습니다)", value=1440),
        app_commands.Choice(name="⏳ 1주일 (장기 휴가)", value=10080)
    ])
    # 서버 설정에서 '멤버 타임아웃' 권한이 있는 사람만 사용 가능
    @app_commands.default_permissions(moderate_members=True)
    async def timeout_user(self, interaction: discord.Interaction, user: discord.Member, duration: app_commands.Choice[int], reason: str = "사유가 지정되지 않았습니다."):
        
        # 1. 예외 처리 (본인, 봇 타임아웃 방지)
        if user == interaction.user:
            await interaction.response.send_message("❌ 자기 자신을 격리할 수는 없습니다!", ephemeral=True)
            return
        if user == self.bot.user:
            await interaction.response.send_message("❌ 봇을 격리할 수는 없습니다! 봐주세요 😭", ephemeral=True)
            return
        # 이미 타임아웃 상태인 유저인지 확인
        if user.is_timed_out():
            await interaction.response.send_message(f"⚠️ **{user.display_name}**님은 이미 격리 중입니다.", ephemeral=True)
            return

        try:
            # 2. 디스코드 타임아웃 실행
            time_delta = timedelta(minutes=duration.value)
            await user.timeout(time_delta, reason=f"관리자 {interaction.user} 명령: {reason}")
            
            # 3. 완료 안내 임베드
            embed = discord.Embed(
                title="⏳ 유저 격리 조치",
                description=f"**{user.mention}** 님의 채팅 및 음성 채널 이용이 제한되었습니다.",
                color=discord.Color.orange()
            )
            embed.add_field(name="격리 시간", value=f"**{duration.name.split(' (')[0]}**", inline=True)
            embed.add_field(name="담당 관리자", value=interaction.user.mention, inline=True)
            embed.add_field(name="상세 사유", value=f"`{reason}`", inline=False)
            
            await interaction.response.send_message(embed=embed)

        except discord.Forbidden:
            await interaction.response.send_message(
                "🚨 **권한 오류:** 봇에게 타임아웃 권한이 없거나, 대상 유저가 관리자라 봇이 건드릴 수 없습니다.", 
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(TimeoutCog(bot))