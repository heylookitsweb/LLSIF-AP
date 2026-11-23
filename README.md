# LLSIF-AP
Archipelago Multiworld implementation for Love Live! School idol festival, built on the [NPPS4 Private Server](https://github.com/DarkEnergyProcessor/NPPS4).

> [!WARNING]
> This AP is very early in development and has not been extensively tested.
> If you run into any problems, please ping me (@ohheywebisherenow) in
> this implementation's post in the [Discord](https://discord.gg/Nu4X9gmGDR), 
> with context and console screenshots if applicable.

# AP Implementation
- Your goal is finishing a select amount of unique live shows, set in the options for your slot.
- Checks are sent for clearing / achieving score ranks / achieving full combos in live shows, and reading Main Story chapters (optionally).
- Items available to receive are unlocks for new live shows to play, and new Main Story Chapters.
- Filler items are Gs, Love Gems Friend Points, and Support Units. (Can be configured in your options)
- Items can be collected through the Present Box in the Home Menu.
- Failing a live show or quitting early will send a Deathlink, if enabled.

## Requirements
- Windows Computer (Linux may be supported in the future.)
- Phone capable of running SIF (Most devices should work)
- A personal WiFi connection for the two devices to communicate, or a method to port-forward the server

## Server Setup
1. Download the [latest version](https://github.com/heylookitsweb/LLSIF-AP/releases/latest/) of the server and extract it.
2. The `config.toml` file can be modified if needed (such as chaning the game assets source), but the defaults should work fine for most.
3. Open the server executable:
   - Windows: Run `npps4.exe`
4. The server will download necessary database files upon first startup, then the server will open.
5. Use this server whenever you want to play a Multiworld, it holds unique save files for each world you play.

(Installing/Running from the included source following [the vanilla server's instructions](https://github.com/heylookitsweb/LLSIF-AP/blob/main/NPPS4/README.md#install-manually) *should* also work, though this hasn't been tested)

## Connecting
1. If you haven't installed a patched client, create one using [https://ethanaobrien.github.io/sif-patcher/](https://ethanaobrien.github.io/sif-patcher/) (Only necessary once)
   - Server URL should be the ip address of the computer you are hosting the NPPS4 server on, followed by the port `51376`. Ex. `http://192.0.2.0:51376`.
   - Your mobile device must be connected to the same internet connection as your computer. (Unless you are port forwarding)
   - In the future, the server address can be changed in the app's settings, instead of creating another installer. (To switch back to the public server if you play on it, change the address to `http://sif.ethanthesleepy.one`)
3. Start the game, and progress through data download and account creation until you reach the AP login screen.
4. Login to the Multiworld, and your account will be created/loaded.

# Credits
- [NPPS4](https://github.com/DarkEnergyProcessor/NPPS4) Private Server by MikuAuahDark, the vanilla server this implementation is based on.
- [archipelagopy](https://github.com/blackoutroulette/archipelagopy) by blackoutroulette (API wrapper for Archipelago, used to create the client used in the server)
