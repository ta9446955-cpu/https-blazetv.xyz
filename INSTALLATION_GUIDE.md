# BlazeTv Kodi Addon - Installation Guide

## Quick Start

### Step 1: Download
Clone or download the repository:
```bash
git clone https://github.com/ta9446955-cpu/https-blazetv.xyz.git
```

### Step 2: Install to Kodi

**Find your Kodi addons directory:**
- **Windows**: `%APPDATA%\Kodi\addons\`
- **Linux**: `~/.kodi/addons/`
- **macOS**: `~/Library/Application Support/Kodi/addons/`
- **Android**: `/storage/emulated/0/Android/data/org.xbmc.kodi/files/.kodi/addons/`

**Copy the addon:**
```bash
cp -r plugin.video.blazetv ~/.kodi/addons/
```

### Step 3: Restart Kodi
Exit Kodi completely and reopen it.

### Step 4: Configure
1. Open the BlazeTv addon
2. Go to Settings
3. Enter your server credentials:
   - Server URL: `http://mains.services/get.php`
   - Username: Your username
   - Password: Your password
   - Stream Type: `m3u_plus`
   - Output Format: `ts`

### Step 5: Enjoy!
Select "Live Channels" and start watching!

## Feature Overview

✅ **Live TV Streaming**
- Stream channels from M3U playlists
- Support for multiple stream formats

✅ **Smart Organization**
- Browse channels by category
- Quick channel search
- Recently watched tracking

✅ **Advanced Features**
- Playlist caching for faster loading
- EPG support
- Playback history
- Debug logging

## Settings Explained

### Server Settings
- **Server URL**: Your M3U provider's endpoint
- **Username/Password**: Your account credentials
- **Stream Type**: Format your server provides (m3u_plus, m3u, pls)
- **Output Format**: Video format (ts, m3u8)

### Display Settings
- **Show Categories**: Display channel categories in menu
- **Load EPG**: Enable program guide (if available)
- **Cache Duration**: How long to cache playlists (minutes)

### Features Settings
- **Channel Search**: Enable/disable search functionality
- **Playback History**: Track watched channels
- **History Retention**: Keep history for N days
- **Debug Logging**: Enable detailed logs

## Troubleshooting

### "No channels found"
1. Check credentials in Settings
2. Verify server is accessible
3. Enable debug logging
4. Check Kodi logs for errors

### Slow loading
1. Reduce cache duration
2. Check internet connection
3. Verify server is responsive

### Addon won't start
1. Verify addon is in correct directory
2. Check folder is named `plugin.video.blazetv`
3. Restart Kodi completely
4. Check file permissions

## System Requirements

- Kodi 18 (Leia) or newer
- Python 3.6+
- Active M3U server subscription
- Stable internet connection

## File Structure

```
plugin.video.blazetv/
├── addon.xml              # Addon metadata
├── main.py               # Main script
├── changelog.txt         # Version history
├── README.md             # Full documentation
├── resources/
│   ├── settings.xml      # Configuration options
│   └── lib/
│       ├── config.py     # Configuration handler
│       ├── m3u_parser.py # Playlist parser
│       ├── epg_handler.py # Program guide
│       ├── search_handler.py # Search
│       └── history_handler.py # History tracking
└── icon.png, fanart.jpg  # Media files
```

## Updating

To update to the latest version:

```bash
cd plugin.video.blazetv
git pull origin main
```

Then restart Kodi.

## Uninstalling

### Via Kodi
1. Go to Add-ons > Video add-ons
2. Right-click BlazeTv
3. Select Uninstall

### Manual
```bash
rm -rf ~/.kodi/addons/plugin.video.blazetv
rm -rf ~/.kodi/userdata/addon_data/plugin.video.blazetv
```

## Getting Help

1. **Check logs**: Enable debug logging in Settings
2. **Review documentation**: Read README.md for detailed info
3. **GitHub Issues**: Report problems or ask questions
4. **Kodi Forums**: Get help from the community

## Security Tips

- Keep your credentials secure
- Use HTTPS URLs when available
- Never share your settings file
- Change credentials if compromised
- Keep Kodi and addons updated

## Performance Tips

- Adjust cache duration for your needs
- Disable EPG if not needed
- Use shorter search queries
- Clean old history periodically

## Next Steps

1. Configure your server in Settings
2. Browse available channels
3. Explore addon features
4. Customize to your preferences

---

**For full documentation**, see [README.md](plugin.video.blazetv/README.md)

**For version history**, see [CHANGELOG](plugin.video.blazetv/changelog.txt)

**GitHub**: https://github.com/ta9446955-cpu/https-blazetv.xyz
