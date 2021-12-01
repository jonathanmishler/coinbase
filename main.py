import logging
import time
from datetime import datetime, timedelta
import asyncio
from coinbase.candle_sync import Coin
from coinbase.candle_async import Coin as AsyncCoin

logging.basicConfig(level=logging.INFO)

end = datetime(2021, 11, 30, 12, 0)
start = end - timedelta(seconds=(300 * 60 * 144))
coin_id = "ADA-USD"

# Async Mode
api = AsyncCoin(coin_id)
start_timer = time.perf_counter()
data = asyncio.run(api.history(60, start, end))
end_timer = time.perf_counter()
print(
    f"Using async requests, made {len(data)} requests in {end_timer-start_timer:0.4f} seconds"
)

# Sync Mode
api = Coin(coin_id)
start_timer = time.perf_counter()
data = api.history(60, start, end)
end_timer = time.perf_counter()
print(
    f"Using normal requests, made {len(data)} requests in {end_timer-start_timer:0.4f} seconds"
)
