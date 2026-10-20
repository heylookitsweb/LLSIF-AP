# LLSIF-AP
Archipelago Multiworld implementation for Love Live! School idol festival, built on the [NPPS4 Private Server](https://github.com/DarkEnergyProcessor/NPPS4).

# DISCLAIMER
This is my first APWorld and my code for the server is definitely not perfect, so issues are very possible. If you run into any errors, please open an issue describing how it happened, or contact me in this APWorld's post on Discord.

# AP Implementation
- Your goal is finishing a select amount of unique live shows, set in the options for your slot.
- Checks are sent for clearing / achieving score ranks / achieving full combos in live shows.
- Items available to receive are unlocks for new live shows to play.
- Filler items are Gs, Love Gems Friend Points, and Support Units. (Can be configures in your options)
- Items can be collected through the Present Box in the Home Menu.
     - Currently, unlocked Live Shows will not appear until your save is reloaded, due to limitations with the game client. Clicking the `What's New` button in the Home Menu will return you to the title screen and update your song list.
- Failing a live show or quitting early will send a Deathlink, if enabled.

# Requirements
- Python 3.12
- A copy of [NPPS4](https://github.com/DarkEnergyProcessor/NPPS4)'s source files, extracted to a folder (Archipelago tested on commit [9edf806](https://github.com/DarkEnergyProcessor/NPPS4/tree/9edf8066ac4f941760d499faea2e803e59b074d9), may not work correctly on newer or older builds.)

# Installation
1. Navigate to the directory of your NPPS4 source files
2. Drag all files and folders from this repository's `NPPS4` directory into the source files, replacing any files you are prompted to
3. Finish installation by following the original steps in [Install Manually](https://github.com/DarkEnergyProcessor/NPPS4/blob/master/README.md#install-manually) and [Starting Up](https://github.com/DarkEnergyProcessor/NPPS4/blob/master/README.md#starting-up)

# Connecting
1. Start your private server following the steps in [Running](https://github.com/DarkEnergyProcessor/NPPS4/blob/master/README.md#running)
2. Create a patched game client using [https://ethanaobrien.github.io/sif-patcher/](url)
   - Server URL should be the ip address and port of the computer you are hosting the NPPS4 server on, Ex. `http://192.0.2.0:8000`.
   - Your mobile device must be connected to the same internet connection as your computer.
   - If needed, the private server address can be changed through the app's settings.
4. Using your installed client, start your game, and login to the Archipelago server using the popup.
5. You will be redirected to the appropriate save file for your Multiworld session.

