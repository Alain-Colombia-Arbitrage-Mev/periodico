"""
Advanced stealth configuration for undetectable scraping
"""
import random
import time
from typing import Dict, List, Tuple
from collections import defaultdict
from datetime import datetime, timedelta


class StealthConfig:
    """Advanced configuration for stealth scraping to avoid detection"""

    # Expanded pool of realistic user agents with more variety
    USER_AGENTS = [
        # Chrome on Windows (latest versions)
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        # Chrome on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        # Edge on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        # Firefox on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        # Firefox on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.6; rv:123.0) Gecko/20100101 Firefox/123.0",
        # Safari on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    ]

    # Realistic browser headers that match the user agent
    @staticmethod
    def get_headers(user_agent: str) -> Dict[str, str]:
        """Generate realistic headers based on user agent"""
        is_chrome = "Chrome" in user_agent and "Edg" not in user_agent
        is_edge = "Edg" in user_agent
        is_firefox = "Firefox" in user_agent

        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        # Chrome/Edge specific headers
        if is_chrome or is_edge:
            headers.update({
                "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"' if is_chrome else '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
            })

        return headers

    @staticmethod
    def get_random_user_agent() -> str:
        """Get a random user agent from the pool"""
        return random.choice(StealthConfig.USER_AGENTS)

    @staticmethod
    def get_viewport_size() -> Tuple[int, int]:
        """Get a realistic viewport size (varies slightly to appear human)"""
        base_widths = [1920, 1366, 1440, 1536, 2560]
        base_heights = [1080, 768, 900, 864, 1440]

        # Pick a common resolution and add small random offset
        width = random.choice(base_widths) + random.randint(-10, 10)
        # Height proportional to width with some variation
        height = random.choice(base_heights) + random.randint(-10, 10)

        return (width, height)

    @staticmethod
    def get_delay(min_seconds: float = 2.0, max_seconds: float = 5.0) -> float:
        """
        Get a random delay with jitter to mimic human behavior (advanced)

        Args:
            min_seconds: Minimum delay
            max_seconds: Maximum delay

        Returns:
            Delay in seconds with realistic human-like distribution
        """
        # Use normal distribution for more realistic timing (humans don't have uniform delays)
        mean = (min_seconds + max_seconds) / 2
        std_dev = (max_seconds - min_seconds) / 4
        
        # Generate delay with normal distribution
        delay = random.gauss(mean, std_dev)
        
        # Clamp to min/max bounds
        delay = max(min_seconds, min(max_seconds, delay))
        
        # Add micro-jitter for extra realism
        micro_jitter = random.uniform(-0.05, 0.05)
        
        return delay + micro_jitter
    
    @staticmethod
    def get_reading_delay() -> float:
        """Get delay that simulates human reading time (longer, more variable)"""
        # Humans read at different speeds, so longer delays with more variance
        return random.gauss(3.5, 1.5)  # Mean 3.5s, std dev 1.5s

    @staticmethod
    def should_add_mouse_movement() -> bool:
        """Randomly decide if we should simulate mouse movement (50% chance for more realism)"""
        return random.random() < 0.5
    
    @staticmethod
    def should_add_scroll() -> bool:
        """Randomly decide if we should scroll (70% chance - most humans scroll)"""
        return random.random() < 0.7
    
    @staticmethod
    def get_mouse_movement_count() -> int:
        """Get realistic number of mouse movements (humans move mouse frequently)"""
        return random.randint(2, 6)  # More movements for realism

    @staticmethod
    def get_scroll_behavior() -> Dict[str, any]:
        """Get realistic scroll behavior parameters"""
        return {
            "smooth": True,
            "delay_ms": random.randint(100, 300),
            "scroll_amount": random.randint(200, 800),
        }


class RateLimiter:
    """Rate limiter per domain to avoid overwhelming servers"""

    def __init__(self, requests_per_minute: int = 10):
        """
        Initialize rate limiter

        Args:
            requests_per_minute: Maximum requests per minute per domain
        """
        self.requests_per_minute = requests_per_minute
        self.request_times: Dict[str, List[datetime]] = defaultdict(list)
        self.min_delay_seconds = 60.0 / requests_per_minute

    def extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc

    async def wait_if_needed(self, url: str):
        """Wait if rate limit is exceeded for this domain"""
        import asyncio

        domain = self.extract_domain(url)
        now = datetime.now()

        # Clean old requests (older than 1 minute)
        cutoff = now - timedelta(minutes=1)
        self.request_times[domain] = [
            t for t in self.request_times[domain] if t > cutoff
        ]

        # Check if we need to wait
        if len(self.request_times[domain]) >= self.requests_per_minute:
            # Calculate time to wait
            oldest_request = min(self.request_times[domain])
            time_to_wait = 60.0 - (now - oldest_request).total_seconds()

            if time_to_wait > 0:
                # Add some jitter to make it less predictable
                wait_with_jitter = time_to_wait + StealthConfig.get_delay(0.5, 2.0)
                await asyncio.sleep(wait_with_jitter)

        # Check minimum delay between requests
        if self.request_times[domain]:
            last_request = max(self.request_times[domain])
            time_since_last = (now - last_request).total_seconds()

            if time_since_last < self.min_delay_seconds:
                wait_time = self.min_delay_seconds - time_since_last
                # Add jitter
                wait_with_jitter = wait_time + StealthConfig.get_delay(0.2, 0.8)
                await asyncio.sleep(wait_with_jitter)

        # Record this request
        self.request_times[domain].append(datetime.now())

    def get_stats(self, url: str) -> Dict[str, any]:
        """Get rate limiting stats for a domain"""
        domain = self.extract_domain(url)
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)

        recent_requests = [
            t for t in self.request_times[domain] if t > cutoff
        ]

        return {
            "domain": domain,
            "requests_last_minute": len(recent_requests),
            "limit": self.requests_per_minute,
            "utilization": f"{len(recent_requests) / self.requests_per_minute * 100:.1f}%",
        }


