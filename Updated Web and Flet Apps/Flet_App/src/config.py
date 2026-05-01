"""
Configuration file for the UniSports app
Each team member can easily change the server IP without rebuilding
"""

import os
import socket
import json
from pathlib import Path

class ServerConfig:
    """Manage server connection settings"""
    
    DEFAULT_PORT = 8000
    
    def __init__(self, storage=None):
        """
        Args:
            storage: Optional storage object for saving IP persistently
                     (will be set by the app later)
        """
        self._storage = storage
        self._ip = None
    
    def set_storage(self, storage):
        """Set the storage object for persistent saving"""
        self._storage = storage
    
    def get_local_ip(self):
        """Auto-detect the local IP address of this computer"""
        try:
            # Create a socket to find the local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def get_base_url(self):
        """Get the full base URL for API calls"""
        ip = self.get_ip()
        return f"http://{ip}:{self.DEFAULT_PORT}"
    
    def get_ip(self):
        """Get the current server IP (saved or auto-detected)"""
        if self._ip:
            return self._ip
        
        # Try to load from storage (only if available)
        if self._storage is not None:
            try:
                saved = self._storage.get("server_ip")
                if saved:
                    self._ip = saved
                    return self._ip
            except Exception:
                pass  # Storage not available or error
        
        # Fallback to auto-detection
        return self.get_local_ip()
    
    def set_ip(self, ip):
        """Manually set the server IP"""
        self._ip = ip
        # Save to storage if available
        if self._storage is not None:
            try:
                self._storage.set("server_ip", ip)
            except Exception:
                pass  # Storage not available
        print(f"Server IP set to: {ip}")
    
    def reset_to_auto(self):
        """Reset to auto-detected IP"""
        self._ip = None
        if self._storage is not None:
            try:
                self._storage.remove("server_ip")
            except Exception:
                pass

# Create a global instance
server_config = ServerConfig()