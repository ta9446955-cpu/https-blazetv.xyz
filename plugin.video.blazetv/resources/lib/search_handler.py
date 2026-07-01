# -*- coding: utf-8 -*-
"""
Channel Search Handler
Provides search functionality for channels
"""

import xbmc
from difflib import SequenceMatcher


class SearchHandler:
    """Handle channel searching"""
    
    def __init__(self, m3u_parser):
        self.m3u_parser = m3u_parser
    
    def search(self, query):
        """
        Search for channels matching the query
        
        Args:
            query: Search string
            
        Returns:
            List of matching channels
        """
        if not query:
            return []
        
        # Parse playlist if not done yet
        channels = self.m3u_parser.get_channels()
        if not channels:
            self.m3u_parser.parse()
            channels = self.m3u_parser.get_channels()
        
        query_lower = query.lower()
        results = []
        
        for channel in channels:
            name = channel.get('name', '').lower()
            group = channel.get('group_title', '').lower()
            tvg_name = channel.get('tvg_name', '').lower()
            
            # Exact match gets highest priority
            if query_lower in name:
                results.append((channel, 3))  # Priority 3
            elif query_lower in group:
                results.append((channel, 2))  # Priority 2
            elif query_lower in tvg_name:
                results.append((channel, 1))  # Priority 1
            else:
                # Fuzzy match
                similarity = max(
                    self._similarity(query_lower, name),
                    self._similarity(query_lower, group),
                    self._similarity(query_lower, tvg_name)
                )
                if similarity > 0.6:  # 60% match threshold
                    results.append((channel, similarity))
        
        # Sort by priority (highest first)
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Return just the channels
        return [ch for ch, _ in results]
    
    @staticmethod
    def _similarity(str1, str2):
        """Calculate similarity between two strings (0-1)"""
        return SequenceMatcher(None, str1, str2).ratio()