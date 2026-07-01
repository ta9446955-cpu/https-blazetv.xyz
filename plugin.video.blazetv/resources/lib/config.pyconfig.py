#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuration Handler for BlazeTv Addon
"""

import xbmcaddon
import xbmc
import os

ADDON = xbmcaddon.Addon()

class Config:
    """
    Handle all addon configuration settings
    """
    
    def __init__(self):
        self.addon = ADDON
    
    def get(self, setting):
        """
        Get a setting value
        """
        try:
            return self.addon.getSetting(setting)
        except Exception as e:
            xbmc.log(f'[BlazeTv Config] Error getting setting {setting}: {str(e)}', xbmc.LOGWARNING)
            return None
    
    def set(self, setting, value):
        """
        Set a setting value
        """
        try:
            self.addon.setSetting(setting, str(value))
            return True
        except Exception as e:
            xbmc.log(f'[BlazeTv Config] Error setting {setting}: {str(e)}', xbmc.LOGWARNING)
            return False
    
    def get_username(self):
        return self.get('username')
    
    def get_password(self):
        return self.get('password')
    
    def get_server_url(self):
        url = self.get('server_url')
        return url if url else 'http://mains.services/get.php'
    
    def get_stream_type(self):
        stream_type = self.get('type')
        return stream_type if stream_type else 'm3u_plus'
