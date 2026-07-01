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


def show_main_menu():
    """Display main addon menu"""
    log('Showing main menu')
    
    menu_items = [
        ('Live Channels', 'channels'),
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
