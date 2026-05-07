import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime, timedelta

# --- 1. 투표 버튼 및 결과 로직 ---
class VoteView(discord.ui.View):
    def __init__(self, title, opt1, opt2, creator, duration=None):
        super().__init__(timeout=None)
        self.title = title
        self.opt1 = opt1
        self.opt2 = opt2
        self.creator = creator
        self.duration = duration
        # 👇 투표 종료 시간을 생성 시점에 미리 계산해서 고정합니다.
        self.end_time = datetime.now() + timedelta(minutes=duration) if duration else None
        
        self.voters = set()
        self.count1 = 0
        self.count2 = 0
        self.thread = None
        self.main_message = None
        self.vote_msg = None

    def generate_embed(self, is_closed=False):
        total = self.count1 + self.count2
        
        def create_bar(count, total):
            if total == 0: return "░░░░░░░░░░ 0%"
            ratio = count / total
            filled = int(ratio * 10)
            bar = "█" * filled + "░" * (10 - filled)
            return f"{bar} {int(ratio * 100)}%"

        if is_closed:
            status_title = f"🏁 최종 집계: {self.title}"
            embed_color = 0xFFD700 
        else:
            status_title = f"📊 실시간 투표: {self.title}"
            embed_color = 0x2ECC71

        embed = discord.Embed(title=status_title, color=embed_color)
        embed.add_field(name=f"1️⃣ {self.opt1}", value=f"{create_bar(self.count1, total)}\n({self.count1}표)", inline=False)
        embed.add_field(name=f"2️⃣ {self.opt2}", value=f"{create_bar(self.count2, total)}\n({self.count2}표)", inline=False)

        if is_closed:
            winner = self.opt1 if self.count1 > self.count2 else self.opt2 if self.count2 > self.count1 else "무승부"
            win_icon = "🏆" if winner != "무승부" else "🤝"
            embed.add_field(name="✨ 집계 결과", value=f"{win_icon} **{winner}** 승리!", inline=False)
            embed.set_footer(text=f"총 {total}명 참여 • 종료되었습니다.")
        else:
            # 👇 타이머(카운트다운) 표시 로직 추가
            if self.end_time:
                timestamp = int(self.end_time.timestamp())
                embed.add_field(name="⏳ 마감 기한", value=f"<t:{timestamp}:R> 에 투표가 종료됩니다.", inline=False)
            
            embed.set_footer(text=f"총 {total}명 참여 • 실시간 집계 중")
            
        return embed

    async def end_vote(self):
        if self.thread and not self.thread.archived:
            for child in self.children:
                child.disabled = True
            
            final_embed = self.generate_embed(is_closed=True)
            await self.vote_msg.edit(embed=final_embed, view=None)
            
            if self.main_message:
                try: await self.main_message.delete()
                except: pass
            
            await self.thread.parent.send(content=f"📢 **{self.title}** 투표 종료!", embed=final_embed)
            await self.thread.edit(locked=True, archived=True)

    @discord.ui.button(label="1번 투표", style=discord.ButtonStyle.primary)
    async def v1(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.voters:
            return await interaction.response.send_message("❌ 이미 투표하셨습니다!", ephemeral=True, delete_after=3)
        self.voters.add(interaction.user.id); self.count1 += 1
        await interaction.response.send_message("✅ 1번 투표!", ephemeral=True, delete_after=3)
        await interaction.message.edit(embed=self.generate_embed())

    @discord.ui.button(label="2번 투표", style=discord.ButtonStyle.danger)
    async def v2(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.voters:
            return await interaction.response.send_message("❌ 이미 투표하셨습니다!", ephemeral=True, delete_after=3)
        self.voters.add(interaction.user.id); self.count2 += 1
        await interaction.response.send_message("✅ 2번 투표!", ephemeral=True, delete_after=3)
        await interaction.message.edit(embed=self.generate_embed())

    @discord.ui.button(label="마감하기", style=discord.ButtonStyle.secondary, row=1)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ 관리자 전용!", ephemeral=True)
        await interaction.response.send_message("🔒 마감 중...", ephemeral=True, delete_after=2)
        await self.end_vote()

# --- 2. 투표 생성 팝업창 (Modal) ---
class VoteCreateModal(discord.ui.Modal, title="🗳️ 투표 생성"):
    topic = discord.ui.TextInput(label="주제", placeholder="예: 오늘 뭐 먹지?", required=True)
    opt1 = discord.ui.TextInput(label="항목 1", placeholder="치킨", required=True)
    opt2 = discord.ui.TextInput(label="항목 2", placeholder="피자", required=True)
    time_limit = discord.ui.TextInput(label="제한 시간(분)", placeholder="예: 5 (미입력 시 수동)", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        duration = int(self.time_limit.value) if self.time_limit.value and self.time_limit.value.isdigit() else None
        main_msg = None
        
        try:
            view = VoteView(self.topic.value, self.opt1.value, self.opt2.value, interaction.user, duration)
            main_msg = await interaction.channel.send(f"🗳️ **{self.topic.value}** 투표 시작!")
            view.main_message = main_msg
            
            thread = await main_msg.create_thread(name=f"📊 투표: {self.topic.value}")
            view.thread = thread
            view.vote_msg = await thread.send(embed=view.generate_embed(), view=view)

            # 생성 완료 메시지 (5초 후 자동 삭제)
            success_followup = await interaction.followup.send(
                content="✅ 투표 쓰레드가 성공적으로 생성되었습니다! (5초 뒤 삭제)", 
                ephemeral=False
            )
            
            async def delete_success():
                await asyncio.sleep(5)
                try: await success_followup.delete()
                except: pass
            asyncio.create_task(delete_success())

            # 6. 실제 투표 타이머 작동
            if duration:
                await asyncio.sleep(duration * 60)
                await view.end_vote()

        except Exception as e:
            if main_msg:
                try: await main_msg.delete()
                except: pass
            
            error_text = "❌ 이 채널에서는 쓰레드를 생성할 수 없습니다!"
            err_msg = await interaction.followup.send(content=f"{error_text} (5초 뒤 삭제)", ephemeral=False)
            await asyncio.sleep(5)
            try: await err_msg.delete()
            except: pass

# --- 3. 코그 설정 ---
class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="투표", description="[관리자] 타이머 투표를 생성합니다.")
    @app_commands.default_permissions(administrator=True)
    async def slash_vote(self, interaction: discord.Interaction):
        await interaction.response.send_modal(VoteCreateModal())

async def setup(bot):
    await bot.add_cog(Vote(bot))