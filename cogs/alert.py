import discord
from discord.ext import commands, tasks
import aiohttp

class Alert(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_live = False
        self.api_url = "https://api.rplay.live/account/getuser?userOid=68b00e18461659179fe6fbce"
        self.stream_url = "https://rplay.live/creatorhome/68b00e18461659179fe6fbce"
        
        # [필수 수정] 알림을 띄울 채널 ID를 꼭 다시 적어주세요!
        self.channel_id = 1491852942486012116 

    # 모듈이 로드될 때 알림 반복(루프)을 시작합니다.
    async def cog_load(self):
        self.check_broadcast.start()

    # 모듈이 언로드될 때 알림 반복을 종료합니다.
    async def cog_unload(self):
        self.check_broadcast.cancel()

    @tasks.loop(minutes=1.0)
    async def check_broadcast(self):
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
                                live_title = data.get('broadcastTitle') or data.get('subject') or data.get('channelIntro') or "라이브 방송이 시작되었습니다!"
                                profile_img = data.get('channelImage', '')
                                
                                # 원하셨던 시간표 텍스트
                                schedule_text = "[V-LusTia] 화·금 10시 30분 & 일 11시 30분 🐻‍❄️❄️"

                                embed = discord.Embed(
                                    title=f"🔴 {live_title}",
                                    description=f"**한율** 님이 알플레이에서 방송 중입니다!\n\n🕒 **방송 시간:** {schedule_text}\n\n[👉 **지금 바로 시청하기**]({self.stream_url})",
                                    url=self.stream_url,
                                    color=0x8A2BE2
                                )
                                embed.set_image(url=profile_img)
                                
                                await channel.send(content="@everyone", embed=embed)
                                print(f"📢 [방송 켜짐] 알림 전송 완료: {live_title}")
                        
                        elif not currently_live and self.is_live:
                            self.is_live = False
                            print("💤 [방송 꺼짐] 대기 모드로 전환합니다.")

            except Exception as e:
                print(f"🚨 알림 상태 확인 중 오류: {e}")

    @check_broadcast.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Alert(bot))