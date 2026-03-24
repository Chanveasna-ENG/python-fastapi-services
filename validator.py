import socket
import ipaddress
from urllib.parse import urlparse


def is_safe_url(url: str) -> bool:
    """Validates that a URL does not point to an internal or restricted IP address."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        
        hostname = parsed.hostname
        if not hostname:
            return False

        # Resolve the domain to an IP address
        ip_str = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(ip_str)

        # Block private (e.g., 192.168.X.X), loopback (127.0.0.1), and link-local IPs
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            return False
            
        return True
    except (socket.gaierror, ValueError):
        # Fails closed if the hostname cannot be resolved or IP is invalid
        return False