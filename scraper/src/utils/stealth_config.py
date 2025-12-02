"""
Ultra-Advanced stealth configuration for undetectable scraping
"""
import random
import time
import hashlib
from typing import Dict, List, Tuple
from collections import defaultdict
from datetime import datetime, timedelta


class StealthConfig:
    """Ultra-advanced configuration for stealth scraping to avoid detection"""

    # 2024 User Agents - Latest versions with realistic fingerprints
    USER_AGENTS = [
        # Chrome 120-124 on Windows 10/11
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        # Chrome on macOS Sonoma/Ventura
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        # Edge on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
        # Firefox ESR and regular
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:125.0) Gecko/20100101 Firefox/125.0",
        # Safari on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
        # Chrome on Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    ]

    # Realistic screen resolutions by frequency of usage
    SCREEN_RESOLUTIONS = [
        (1920, 1080, 35),   # 35% - Most common
        (1366, 768, 20),    # 20% - Laptops
        (1536, 864, 10),    # 10% - Scaled laptops
        (1440, 900, 8),     # 8% - MacBooks
        (1280, 720, 7),     # 7% - HD
        (2560, 1440, 8),    # 8% - QHD
        (3840, 2160, 5),    # 5% - 4K
        (1680, 1050, 4),    # 4% - WSXGA+
        (1280, 1024, 3),    # 3% - Legacy
    ]

    # Realistic color depths
    COLOR_DEPTHS = [24, 32]

    # Realistic timezones (Argentina focused)
    TIMEZONES = [
        "America/Argentina/Buenos_Aires",
        "America/Argentina/Cordoba",
        "America/Argentina/Mendoza",
    ]

    @classmethod
    def get_browser_fingerprint(cls, user_agent: str) -> Dict:
        """Generate a consistent browser fingerprint based on user agent"""
        # Create hash for consistency
        ua_hash = int(hashlib.md5(user_agent.encode()).hexdigest(), 16)

        # Determine browser type
        is_chrome = "Chrome" in user_agent and "Edg" not in user_agent
        is_edge = "Edg" in user_agent
        is_firefox = "Firefox" in user_agent
        is_safari = "Safari" in user_agent and "Chrome" not in user_agent
        is_mac = "Mac" in user_agent
        is_windows = "Windows" in user_agent
        is_linux = "Linux" in user_agent

        # Extract version
        if is_chrome or is_edge:
            version = user_agent.split("Chrome/")[1].split(" ")[0] if "Chrome/" in user_agent else "124.0.0.0"
        elif is_firefox:
            version = user_agent.split("Firefox/")[1].split(" ")[0] if "Firefox/" in user_agent else "125.0"
        else:
            version = "17.4"

        major_version = version.split(".")[0]

        return {
            "is_chrome": is_chrome,
            "is_edge": is_edge,
            "is_firefox": is_firefox,
            "is_safari": is_safari,
            "is_mac": is_mac,
            "is_windows": is_windows,
            "is_linux": is_linux,
            "version": version,
            "major_version": major_version,
            "ua_hash": ua_hash,
        }

    @classmethod
    def get_headers(cls, user_agent: str) -> Dict[str, str]:
        """Generate ultra-realistic headers based on user agent"""
        fp = cls.get_browser_fingerprint(user_agent)

        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }

        # Chrome/Edge specific headers with correct version
        if fp["is_chrome"] or fp["is_edge"]:
            brand = "Google Chrome" if fp["is_chrome"] else "Microsoft Edge"
            platform = '"Windows"' if fp["is_windows"] else ('"macOS"' if fp["is_mac"] else '"Linux"')

            headers.update({
                "sec-ch-ua": f'"Chromium";v="{fp["major_version"]}", "Not_A Brand";v="8", "{brand}";v="{fp["major_version"]}"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": platform,
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
            })

        # Firefox specific
        elif fp["is_firefox"]:
            headers.update({
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
            })

        return headers

    @staticmethod
    def get_random_user_agent() -> str:
        """Get a weighted random user agent (Chrome more common)"""
        weights = []
        for ua in StealthConfig.USER_AGENTS:
            if "Chrome" in ua and "Edg" not in ua:
                weights.append(3)  # Chrome 3x more likely
            elif "Firefox" in ua:
                weights.append(2)  # Firefox 2x
            else:
                weights.append(1)  # Others 1x

        return random.choices(StealthConfig.USER_AGENTS, weights=weights, k=1)[0]

    @staticmethod
    def get_viewport_size() -> Tuple[int, int]:
        """Get a weighted realistic viewport size"""
        resolutions = StealthConfig.SCREEN_RESOLUTIONS
        weights = [r[2] for r in resolutions]
        selected = random.choices(resolutions, weights=weights, k=1)[0]

        # Add small random offset for uniqueness
        width = selected[0] + random.randint(-5, 5)
        height = selected[1] + random.randint(-5, 5)

        return (width, height)

    @staticmethod
    def get_delay(min_seconds: float = 2.0, max_seconds: float = 5.0) -> float:
        """Get human-like delay with realistic distribution"""
        # Use log-normal distribution (more realistic for human timing)
        mean = (min_seconds + max_seconds) / 2
        sigma = 0.5

        delay = random.lognormvariate(0, sigma) * mean / 1.65
        delay = max(min_seconds, min(max_seconds, delay))

        # Add micro-variations
        delay += random.uniform(-0.1, 0.1)

        return max(0.1, delay)

    @staticmethod
    def get_reading_delay() -> float:
        """Simulate realistic content reading time"""
        # Humans read ~200-300 words per minute
        # Average article section = 2-4 seconds to skim
        return random.lognormvariate(1.0, 0.5)  # ~3s average with variance

    @staticmethod
    def get_typing_delay() -> float:
        """Get realistic typing delay between characters"""
        # Average typing speed: 40-60 WPM = 200-300ms per character
        return random.gauss(0.12, 0.04)

    @staticmethod
    def should_add_mouse_movement() -> bool:
        """80% chance of mouse movement (very natural)"""
        return random.random() < 0.80

    @staticmethod
    def should_add_scroll() -> bool:
        """90% chance of scrolling (almost everyone scrolls)"""
        return random.random() < 0.90

    @staticmethod
    def should_pause_reading() -> bool:
        """40% chance to pause and 'read' content"""
        return random.random() < 0.40

    @staticmethod
    def get_mouse_movement_count() -> int:
        """Get realistic number of mouse movements"""
        return random.randint(3, 8)

    @staticmethod
    def get_scroll_behavior() -> Dict:
        """Get ultra-realistic scroll behavior"""
        return {
            "smooth": True,
            "delay_ms": random.randint(50, 200),
            "scroll_amount": random.randint(100, 500),
            "scroll_count": random.randint(2, 6),
            "pause_probability": 0.3,
            "pause_duration": random.uniform(0.5, 2.0),
        }


