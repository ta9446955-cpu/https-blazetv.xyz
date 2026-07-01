# BlazeTv - Kodi Addon

A feature-rich Kodi addon for streaming live TV channels with playlist support, search, EPG integration, and playback history tracking.

## 🔗 Quick Links

- **📂 Addon Folder**: https://github.com/ta9446955-cpu/https-blazetv.xyz/tree/addon-development/plugin.video.blazetv
- **📋 Addon Branch**: https://github.com/ta9446955-cpu/https-blazetv.xyz/tree/addon-development
- **📖 Installation Guide**: https://github.com/ta9446955-cpu/https-blazetv.xyz/blob/addon-development/INSTALLATION_GUIDE.md
- **🐛 Report Issues**: https://github.com/ta9446955-cpu/https-blazetv.xyz/issues

## Features

### Core Features
- **Live Channel Streaming**: Stream channels from M3U playlists
- **Category Organization**: Browse channels organized by category
- **Channel Search**: Fuzzy search to find channels by name
- **Playback History**: Automatic tracking of watched channels
- **EPG Support**: Electronic Program Guide integration (expandable)
- **Smart Caching**: Automatic playlist caching for faster loading

### Configuration
- **Flexible Credentials**: Easy-to-configure server URL, username, and password
- **Stream Type Selection**: Support for different M3U stream types (m3u_plus, m3u, pls)
- **Output Formats**: Choose between ts and m3u8 output formats
- **Cache Management**: Configurable cache duration and history retention

### Advanced Features
- **Watch Statistics**: Track viewing habits and most-watched channels
- **Recent Channels**: Quick access to recently watched channels
- **History Management**: View and manage playback history
- **Debug Logging**: Built-in debug logging for troubleshooting

## Installation

### Quick Start
1. **Download**: Clone or download from https://github.com/ta9446955-cpu/https-blazetv.xyz/tree/addon-development/plugin.video.blazetv
2. **Extract** the `plugin.video.blazetv` folder
3. **Place** in your Kodi addons directory:
   - Windows: `%APPDATA%\Kodi\addons\`
   - Linux/Mac: `~/.kodi/addons/`
4. **Restart Kodi**
5. **Configure** your credentials in Settings

**For detailed instructions**, see [INSTALLATION_GUIDE.md](https://github.com/ta9446955-cpu/https-blazetv.xyz/blob/addon-development/INSTALLATION_GUIDE.md)

## Configuration

### First Time Setup

1. Open the addon
2. Click on **Settings**
3. Configure the following:

#### Server Settings
- **Server URL**: Your M3U server endpoint (default: http://mains.services/get.php)
- **Username**: Your server username
- **Password**: Your server password
- **Stream Type**: M3U format type (m3u_plus, m3u, or pls)
- **Output Format**: Video format (ts or m3u8)

#### Display Options
- **Show Channel Categories**: Enable/disable category browsing
- **Load EPG Data**: Enable/disable program guide
- **Cache Duration**: How long to cache playlists (5-1440 minutes)

#### Advanced Features
- **Enable Channel Search**: Turn search functionality on/off
- **Enable Playback History**: Track watched channels
- **History Retention**: How many days to keep history (1-365 days)
- **Enable Debug Logging**: Enable detailed logging for troubleshooting

## Usage

### Main Menu
1. **Live Channels**: Browse and stream all available channels
2. **Search Channels**: Find specific channels by name
3. **Categories**: Browse channels organized by category
4. **Recently Watched**: View recently watched channels
5. **Settings**: Configure addon options

### Viewing Channels
1. Select a channel from the list
2. Playback starts automatically
3. The channel is added to your watch history

### Searching for Channels
1. Select "Search Channels" from the main menu
2. Enter your search query
3. Results are sorted by relevance
4. Select a channel to play

## Troubleshooting

### No Channels Found
- Verify your credentials in Settings are correct
- Check that your server is accessible
- Ensure the stream format is correct for your server
- Enable debug logging (Settings > Advanced > Enable Debug Logging)

### Slow Loading
- Adjust cache duration (shorter = more frequent refreshes)
- Check your internet connection
- Verify server response time

### Playback Issues
- Verify the stream URL is accessible
- Check Kodi's video player codec support
- Try different output format (ts vs m3u8)
- Review debug logs for errors

## Security & Privacy

### Credential Handling
- Credentials are stored in Kodi's encrypted settings
- Never hardcoded in the addon code
- Always verify your server URL is HTTPS when possible

### Playback Data
- Watch history is stored locally on your device
- No data is sent to external servers
- History can be cleared at any time

## System Requirements

- Kodi 18 (Leia) or newer
- Python 3.6+
- Stable internet connection
- Active M3U server subscription

## License

This addon is provided as-is for educational purposes.

## Support

- **GitHub Issues**: https://github.com/ta9446955-cpu/https-blazetv.xyz/issues
- **Installation Help**: https://github.com/ta9446955-cpu/https-blazetv.xyz/blob/addon-development/INSTALLATION_GUIDE.md
- **Documentation**: See files in addon directory

## Project Structure

```
plugin.video.blazetv/
├── addon.xml                 # Addon metadata
├── main.py                   # Main addon script
├── changelog.txt             # Version history
├── README.md                 # Full documentation
├── resources/
│   ├── settings.xml         # Addon settings
│   └── lib/
│       ├── config.py        # Configuration handler
│       ├── m3u_parser.py    # Playlist parser
│       ├── epg_handler.py   # Program guide
│       ├── search_handler.py # Search functionality
│       └── history_handler.py # History tracking
└── icon.png, fanart.jpg     # Media assets
```

## Features Implemented

✅ Secure credential management  
✅ M3U playlist parsing and caching  
✅ Channel browsing by category  
✅ Fuzzy channel search  
✅ Automatic playback history  
✅ EPG support (extensible)  
✅ Configurable settings  
✅ Debug logging  
✅ Error handling  
✅ Complete documentation  

---

**Last Updated**: 2026-07-01  
**Version**: 1.0.0  
**Repository**: https://github.com/ta9446955-cpu/https-blazetv.xyz
