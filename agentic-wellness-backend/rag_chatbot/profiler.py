# profiler.py

import time
from functools import wraps
from contextlib import contextmanager
from typing import Dict, List
import threading

class PerformanceProfiler:
    """Thread-safe performance profiler for RAG pipeline"""
    
    def __init__(self):
        self._local = threading.local()
    
    @property
    def timings(self) -> Dict[str, float]:
        if not hasattr(self._local, 'timings'):
            self._local.timings = {}
        return self._local.timings
    
    @contextmanager
    def timer(self, stage_name: str, print_immediate: bool = True):
        """Context manager for timing code blocks"""
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = (time.perf_counter() - start) * 1000  # milliseconds
            self.timings[stage_name] = elapsed
            if print_immediate:
                print(f"⏱️  [{stage_name}] {elapsed:.2f}ms")
    
    def summary(self, title: str = "PERFORMANCE SUMMARY"):
        """Print detailed timing breakdown"""
        if not self.timings:
            return
        
        print("\n" + "="*70)
        print(f"📊 {title}")
        print("="*70)
        
        total = sum(self.timings.values())
        sorted_timings = sorted(self.timings.items(), key=lambda x: x[1], reverse=True)
        
        for stage, duration in sorted_timings:
            percentage = (duration / total * 100) if total > 0 else 0
            bar_length = int(percentage / 2)  # Max 50 chars
            bar = "█" * bar_length
            print(f"{stage:35s} {duration:8.2f}ms ({percentage:5.1f}%) {bar}")
        
        print("-"*70)
        print(f"{'TOTAL':35s} {total:8.2f}ms (100.0%)")
        print("="*70 + "\n")
        
        return self.timings
    
    def reset(self):
        """Clear current timings"""
        self.timings.clear()

# Global profiler instance
profiler = PerformanceProfiler()
