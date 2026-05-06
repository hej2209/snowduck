import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))
DATA_FILE = "exercise_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"count": 0, "last_date": ""}
    return {"count": 0, "last_date": ""}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

class Exercise(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # [필수 수정] 질문자님의 디스코드 고유 ID (숫자만)
        self.target_user_id = 385354044232826880
        
        # [필수 수정] 인증 글을 올릴 '포럼(게시판) 채널'의 ID (숫자만)
        self.cert_forum_id = 1491852976359215244 

    @app_commands.command(name="운동상태", description="현재 나의 31일 운동 미션 진행도를 나만 보이게 확인합니다.")
    async def check_status(self, interaction: discord.Interaction):
        data = load_data()
        current_count = data["count"]
        last_date = data["last_date"]

        if current_count == 0:
            await interaction.response.send_message("아직 운동 인증 기록이 없습니다! 오늘부터 당장 시작해보세요 💪", ephemeral=True)
            return

        remain_days = 31 - current_count
        
        embed = discord.Embed(
            title="🏃‍♂️ 31일 연속 운동 미션 현황",
            description="한율님과의 내기... 절대 질 수 없죠!",
            color=0x00FF00
        )
        embed.add_field(name="현재 진행도", value=f"**{current_count}일차** 성공!", inline=False)
        embed.add_field(name="최근 인증일", value=f"{last_date}", inline=False)
        embed.add_field(name="남은 일수", value=f"벌칙 방어까지 **{remain_days}일** 남음!", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # 🚨 [디버깅 1단계] 봇이 어떤 메시지든 읽기만 하면 무조건 터미널에 띄웁니다.
        print(f"👀 [메시지 감지] 채널: {message.channel}, 작성자: {message.author.name}, 사진: {len(message.attachments)}장")

        if isinstance(message.channel, discord.Thread):
            # 🚨 [디버깅 2단계] 포럼(게시글)에 글이 올라오면 ID를 비교해서 터미널에 보여줍니다.
            print(f"  👉 [ID 확인] 이 게시판의 ID: {message.channel.parent_id} / 내가 설정한 게시판 ID: {self.cert_forum_id}")
            print(f"  👉 [사람 확인] 글쓴사람 ID: {message.author.id} / 내가 설정한 내 ID: {self.target_user_id}")
            
            if message.channel.parent_id == self.cert_forum_id and message.author.id == self.target_user_id:
                if len(message.attachments) > 0:
                    print("  ✅ [조건 완벽 일치!] 운동 기록을 저장하고 댓글을 답니다.")
                    now = datetime.now(KST)
                    today_str = now.strftime("%Y-%m-%d")
                    data = load_data()
                    last_date_str = data["last_date"]
                    
                    if last_date_str == today_str:
                        await message.reply("💪 오늘은 이미 인증을 완료하셨습니다! 푹 쉬시고 내일 또 봬요!")
                        return
                    
                    if last_date_str:
                        last_date = datetime.strptime(last_date_str, "%Y-%m-%d").replace(tzinfo=KST)
                        delta = (now.date() - last_date.date()).days
                        
                        if delta > 1:
                            data["count"] = 1 
                            data["last_date"] = today_str
                            save_data(data)
                            await message.reply("🚨 **[비상사태]** 어제 운동 인증을 빼먹으셨습니다!!\n한율님과의 31일 연속 미션 **실패**... 벌칙을 수행하셔야 합니다 😭\n(눈물을 머금고 카운트가 1일차로 초기화되었습니다.)")
                            return
                    
                    data["count"] += 1
                    data["last_date"] = today_str
                    save_data(data)
                    current_count = data["count"]
                    remain_days = 31 - current_count
                    
                    if current_count >= 31:
                        await message.reply(f"🎉 **미션 대성공!!** 🎉\n31일 연속 운동 인증에 성공하셨습니다!! 한율님, 보고 계신가요?!")
                    else:
                        await message.reply(f"✅ **{current_count}일차 운동 인증 완료!**\n고생하셨습니다! 벌칙 방어까지 앞으로 **{remain_days}일** 남았습니다 🐻‍❄️❄️")
                else:
                    print("  ❌ [조건 불일치] 사진이 첨부되지 않았습니다.")

async def setup(bot):
    await bot.add_cog(Exercise(bot))