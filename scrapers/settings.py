BOT_NAME = "linkedin_saas_sniper"
SPIDER_MODULES = ["scrapers.spiders"]
NEWSPIDER_MODULE = "scrapers.spiders"

# Obey robots.txt (set to False for LinkedIn - they block scrapers in robots.txt)
ROBOTSTXT_OBEY = False

# User-Agent (rotate for stealth)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Logging
LOG_LEVEL = "INFO"