class StealthBrowser:
    """Helper class for stealth browser operations"""

    @staticmethod
    async def human_type(page, selector: str, text: str):
        """Type text with human-like delays"""
        import asyncio

        await page.focus(selector)
        for char in text:
            await page.keyboard.type(char)
            # Random delay between keystrokes (50-150ms)
            await asyncio.sleep(random.uniform(0.05, 0.15))

    @staticmethod
    async def human_scroll(page):
        """Scroll page like a human would"""
        import asyncio

        scroll_config = StealthConfig.get_scroll_behavior()

        # Scroll down in chunks
        total_height = await page.evaluate("document.body.scrollHeight")
        current_position = 0

        while current_position < total_height:
            scroll_amount = scroll_config["scroll_amount"]
            await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            current_position += scroll_amount

            # Random delay between scrolls
            await asyncio.sleep(scroll_config["delay_ms"] / 1000.0)

            # Sometimes pause longer (reading content)
            if random.random() < 0.3:
                await asyncio.sleep(random.uniform(1.0, 3.0))

    @staticmethod
    async def random_mouse_movement(page):
        """Simulate realistic random mouse movements with curves"""
        import asyncio

        viewport = await page.viewport_size()
        if not viewport:
            return

        # Get current mouse position (or start from center)
        current_x = viewport["width"] // 2
        current_y = viewport["height"] // 2

        # Move mouse in smooth curves (more human-like)
        moves = random.randint(2, 4)
        
        for _ in range(moves):
            # Target position
            target_x = random.randint(0, viewport["width"])
            target_y = random.randint(0, viewport["height"])
            
            # Move in steps to create smooth curve
            steps = random.randint(5, 10)
            for step in range(steps):
                # Bezier-like interpolation
                t = step / steps
                # Add some randomness to the curve
                curve_factor = random.uniform(0.3, 0.7)
                x = current_x + (target_x - current_x) * t + random.uniform(-10, 10) * curve_factor
                y = current_y + (target_y - current_y) * t + random.uniform(-10, 10) * curve_factor
                
                # Clamp to viewport
                x = max(0, min(viewport["width"], x))
                y = max(0, min(viewport["height"], y))
                
                await page.mouse.move(int(x), int(y))
                await asyncio.sleep(random.uniform(0.05, 0.15))
            
            current_x = target_x
            current_y = target_y
            
            # Pause between movements
            await asyncio.sleep(random.uniform(0.2, 0.5))

    @staticmethod
    async def stealth_page_load(page, url: str):
        """Load page with stealth behaviors"""
        import asyncio

        # Navigate to page
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Wait a bit (simulate reading)
        await asyncio.sleep(StealthConfig.get_delay(2, 4))

        # Sometimes scroll
        if random.random() < 0.5:
            await StealthBrowser.human_scroll(page)

        # Sometimes move mouse
        await StealthBrowser.random_mouse_movement(page)

        # Wait a bit more
        await asyncio.sleep(StealthConfig.get_delay(1, 3))
