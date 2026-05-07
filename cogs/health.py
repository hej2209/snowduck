import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

# --- 1. 입력 팝업창(Modal) 정의 ---
class HeartRateModal(discord.ui.Modal):
    def __init__(self, mode):
        self.mode = mode
        title = "간이 공식 계산기" if mode == "simple" else "카르보넨 정밀 계산기"
        super().__init__(title=title)

        # 생년월일 입력칸 (공통)
        self.birth = discord.ui.TextInput(
            label="생년월일 8자리",
            placeholder="예: 19941208",
            min_length=8,
            max_length=8
        )
        self.add_item(self.birth)

        # 카르보넨 방식일 때만 '안정시 심박수' 칸을 추가합니다.
        if mode == "karvonen":
            self.rhr = discord.ui.TextInput(
                label="안정 시 심박수 (BPM)",
                placeholder="평소 편안할 때의 심박수 (예: 70)",
                min_length=2,
                max_length=3
            )
            self.add_item(self.rhr)

    async def on_submit(self, interaction: discord.Interaction):
        # 나이 계산 로직
        birth_str = self.birth.value
        if not birth_str.isdigit():
            await interaction.response.send_message("❌ 숫자로만 입력해주세요!", ephemeral=True, delete_after=5)
            return

        year, month, day = int(birth_str[:4]), int(birth_str[4:6]), int(birth_str[6:])
        today = datetime.now()
        
        try:
            is_birthday_passed = (today.month, today.day) >= (month, day)
            age = today.year - year - (0 if is_birthday_passed else 1)
        except ValueError:
            await interaction.response.send_message("❌ 올바른 날짜가 아닙니다!", ephemeral=True, delete_after=5)
            return

        max_hr = 220 - age
        embed = discord.Embed(title="🏃‍♂️ 존 2(Zone 2) 결과", color=discord.Color.blue())
        
        if self.mode == "simple":
            low, high = int(max_hr * 0.6), int(max_hr * 0.7)
            embed.add_field(name="📊 방식", value="간이 공식", inline=True)
        else:
            rhr_val = int(self.rhr.value)
            hrr = max_hr - rhr_val
            low = int((hrr * 0.6) + rhr_val)
            high = int((hrr * 0.7) + rhr_val)
            embed.add_field(name="📊 방식", value=f"카르보넨 (안정시: {rhr_val}bpm)", inline=True)

        embed.description = f"**{interaction.user.display_name}**님(만 {age}세) 가이드"
        embed.add_field(name="💓 목표 범위", value=f"**{low} ~ {high} bpm**", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# --- 2. 버튼 뷰 정의 ---
class HeartRateView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="간이 공식", style=discord.ButtonStyle.secondary)
    async def simple_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(HeartRateModal(mode="simple"))

    @discord.ui.button(label="카르보넨 공식 (정밀)", style=discord.ButtonStyle.primary)
    async def karvonen_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(HeartRateModal(mode="karvonen"))

# --- 3. 코그(Cog) 설정 ---
class Health(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="심박수", description="나에게 맞는 존 2 운동 범위를 계산합니다.")
    async def slash_heartrate(self, interaction: discord.Interaction):
        # 먼저 버튼을 띄워 유저가 선택하게 합니다.
        await interaction.response.send_message(
            content="💡 **원하시는 계산 방식을 선택해주세요!**",
            view=HeartRateView(),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Health(bot))