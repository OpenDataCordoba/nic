import re


class BotDetector:
    """
    Utility class for detecting bots and crawlers based on various signals
    """

    # Known bot user agents patterns
    BOT_PATTERNS = [
        # Search engine bots
        r'googlebot',
        r'bingbot',
        r'slurp',  # Yahoo
        r'duckduckbot',
        r'baiduspider',
        r'yandexbot',
        r'facebookexternalhit',
        r'twitterbot',
        r'linkedinbot',
        r'whatsapp',
        r'telegrambot',

        # SEO and monitoring bots
        r'ahrefsbot',
        r'semrushbot',
        r'mj12bot',
        r'dotbot',
        r'rogerbot',
        r'exabot',
        r'facebot',
        r'ia_archiver',

        # Other crawlers
        r'crawler',
        r'spider',
        r'scraper',
        r'bot\b',
        r'crawl',
        r'slurp',
        r'wget',
        r'curl',
        r'python-requests',
        r'python-urllib',
        r'scrapy',
        r'selenium',
        r'phantom',
        r'headless',

        # Specific bots from your logs
        r'barkrowler',
        r'petalbot',
        r'applebot',
        r'semrushbot',
    ]

    def __init__(self):
        self.bot_regex = re.compile('|'.join(self.BOT_PATTERNS), re.IGNORECASE)

    def detect_bot_by_user_agent(self, user_agent):
        """
        Detect if user agent belongs to a bot

        Returns:
            Tuple of (is_bot, bot_type)
        """
        if not user_agent:
            return False, None

        match = self.bot_regex.search(user_agent)
        if match:
            return True, match.group(0).lower()

        return False, None
