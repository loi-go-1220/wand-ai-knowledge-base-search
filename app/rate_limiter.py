"""
Simple rate limiting for API endpoints
Prevents abuse and manages OpenAI API usage
"""

import time
from collections import defaultdict, deque
from typing import Dict, Optional

class SimpleRateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(deque)  # IP -> deque of timestamps
        self.window_size = 60  # 1 minute window
    
    def is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed for this client IP"""
        now = time.time()
        
        client_requests = self.requests[client_ip]
        while client_requests and client_requests[0] < now - self.window_size:
            client_requests.popleft()
        
        if len(client_requests) < self.requests_per_minute:
            client_requests.append(now)
            return True
        
        return False
    
    def get_reset_time(self, client_ip: str) -> Optional[float]:
        """Get when the rate limit will reset for this client"""
        client_requests = self.requests[client_ip]
        if not client_requests:
            return None
        
        return client_requests[0] + self.window_size
    
    def get_stats(self) -> Dict:
        """Get rate limiting statistics"""
        now = time.time()
        active_clients = 0
        total_recent_requests = 0
        
        for client_ip, requests in self.requests.items():
            recent_requests = sum(1 for req_time in requests if req_time > now - self.window_size)
            if recent_requests > 0:
                active_clients += 1
                total_recent_requests += recent_requests
        
        return {
            "active_clients": active_clients,
            "total_recent_requests": total_recent_requests,
            "requests_per_minute_limit": self.requests_per_minute,
            "window_size_seconds": self.window_size
        }

upload_limiter = SimpleRateLimiter(requests_per_minute=10)
general_limiter = SimpleRateLimiter(requests_per_minute=60)
