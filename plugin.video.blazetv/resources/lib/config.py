#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BlazeTv Config Handler - Manages addon settings and configuration
"""

import xbmcaddon


class Config:
    """Handle addon configuration and settings"""
    
    def __init__(self):
        self.addon = xbmcaddon.Addon('plugin.video.blazetv')
    
    def get(self, key, default=None):
        """Get setting value"""
        try:
            return self.addon.getSetting(key)
        except:
            return default
    
    def set(self, key, value):
        """Set setting value"""
        try:
            self.addon.setSetting(key, str(value))
            return True
        except:
            return False
    
    def get_bool(self, key, default=False):
        """Get boolean setting value"""
        try:
            value = self.addon.getSetting(key)
            return value.lower() in ('true', '1', 'yes')
        except:
            return default
    
    def get_int(self, key, default=0):
        """Get integer setting value"""
        try:
            return int(self.addon.getSetting(key))
        except:
            return default
    
    def get_m3u_source(self):
        """Get M3U source (url, file, or xtream)"""
        m3u_url = self.get('m3u_url', '').strip()
        m3u_file = self.get('m3u_file_path', '').strip()
        
        if m3u_url:
            return {'type': 'url', 'value': m3u_url}
        elif m3u_file:
            return {'type': 'file', 'value': m3u_file}
        else:
            # Check if Xtream codes are configured
            username = self.get('username', '').strip()
            password = self.get('password', '').strip()
            if username and password:
                return {'type': 'xtream', 'username': username, 'password': password}
        
        return {'type': None, 'value': None}
