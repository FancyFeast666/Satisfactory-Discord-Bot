Satisfactory Discord bot that utilizes API calls, web-scraping, and databases. 
The code for the API calls was made by: https://github.com/Jayy001/PyFactoryBridge/tree/main/pyfactorybridge
Currently web-scrapes off: https://satisfactory-calculator.com/en/interactive-map for certain in-game statistics

Current support discord commands:

/close_server shuts down the server, it is recommended to restrict access for this command
/game_duration returns the total time spent on the save
/get_collectibles returns information on obtained collectibles in the current save (slugs, hard drives etc)
/get_save sends the current save of the server to the user
/inventory WIP command, recommended to disable
/lizard_doggo also WIP command, recommended to disable
/ping returns the average ping of the server in Ticks per Second
/player_count returns the amount of players online on the server
/restart_server restarts the server, it is recommended to restrict access for this command
/server_status returns whether the game server is online
/start_server starts the server if it is offline

Important notes: 
Update your file paths and download chrome driver and chrome developer to ensure web-scraping functionality
Update IP addresses and ports to what your server is set to
Upon launch of the bot the bot will start the server on its own through the server's bat file if you have created one
The previous note is sometimes tedious to get to work properly, but once it starts it will run fine. Will be looked into on future versions