class RateLimiter:
    """Intelligent rate limiter with domain-aware throttling"""

    def __init__(self, requests_per_minute: int = 10, burst_limit: int = 3):
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.request_times: Dict[str, List[datetime]] = defaultdict(list)
        self.min_delay_seconds = 60.0 / requests_per_minute
        self.domain_penalties: Dict[str, float] = {}  # Track domains that show resistance

    def extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc

    def add_penalty(self, url: str, penalty_seconds: float = 30.0):
        """Add delay penalty for a domain (when we detect resistance)"""
        domain = self.extract_domain(url)
        self.domain_penalties[domain] = self.domain_penalties.get(domain, 0) + penalty_seconds

    async def wait_if_needed(self, url: str):
        """Smart waiting with adaptive delays"""
        import asyncio

        domain = self.extract_domain(url)
        now = datetime.now()

        # Clean old requests
        cutoff = now - timedelta(minutes=1)
        self.request_times[domain] = [t for t in self.request_times[domain] if t > cutoff]

        # Check penalty
        if domain in self.domain_penalties and self.domain_penalties[domain] > 0:
            penalty = self.domain_penalties[domain]
            await asyncio.sleep(penalty)
            self.domain_penalties[domain] = max(0, penalty - 10)  # Reduce penalty over time

        # Check rate limit
        if len(self.request_times[domain]) >= self.requests_per_minute:
            oldest_request = min(self.request_times[domain])
            time_to_wait = 60.0 - (now - oldest_request).total_seconds()
            if time_to_wait > 0:
                wait_with_jitter = time_to_wait + StealthConfig.get_delay(1.0, 3.0)
                await asyncio.sleep(wait_with_jitter)

        # Check burst limit (no more than N requests in quick succession)
        recent_burst = [t for t in self.request_times[domain] if (now - t).total_seconds() < 5]
        if len(recent_burst) >= self.burst_limit:
            await asyncio.sleep(StealthConfig.get_delay(2.0, 5.0))

        # Minimum delay between requests
        if self.request_times[domain]:
            last_request = max(self.request_times[domain])
            time_since_last = (now - last_request).total_seconds()
            if time_since_last < self.min_delay_seconds:
                wait_time = self.min_delay_seconds - time_since_last
                await asyncio.sleep(wait_time + StealthConfig.get_delay(0.5, 1.5))

        self.request_times[domain].append(datetime.now())

    def get_stats(self, url: str) -> Dict:
        """Get rate limiting stats"""
        domain = self.extract_domain(url)
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        recent = [t for t in self.request_times[domain] if t > cutoff]

        return {
            "domain": domain,
            "requests_last_minute": len(recent),
            "limit": self.requests_per_minute,
            "penalty": self.domain_penalties.get(domain, 0),
            "utilization": f"{len(recent) / self.requests_per_minute * 100:.1f}%",
        }


