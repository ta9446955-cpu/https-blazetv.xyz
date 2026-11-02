#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BlazeTv Kodi Addon - Main Plugin Script
Handles routing, playlist loading, search, and playback
"""

import sys
import xbmc
import xbmcvfs
import xbmcgui
import xbmcplugin
import xbmcaddon
from urllib.parse import urlencode, parse_qs
import os
import json
from datetime import datetime, timedelta

# Import our custom modules
addon_dir = xbmcvfs.translatePath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(addon_dir, 'resources', 'lib'))

from m3u_parser import M3UParser
from epg_handler import EPGHandler
from search_handler import SearchHandler
from history_handler import HistoryHandler
from config import Config

# Get addon handle
handle = int(sys.argv[1])
args = parse_qs(sys.argv[2][1:])

# Initialize config and handlers
config = Config()
m3u_parser = M3UParser(config)
epg_handler = EPGHandler(config)
search_handler = SearchHandler(m3u_parser)
history_handler = HistoryHandler(config)


def log(msg, level=xbmc.LOGDEBUG):
    """Log message to Kodi log"""
    if config.get('enable_debug'):
        xbmc.log(f'[BlazeTv] {msg}', level)


def show_error(message):
    """Show error dialog"""
    dialog = xbmcgui.Dialog()
    dialog.notification('BlazeTv Error', message, xbmcgui.NOTIFICATION_ERROR, 5000)
    log(f'ERROR: {message}', xbmc.LOGWARNING)


def browse_downloads_for_m3u():
    """Browse the device Downloads folder for .m3u/.m3u8 files using Kodi's own list dialog"""
    log('Browsing Downloads folder for M3U files')

    candidate_dirs = [
        '/storage/emulated/0/Download/',
        '/sdcard/Download/',
        'special://home/../Download/',
        'special://temp/',
    ]

    found_files = []
    found_dir = None

    for candidate in candidate_dirs:
        try:
            real_path = xbmcvfs.translatePath(candidate)
            dirs, files = xbmcvfs.listdir(real_path)
            m3u_files = [f for f in files if f.lower().endswith(('.m3u', '.m3u8'))]
            if m3u_files:
                found_files = sorted(m3u_files)
                found_dir = real_path
                break
        except Exception as e:
            log(f'Could not read {candidate}: {str(e)}')
            continue

    if not found_files:
        xbmcgui.Dialog().ok(
            'BlazeTv',
            'No .m3u or .m3u8 files found in your Downloads folder. '
            'Download your playlist file first, then try again. '
            'Alternatively, paste the URL directly in Settings.'
        )
        xbmcplugin.endOfDirectory(handle, succeeded=False, updateListing=False, cacheToDisc=False)
        return

    choice = xbmcgui.Dialog().select('Select your M3U Playlist file', found_files)

    if choice == -1:
        xbmcplugin.endOfDirectory(handle, succeeded=False, updateListing=False, cacheToDisc=False)
        return

    selected_file = found_files[choice]
    full_path = found_dir.rstrip('/') + '/' + selected_file

    addon = xbmcaddon.Addon()
    addon.setSetting('m3u_url', full_path)

    xbmcgui.Dialog().notification(
        'BlazeTv',
        f'M3U set: {selected_file}',
        xbmcgui.NOTIFICATION_INFO,
        3000
    )
    log(f'M3U playlist set to: {full_path}')
    xbmcplugin.endOfDirectory(handle, succeeded=False, updateListing=False, cacheToDisc=False)


VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov', '.m4v', '.ts', '.webm', '.wmv', '.mpg', '.mpeg', '.flv')


def get_movie_roots():
    """Return a list of (label, path) folders that exist and can be read.
    Custom folder from Settings comes first, then common phone and computer folders."""
    home = os.path.expanduser('~')
    candidates = []

    custom = (config.get('movies_folder') or '').strip()
    if custom:
        candidates.append(('My Movies Folder', custom))

    candidates += [
        ('Downloads', '/storage/emulated/0/Download'),
        ('Movies', '/storage/emulated/0/Movies'),
        ('Downloads', '/sdcard/Download'),
        ('Downloads', os.path.join(home, 'Downloads')),
        ('Videos', os.path.join(home, 'Videos')),
        ('Movies', os.path.join(home, 'Movies')),
    ]

    roots = []
    seen = set()
    for label, path in candidates:
        key = os.path.normpath(path).lower()
        if key in seen:
            continue
        try:
            xbmcvfs.listdir(path)
            if not xbmcvfs.exists(os.path.join(path, '')):
                continue
        except Exception as e:
            log(f'Could not read {path}: {str(e)}')
            continue
        seen.add(key)
        roots.append((label, path))
    return roots


