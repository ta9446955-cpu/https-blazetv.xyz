#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BlazeTv Kodi Addon - Main Plugin Script (Enhanced)
Handles routing, playlist loading, search, and playback with M3U file management
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
from m3u_file_handler import M3UFileHandler
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
m3u_file_handler = M3UFileHandler(config)
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


def show_success(message):
    """Show success notification"""
    dialog = xbmcgui.Dialog()
    dialog.notification('BlazeTv', message, xbmcgui.NOTIFICATION_INFO, 3000)


def show_main_menu():
    """Display main addon menu"""
    log('Showing main menu')
    
    menu_items = [
        ('Live Channels', 'channels'),
        ('Search Channels', 'search') if config.get('enable_search') else None,
        ('Categories', 'categories') if config.get('show_categories') else None,
        ('Recently Watched', 'history') if config.get('enable_history') else None,
        ('M3U File Management', 'm3u_management'),
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


def show_m3u_management():
    """Display M3U file management menu"""
    log('Showing M3U management menu')
    
    menu_items = [
        ('Upload/Browse M3U File', 'browse_m3u'),
        ('View Current M3U Info', 'view_m3u_info'),
        ('Export M3U File', 'export_m3u'),
        ('Restore from Backup', 'restore_backup'),
        ('List Backups', 'list_backups'),
    ]
    
    for label, action in menu_items:
        add_menu_item(
            label=label,
            action=action,
            is_folder=False,
            icon='DefaultFolder.png'
        )
    
    xbmcplugin.endOfDirectory(handle)


def browse_m3u_file():
    """Browse and select M3U file"""
    log('Opening M3U file browser')
    file_path = m3u_file_handler.browse_for_m3u_file()
    
    if file_path:
        if m3u_file_handler.save_m3u_file(file_path):
            show_success('M3U file loaded successfully!')
            # Clear URL setting when file is selected
            config.set('m3u_url', '')
        else:
            show_error('Failed to load M3U file')
    
    xbmcplugin.endOfDirectory(handle)


def view_m3u_info():
    """Display current M3U file information"""
    log('Viewing M3U info')
    
    info = m3u_file_handler.get_m3u_info()
    
    if not info:
        show_error('No M3U file loaded')
    else:
        message = f"M3U File Information:\n\n" \
                  f"Channels: {info['channels']}\n" \
                  f"Size: {info['size_kb']} KB\n" \
                  f"Modified: {info['modified']}\n" \
                  f"Path: {info['path']}"
        
        dialog = xbmcgui.Dialog()
        dialog.textviewer('M3U Information', message)
    
    xbmcplugin.endOfDirectory(handle)


def export_m3u():
    """Export current M3U file"""
    log('Exporting M3U file')
    
    if m3u_file_handler.export_m3u_file():
        show_success('M3U file exported successfully!')
    else:
        show_error('Failed to export M3U file')
    
    xbmcplugin.endOfDirectory(handle)


def restore_backup():
    """Restore M3U from backup"""
    log('Opening restore backup dialog')
    
    backups = m3u_file_handler.list_backups()
    
    if not backups:
        show_error('No backups available')
        xbmcplugin.endOfDirectory(handle)
        return
    
    backup_names = [b['name'] for b in backups]
    dialog = xbmcgui.Dialog()
    selected = dialog.select('Select Backup to Restore', backup_names)
    
    if selected >= 0:
        if m3u_file_handler.restore_backup(backups[selected]['path']):
            show_success('M3U restored successfully!')
        else:
            show_error('Failed to restore backup')
    
    xbmcplugin.endOfDirectory(handle)


def list_backups():
    """List all available backups"""
    log('Listing backups')
    
    backups = m3u_file_handler.list_backups()
    
    if not backups:
        show_error('No backups available')
        xbmcplugin.endOfDirectory(handle)
        return
    
    for backup in backups:
        size_kb = round(backup['size'] / 1024, 2)
        add_menu_item(
            label=f"{backup['name']} ({size_kb} KB)",
            action='',
            is_folder=False,
            icon='DefaultFile.png'
        )
    
    xbmcplugin.endOfDirectory(handle)


def show_channels(category=None):
    """Display all channels or channels in specific category"""
    log(f'Loading channels (category: {category})')
    
    # Fetch M3U playlist
    try:
        channels = m3u_parser.get_channels(category)
        
        if not channels:
            show_error('No channels found. Check your M3U configuration in Settings.')
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
    elif action == 'm3u_management':
        show_m3u_management()
    elif action == 'browse_m3u':
        browse_m3u_file()
    elif action == 'view_m3u_info':
        view_m3u_info()
    elif action == 'export_m3u':
        export_m3u()
    elif action == 'restore_backup':
        restore_backup()
    elif action == 'list_backups':
        list_backups()
    else:
        show_main_menu()


if __name__ == '__main__':
    try:
        router()
    except Exception as e:
        show_error(f'Addon error: {str(e)}')
        log(f'Fatal exception: {str(e)}', xbmc.LOGWARNING)
