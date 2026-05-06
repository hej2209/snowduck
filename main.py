import discord
from discord.ext import commands
import os
from dotenv import load_dotenv # 👈 1. dotenv 라이브러리를 불러옵니다.

# 👈 2. .env 파일에 숨겨둔 비밀번호(환경 변수)들을 읽어옵니다.
load_dotenv() 

# 모듈화를 위해 discord.Client 대신 commands.Bot을 사용합니다.
class HanyulBot(commands.Bot):
    def __init__(self):
        # 👇 우리가 쓸 권한(기본 권한 + 채팅 읽기)만 쏙쏙 골라서 설정합니다.
        my_intents = discord.Intents.default()
        my_intents.message_content = True
        
        super().__init__(
            command_prefix="!", 
            intents=my_intents # 👈 수정한 권한 적용
        )

    async def setup_hook(self):
        # 1. cogs 폴더 안의 모든 모듈(.py)을 자동으로 불러옵니다.
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(f"📦 모듈 로드 완료: {filename}")
        
        # 2. 슬래시 명령어들을 디스코드 서버와 동기화합니다.
        await self.tree.sync()
        print("✅ 슬래시 명령어 동기화 완료!")

    async def on_ready(self):
        print(f'✅ {self.user} 메인 시스템 로그인 완료!')

client = HanyulBot()

# 👈 3. 읽어온 값들 중 'DISCORD_TOKEN'이라는 이름표가 붙은 진짜 토큰을 가져옵니다.
TOKEN = os.getenv('DISCORD_TOKEN')

# [중요] 빈칸 대신, 방금 가져온 TOKEN 변수를 넣어줍니다!
client.run(TOKEN)