def show_local_movies(path=None):
    """List video files and folders from a movie folder on this device"""
    log(f'Browsing local movies: {path}')

    if not path:
        roots = get_movie_roots()

        if not roots:
            xbmcgui.Dialog().ok(
                'BlazeTv',
                'Could not find a movie folder. Set "Movies folder" in '
                'Settings > Features, or give Kodi storage permission '
                'in your device settings, then try again.'
            )
            xbmcplugin.endOfDirectory(handle, succeeded=False)
            return

        if len(roots) > 1:
            for label, root in roots:
                add_menu_item(
                    label=f'{label}  ({root})',
                    action='local_movies',
                    params={'path': root},
                    is_folder=True,
                    icon='DefaultFolder.png'
                )
            xbmcplugin.endOfDirectory(handle)
            return

        path = roots[0][1]

    try:
        dirs, files = xbmcvfs.listdir(path)
    except Exception as e:
        show_error(f'Cannot read folder: {str(e)}')
        xbmcplugin.endOfDirectory(handle, succeeded=False)
        return

    # Subfolders
    for d in sorted(dirs, key=str.lower):
        add_menu_item(
            label=f'[{d}]',
            action='local_movies',
            params={'path': os.path.join(path, d)},
            is_folder=True,
            icon='DefaultFolder.png'
        )

    # Video files
    video_files = [f for f in files if f.lower().endswith(VIDEO_EXTENSIONS)]
    for f in sorted(video_files, key=str.lower):
        full_path = os.path.join(path, f)
        params = {'action': 'play_local', 'path': full_path, 'name': f}
        url = f'{sys.argv[0]}?{urlencode(params)}'
        list_item = xbmcgui.ListItem(os.path.splitext(f)[0])
        list_item.setProperty('IsPlayable', 'true')
        list_item.setArt({'icon': 'DefaultMovies.png'})
        list_item.setInfo('video', {'title': os.path.splitext(f)[0]})
        xbmcplugin.addDirectoryItem(handle, url, list_item, False)

    if not dirs and not video_files:
        xbmcgui.Dialog().notification(
            'BlazeTv', 'No video files found here', xbmcgui.NOTIFICATION_INFO, 3000
        )

    xbmcplugin.endOfDirectory(handle)


def play_local(file_path, name):
    """Play a video file from the device"""
    log(f'Playing local file: {file_path}')
    try:
        list_item = xbmcgui.ListItem(name)
        list_item.setPath(file_path)
        xbmcplugin.setResolvedUrl(handle, True, list_item)
    except Exception as e:
        show_error(f'Failed to play file: {str(e)}')
        log(f'Exception: {str(e)}', xbmc.LOGWARNING)
        xbmcplugin.setResolvedUrl(handle, False, xbmcgui.ListItem())


def show_main_menu():
    """Display main addon menu"""
    log('Showing main menu')
    
    menu_items = [
        ('Live Channels', 'channels'),
        ('My Downloads (Movies)', 'local_movies'),
        ('Load M3U from Downloads', 'browse_m3u'),
        ('Search Channels', 'search') if config.get('enable_search') else None,
        ('Categories', 'categories') if config.get('show_categories') else None,
        ('Recently Watched', 'history') if config.get('enable_history') else None,
        ('Settings', 'settings'),
    ]
    
    # Filter out None items
    menu_items = [item for item in menu_items if item is not None]
    
    for label, action in menu_items:
        add_menu_item(
            label=label,
            action=action,
            is_folder=True,
            icon='DefaultVideo.png'
        )
    
    xbmcplugin.endOfDirectory(handle)


def show_channels(category=None):
    """Display all channels or channels in specific category"""
    log(f'Loading channels (category: {category})')
    
    # Fetch M3U playlist
    try:
        channels = m3u_parser.get_channels(category)
        
        if not channels:
            show_error('No channels found. Check your credentials in Settings.')
            return
        
        for channel in channels:
            add_channel_item(channel)
        
        xbmcplugin.endOfDirectory(handle)
    except Exception as e:
        show_error(f'Failed to load channels: {str(e)}')
        log(f'Exception: {str(e)}', xbmc.LOGWARNING)


def show_categories():
    """Display channel categories"""
    log('Loading categories')
    
    try:
        categories = m3u_parser.get_categories()
        
        if not categories:
            show_error('No categories found.')
            return
        
        for category in categories:
            add_menu_item(
                label=f'{category} ({len(m3u_parser.get_channels(category))}) channels',
                action='channels',
                params={'category': category},
                is_folder=True,
                icon='DefaultTVShows.png'
            )
        
        xbmcplugin.endOfDirectory(handle)
    except Exception as e:
        show_error(f'Failed to load categories: {str(e)}')
        log(f'Exception: {str(e)}', xbmc.LOGWARNING)


