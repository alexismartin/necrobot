#TODO: more robust message reading (e.g. should be able to read history in case of temporary crash etc)
#TODO: thread safety for database access

import asyncio
import datetime
import discord
import logging
import os
import sqlite3
import textwrap
import time

import config
import seedgen

from necrobot import Necrobot
from raceinfo import RaceInfo
from race import Race


##-Logging-------------------------------
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
##--------------------------------------


class LoginData(object):
    email = ''
    password = ''
    admin_id = None
    server_id = None

## Global variables
login_data = LoginData()                    # data to be read from the login file
client = discord.Client()                   # the client for discord
necrobot = Necrobot(client)                 # main class for necrobot behavior

## Database documentation:
## In races.db:------------------------------------------------------------------------------
##    TABLE race_data  : stores one entry for every race in the database
##        raceid       : a unique identifier for the race
##        timestamp    : the UTC time that the race started
##        character    : mirrors Race.RaceInfo
##        descriptor   : mirrors Race.RaceInfo
##        seeded       : mirrors Race.RaceInfo
##        seed         : mirrors Race.RaceInfo
##        sudden_death : mirrors Race.RaceInfo
##        flagplant    : mirrors Race.RaceInfo
##    TABLE racer_data : stores one entry per racer per race in the database
##        raceid       : the identifier for this race
##        playerid     : the player's unique discord identifier
##        name         : the player's username 
##        finished     : whether the player finished the race (rather than forfeiting) 
##        time         : the time (in hundredths of a second) for the race (undefined for forfeit races)
##        rank         : the rank the player finished in (undefined for forfeit races)
##        igt          : the in-game time, if the racer entered one (otherwise, -1)
##        comment      : any comment the racer entered
## In daily.db:-------------------------------------------------------------------------------
##    TABLE daily_races: stores one entry for each player-run of each daily
##        date         : the number of days since 1/1/2016 for this daily (with 1/1/2016 being date = 0) (the 'daily's number')
##        name         : the player's username
##        playerid     : the player's unique discord identifier
##        level        : the level the player ended on (ranges from 1 to 17, with special values 18 = win, 0 = unknown death)
##        time         : the player's time (total hundredths of a second) (undefined for deaths)
##    TABLE daily_seeds: stores one entry per race; contains info about the daily
##        date         : the daily's number
##        seed         : the seed for this daily
##        msgid        : the discord id for the leaderboard message 
##    TABLE last_daily : tracks dailies for which the player has registered (by calling .dailyseed)
##        playerid     : a unique identifier for the player
##        date         : a number for a daily for which the player has registered

## Set up the databases for the first time.    
def set_up_databases():

##    if config.RACE_DB_DO_RESET:
##        if os.path.isfile(config.RACE_DB_FILENAME):
##            backup_daily_db_filename = config.RACE_DB_FILENAME[:-3] + '_backup.db'
##            if os.path.isfile(backup_daily_db_filename):
##                os.remove(backup_daily_db_filename)
##            os.rename(config.RACE_DB_FILENAME, backup_daily_db_filename)

    if not os.path.isfile(config.RACE_DB_FILENAME):
        races_db_conn = sqlite3.connect(config.RACE_DB_FILENAME)
        races_db_cur = races_db_conn.cursor()
        races_db_cur.execute("""CREATE TABLE race_data
                            (raceid int, timestamp bigint, character varchar(255), descriptor varchar(255), seeded boolean, seed int, sudden_death boolean, flagplant boolean)""")
        races_db_cur.execute("""CREATE TABLE racer_data
                            (raceid int, playerid bigint, name varchar(255), finished boolean, time int, rank tinyint, igt int, comment varchar(255))""")
        races_db_conn.commit()
        races_db_conn.close()

##    if config.DAILY_DB_DO_RESET:
##        if os.path.isfile(config.DAILY_DB_FILENAME):
##            backup_daily_db_filename = config.DAILY_DB_FILENAME[:-3] + '_backup.db'
##            if os.path.isfile(backup_daily_db_filename):
##                os.remove(backup_daily_db_filename)
##            os.rename(config.DAILY_DB_FILENAME, backup_daily_db_filename)

    if not os.path.isfile(config.DAILY_DB_FILENAME):
        daily_db_conn = sqlite3.connect(config.DAILY_DB_FILENAME)
        daily_db_cur = daily_db_conn.cursor()
        daily_db_cur.execute("""CREATE TABLE daily_races
                            (date smallint, name varchar(255), playerid bigint, level tinyint, time int)""")
        daily_db_cur.execute("""CREATE TABLE daily_seeds (date smallint, seed int, msgid bigint)""")
        daily_db_cur.execute("""CREATE TABLE last_daily (playerid bigint, date smallint)""")
        daily_db_conn.commit()
        daily_db_conn.close()  

#----Main------------------------------------------------------
config.init()

set_up_databases()

login_info = open('data/login_info', 'r')
login_data.email = login_info.readline().rstrip('\n')
login_data.password = login_info.readline().rstrip('\n')
login_data.admin_id = login_info.readline().rstrip('\n')
login_data.server_id = login_info.readline().rstrip('\n')
login_info.close()

seedgen.init_seed()
     
# Define client events
@client.event
@asyncio.coroutine
def on_ready():
    print('-Logged in---------------')
    print('User name: {0}'.format(client.user.name))
    print('User id  : {0}'.format(client.user.id))
    print('-------------------------')
    print(' ')
    print('Initializing necrobot...')
    necrobot.post_login_init(login_data.server_id, login_data.admin_id)
    print('...done.')

@client.event
@asyncio.coroutine
def on_message(message):
    yield from necrobot.parse_message(message)

# Run client (TODO: use login(), start(), whatever to not get a blocking method)
client.run(login_data.email, login_data.password)