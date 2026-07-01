# -*- coding: utf-8 -*-
"""
EPG (Electronic Program Guide) Handler
Manages program guide data and schedule information
"""

import xbmc
import os
import requests
from datetime import datetime, timedelta


class EPGHandler:
    """Handle EPG data for channels"""
    
    def __init__(self, config):
        self.config = config
        self.epg_data = {}
        self.last_update = None
    
    def fetch_epg(self, force_refresh=False):
        """
        Fetch EPG data
        You can extend this to fetch from XMLTV sources or APIs
        """
        cache_file = os.path.join(self.config.get_cache_dir(), 'epg_cache.json')
        
        # Check cache validity
        if not force_refresh and self.config.is_cache_valid(cache_file):
            xbmc.log('[BlazeTv] Using cached EPG data')
            self.epg_data = self.config.load_json('epg_cache.json', {})
            return True
        
        try:
            xbmc.log('[BlazeTv] Fetching EPG data...')
            # Placeholder for actual EPG source
            # You can integrate with:
            # - XMLTV format
            # - TuneIn API
            # - Custom EPG API
            
            # For now, we'll create a basic structure
            self.epg_data = self._generate_placeholder_epg()
            
            # Cache the data
            self.config.save_json('epg_cache.json', self.epg_data)
            self.last_update = datetime.now()
            
            xbmc.log('[BlazeTv] EPG data updated successfully')
            return True
        except Exception as e:
            xbmc.log(f'[BlazeTv] Failed to fetch EPG data: {str(e)}', xbmc.LOGWARNING)
            # Try to load cached version
            self.epg_data = self.config.load_json('epg_cache.json', {})
            return bool(self.epg_data)
    
    def get_channel_epg(self, channel_name):
        """Get EPG info for a specific channel"""
        if not self.epg_data:
            self.fetch_epg()
        
        return self.epg_data.get(channel_name, {})
    
    def get_channel_schedule(self, channel_name, days=7):
        """Get upcoming schedule for a channel"""
        epg = self.get_channel_epg(channel_name)
        schedule = epg.get('schedule', [])
        
        # Filter to requested days
        current_time = datetime.now()
        end_time = current_time + timedelta(days=days)
        
        filtered = []
        for program in schedule:
            try:
                prog_time = datetime.fromisoformat(program.get('start', ''))
                if current_time <= prog_time <= end_time:
                    filtered.append(program)
            except (ValueError, TypeError):
                continue
        
        return filtered
    
    def _generate_placeholder_epg(self):
        """Generate placeholder EPG data"""
        # This is a placeholder structure
        # In production, this would fetch real EPG data
        return {}
    
    def clear_cache(self):
        """Clear EPG cache"""
        cache_file = os.path.join(self.config.get_cache_dir(), 'epg_cache.json')
        try:
            if os.path.exists(cache_file):
                os.remove(cache_file)
            self.epg_data = {}
            return True
        except Exception as e:
            xbmc.log(f'[BlazeTv] Error clearing EPG cache: {str(e)}')
            return False