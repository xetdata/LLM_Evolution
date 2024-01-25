import time
from threading import Lock
import sys
import random

class RateLimiter:
    def __init__(self):
        self.rate_limit_lock = Lock()
        self.next_query_time = time.time()
        self.query_spacing = 0.1
        self.total_query_spacing_for_rate_limited_requests = 0.0
        self.num_rate_limited_requests = 0

        # Seed this with a basic one. 
        self.total_query_spacing_for_successful_requests = 0.1
        self.num_successful_requests = 1

        self.last_query_spacing_adjustment = time.time()

    def register_successful(self, spacing): 
        if time.time() - self.last_query_spacing_adjustment > 5.0:
            self.last_query_spacing_adjustment = time.time()
            self.query_spacing = max(0.9 * self.query_spacing, self.min_query_spacing())

        self.total_query_spacing_for_successful_requests += spacing
        self.num_successful_requests += 1

    def register_rate_limited(self, spacing): 

        if time.time() - self.last_query_spacing_adjustment > 5.0:
            # Chill for a bit
            self.next_query_time = time.time() + random.uniform(5.0, 10.0) 
            self.last_query_spacing_adjustment = time.time()
            successful_average = (self.total_query_spacing_for_successful_requests / max(1, self.num_successful_requests))
            self.query_spacing = max(successful_average, 1.5 * self.query_spacing)

        self.total_query_spacing_for_rate_limited_requests += spacing
        self.num_rate_limited_requests += 1

    def min_query_spacing(self):

        rate_limited_average = (self.total_query_spacing_for_rate_limited_requests / max(1, self.num_rate_limited_requests))
        successful_average = (self.total_query_spacing_for_successful_requests/ max(1, self.num_successful_requests))

        # A 10% buffer off of the average query spacing when things been gotten bad, but then also take into account what's 
        # been working
        return max(1.1 * rate_limited_average, 0.5 * (rate_limited_average + successful_average))

    def wait_to_go(self):
        with self.rate_limit_lock: 
            current_query_spacing = self.query_spacing
            remaining_time = self.next_query_time - time.time()  
            if remaining_time > 0:
                if remaining_time >= 1.0:
                    sys.stderr.write('D')
                    sys.stderr.flush()
                time.sleep(remaining_time)
            self.next_query_time = time.time() + self.query_spacing

        return current_query_spacing

        
