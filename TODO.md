# Necrobot TODO

Current version: 0.3.2

### Possiblilites to consider (not sure I want these yet)

- Make #dailyspoilerchat unreadable until the user submits for the daily, and accept submissions via PM. At the moment I'd like this to be an opt-in option. My main worry about doing this is that in the current system, people are forced into #dailyspoilerchat and forced to type in that channel when they submit, which encourages talking.
- Old daily leaderboards should show the seed for that daily. (I can't tell if this is working or not.)
- If a user has two seeds active and both are submittable, force them to use a `-date` flag for their
submission. (This should work like `-date Jan20`.)
- In general, allow use of the `-date` flag for daily submission, giving an error if the user inputs
a date that isn't their most recent seed.
- Add options for setting personal defaults on `.make` (or `.makeprivate`)
- Make race channels vanish for non-admin, non-racer once the race has begun
- Add hyperlinks to daily leaderboard times, so people can link vods/screenshots (I don't know
how to do this and keep the nice formatting at the moment.)
- Add comments to daily leaderboards, visible by hovering over them or something like that. (Again,
I don't know how this could be done in Discord at the moment. Actually displaying the comments likely
takes up too much screen real-estate.)
- Properly bugfix for when the bot is subscribed to multiple servers. (Calls like client.get_all_channels
should be rewritten. This may also require a refactor. I'm not actually sure what the use case is for this
at the moment, so it's hard to see exactly how the code should be written to support it.)

## Major improvements

### Support for voice rooms attached to race rooms

Create a raceroom command `.addvoice` that attaches a private voice channel to the race channel. 
In a public race, users entering the race could be automatically moved to this voice channel; 
in a private race, both admins and racers will be moved to the channel. The channel
should be destroyed when the race room is destroyed.

### Encapsulate database access, and make "thread-safe"

Currently the bot accesses two databases, daily.db and races.db, which keep track of
the times for the speedrun daily and results of public races. Presumably more will be
added. It does this through sqlite3.

I would like to encapsulate all these accesses in a single class responsible for handling
the databases. One primary objective of doing this is to make these database accesses
"thread-safe" -- by this, I mean that because this program uses asyncio, it's possible
for two coroutines to be accessing the database at the same time, which may cause
problems with sqlite (I am not sure). What is the right way to deal with this? (It's possible
that a simple mutex will do the job fine.) So far this hasn't been a problem; unfortunately I'm ignorant
of how much this 'ought to' be a problem because I'm still hazy on the exact details of how asyncio -- and,
for that matter, sqlite3 -- work.

### Database search & statistics; ratings based on daily/race rankings

Implement some algorithms for ranking people based on daily performance (and participation) and race performance (and participation), much like the NecroLab power rank and SRL ranks. (These are two separate ranks.) 

### Code refactoring: A skeleton bot with attachable "modules"

Something that seems like a nice way to refactor the code would be to make necrobot.py into a skeleton to which we can attach "modules", of which we would currently have two: the "racing" module and the "daily" module. Each module would be independently responsible for handling commands, writing to the main channel, etc; we could put a lot of the stuff in main.py into necrobot.py (maybe, though I hate combining modules), and move the specific handling of commands to the modules. This would help for the future, when we want to make a necrobot for season 4, which should have something like (but not identical to) the current race functionality, but nothing like the daily functionality.

### Stream support / Twitch integration

Allow for users to register their streams and to tag certain races as "streamed". For such races,
generate a multitwitch or kadgar link upon asking. As an even bigger project, make the bot able to
check whether said users are actually streaming. Also, make the bot able to report in your twitch chat
when people in your race have finished or forfeit (and who won, etc.)

### Support for best-of-x or repeat-y-times races

Add support to private race rooms for matches to be played best-of-x (when two racers only, presumably)
or repeat-y-times. The race room should remain the same for all matches and should keep track of the
current match score, and results should be reported as one match. The main purpose of this is for CoNDOR Season 4, when repeat-3-times will be the standard.

### Support for an optimized speedrun daily

Add a daily that's intended for optimizing a seed. May also want to consider adding dailies for other
categories as well. The main difficulty here is figuring out how to organize things from a UI
perspective, rather than writing the code.