# -*- coding: utf-8 -*-
"""
Configuration handler for BlazeTv addon
Manages settings and addon configuration
"""

import xbmc
import xbmcaddon
import os
import json
from datetime import datetime


class Config:
    """Handle addon configuration and settings"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.addon_path = xbmc.translatePath(self.addon.getAddonInfo('path'))
        self.profile_path = xbmc.translatePath(self.addon.getAddonInfo('profile'))
        
        # Ensure profile directory exists
        if not os.path.exists(self.profile_path):
            os.makedirs(self.profile_path)
    
    def get(self, setting_id, default=None):
        """Get a setting value"""
        try:
            value = self.addon.getSetting(setting_id)
            
            # Handle boolean settings
            if value.lower() in ['true', 'false']:
                return value.lower() == 'true'
            
            # Handle integer settings
            if setting_id in ['cache_duration', 'history_days']:
                try:
                    return int(value) if value else (default or 0)
                except ValueError:
                    return default or 0
            
            return value if value else default
        except Exception as e:
            xbmc.log(f'[BlazeTv] Error getting setting {setting_id}: {str(e)}')
            return default
    
    def set(self, setting_id, value):
        """Set a setting value"""
        try:
            self.addon.setSetting(setting_id, str(value))
            return True
        except Exception as e:
            xbmc.log(f'[BlazeTv] Error setting {setting_id}: {str(e)}')
            return False
    
    def get_server_url(self):
        """Build complete server URL with credentials"""
        base_url = self.get('server_url', 'http://mains.services/get.php')
        username = self.get('username', '')
        password = self.get('password', '')
        stream_type = self.get('type', 'm3u_plus')
        output = self.get('output', 'ts')
        
        if not username or not password:
            return None
        
        params = {
            'username': username,
            'password': password,
            'type': stream_type,
            'output': output
        }
        
        # Build query string
        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        return f'{base_url}?{query_string}'
    
    def get_cache_dir(self):
        """Get cache directory path"""
        cache_dir = os.path.join(self.profile_path, 'cache')
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        return cache_dir
    
    def get_data_dir(self):
        """Get data directory path (for history, etc)"""
        data_dir = os.path.join(self.profile_path, 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        return data_dir
    
    def is_cache_valid(self, cache_file):
        """Check if cache file is still valid"""
        cache_duration = self.get('cache_duration', 60)  # minutes
        
        if not os.path.exists(cache_file):
            return False
        
        file_age = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))).total_seconds() / 60
        return file_age < cache_duration
    
    def save_json(self, filename, data):
        """Save data to JSON file in profile"""
        filepath = os.path.join(self.get_data_dir(), filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            xbmc.log(f'[BlazeTv] Error saving {filename}: {str(e)}')
            return False
    
    def load_json(self, filename, default=None):
        """Load data from JSON file in profile"""
        filepath = os.path.join(self.get_data_dir(), filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            xbmc.log(f'[BlazeTv] Error loading {filename}: {str(e)}')
        
        return default if default is not None else {}