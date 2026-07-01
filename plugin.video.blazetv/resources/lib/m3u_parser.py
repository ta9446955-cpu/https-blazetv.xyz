# -*- coding: utf-8 -*-
"""
M3U Playlist Parser
Fetches and parses M3U playlists from the server
"""

import requests
import xbmc
import re
from datetime import datetime
import os


class M3UParser:
    """Parse M3U playlists"""
    
    def __init__(self, config):
        self.config = config
        self.channels = []
        self.categories = {}
        self.last_update = None
    
    def fetch_playlist(self, force_refresh=False):
        """Fetch M3U playlist from server"""
        cache_file = os.path.join(self.config.get_cache_dir(), 'm3u_cache.m3u')
        
        # Check cache validity
        if not force_refresh and self.config.is_cache_valid(cache_file):
            xbmc.log('[BlazeTv] Using cached playlist')
            return self._load_from_file(cache_file)
        
        try:
            url = self.config.get_server_url()
            if not url:
                xbmc.log('[BlazeTv] No server URL configured')
                return None
            
            xbmc.log(f'[BlazeTv] Fetching playlist from server...')
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Cache the response
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            xbmc.log('[BlazeTv] Playlist cached successfully')
            return response.text
        except requests.exceptions.RequestException as e:
            xbmc.log(f'[BlazeTv] Failed to fetch playlist: {str(e)}', xbmc.LOGWARNING)
            # Try to use cached version if available
            if os.path.exists(cache_file):
                xbmc.log('[BlazeTv] Using cached playlist (fetch failed)')
                return self._load_from_file(cache_file)
            return None
    
    def _load_from_file(self, filepath):
        """Load M3U from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            xbmc.log(f'[BlazeTv] Error reading file: {str(e)}', xbmc.LOGWARNING)
            return None
    
    def parse(self):
        """Parse M3U content"""
        content = self.fetch_playlist()
        if not content:
            return False
        
        self.channels = []
        self.categories = {}
        
        lines = content.split('\n')
        current_channel = None
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and M3U header
            if not line or line.startswith('#EXTM3U'):
                continue
            
            # Parse EXTINF header
            if line.startswith('#EXTINF'):
                current_channel = self._parse_extinf(line)
            # Parse channel URL
            elif current_channel and not line.startswith('#'):
                current_channel['url'] = line
                self.channels.append(current_channel)
                
                # Add to categories
                group = current_channel.get('group_title', 'Uncategorized')
                if group not in self.categories:
                    self.categories[group] = []
                self.categories[group].append(current_channel)
                
                current_channel = None
        
        self.last_update = datetime.now()
        xbmc.log(f'[BlazeTv] Parsed {len(self.channels)} channels')
        return True
    
    def _parse_extinf(self, line):
        """Parse EXTINF line to extract channel info"""
        channel = {
            'name': '',
            'logo': '',
            'group_title': '',
            'tvg_id': '',
            'tvg_name': '',
        }
        
        # Extract info from line: #EXTINF:-1 tvg-id="..." tvg-name="..." tvg-logo="..." group-title="...",Channel Name
        
        # Extract attributes
        attrs = re.findall(r'(\w+(?:-\w+)*)="([^"]*)"', line)
        for attr, value in attrs:
            attr_lower = attr.lower().replace('-', '_')
            if attr_lower == 'tvg_id':
                channel['tvg_id'] = value
            elif attr_lower == 'tvg_name':
                channel['tvg_name'] = value
            elif attr_lower == 'tvg_logo':
                channel['logo'] = value
            elif attr_lower == 'group_title':
                channel['group_title'] = value
        
        # Extract channel name (after the comma)
        name_match = re.search(r',(.+)$', line)
        if name_match:
            channel['name'] = name_match.group(1).strip()
        
        return channel
    
    def get_channels(self, category=None):
        """Get channels, optionally filtered by category"""
        if not self.channels:
            self.parse()
        
        if category:
            return self.categories.get(category, [])
        return self.channels
    
    def get_categories(self):
        """Get all categories"""
        if not self.channels:
            self.parse()
        
        return list(self.categories.keys())
    
    def refresh(self):
        """Force refresh of playlist"""
        self.parse()
        return True