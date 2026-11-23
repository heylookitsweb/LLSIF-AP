# LLSIF-AP
Archipelago Multiworld implementation for Love Live! School idol festival, built on the [NPPS4 Private Server](https://github.com/DarkEnergyProcessor/NPPS4).

> [!WARNING]
> This AP is very early in development and has not been extensively tested.
> If you run into any problems or errors, please ping me (@ohheywebisherenow) in
> this implementation's post in the [Discord](https://discord.gg/Nu4X9gmGDR), 
> with context and console screenshots if applicable.

# AP Implementation
- Your goal is "completing" a select amount of unique live shows. Completion requirements and counts are set in your slot options.
- Checks are sent for clearing / achieving score ranks / achieving full combos in live shows, and reading Main Story chapters (optionally).
- Items available to receive are unlocks for new live shows to play, and progressive Main Story Chapters.
- Filler items are Gs, Love Gems Friend Points, and Support Units.
- Received items are collected through the Present Box in the Home Menu.
- Failing a live show or quitting a show early will send a Deathlink, if enabled.

## Requirements
- Windows Computer (Possible Linux support in the future)
- Phone capable of running SIF (Most devices should work)
- A personal WiFi connection for the two devices to communicate, or a method to port-forward the server

## Server Setup
1. Download the [latest version](https://github.com/heylookitsweb/LLSIF-AP/releases/latest/) of the server and extract it.
3. Run the server executable:
   - Windows: Run `npps4.exe`
4. The server will download necessary database files upon first startup, then the server will open.
5. Use this server whenever you want to play a Multiworld, it holds unique save files for each world you play.

## Connecting
1. Create a patched game client using [https://ethanaobrien.github.io/sif-patcher/](https://ethanaobrien.github.io/sif-patcher/) (Only necessary once)
   - Server URL should be the ip address of the computer you are hosting the NPPS4 server on, followed by the port `51376`. Ex. `http://192.0.2.0:51376`.
   - Your mobile device must be connected to the same internet connection as your computer. (Unless you are port forwarding)
2. If you already have the app installed, go to the app settings to set the server address. (To switch back to the public server if you play on it, change the address to `http://sif.ethanthesleepy.one`)
3. Using the client, start your game, and progress through the steps of account creation until you reach the AP login screen.
4. Login to the Multiworld, and the linked account will be created / loaded.

# Credits
- [NPPS4](https://github.com/DarkEnergyProcessor/NPPS4) Private Server by MikuAuahDark
- [archipelagopy](https://github.com/blackoutroulette/archipelagopy) by blackoutroulette (API wrapper for Archipelago, used to create the client used in the server)
