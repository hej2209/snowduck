import discord
from discord.ext import commands
import os
from dotenv import load_dotenv 

load_dotenv() 

class HanyulBot(commands.Bot):
    def __init__(self):
        # 1. 'intents'라는 이름의 바구니를 만듭니다.
        intents = discord.Intents.default()
        intents.message_content = True  
        intents.presences = True  
        intents.members = True    

        super().__init__(
            command_prefix="!", 
            # 2. 👇 방금 만든 'intents' 바구니를 정확하게 넣어줍니다!
            intents=intents 
        )

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(f"📦 모듈 로드 완료: {filename}")
        
        await self.tree.sync()
        print("✅ 슬래시 명령어 동기화 완료!")

    async def on_ready(self):
        print(f'✅ {self.user} 메인 시스템 로그인 완료!')

client = HanyulBot()

TOKEN = os.getenv('DISCORD_TOKEN')
client.run(TOKEN)