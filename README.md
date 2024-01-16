# ETSWhere
A set of utility Python scripts to obtain real-time bus tracking for Edmonton Transit Service (with Discord bot interface).

ETS has offered a few GTFS data feeds through (City of Edmonton's Open Data Portal)[https://data.edmonton.ca/browse?category=Transit]:
* Non real-time: Trips, Transfers, Stops, Routes
* Real-time: Vehicle Positions

The script compiles the relavant GTFS feeds to obtain real-time bus info given a stop number, a Discord bot is included as user interface.

## Usage
Requires `discord.py`, set Discord bot token `TOKEN` in `.env` file.

Run `python discord_bot.py`

## Screenshot
![screenshot](https://github.com/marcus65001/etswhere/blob/main/.screenshot/sc_etswhere.png?raw=true)
