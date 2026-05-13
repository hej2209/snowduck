import discord
from discord.ext import commands
from discord import app_commands
import random
from datetime import datetime
import json
import os

# ==========================================
# 📢 공유하기 버튼 UI 클래스 (자동 닫기 적용)
# ==========================================
class ShareView(discord.ui.View):
    def __init__(self, embed: discord.Embed, user: discord.Member):
        super().__init__(timeout=None)
        self.embed = embed
        self.user = user

    @discord.ui.button(label="채널에 공유하기", style=discord.ButtonStyle.green, emoji="📢")
    async def share_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 1. 봇이 버튼 클릭을 확인했다는 처리 (에러 방지용)
        await interaction.response.defer()
        
        # 2. 버튼이 눌린 '현재 채널'에 모두가 볼 수 있는 일반 메시지로 전송
        await interaction.channel.send(
            content=f"📢 **{self.user.display_name}**님이 오늘의 운세를 공유했습니다!",
            embed=self.embed
        )
        
        # 3. 펑! 버튼이 달려있던 기존의 '나만 보기' 메시지는 깔끔하게 삭제 (자동 닫기)
        await interaction.delete_original_response()


# ==========================================
# 🔮 운세 모달 (입력창 복구 버전)
# ==========================================
class FortuneModal(discord.ui.Modal, title='🔮 오늘의 운세 분석'):
    def __init__(self):
        super().__init__()
        
        self.name_input = discord.ui.TextInput(
            label='이름', placeholder='본인의 이름을 입력하세요.', required=True, max_length=10
        )
        self.birthdate_input = discord.ui.TextInput(
            label='생년월일', placeholder='예: 950101', required=True, max_length=8
        )
        # 🚨 스크롤 대신 다시 텍스트 입력으로 롤백했습니다.
        self.gender_input = discord.ui.TextInput(
            label='성별', placeholder='남성 또는 여성 (직접 입력)', required=True, max_length=10
        )
        
        self.add_item(self.name_input)
        self.add_item(self.birthdate_input)
        self.add_item(self.gender_input)

    async def on_submit(self, interaction: discord.Interaction):
        name = self.name_input.value
        birthdate = self.birthdate_input.value
        # 다시 .value 로 값을 가져옵니다.
        gender = self.gender_input.value 
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 고유 키 생성 및 시드 고정
        unique_key = f"{name}_{birthdate}_{gender}_{today}"
        random.seed(unique_key)
        
        # JSON 파일 읽어오기
        file_path = os.path.join(os.getcwd(), 'omikuji_data.json')
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                omikuji_data = json.load(f)
        except FileNotFoundError:
            await interaction.response.send_message("🚨 운세 데이터를 찾을 수 없습니다.", ephemeral=True)
            return
        
        # 데이터 뽑기
        tier = random.choice(list(omikuji_data.keys()))
        comment = random.choice(omikuji_data[tier])
        
        lucky_colors = [
            "레드 ❤️", "블루 💙", "옐로우 💛", "그린 💚", "퍼플 💜", 
            "블랙 🖤", "화이트 🤍", "핑크 🩷", "민트 🩵", "브라운 🤎"
        ]
        result_color = random.choice(lucky_colors)
        result_number = random.randint(1, 45)
        
        # 시드 초기화
        random.seed()
        
        # 임베드 색상 설정
        if "대길" in tier:
            embed_color = discord.Color.gold()
        elif "길" in tier or "중길" in tier or "소길" in tier:
            embed_color = discord.Color.green()
        elif "말길" in tier:
            embed_color = discord.Color.blue()
        elif "흉" in tier:
            embed_color = discord.Color.orange()
        elif "대흉" in tier:
            embed_color = discord.Color.red()
        else:
            embed_color = discord.Color.default()

        # ==========================================
        # 📋 가독성 폭발! 한줄평 글씨 확대 적용
        # ==========================================
        embed = discord.Embed(
            # 인용구(>)를 빼고, ### 를 사용해 굵고 하얀 큰 글씨로 변경했습니다.
            description=f"# {tier}\n\n**📜 오늘의 한줄평**\n### {comment}\n\n",
            color=embed_color
        )
        embed.add_field(name="🎨 럭키 컬러", value=f"**{result_color}**", inline=True)
        embed.add_field(name="🔢 행운의 숫자", value=f"**{result_number}**", inline=True)
        embed.set_footer(text=f"📅 {today}")
        
        # 공유하기 버튼 뷰 장착
        view = ShareView(embed=embed, user=interaction.user)
        
        # 메시지 전송
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class FortuneCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="운세", description="이름, 생년월일, 성별을 바탕으로 오늘의 오미쿠지를 뽑습니다. (나만 보기)")
    async def fortune(self, interaction: discord.Interaction):
        # 이제 클래스에 __init__을 만들었으므로 ()로 호출합니다.
        await interaction.response.send_modal(FortuneModal())


async def setup(bot):
    await bot.add_cog(FortuneCog(bot))