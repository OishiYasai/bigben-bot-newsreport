import discord
import asyncio
import logging
import random
import os
from datetime import datetime
import pytz
from gtts import gTTS
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Paths
CHIME_PATH = "chime.mp3"      # your news-style chime
TIME_TTS_PATH = "time.mp3"    # generated TTS for the time
NEWS_TTS_PATH = "news.mp3"    # generated TTS for the additional item

# Timezone for Luxembourg
LUX_TIMEZONE = pytz.timezone("Europe/Luxembourg")

# Pre-generated facts
FACTS = [
    "Honey never spoils; archaeologists have found pots of honey in ancient Egyptian tombs over 3,000 years old and still edible.",
    "Bananas are berries, but strawberries aren’t—botanically, berries have seeds inside.",
    "A day on Venus lasts longer than its year; it rotates on its axis slower than it orbits the Sun.",
    "Octopuses have three hearts and blue blood to pump oxygen more efficiently.",
    "There are more possible iterations of a game of chess than atoms in the known universe.",
    "A single bolt of lightning contains enough energy to toast 100,000 slices of bread.",
    "Wombat poop is cube-shaped, which prevents it from rolling away.",
    "Humans share about 60% of their DNA with bananas.",
    "The Eiffel Tower can be 15 cm taller during the summer due to thermal expansion.",
    "Sea otters hold hands while sleeping to keep from drifting apart.",
    "A group of flamingos is called a 'flamboyance'.",
    "Cleopatra lived closer in time to the Moon landing than to the building of the Great Pyramid.",
    "The world's quietest room is in Microsoft's headquarters; it measures −20.35 dBA.",
    "Sharks existed before trees; sharks have been around for 400 million years.",
    "Koalas have unique fingerprints nearly indistinguishable from humans'.",
    "A day on Mercury lasts 59 Earth days.",
    "Bees sometimes sting other bees to defend the hive.",
    "Sloths can hold their breath longer than dolphins, up to 40 minutes.",
    "The word 'nerd' was first coined by Dr. Seuss in 1950.",
    "Venus rotates in the opposite direction to most planets in our solar system.",
]

# Pre-generated story templates (placeholders: {time_phrase}, {username})
STORY_TEMPLATES = [
    "Breaking news: At {time_phrase}, local teen {username} made headlines after foiling a petty theft downtown.",
    "Reports confirm that at {time_phrase}, resident {username} discovered a hidden tunnel beneath the city library.",
    "This just in: At {time_phrase}, {username} set a new world record for the fastest puzzle solve.",
    "In an unusual event at {time_phrase}, {username} rescued a stranded kitten from a busy intersection.",
    "Today at {time_phrase}, {username} was spotted painting a massive mural on the town hall walls.",
    "At {time_phrase}, {username} organized an impromptu concert in the central park, delighting passersby.",
    "Special report: {username} launched a homemade rocket at {time_phrase}, reaching a height of 20 feet.",
    "Eye-witnesses say that at {time_phrase}, {username} taught a yoga class to neighborhood dogs.",
    "Local hero {username} repaired the community fountain single-handedly at {time_phrase}.",
    "At {time_phrase}, {username} baked the largest pancake ever recorded in the city.",
    "Residents were surprised when {username} hosted a pop-up book reading at {time_phrase}.",
    "At {time_phrase}, {username} charted the flight path of a rare bird in the city center.",
    "Breaking: {username} calibrated the town clock at {time_phrase}, ensuring perfect timing for all.",
    "At {time_phrase}, {username} unveiled a new mobile app designed to help local volunteers.",
    "Newsflash: {username} taught cybersecurity tips at {time_phrase} in the community hall.",
    "At {time_phrase}, {username} choreographed a flash mob that took over the main square.",
    "Witnesses report {username} parachuted onto the rooftop garden at {time_phrase}.",
    "At {time_phrase}, {username} discovered a new species of mushroom in the city park.",
    "Today at {time_phrase}, {username} hosted a charity run that attracted hundreds of participants.",
    "At {time_phrase}, {username} repaired a historic clock tower mechanism single-handedly.",
]

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# Discord intents
intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

# Scheduler
scheduler = AsyncIOScheduler(timezone=LUX_TIMEZONE)

async def play_news_bulletin():
    logging.info("Starting news bulletin routine…")

    for guild in client.guilds:
        # Find the most populated voice channel
        most_populated = None
        max_users = 0
        for vc in guild.voice_channels:
            users = [m for m in vc.members if not m.bot]
            count = len(users)
            if count > max_users:
                max_users = count
                most_populated = vc

        if not most_populated or max_users == 0:
            logging.warning("No populated voice channel found; skipping bulletin.")
            continue

        # Determine current time
        now = datetime.now(LUX_TIMEZONE)
        hour_12 = now.hour if 1 <= now.hour <= 12 else abs(now.hour - 12)
        hour_12 = 12 if hour_12 == 0 else hour_12
        minute = now.minute
        period = "AM" if now.hour < 12 else "PM"
        if minute == 0:
            time_phrase = f"{hour_12} o'clock {period}"
        else:
            time_phrase = f"{hour_12}:{minute:02d} {period}"
        time_text = f"This is your hourly news bulletin. The time is {time_phrase}."
        logging.info(f"Time announcement: {time_text}")

        # Generate additional report
        if random.choice([True, False]):
            additional_text = random.choice(FACTS)
        else:
            member_names = [m.name for m in most_populated.members if not m.bot]
            if member_names:
                template = random.choice(STORY_TEMPLATES)
                selected = random.choice(member_names)
                additional_text = template.format(time_phrase=time_phrase, username=selected)
            else:
                additional_text = random.choice(FACTS)
        logging.info(f"Additional report: {additional_text}")

        # Generate TTS audio files
        try:
            gTTS(text=time_text, lang="en").save(TIME_TTS_PATH)
            gTTS(text=additional_text, lang="en").save(NEWS_TTS_PATH)
        except Exception as e:
            logging.error(f"Failed to generate TTS: {e}")
            continue

        # Connect & play: chime → time TTS → news TTS
        try:
            vc_conn = await most_populated.connect()
            vc_conn.play(discord.FFmpegPCMAudio(CHIME_PATH))
            while vc_conn.is_playing():
                await asyncio.sleep(0.1)
            await asyncio.sleep(0.5)

            vc_conn.play(discord.FFmpegPCMAudio(TIME_TTS_PATH))
            while vc_conn.is_playing():
                await asyncio.sleep(0.1)
            await asyncio.sleep(0.5)

            vc_conn.play(discord.FFmpegPCMAudio(NEWS_TTS_PATH))
            while vc_conn.is_playing():
                await asyncio.sleep(0.1)

            # ─── NEW SLEEP TO AVOID CUT-OFF ─────────────────────────
            logging.info("Pausing 5 seconds to let the sentence finish…")
            await asyncio.sleep(5)

            await vc_conn.disconnect()
            logging.info("Finished news bulletin and disconnected.")
        except Exception as e:
            logging.error(f"Error during voice playback: {e}")

# Discord client setup
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user}")
    scheduler.add_job(play_news_bulletin, CronTrigger(minute=0))
    scheduler.start()
    logging.info("Scheduled news bulletins on the hour.")
    logging.info("Running initial bulletin now for testing…")
    await play_news_bulletin()

client.run(TOKEN)
