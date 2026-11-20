# LLSIF-AP
Archipelago Multiworld implementation for Love Live! School idol festival, built on the [NPPS4 Private Server](https://github.com/DarkEnergyProcessor/NPPS4).

# DISCLAIMER
This is my first APWorld, so issues are very possible. If you run into any errors, please ping me with it in this APWorld's post on the Discord.

# AP Implementation
- Your goal is finishing a select amount of unique live shows, set in the options for your slot.
- Checks are sent for clearing / achieving score ranks / achieving full combos in live shows, and reading Main Story chapters (optionally).
- Items available to receive are unlocks for new live shows to play, and new Main Story Chapters.
- Filler items are Gs, Love Gems Friend Points, and Support Units. (Can be configured in your options)
- Items can be collected through the Present Box in the Home Menu.
- Failing a live show or quitting early will send a Deathlink, if enabled.

# Server Setup
1. 

# Connecting
1. Create a patched game client using [https://ethanaobrien.github.io/sif-patcher/](https://ethanaobrien.github.io/sif-patcher/)
   - Server URL should be the ip address and port of the computer you are hosting the NPPS4 server on, Ex. `http://192.0.2.0:8000`.
   - Your mobile device must be connected to the same internet connection as your computer.
   - If needed, the private server address can be changed through the app's settings.
2. Using the client, start your game, and progress through the steps of account creation until you reach the login screen.
3. Login to the Multiworld, and the linked account will be created / loaded.

# Credits
- [NPPS4](https://github.com/DarkEnergyProcessor/NPPS4) Private Server by MikuAuahDark
- [archipelagopy](https://github.com/blackoutroulette/archipelagopy) by blackoutroulette (API wrapper for Archipelago, used to create the client used in the server)