def search_channels():
    """Search for channels"""
    log('Opening search dialog')
    
    keyboard = xbmc.Keyboard('', 'Search channels...')
    keyboard.doModal()
    
    if keyboard.isConfirmed():
        query = keyboard.getText()
        if query:
            try:
                results = search_handler.search(query)
                
                if not results:
                    show_error(f'No channels found matching "{query}"')
                    return
                
                for channel in results:
                    add_channel_item(channel)
                
                xbmcplugin.endOfDirectory(handle)
            except Exception as e:
                show_error(f'Search failed: {str(e)}')
                log(f'Exception: {str(e)}', xbmc.LOGWARNING)


def show_history():
    """Display recently watched channels"""
    log('Loading watch history')
    
    try:
        history = history_handler.get_history()
        
        if not history:
            show_error('No watch history found.')
            return
        
        for entry in history:
            channel = entry['channel']
            watched = entry['watched_at']
            add_channel_item(
                channel,
                label_suffix=f" [Watched: {watched}]"
            )
        
        xbmcplugin.endOfDirectory(handle)
    except Exception as e:
        show_error(f'Failed to load history: {str(e)}')
        log(f'Exception: {str(e)}', xbmc.LOGWARNING)


def play_channel(channel_url, channel_name):
    """Play a channel"""
    log(f'Playing channel: {channel_name} - {channel_url}')
    
    try:
        # Record in history
        if config.get('enable_history'):
            history_handler.add_entry(channel_name, channel_url)
        
        # Create list item
        list_item = xbmcgui.ListItem(channel_name)
        list_item.setPath(channel_url)
        list_item.setMimeType('application/x-mpegURL')
        list_item.setProperty('IsPlayable', 'true')
        
        # Load EPG info if available
        if config.get('load_epg'):
            epg_info = epg_handler.get_channel_epg(channel_name)
            if epg_info:
                list_item.setInfo('video', {
                    'title': epg_info.get('title', channel_name),
                    'plot': epg_info.get('plot', ''),
                })
        
        # Resolve and play
        xbmcplugin.setResolvedUrl(handle, True, list_item)
    except Exception as e:
        show_error(f'Failed to play channel: {str(e)}')
        log(f'Exception: {str(e)}', xbmc.LOGWARNING)
        xbmcplugin.setResolvedUrl(handle, False, xbmcgui.ListItem())


def add_menu_item(label, action, params=None, is_folder=True, icon='DefaultFolder.png'):
    """Add a menu item to the directory"""
    if params is None:
        params = {}
    
    params['action'] = action
    url = f'{sys.argv[0]}?{urlencode(params)}'
    
    list_item = xbmcgui.ListItem(label)
    list_item.setArt({'icon': icon})
    
    xbmcplugin.addDirectoryItem(handle, url, list_item, is_folder)


def add_channel_item(channel, label_suffix=''):
    """Add a channel item to the directory"""
    label = f"{channel.get('name', 'Unknown')}{label_suffix}"
    params = {
        'action': 'play',
        'url': channel.get('url', ''),
        'name': channel.get('name', 'Channel'),
    }
    url = f"{sys.argv[0]}?{urlencode(params)}"
    
    list_item = xbmcgui.ListItem(label)
    list_item.setProperty('IsPlayable', 'true')
    
    # Set icon if available
    if channel.get('logo'):
        list_item.setArt({'thumb': channel['logo'], 'icon': channel['logo']})
    
    # Set info
    list_item.setInfo('video', {
        'title': channel.get('name', 'Unknown'),
        'plot': channel.get('group_title', 'No category'),
    })
    
    xbmcplugin.addDirectoryItem(handle, url, list_item, False)


def open_settings():
    """Open addon settings"""
    xbmcaddon.Addon().openSettings()


def router():
    """Main router function"""
    action = args.get('action', ['main'])[0]
    
    log(f'Router action: {action}')
    
    if action == 'main':
        show_main_menu()
    elif action == 'channels':
        category = args.get('category', [None])[0]
        show_channels(category)
    elif action == 'categories':
        show_categories()
    elif action == 'search':
        search_channels()
    elif action == 'history':
        show_history()
    elif action == 'play':
        channel_url = args.get('url', [''])[0]
        channel_name = args.get('name', ['Channel'])[0]
        play_channel(channel_url, channel_name)
    elif action == 'settings':
        open_settings()
    elif action == 'browse_m3u':
        browse_downloads_for_m3u()
    elif action == 'local_movies':
        show_local_movies(args.get('path', [None])[0])
    elif action == 'play_local':
        play_local(args.get('path', [''])[0], args.get('name', ['Movie'])[0])
    else:
        show_main_menu()


if __name__ == '__main__':
    try:
        router()
    except Exception as e:
        show_error(f'Addon error: {str(e)}')
        log(f'Fatal exception: {str(e)}', xbmc.LOGWARNING)
