#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Playback History Handler for BlazeTv Addon
"""

import xbmc
import xbmcvfs
import json
import os
from datetime import datetime

class HistoryHandler:
    """
    Handle playback history tracking
    """
    
    def __init__(self, config):
        self.config = config
        self.profile_dir = xbmcvfs.translatePath('special://profile/addon_data/plugin.video.blazetv/')
        self.history_file = os.path.join(self.profile_dir, 'history.json')
        
        # Create directory if it doesn't exist
        if not os.path.exists(self.profile_dir):
            os.makedirs(self.profile_dir)
    
    def add_entry(self, channel_name, channel_url):
        """
        Add a channel to watch history
        """
        try:
            history = self._load_history()
            
            entry = {
                'channel_name': channel_name,
                'channel_url': channel_url,
                'watched_at': datetime.now().isoformat()
            }
            
            history.insert(0, entry)
            # Keep only last 50 entries
            history = history[:50]
            
            self._save_history(history)
        except Exception as e:
            xbmc.log(f'[BlazeTv History] Error adding entry: {str(e)}', xbmc.LOGWARNING)
    
    def get_history(self):
        """
        Get watch history
        """
        try:
            history = self._load_history()
            
            result = []
            for entry in history:
                result.append({
                    'channel': {
                        'name': entry.get('channel_name', ''),
                        'url': entry.get('channel_url', '')
                    },
                    'watched_at': entry.get('watched_at', '')
                })
            
            return result
        except Exception as e:
            xbmc.log(f'[BlazeTv History] Error getting history: {str(e)}', xbmc.LOGWARNING)
            return []
    
    def _load_history(self):
        """
        Load history from file
        """
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_history(self, history):
        """
        Save history to file
        """
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
