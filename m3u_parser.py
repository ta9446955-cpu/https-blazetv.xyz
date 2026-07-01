#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
M3U Playlist Parser for BlazeTv Addon
"""

import requests
import xbmc
from urllib.parse import unquote

class M3UParser:
    """
    Parse M3U playlists from remote server
    """
    
    def __init__(self, config):
        self.config = config
        self.channels = []
        self.categories = {}
    
    def fetch_playlist(self):
        """
        Fetch M3U playlist from configured server
        """
        try:
            username = self.config.get_username()
            password = self.config.get_password()
            server_url = self.config.get_server_url()
            stream_type = self.config.get_stream_type()
            
            if not username or not password:
                raise Exception('Missing credentials')
            
            # Build URL
            url = f"{server_url}?username={username}&password={password}&type={stream_type}"
            
            xbmc.log(f'[BlazeTv] Fetching playlist from: {url}', xbmc.LOGDEBUG)
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            return response.text
        except Exception as e:
            xbmc.log(f'[BlazeTv] Error fetching playlist: {str(e)}', xbmc.LOGWARNING)
            raise
    
    def parse_playlist(self, content):
        """
        Parse M3U content
        """
        self.channels = []
        self.categories = {}
        
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('#EXTINF:'):
                channel = self._parse_extinf(line)
                
                # Get stream URL from next line
                if i + 1 < len(lines):
                    stream_url = lines[i + 1].strip()
                    if stream_url and not stream_url.startswith('#'):
                        channel['url'] = stream_url
                        self.channels.append(channel)
                        
                        # Track categories
                        category = channel.get('group_title', 'Uncategorized')
                        if category not in self.categories:
                            self.categories[category] = []
                        self.categories[category].append(channel)
                        i += 1
            
            i += 1
    
    def _parse_extinf(self, extinf_line):
        """
        Parse EXTINF line
        Example: #EXTINF:-1 tvg-id="1" tvg-name="Channel 1" group-title="News",Channel 1
        """
        channel = {'name': '', 'logo': '', 'group_title': ''}
        
        # Extract name (after last comma)
        parts = extinf_line.split(',')
        if len(parts) > 1:
            channel['name'] = parts[-1].strip()
        
        # Extract attributes
        attrs_part = ','.join(parts[:-1])
        
        # Parse tvg-id
        if 'tvg-id="' in attrs_part:
            start = attrs_part.find('tvg-id="') + 8
            end = attrs_part.find('"', start)
            channel['tvg_id'] = attrs_part[start:end]
        
        # Parse tvg-name
        if 'tvg-name="' in attrs_part:
            start = attrs_part.find('tvg-name="') + 10
            end = attrs_part.find('"', start)
            channel['tvg_name'] = attrs_part[start:end]
        
        # Parse tvg-logo
        if 'tvg-logo="' in attrs_part:
            start = attrs_part.find('tvg-logo="') + 10
            end = attrs_part.find('"', start)
            channel['logo'] = attrs_part[start:end]
        
        # Parse group-title
        if 'group-title="' in attrs_part:
            start = attrs_part.find('group-title="') + 13
            end = attrs_part.find('"', start)
            channel['group_title'] = attrs_part[start:end]
        
        return channel
    
    def get_channels(self, category=None):
        """
        Get channels, optionally filtered by category
        """
        if not self.channels:
            content = self.fetch_playlist()
            self.parse_playlist(content)
        
        if category and category in self.categories:
            return self.categories[category]
        
        return self.channels
    
    def get_categories(self):
        """
        Get all available categories
        """
        if not self.channels:
            content = self.fetch_playlist()
            self.parse_playlist(content)
        
        return list(self.categories.keys())
