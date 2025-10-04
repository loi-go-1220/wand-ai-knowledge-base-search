"""
System monitoring and metrics collection
Tracks performance and usage statistics
"""

import time
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict, deque

class SystemMonitor:
    """Simple monitoring system for tracking API usage and performance"""
    
    def __init__(self):
        self.request_counts = defaultdict(int)
        self.response_times = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.start_time = datetime.now()
        
        self.max_response_times = 100
    
    def record_request(self, endpoint: str, response_time: float, status_code: int):
        """Record API request metrics"""
        self.request_counts[endpoint] += 1
        
        if endpoint not in self.response_times:
            self.response_times[endpoint] = deque(maxlen=self.max_response_times)
        
        self.response_times[endpoint].append(response_time)
        
        if status_code >= 400:
            self.error_counts[endpoint] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        uptime = datetime.now() - self.start_time
        
        avg_response_times = {}
        for endpoint, times in self.response_times.items():
            if times:
                avg_response_times[endpoint] = sum(times) / len(times)
        
        return {
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_formatted": str(uptime).split('.')[0],  # Remove microseconds
            "total_requests": sum(self.request_counts.values()),
            "requests_by_endpoint": dict(self.request_counts),
            "average_response_times": avg_response_times,
            "error_counts": dict(self.error_counts),
            "error_rate": self._calculate_error_rate(),
            "most_used_endpoint": self._get_most_used_endpoint(),
            "slowest_endpoint": self._get_slowest_endpoint()
        }
    
    def _calculate_error_rate(self) -> float:
        """Calculate overall error rate"""
        total_requests = sum(self.request_counts.values())
        total_errors = sum(self.error_counts.values())
        
        if total_requests == 0:
            return 0.0
        
        return round((total_errors / total_requests) * 100, 2)
    
    def _get_most_used_endpoint(self) -> str:
        """Get the most frequently used endpoint"""
        if not self.request_counts:
            return "None"
        
        return max(self.request_counts.items(), key=lambda x: x[1])[0]
    
    def _get_slowest_endpoint(self) -> str:
        """Get the endpoint with highest average response time"""
        if not self.response_times:
            return "None"
        
        avg_times = {}
        for endpoint, times in self.response_times.items():
            if times:
                avg_times[endpoint] = sum(times) / len(times)
        
        if not avg_times:
            return "None"
        
        return max(avg_times.items(), key=lambda x: x[1])[0]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health indicators"""
        stats = self.get_stats()
        
        high_error_rate = 10.0
        slow_response_time = 5.0 
        
        health_issues = []
        
        if stats["error_rate"] > high_error_rate:
            health_issues.append(f"High error rate: {stats['error_rate']}%")
        
        for endpoint, avg_time in stats["average_response_times"].items():
            if avg_time > slow_response_time:
                health_issues.append(f"Slow endpoint {endpoint}: {avg_time:.2f}s avg")
        
        return {
            "status": "healthy" if not health_issues else "degraded",
            "issues": health_issues,
            "uptime": stats["uptime_formatted"],
            "total_requests": stats["total_requests"],
            "error_rate": f"{stats['error_rate']}%"
        }

monitor = SystemMonitor()