class StealthBrowser:
    """Ultra-realistic browser behavior simulation"""

    @staticmethod
    async def human_type(page, selector: str, text: str):
        """Type with human-like timing and occasional mistakes"""
        import asyncio

        await page.focus(selector)

        for i, char in enumerate(text):
            # Occasional typo (2% chance) - type wrong then correct
            if random.random() < 0.02 and i < len(text) - 1:
                wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                await page.keyboard.type(wrong_char)
                await asyncio.sleep(random.uniform(0.1, 0.3))
                await page.keyboard.press('Backspace')
                await asyncio.sleep(random.uniform(0.05, 0.15))

            await page.keyboard.type(char)

            # Variable delay - faster for common letter sequences
            delay = StealthConfig.get_typing_delay()
            if char in ' .,!?':  # Pause slightly at punctuation
                delay *= 1.5
            await asyncio.sleep(delay)

    @staticmethod
    async def human_scroll(page, partial: bool = False):
        """Scroll like a human - variable speed, pauses, direction changes"""
        import asyncio

        config = StealthConfig.get_scroll_behavior()

        try:
            total_height = await page.evaluate("document.body.scrollHeight")
            viewport_height = await page.evaluate("window.innerHeight")
        except:
            return

        current_position = 0
        target_position = total_height if not partial else total_height * random.uniform(0.3, 0.7)

        while current_position < target_position:
            # Variable scroll amount
            scroll_amount = random.randint(100, 400)

            # Sometimes scroll up a bit (like re-reading)
            if random.random() < 0.1 and current_position > 200:
                await page.evaluate(f"window.scrollBy(0, -{random.randint(50, 150)})")
                await asyncio.sleep(random.uniform(0.3, 0.8))

            await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            current_position += scroll_amount

            # Variable delay between scrolls
            await asyncio.sleep(config["delay_ms"] / 1000.0 + random.uniform(0, 0.2))

            # Pause to "read" content
            if StealthConfig.should_pause_reading():
                await asyncio.sleep(StealthConfig.get_reading_delay())

            # Occasionally stop scrolling early
            if random.random() < 0.05:
                break

    @staticmethod
    async def random_mouse_movement(page, natural: bool = True):
        """Ultra-realistic mouse movements with Bezier curves"""
        import asyncio
        import math

        try:
            viewport = await page.viewport_size()
            if not viewport:
                return
        except:
            return

        # Start from a realistic position (not exact center)
        current_x = viewport["width"] * random.uniform(0.3, 0.7)
        current_y = viewport["height"] * random.uniform(0.3, 0.7)

        moves = random.randint(2, 5)

        for _ in range(moves):
            # Target areas that humans typically look at
            target_zones = [
                (0.2, 0.8, 0.1, 0.3),   # Top content area
                (0.1, 0.9, 0.3, 0.7),   # Main content
                (0.1, 0.5, 0.7, 0.9),   # Bottom left (often nav)
            ]
            zone = random.choice(target_zones)

            target_x = viewport["width"] * random.uniform(zone[0], zone[1])
            target_y = viewport["height"] * random.uniform(zone[2], zone[3])

            # Bezier curve movement
            steps = random.randint(10, 25)

            # Control points for bezier curve
            ctrl_x = current_x + (target_x - current_x) * random.uniform(0.3, 0.7) + random.uniform(-50, 50)
            ctrl_y = current_y + (target_y - current_y) * random.uniform(0.3, 0.7) + random.uniform(-50, 50)

            for step in range(steps):
                t = step / steps
                # Quadratic Bezier curve
                x = (1-t)**2 * current_x + 2*(1-t)*t * ctrl_x + t**2 * target_x
                y = (1-t)**2 * current_y + 2*(1-t)*t * ctrl_y + t**2 * target_y

                # Add micro-tremor (human hands shake slightly)
                x += random.gauss(0, 0.5)
                y += random.gauss(0, 0.5)

                # Clamp to viewport
                x = max(0, min(viewport["width"] - 1, x))
                y = max(0, min(viewport["height"] - 1, y))

                try:
                    await page.mouse.move(int(x), int(y))
                except:
                    pass

                # Variable speed (slower at start and end)
                speed_factor = math.sin(t * math.pi)  # Slow-fast-slow
                await asyncio.sleep(0.01 + 0.02 * (1 - speed_factor))

            current_x, current_y = target_x, target_y

            # Pause between movements
            await asyncio.sleep(random.uniform(0.1, 0.4))

            # Sometimes click (5% chance)
            if random.random() < 0.05:
                try:
                    await page.mouse.click(int(current_x), int(current_y))
                    await asyncio.sleep(random.uniform(0.2, 0.5))
                except:
                    pass

    @staticmethod
    async def stealth_page_load(page, url: str, wait_for_content: bool = True):
        """Load page with complete human-like behavior"""
        import asyncio

        # Navigate
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            # Retry with longer timeout
            await page.goto(url, wait_until="load", timeout=90000)

        # Initial pause (looking at page)
        await asyncio.sleep(StealthConfig.get_delay(1.5, 3.0))

        # Mouse movement (looking around)
        if StealthConfig.should_add_mouse_movement():
            await StealthBrowser.random_mouse_movement(page)

        # Scroll behavior
        if StealthConfig.should_add_scroll():
            await StealthBrowser.human_scroll(page, partial=True)

        # Final reading pause
        await asyncio.sleep(StealthConfig.get_reading_delay())

        return True
