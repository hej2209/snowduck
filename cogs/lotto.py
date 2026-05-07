import discord
from discord.ext import commands
from discord import app_commands
import random

# --- 로또 입력 팝업창 ---
class LottoModal(discord.ui.Modal, title="🎰 행운의 로또 번호 선택"):
    # 입력 칸 정의
    numbers = discord.ui.TextInput(
        label="좋아하는 숫자 (최대 5개)",
        placeholder="예: 7, 15, 22 (안 적으면 완전 자동!)",
        required=False, # 필수 입력 아님
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        all_numbers = list(range(1, 46))
        picked_numbers = []
        user_input = self.numbers.value.strip()

        # 1. 번호를 입력한 경우 (반자동)
        if user_input:
            try:
                # 쉼표나 공백으로 구분된 숫자를 리스트로 변환
                user_numbers = list(set([int(n.strip()) for n in user_input.replace(',', ' ').split()]))
                
                if any(n < 1 or n > 45 for n in user_numbers):
                    await interaction.response.send_message("❌ 숫자는 1~45 사이여야 합니다!", ephemeral=True, delete_after=5)
                    return
                if len(user_numbers) > 5:
                    await interaction.response.send_message("❌ 숫자는 최대 5개까지만 골라주세요!", ephemeral=True, delete_after=5)
                    return

                picked_numbers = user_numbers.copy()
                remaining = 6 - len(picked_numbers)
                available = [n for n in all_numbers if n not in picked_numbers]
                picked_numbers.extend(random.sample(available, remaining))
                mode_text = f"✨ **반자동** (선택: {', '.join(map(str, sorted(user_numbers)))})"
                
            except ValueError:
                await interaction.response.send_message("❌ 숫자만 입력 가능합니다. (예: 7, 15, 22)", ephemeral=True, delete_after=5)
                return
        # 2. 입력 안 한 경우 (자동)
        else:
            picked_numbers = random.sample(all_numbers, 6)
            mode_text = "🎲 **완전 자동**"

        picked_numbers.sort()
        embed = discord.Embed(title="🎰 로또 추첨 결과", color=discord.Color.gold())
        embed.add_field(name="추첨 모드", value=mode_text, inline=False)
        embed.add_field(name="행운의 번호", value=f"**{', '.join(map(str, picked_numbers))}**", inline=False)
        embed.set_footer(text="당첨되면 한율한테 1억! 😉")

        await interaction.response.send_message(embed=embed, ephemeral=True)

class Lotto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="로또", description="팝업창에 번호를 입력해 로또를 추첨합니다.")
    async def slash_lotto(self, interaction: discord.Interaction):
        # 바로 모달창(팝업)을 띄워줍니다.
        await interaction.response.send_modal(LottoModal())

async def setup(bot):
    await bot.add_cog(Lotto(bot))