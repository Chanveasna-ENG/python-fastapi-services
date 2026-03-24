import socket
import ipaddress
from urllib.parse import urlparse


def is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        
        hostname = parsed.hostname
        if not hostname:
            return False

        # Get all possible IP addresses for this host (v4 and v6)
        # This prevents DNS Rebinding and handles IPv6-only sites
        addr_info = socket.getaddrinfo(hostname, None)
        
        for info in addr_info:
            ip_str = info[4][0]
            ip = ipaddress.ip_address(ip_str)

            # If ANY resolved IP is internal/private, the whole URL is unsafe
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return False
            
        return True
    except (socket.gaierror, ValueError):
        return False