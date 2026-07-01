#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Search Handler for BlazeTv Addon
"""

import xbmc

class SearchHandler:
    """
    Handle channel search functionality
    """
    
    def __init__(self, m3u_parser):
        self.m3u_parser = m3u_parser
    
    def search(self, query):
        """
        Search for channels by name or category
        """
        try:
            channels = self.m3u_parser.get_channels()
            query_lower = query.lower()
            
            results = []
            for channel in channels:
                name = channel.get('name', '').lower()
                category = channel.get('group_title', '').lower()
                
                if query_lower in name or query_lower in category:
                    results.append(channel)
            
            return results
        except Exception as e:
            xbmc.log(f'[BlazeTv Search] Error searching: {str(e)}', xbmc.LOGWARNING)
            return []
