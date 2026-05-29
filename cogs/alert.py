import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiohttp
import datetime  # 👈 시간 확인을 위해 추가됨

class Alert(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_live = False
        self.api_url = "https://api.rplay.live/account/getuser?userOid=68b00e18461659179fe6fbce"
        self.stream_url = "https://rplay.live/live/68b00e18461659179fe6fbce"
        
        # [필수 수정] 알림을 띄울 채널 ID
        self.channel_id = 1421504363834118256

    # 모듈이 로드될 때 알림 반복(루프)을 시작합니다.
    async def cog_load(self):
        self.check_broadcast.start()

    # 모듈이 언로드될 때 알림 반복을 종료합니다.
    async def cog_unload(self):
        self.check_broadcast.cancel()

    @tasks.loop(minutes=1.0)
    async def check_broadcast(self):
        # 🕒 [트래픽 최적화 로직] 🕒
        # 방송이 꺼져있을 때만 지정된 시간에 확인하여 불필요한 API 호출을 막습니다.
        # (이미 방송 중이라면 언제 꺼지는지 확인해야 하므로 계속 루프를 돕니다.)
        if not self.is_live:
            tz_kst = datetime.timezone(datetime.timedelta(hours=9))
            now = datetime.datetime.now(tz_kst)
            
            # 파이썬 요일: 월(0), 화(1), 수(2), 목(3), 금(4), 토(5), 일(6)
            target_days = [5]  # 토
            
            # 방송하는 요일이 아니면 API 확인 안 하고 바로 넘김
            if now.weekday() not in target_days:
                return
            
            # 방송 시작 예상 시간대: 밤 10시(22시) ~ 11시 59분(23시)
            # 만약 오전 방송이라면 이 부분을 (10 <= now.hour <= 11) 로 수정하세요.
            if not (22 <= now.hour <= 23):
                return

        # --- 여기서부터는 기존 작동 로직과 동일합니다 ---
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.api_url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json(content_type=None)
                        currently_live = data.get('isLive', False) 
                        
                        if currently_live and not self.is_live:
                            self.is_live = True
                            channel = self.bot.get_channel(self.channel_id)
                            
                            if channel:
                                schedule_text = "[V-LusTia] 화·금 10시 30분 & 일 11시 30분 🐻‍❄️❄️"
                                file = discord.File("images/live_banner.png", filename="live_banner.png")

                                embed = discord.Embed(
                                    title="🔴 라이브 방송 중",
                                    description=f"**한율** 님이 알플레이에서 방송 중입니다!\n\n🕒 **방송 시간:** {schedule_text}\n\n[👉 **지금 바로 시청하기**]({self.stream_url})",
                                    color=0x8A2BE2
                                )
                                embed.set_image(url="attachment://live_banner.png")
                                
                                await channel.send(content="@everyone", embed=embed, file=file)
                                
                                live_title = data.get('broadcastTitle') or data.get('subject') or data.get('channelIntro') or "방제 없음"
                                print(f"📢 [방송 켜짐] 알림 전송 완료: {live_title}")
                        
                        elif not currently_live and self.is_live:
                            self.is_live = False
                            print("💤 [방송 꺼짐] 대기 모드로 전환합니다.")

            except Exception as e:
                print(f"🚨 알림 상태 확인 중 오류: {e}")

    @check_broadcast.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    @commands.command(name="알림테스트")
    @commands.has_permissions(administrator=True)
    async def test_alert(self, ctx):
        """!알림테스트 라고 치면 방송 알림 레이아웃을 확인합니다."""
        try:
            file = discord.File("images/live_banner.png", filename="live_banner.png")
        except FileNotFoundError:
            await ctx.send("❌ `images` 폴더 안에 `live_banner.png`가 없습니다!", delete_after=5.0)
            return

        schedule_text = "[V-LusTia] 화·금 10시 30분 & 일 11시 30분 🐻‍❄️❄️"

        embed = discord.Embed(
            title="🔴 라이브 방송 중 (테스트)",
            description=f"**한율** 님이 알플레이에서 방송 중입니다!\n\n🕒 **방송 시간:** {schedule_text}\n\n[👉 **지금 바로 시청하기**]({self.stream_url})",
            color=0x8A2BE2
        )
        embed.set_image(url="attachment://live_banner.png")
        
        await ctx.send("✅ 채널에 테스트 알림을 보냅니다! (5초 뒤 삭제)", delete_after=5.0)
        await ctx.send(content="@everyone (이것은 테스트 알림입니다)", embed=embed, file=file)

async def setup(bot):
    await bot.add_cog(Alert(bot))