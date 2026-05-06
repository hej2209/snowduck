import discord
from discord.ext import commands
from discord import app_commands

class VoteView(discord.ui.View):
    def __init__(self, title, option1, option2):
        super().__init__(timeout=None) 
        self.title = title
        self.option1 = option1
        self.option2 = option2
        self.voters = set()
        self.count1 = 0
        self.count2 = 0

    def generate_embed(self):
        embed = discord.Embed(title=f"📊 {self.title}", color=discord.Color.green())
        embed.add_field(name=f"1️⃣ {self.option1}", value=f"**{self.count1}표**", inline=False)
        embed.add_field(name=f"2️⃣ {self.option2}", value=f"**{self.count2}표**", inline=False)
        embed.set_footer(text=f"현재 총 투표수: {self.count1 + self.count2}표")
        return embed

    # 1번 투표 버튼
    @discord.ui.button(label="1번 투표", style=discord.ButtonStyle.primary, custom_id="vote_1")
    async def button1_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.voters:
            await interaction.response.send_message("❌ 이미 투표하셨습니다!", ephemeral=True)
            return
        self.voters.add(interaction.user.id)
        self.count1 += 1
        await interaction.response.send_message("✅ 1번에 투표하셨습니다!", ephemeral=True)
        await interaction.message.edit(embed=self.generate_embed(), view=self)

    # 2번 투표 버튼
    @discord.ui.button(label="2번 투표", style=discord.ButtonStyle.danger, custom_id="vote_2")
    async def button2_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.voters:
            await interaction.response.send_message("❌ 이미 투표하셨습니다!", ephemeral=True)
            return
        self.voters.add(interaction.user.id)
        self.count2 += 1
        await interaction.response.send_message("✅ 2번에 투표하셨습니다!", ephemeral=True)
        await interaction.message.edit(embed=self.generate_embed(), view=self)

    # 👇 새로 추가된 [투표 마감하기] 버튼 (row=1을 줘서 투표 버튼들 아래 줄에 배치합니다)
    @discord.ui.button(label="투표 마감하기", style=discord.ButtonStyle.secondary, custom_id="vote_close", row=1)
    async def close_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 관리자 권한이 있는지 확인! 일반 유저가 누르면 튕겨냅니다.
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ 관리자만 투표를 마감할 수 있습니다!", ephemeral=True)
            return

        # 모든 버튼을 순회하며 '비활성화(회색 버튼)' 상태로 만듭니다.
        for child in self.children:
            child.disabled = True
            
        # 제목 앞에 [마감됨] 을 붙여주고 색상을 빨간색으로 바꿉니다.
        self.title = f"[마감됨] {self.title}"
        closed_embed = self.generate_embed()
        closed_embed.color = discord.Color.red()

        # 결과를 채팅창에 덮어씌우고 마감 처리 완료!
        await interaction.response.send_message("🔒 투표가 마감되었습니다!", ephemeral=True)
        await interaction.message.edit(embed=closed_embed, view=self)


class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="투표", description="[관리자 전용] 버튼 방식의 실시간 투표를 엽니다.")
    @app_commands.describe(
        주제="투표할 주제를 적어주세요.",
        항목1="첫 번째 선택지를 적어주세요.",
        항목2="두 번째 선택지를 적어주세요."
    )
    @app_commands.default_permissions(administrator=True) 
    async def slash_vote(self, interaction: discord.Interaction, 주제: str, 항목1: str, 항목2: str):
        view = VoteView(주제, 항목1, 항목2)
        # 1. 먼저 채널에 투표 메시지를 띄웁니다.
        await interaction.response.send_message(embed=view.generate_embed(), view=view)
        
        # 2. 방금 봇이 띄운 그 투표 메시지를 다시 찾아옵니다.
        message = await interaction.original_response()
        
        # 3. 그 메시지 바로 밑에 스레드(댓글창)를 자동으로 생성합니다!
        await message.create_thread(name=f"💬 [{주제}] 의견 나누기", auto_archive_duration=1440)

async def setup(bot):
    await bot.add_cog(Vote(bot))