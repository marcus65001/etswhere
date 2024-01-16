import discord
import os
from dotenv import load_dotenv
from main import get_feed, get_stop, stop_info, get_stop_name
from datetime import datetime

load_dotenv()  # load all the variables from the env file
bot = discord.Bot()


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx):
    await ctx.respond("Hey!")


@bot.slash_command(name="stop", description="Get stop info")
async def stop(ctx, stop_id: discord.Option(discord.SlashCommandOptionType.string)):
    feed = get_feed(force_update=True, save_cache=True)
    trip_info = stop_info(feed, stop_id)
    stops = get_stop()
    if len(trip_info) > 0:
        embed = discord.Embed(
            title="[{}] {}".format(stop_id, get_stop_name(stops, stop_id)),
            description="Current trips from the stop",
            color=discord.Colour.blurple(),
        )
        route_text = ""
        stat_text = ""
        time_now = datetime.now().timestamp()
        for trip in trip_info:
            route_text = "[{id}]  `{route:^5}`  <{direction:^12}> ({vehicle:^4})".format(
                **trip)
            stat_text = "`    At {time_f:5} ({time_e})`".format(
                time_f=datetime.fromtimestamp(trip["time"]).strftime("%H:%M"),
                time_e="past" if time_now > trip["time"] else "in {time_d:.1f} min{delay_f}".format(
                    time_d=(trip["time"] - datetime.now().timestamp()) / 60,
                    delay_f="" if not trip["delay"] else
                    ", {:.1f} min {}".format(abs(trip["delay"] / 60),
                                             ("early" if trip[
                                                 "delay"] < 0 else "late"))
                )
            )
            embed.add_field(name=route_text, value=stat_text, inline=False)
        await ctx.respond("", embed=embed)
    else:
        if get_stop_name(stops, stop_id) != "Unknown":
            embed = discord.Embed(
                title="[{}] {}".format(stop_id, get_stop_name(stops, stop_id)),
                description="Current trips from the stop",
                color=discord.Colour.blurple(),
            )
            embed.add_field(
                name="Oof!", value="There's currently no active trips from this stop.", inline=False)
            await ctx.respond("", embed=embed)
        else:
            await ctx.respond("Incorrect Stop ID.")


bot.run(os.getenv('TOKEN'))
