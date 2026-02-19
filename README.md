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

  * After watching this market for a couple days, this project is no longer worth time improving. The weather reads from the Polymarket source are inaccurate for its live temp and only gets updates once an hour. There is too much risk for the return in this market. There are even times when bets get over 95% confidence and lose.
