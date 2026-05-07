import discord
from discord.ext import commands
from discord import app_commands
import yfinance as yf
import aiohttp
import re
import asyncio

class Stock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.common_tickers = {
            "나스닥 (^IXIC)": "^IXIC",
            "S&P 500 (^GSPC)": "^GSPC",
            "코스피 (^KS11)": "^KS11",
            "코스닥 (^KQ11)": "^KQ11",
            "비트코인 (BTC-USD)": "BTC-USD",
            "테슬라 (TSLA)": "TSLA",
            "애플 (AAPL)": "AAPL",
            "엔비디아 (NVDA)": "NVDA",
            "마이크로소프트 (MSFT)": "MSFT"
        }
        
        # 🛡️ 과부하 방지용 메모리 (한 번 검색한 주식은 여기에 저장해서 네이버 API 호출을 줄임)
        self.ticker_cache = {}

    async def get_korean_ticker(self, keyword: str):
        # 이미 검색해 본 주식이면 캐시에서 바로 꺼내줌 (네이버 서버 안 거침)
        if keyword in self.ticker_cache:
            return self.ticker_cache[keyword]

        url = f"https://ac.finance.naver.com/ac?q={keyword}&q_enc=utf-8&st=111&r_format=json&r_enc=utf-8"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    items = data.get("items", [])
                    if items and items[0]:
                        first_result = items[0][0]
                        code = first_result[0]
                        market = first_result[3]
                        
                        result_ticker = None
                        if market == "Kospi":
                            result_ticker = f"{code}.KS"
                        elif market == "Kosdaq":
                            result_ticker = f"{code}.KQ"
                        
                        # 찾은 결과를 메모리에 저장 (다음번 검색을 위해)
                        if result_ticker:
                            self.ticker_cache[keyword] = result_ticker
                            return result_ticker
        except Exception as e:
            print(f"네이버 API 검색 중 오류: {e}")
        return None

    async def ticker_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=name, value=ticker)
            for name, ticker in self.common_tickers.items()
            if current.lower() in name.lower() or current.lower() in ticker.lower()
        ][:25]

    # 🛡️ 봇 멈춤 방지: yfinance 작업을 별도의 스레드에서 실행하도록 빼냄
    def fetch_stock_data(self, ticker_symbol):
        ticker = yf.Ticker(ticker_symbol)
        return ticker.history(period="5d")

    @app_commands.command(name="지수", description="특정 종목이나 지수의 실시간 시세를 확인합니다. (나만 보기)")
    @app_commands.describe(symbol="조회할 종목 이름이나 영문 티커를 입력하세요. (예: 카카오, AAPL)")
    @app_commands.autocomplete(symbol=ticker_autocomplete)
    async def get_stock(self, interaction: discord.Interaction, symbol: str):
        await interaction.response.defer(ephemeral=True)

        original_input = symbol
        search_ticker = None
        display_name = symbol

        for name, t in self.common_tickers.items():
            if symbol.upper() in name.upper() or symbol.upper() == t:
                search_ticker = t
                display_name = name
                break

        if not search_ticker:
            if re.search('[가-힣]', symbol):
                search_ticker = await self.get_korean_ticker(symbol)
                if not search_ticker:
                    await interaction.followup.send(f"❌ `{symbol}`에 해당하는 한국 주식을 찾을 수 없습니다.")
                    return
            else:
                search_ticker = symbol.upper()
                display_name = search_ticker

        try:
            # 🛡️ 봇이 멈추지 않도록 asyncio.to_thread 를 사용하여 백그라운드에서 주가 가져오기
            hist = await asyncio.to_thread(self.fetch_stock_data, search_ticker)
            
            if hist.empty or len(hist) < 2:
                await interaction.followup.send(f"❌ `{display_name}` (티커: {search_ticker})의 시세 정보를 불러올 수 없습니다.")
                return
            
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100
            
            color = 0xff4747 if change > 0 else 0x4777ff if change < 0 else 0x95a5a6
            icon = "🔺" if change > 0 else "🔻" if change < 0 else "➖"

            embed = discord.Embed(
                title=f"{icon} {display_name} 시세 정보",
                description=f"`티커: {search_ticker}`",
                color=color,
                timestamp=interaction.created_at
            )
            
            price_text = f"**현재가:** {current_price:,.2f}\n**전일대비:** {change:+,.2f} ({change_percent:+.2f}%)"
            embed.add_field(name="가격", value=price_text, inline=False)

            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"❌ 데이터를 가져오는 중 오류가 발생했습니다.\n`{e}`")

async def setup(bot):
    await bot.add_cog(Stock(bot))