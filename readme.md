
# One Punch Man Road to Hero 2.0 Database

Okay, so by some miracle you stumbled across this repo. 
 If you're reading this, I'll wager you also play a years old mobile gacha game, One Punch Man: Road to Hero 2.0.
If you're still reading, then you're one of the 0.000001% people who play the game who are tired of it being a pain in the arse to parse through the 150+ hero abilities and are ready to do something about it.
Well, you're in luck, because I did most of the heavy lifting, and you can see the results at https://thelazygame.com.

## Requirements:
- Windows PC
- Noxplayer (https://www.bignox.com/)
- Node.js (https://nodejs.org/en)
- Python 3.6+

## Optional:
- AWS Account
- Discord
- Discord Bot Account

## Where do I start?
We can split up the work between three different aspects:
- heroList.py - Data Generation
- public - Website
- opm-bot - Discord Bot

### Data Generation
All of the data files used by the website and discord-bot are generated through the heroList.py script which is where your changes will be made. There are two flags that are important to the whole thing working properly for you:
- *adb_pull*: This is responsible for pulling the csv files from the game into the hero_data directory.
- *b_s3_upload*: This is responsible for pushing the new data files to s3, which will be used by the website.

If you decide to upload those files automatically to s3, my script assumes there is a .env file, which will contain your access_key and secret_key. It will create any directories for you when uploading, so just make sure the *bucket* variable is correct for you.

For the adb_pull, make sure nox is running and opened the One Punch Man: RTH2.0 app to download the latest updates.

#### Scanning new csv files
So you want to make changes to the script and add in new csv files to check? Awesome! In the script, you may have noticed the list *lFiles*. You can add the file to map out in that list. But wait, there's more! \
You'll need to add a corresponding definition for the file, as their csv file are non-standard csv files and I have not taken the time to figure out how to convert them to a standardized format. If you read through those files, you'll notice that that the there are many that don't have the same number of delimiters per line, so make sure to figure out what you need from the file and add it to the definition. \
As a note, the first number of every single file is the index. \
They do nesting by using the ; delimiter. \
Finally, its a pain in the ass to do index references, but it isn't too bad once you understand how noSQL does indexing. \
Just read through the other file references to understand how I'm mapping out files and it shouldn't be terrible to add a new file in.

### Website
You shouldn't need to mess with the index.html file unless you're adding new filters or features. All of the data is generated through public/js/data.js

#### Testing
To test the application before deploying it, open up your system terminal and navigate to the script root directory. \
Run the following command `node app.js` \
Open your browser and navigate to https://127.0.0.1. \
If you have not deployed to AWS, you'll need to update the variable [API_URL](https://github.com/jhernandez6354/OPM/blob/master/public/js/data.js#L1) in the data.js file to use the local data file.

### OPM-Bot
The OPM Bot can be deployed directly on the same instance as the website, and only requires that the instance have python and the discord.py python library and requests.
It will post 5 requests at a time, with a limit of 50 requests per second as the default rate. \
I added a hard requirement of at least 2 non-special characters for any of the hero searches to prevent server spam.
When the bot is up and running, you can use the following commands:
*    English:
    - Simple - $opm Terrible Tornado
    - Acronym - $opm TT
    - Fuzzy - $opm Terr*

*    Russian:
    - Simple - $opm!ru Штормовой Ветер
    - Acronym - Not supported
    - Fuzzy - $opm!ru Штор*

*    Spanish:
    - Simple - $opm!es Terrible Tornado
    - Acronym - $opm!es TT 
    - Fuzzy - $opm!es Torn*

*    Unreleased Planned Heroes: $opm upcoming
***The strings are not case sensitive, but the $opm command is.***

Again, make sure you have a .env file that in the opm-bot directory with a reference to your bots `DISCORD_TOKEN`.