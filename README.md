# Polymarket Trading/Tracking

**To run:**
* python run.py ../utils/configs/configs-{location}.py

**When script purchases a bet:**
  * If current temp has reached inputed temp_target
  * If temp dropped from its tracked daily high (temp not getting higher)
  * If temp range is invaild considering a new high, buys 'no' bets

**TIMING**:
  * 12-1 MIA
  * 3-4 NYC/ATL
  * 4-6 SEA

  * After watching this market for a week, this project produces too much risk on trades for it to be worth continuing. The weather reads from the Polymarket source are inaccurate for live temp and only gets updates once an hour with the temp that Polymarket uses to confirm a winning trade. NOAA has public data that some people have used to anayzle weather patterns and create prediction models; however, just by trying to be faster than the polymarket source does not create a high likelihood of profitability.
