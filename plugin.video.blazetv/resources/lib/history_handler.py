# -*- coding: utf-8 -*-
"""
Playback History Handler
Tracks watched channels and playback history
"""

import xbmc
from datetime import datetime, timedelta
import os


class HistoryHandler:
    """Handle channel playback history"""
    
    def __init__(self, config):
        self.config = config
        self.history_file = 'history.json'
    
    def add_entry(self, channel_name, channel_url):
        """
        Add a channel to watch history
        
        Args:
            channel_name: Name of the channel
            channel_url: URL of the channel stream
        """
        try:
            history = self.config.load_json(self.history_file, [])
            
            # Remove duplicate if it exists (to move it to top)
            history = [h for h in history if h.get('name') != channel_name]
            
            # Add new entry to the top
            entry = {
                'name': channel_name,
                'url': channel_url,
                'watched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'timestamp': datetime.now().isoformat()
            }
            
            history.insert(0, entry)
            
            # Keep only specified number of days of history
            max_age_days = self.config.get('history_days', 30)
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            history = [
                h for h in history
                if datetime.fromisoformat(h.get('timestamp', '')) > cutoff_date
            ]
            
            # Save updated history
            self.config.save_json(self.history_file, history)
            xbmc.log(f'[BlazeTv] Added to history: {channel_name}')
            return True
        except Exception as e:
            xbmc.log(f'[BlazeTv] Error adding to history: {str(e)}', xbmc.LOGWARNING)
            return False
    
    def get_history(self, limit=None):
        """
        Get watch history
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of history entries
        """
        try:
            history = self.config.load_json(self.history_file, [])
            
            if limit:
                history = history[:limit]
            
            # Convert to channel-like format
            result = []
            for entry in history:
                result.append({
                    'channel': {
                        'name': entry.get('name', 'Unknown'),
                        'url': entry.get('url', ''),
                    },
                    'watched_at': entry.get('watched_at', '')
                })
            
            return result
        except Exception as e:
            xbmc.log(f'[BlazeTv] Error getting history: {str(e)}', xbmc.LOGWARNING)
            return []
    
    def clear_history(self):
        """Clear all watch history"""
        try:
            self.config.save_json(self.history_file, [])
            xbmc.log('[BlazeTv] History cleared')
            return True
        except Exception as e:
            xbmc.log(f'[BlazeTv] Error clearing history: {str(e)}')
            return False