# careersle
A simple game to identify footballers from their careers

This game is inspired by the likes of wordle - a new challenge everyday where a user will make multiple guesses to try and identify a footballer from increasing information about them and their career.

The user will first be shown a list of clubs. E.g:

| Clubs |
|-------|
| Sporting CP B	|
|	Sporting CP	|
|	Manchester United	|
|	Real Madrid	|
|	Juventus	|
|	Manchester United	|
|	Al Nassr	|

For each incorrect guess, the user is shown more information:

- the years that player was at those clubs

| Years | Clubs |
|-------|-------|
| 2002–2003	| Sporting CP B |
| 2002–2003 |	Sporting CP |
| 2003–2009 |	Manchester United |
| 2009–2018	| Real Madrid |
| 2018–2021 |	Juventus |
| 2021–2022 |	Manchester United |
| 2023– |	Al Nassr |
  
- the goals and appearances for those clubs

| Years | Clubs | Appearances (Goals) |
|-------|-------|-------------|
| 2002–2003 | Sporting CP B |2 (0) |
| 2002–2003 | Sporting CP | 25 (3) |
| 2003–2009 | Manchester United | 196 (84) |
| 2009–2018 | Real Madrid | 292 (311) |
| 2018–2021 | Juventus | 98 (81) |
| 2021–2022 | Manchester United | 40 (19) |
| 2023– | Al Nassr | 34 (34) |
  
- the player's position

| Position |
|--|
| Forward |

- the player's nationality

| Nationality |
| -- |
| Portuguese |

If the user still fails to guess, the player is revealed.

| Player |
| -- |
| Cristiano Ronaldo |

After a completed game, the user should be able to share their result as a series of emojis along with a link.

## Plan

A python script triggered by chron at 23:00  that choses a player from a list at random, checks that they have not been selected within the past 6 months, then scrapes the required info from the relevant website and stores it in a file `YYYY-MM-DD.json` where the date is the following day's date

A front end webpage with javascript that gets the current UTC date and requests `<today's date>.json`, and uses that to provide the functionality above.
