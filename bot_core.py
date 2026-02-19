#!/usr/bin/env python3
"""
SubX Twitter Bot Core - Multi-user support
Handles: Tweet scheduling, keyword monitoring, auto-replies, analytics
"""

import tweepy
import schedule
import time
import json
import random
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import re
from tweet_generator import generate_tweet
from credentials import CredentialManager
from user_manager import UserManager

# Load environment variables
load_dotenv()

# Default configuration (can be overridden per user)
DEFAULT_CONFIG = {
    'tweets_per_day': 6,
    'posting_times': ['16:00', '20:00', '00:00', '04:00', '08:00', '12:00'],
    'engagement_interval': 15,  # minutes between engagement scans
    'max_replies_per_hour': 5,
}

# Keywords to monitor (organized by topic)
KEYWORDS = {
    'betting': [
        'betting loss Nigeria',
        'lost money betting',
        'stop betting',
        'gambling addiction',
        'bet9ja losses',
        'sports betting',
        'sports betting waste',
        'betking loss',
        'sportybet loss',
        'bet9ja regret'
    ],
    'investment': [
        'how to invest Nigeria',
        'passive income Nigeria',
        'investment opportunities',
        'investment opportunities Nigeria',
        'where to invest',
        'where to invest Nigeria',
        'wealth building',
        'small money investment'
    ],
    'land': [
        'buy land Lagos',
        'buy land Abeokuta',
        'land ownership Nigeria',
        'affordable land',
        'affordable land Nigeria',
        'land investment',
        'real estate Lagos',
        'farmland Nigeria',
        'real estate investment Nigeria',
        'property investment Nigeria'
    ],
    'co_ownership': [
        'fractional ownership',
        'fractional ownership Nigeria',
        'co-ownership property',
        'shared ownership',
        'shared ownership real estate',
        'real estate syndication',
        'group land purchase'
    ]
}

# Reply templates by category
REPLY_TEMPLATES = {
    'betting': [
        "Lost ₦500k to betting this year? That same ₦500k could've bought you 14 units in Hidden Leaf Village. By next year, you'd be earning ₦192k annually instead of chasing losses. Stop betting on luck. Start investing in assets. @1Subx",
        "You've lost more money on Bet9ja than you think you have. ₦10k here. ₦20k there. Over 3 years? That's ₦500k-1M gone. What if you put that into land instead? ₦1M in 2 Seasons farmland = ₦200k+ annual returns after maturity. The house always wins. Be the house. @2seasonsabk",
        "Betting promises you ₦1M from ₦1k. Real estate gives you ₦1.8M from ₦350k in 5 years. One is gambling. One is investing. Choose better. @1Subx",
        "Every week you bet ₦5k and lose. That's ₦20k/month. ₦240k/year. In 2 years, that's ₦480k — enough to co-own income-generating real estate. Stop funding bookmakers. Start funding your future. Hidden Leaf Village: ₦35k per unit. DM to learn more. @1Subx",
        "Nigeria has more sports betting shops than hospitals. Let that sink in. You're not failing at betting. The system is designed for you to lose. Redirect that ₦10k/week into land ownership. @2seasonsabk makes it possible from ₦1.25M for 1,000 sqm farmland.",
        "If you've lost money betting, you're not alone. But here's the truth: You can't gamble your way to wealth. ₦35,000 in @1Subx = co-ownership in real estate that earns 39% annually. ₦35,000 in betting = 99% chance it's gone by Friday. Choose wisely.",
        "Betting addiction starts with \"just ₦1k.\" Then it's ₦5k. Then ₦20k. Then your salary. If you're reading this and it hurts, there's a better way. Take your next betting money and buy 1 unit of real estate instead. Start here: @1Subx You'll thank yourself in 5 years.",
        "You don't have a betting problem. You have an access problem. Betting is accessible (₦100 entry). Real estate isn't (₦10M+ entry). So you bet, hoping to win enough to invest. We fixed the access problem. @1Subx: Co-own real estate from ₦35k. No gambling required.",
        "Lost ₦200k betting this year? That's 5.7 units in Hidden Leaf Village. That's ₦78k annual passive income starting Year 2. That's ₦312k over 4 years + your ₦200k back. ₦512k total. Betting gave you ₦0. Stop losing. Start owning. @1Subx",
        "The bookmakers know something you don't: Real wealth isn't built by betting. It's built by owning assets. They use YOUR betting losses to buy land, properties, businesses. Join the other side. Own land. Earn income. Build wealth. @2seasonsabk @1Subx",
        "Betting loss Nigeria is becoming too common. If you've lost money betting, it's not discipline you lack — it's a broken system. Time to redirect risk into assets. @1Subx",
        "Lost money betting again? Betting loss Nigeria isn't bad luck, it's math working against you. Ownership beats odds every single time. @1Subx",
    ],
    'investment': [
        "\"How do I invest in Nigeria?\" Start here: ₦35,000 → 1 unit in Hidden Leaf Village. ₦350,000 → 10 units (₦138k/year passive income). ₦1.25M → 1,000 sqm farmland (₦200k+/year after maturity). Real assets. Real returns. Real documentation. @1Subx @2seasonsabk",
        "Passive income isn't a myth. It's just locked behind high entry barriers in Nigeria. ₦35M for a rental property? Out of reach. ₦35k for fractional ownership? Accessible. We're redesigning access. @1Subx: Co-own income-generating real estate from ₦35k.",
        "Everyone talks about \"investment opportunities in Nigeria.\" But nobody talks about entry size. You don't lack intelligence. You lack access to capital. We changed that: 1,000 people × ₦35k = ₦35M resort. Everyone earns. Everyone owns. That's @1Subx.",
        "Where to invest ₦500k in Nigeria: ❌ Fixed deposit: ₦50k/year (10%). ❌ Stocks: Volatile, risky. ✅ @1Subx: 14 units = ₦193k/year (39% return). ✅ @2seasonsabk: Farmland with immediate planting bonus. Choose wealth over safety.",
        "Wealth building in Nigeria isn't complicated. It's just gatekept. Most investments require ₦5M, ₦10M, ₦50M entry. @focalpointprop builds systems that let you start from ₦35k. Co-ownership. Group buying. Fractional participation. Access redesigned.",
        "You can't save your way to wealth in Nigeria. Inflation eats your savings faster than you can stack. But you CAN invest your way to wealth. ₦35k today → ₦90k in 5 years (@1Subx). ₦6.5M today → ₦1.5M/year after 4 years (@2seasonsabk farmland). Assets > Savings.",
        "\"Investment opportunities\" in Nigeria usually mean: Ponzi schemes, Forex \"experts\", Crypto pump & dumps, Real estate you can't afford. @1Subx is different: Real land. Real structure. Real returns. ₦35k entry. 39% projected annual return. No tricks. Just ownership.",
        "Passive income checklist: ✅ Requires capital: Yes (₦35k minimum). ✅ Requires work: No (we manage operations). ✅ Requires time: Yes (5-year commitment). ✅ Requires trust: Yes (transparent documentation). If you can check these boxes, @1Subx is for you. Quarterly income from Year 2.",
        "How to invest ₦100k in Nigeria: Option A: Keep in savings (loses value to inflation). Option B: Buy crypto (volatile, risky). Option C: Bet on sports (statistically, you lose). Option D: Buy 2.8 units @1Subx (₦38k annual return projected). Choose D.",
        "Investment is just deferred consumption. You give up ₦350k today. You receive ₦900k+ in 5 years. But only if you invest in ASSETS, not liabilities. @1Subx: Real estate co-ownership. @2seasonsabk: Farmland with income potential. Both = assets.",
    ],
    'land': [
        "\"I want to buy land in Lagos.\" Cool. You need ₦30-50M. \"I don't have ₦30M.\" Then you don't buy land in Lagos. That's the system. Until now. Group buying: Pool funds with 10-20 people. Buy land early. Exit together. @focalpointprop makes it possible.",
        "Land ownership in Nigeria is for the top 1%. Everyone else rents forever. Not because you don't work hard. But because entry size is ₦10M, ₦20M, ₦50M. We're building systems where 100 people can co-own what 1 person used to own alone. @2seasonsabk @1Subx",
        "Affordable land in Nigeria doesn't exist. What exists: Land you can't afford alone. Solution? Group buying. 10 people × ₦2M = ₦20M land purchase. Hold for 3 years → ₦40M. Everyone doubles their money. Same land. Smaller entry. @focalpointprop",
        "Land investment in Nigeria has one rule: Buy early. Hold long. Exit rich. But if you can't afford \"buy early,\" you're locked out. @2seasonsabk solves this: Farmland from ₦1.25M/1,000 sqm. Or co-own from ₦35k via @1Subx. Access redesigned.",
        "Real estate in Lagos prices out 99% of Nigerians. ₦30M for a plot. ₦100M for a house. Meanwhile, your rent is ₦1M/year. In 30 years, you've paid ₦30M and own nothing. @focalpointprop is building differently. Co-ownership. Group buying. Smaller entries.",
        "Farmland in Nigeria is the most underrated investment. ₦1.25M for 1,000 sqm at @2seasonsabk. Plant. Wait. Harvest. Plantains: ₦700k/year after maturity. Fruit trees: ₦800k/year after 4 years. ₦1.5M annual income from ₦6.5M investment (1 acre). That's 23% annual return. Passively.",
        "You don't need ₦50M to own land. You need: ₦35k for fractional ownership (@1Subx). ₦1.25M for 1,000 sqm farmland (@2seasonsabk). ₦2M for group land buying (@focalpointprop). Stop waiting for ₦50M. Start owning with what you have.",
        "Land ownership isn't reserved for the rich. It's just structured that way. ₦20M plot? Out of reach. ₦2M group contribution? Accessible. Same land. Different structure. @focalpointprop builds the structures that let you participate.",
        "Buy land in Lagos: ₦30-50M. Buy land in Ogun (@2seasonsabk): ₦1.25M+. \"But Lagos appreciates faster!\" True. But 0% of ₦30M (because you can't afford it) = ₦0. 100% of ₦1.25M = ownership + income + appreciation. Own something > own nothing.",
        "Farmland at @2seasonsabk isn't just land. It's: 1,000+ sqm of titled property. Income-generating asset (plantain, fruits). Inflation hedge. Generational wealth foundation. From ₦1.25M. Stop renting. Start owning.",
    ],
    'co_ownership': [
        "Fractional ownership sounds complicated. It's not. 10 people co-own a ₦35M resort. Each owns ₦3.5M worth. Each paid ₦350k. Resort earns ₦13.8M/year. You receive 1% = ₦138k/year. 39% return on your ₦350k. That's @1Subx. Simple.",
        "Co-ownership isn't \"poor man's real estate.\" It's smart capital allocation. Instead of 1 person owning 1 property... 1,000 people own 1 property. Everyone earns. Everyone benefits. Risk is distributed. Returns are proportional. @1Subx",
        "\"Do I own a physical room?\" No. \"Then what do I own?\" Economic participation. You own a share of the INCOME, not a specific space. Think: MTN shares. You don't own a cell tower. You own a % of MTN's profits. Same concept. Real estate. @1Subx",
        "Shared ownership of property isn't new. Rich Nigerians have done it privately for decades. We just made it: Transparent. Legal. Accessible (₦35k vs ₦35M). Structured (documented, managed). @1Subx = democratized co-ownership.",
        "Real estate syndication in Nigeria used to be: \"Oga, my uncle knows someone who knows someone...\" Now it's: @1Subx: Clear structure. Legal documentation. Transparent financials. ₦35k entry. No \"uncle.\" Just systems.",
        "Co-ownership property model: 1,000 people buy units at ₦35k each = ₦35M. Property built + operated professionally. Income distributed quarterly based on units owned. You manage nothing. You receive income. That's the model. @1Subx",
        "Fractional ownership removes 3 barriers: 1. Capital (₦35k vs ₦35M). 2. Management (we handle operations). 3. Risk (distributed across 1,000 people). You get the returns without the traditional burdens. @1Subx: Accessible real estate income.",
        "Why would I co-own when I could own alone? Because: Alone: You need ₦35M. You don't have it. You own nothing. Co-own: You have ₦35k. You own 0.1%. You earn ₦13,797/year. 0.1% ownership > 0% ownership. @1Subx",
        "Co-ownership isn't a compromise. It's optimization. Instead of: Saving 15 years for ₦35M. Managing property yourself. Bearing 100% of risk. You: Start today with ₦35k. Professional management included. Risk shared across 1,000 people. @1Subx",
        "Real estate syndication used to be: \"Only for accredited investors.\" @1Subx made it: \"For anyone with ₦35,000 and a 5-year vision.\" Ownership redesigned.",
    ]
}

# Engagement phrases to look for
ENGAGEMENT_TRIGGERS = [
    'want to invest',
    'how do I start',
    'need passive income',
    'tired of betting',
    'want to own land',
    'real estate advice',
    'investment tips',
    'where to put money'
]

# Ripple Effect Trigger Words and Replies
RIPPLE_TRIGGERS = {
    'nigeria development': [
        "You don't build Nigeria with slogans. You build it with land reform, housing access, infrastructure, and institutions that work. Development is policy made visible.",
        "A country that cannot organize land use and cities cannot organize economic growth. Real estate is development in concrete form."
    ],
    'government bad': [
        "Government is a reflection of the society it rules. Before elections, society already decided who it rewards with attention.",
        "If noise keeps winning attention, noise will keep winning power. Leadership doesn't emerge randomly."
    ],
    'leaders useless': [
        "Government is a reflection of the society it rules. Before elections, society already decided who it rewards with attention.",
        "If noise keeps winning attention, noise will keep winning power. Leadership doesn't emerge randomly."
    ],
    'politicians problem': [
        "Government is a reflection of the society it rules. Before elections, society already decided who it rewards with attention.",
        "If noise keeps winning attention, noise will keep winning power. Leadership doesn't emerge randomly."
    ],
    'inflation': [
        "Inflation is not just economics. It reflects weak planning, broken supply chains, land use failures, and poor governance.",
        "Ask any politician one question consistently: what caused food inflation? Repetition exposes preparation gaps faster than outrage."
    ],
    'food prices': [
        "Inflation is not just economics. It reflects weak planning, broken supply chains, land use failures, and poor governance.",
        "Ask any politician one question consistently: what caused food inflation? Repetition exposes preparation gaps faster than outrage."
    ],
    'cost of living': [
        "Inflation is not just economics. It reflects weak planning, broken supply chains, land use failures, and poor governance.",
        "Ask any politician one question consistently: what caused food inflation? Repetition exposes preparation gaps faster than outrage."
    ],
    'real estate nigeria': [
        "Real estate isn't about buildings. It's about law, trust, and long-term planning. Get land governance right and development follows.",
        "When property rights are unclear, investment slows and conflict grows. Housing policy is national security.",
        "Land ownership creates generational wealth. Buildings depreciate. Land appreciates. Choose the asset that grows.",
        "Real estate value comes from location, rights, and development—not just structures. Land is the foundation.",
        "Clear land titles = investment confidence. Unclear titles = conflict and stagnation. Governance matters."
    ],
    'land': [
        "When property rights are unclear, investment slows and conflict grows. Housing policy is national security.",
        "Land ownership creates generational wealth. Buildings depreciate. Land appreciates. Choose the asset that grows.",
        "Real estate value comes from location, rights, and development—not just structures. Land is the foundation.",
        "Clear land titles = investment confidence. Unclear titles = conflict and stagnation. Governance matters.",
        "Land appreciates. Buildings depreciate. Smart investors focus on the asset that grows in value.",
        "Property rights are the foundation of economic development. Without clear ownership, progress stalls."
    ],
    'housing': [
        "Housing policy is national security. When people can't afford homes, stability suffers.",
        "Clear land titles = investment confidence. Unclear titles = conflict and stagnation. Governance matters.",
        "Land ownership creates generational wealth. Buildings depreciate. Land appreciates. Choose the asset that grows.",
        "Real estate value comes from location, rights, and development—not just structures. Land is the foundation.",
        "Housing isn't just shelter—it's wealth building, stability, and economic participation.",
        "When housing is accessible, society thrives. When it's gatekept, inequality grows."
    ],
    'property': [
        "Property rights are the foundation of economic development. Without clear ownership, progress stalls.",
        "Land appreciates. Buildings depreciate. Smart investors focus on the asset that grows in value.",
        "Real estate value comes from location, rights, and development—not just structures. Land is the foundation.",
        "Clear land titles = investment confidence. Unclear titles = conflict and stagnation. Governance matters.",
        "When property rights are unclear, investment slows and conflict grows. Housing policy is national security.",
        "Land ownership creates generational wealth. Buildings depreciate. Land appreciates. Choose the asset that grows."
    ],
    'youth': [
        "Youth don't need motivation speeches. They need access to land, capital, skills, and systems that reward competence.",
        "A society that blocks youth from owning, renting, or building creates instability, not innovation."
    ],
    'nigerian youth': [
        "Youth don't need motivation speeches. They need access to land, capital, skills, and systems that reward competence.",
        "A society that blocks youth from owning, renting, or building creates instability, not innovation."
    ],
    'young people': [
        "Youth don't need motivation speeches. They need access to land, capital, skills, and systems that reward competence.",
        "A society that blocks youth from owning, renting, or building creates instability, not innovation."
    ],
    'unity': [
        "Unity doesn't come from pretending differences don't exist. It comes from fair systems that don't permanently exclude anyone.",
        "Many ethnic tensions are intensified by competition over land and housing. Clear land laws reduce conflict."
    ],
    'tribalism': [
        "Unity doesn't come from pretending differences don't exist. It comes from fair systems that don't permanently exclude anyone.",
        "Many ethnic tensions are intensified by competition over land and housing. Clear land laws reduce conflict."
    ],
    'ethnic issues': [
        "Unity doesn't come from pretending differences don't exist. It comes from fair systems that don't permanently exclude anyone.",
        "Many ethnic tensions are intensified by competition over land and housing. Clear land laws reduce conflict."
    ],
    'corruption': [
        "Corruption thrives where attention is emotional and data is absent. Visual evidence beats shouting.",
        "Take pictures of infrastructure. Tag officials. Build an archive. Facts are harder to escape than insults."
    ],
    'accountability': [
        "Corruption thrives where attention is emotional and data is absent. Visual evidence beats shouting.",
        "Take pictures of infrastructure. Tag officials. Build an archive. Facts are harder to escape than insults."
    ],
    'blogs': [
        "If media pages shared 60% educative content within their niche, productivity would rise quietly across society.",
        "Entertainment without education weakens society. Attention is currency—spend it deliberately."
    ],
    'media': [
        "If media pages shared 60% educative content within their niche, productivity would rise quietly across society.",
        "Entertainment without education weakens society. Attention is currency—spend it deliberately."
    ],
    'podcasts': [
        "If media pages shared 60% educative content within their niche, productivity would rise quietly across society.",
        "Entertainment without education weakens society. Attention is currency—spend it deliberately."
    ],
    'influencers': [
        "If media pages shared 60% educative content within their niche, productivity would rise quietly across society.",
        "Entertainment without education weakens society. Attention is currency—spend it deliberately."
    ],
    'elections': [
        "Elections work better when citizens already have data: roads, housing, projects, and outcomes—not promises.",
        "Voting is the final step. Civic behavior before elections determines the quality of options."
    ],
    'voting': [
        "Elections work better when citizens already have data: roads, housing, projects, and outcomes—not promises.",
        "Voting is the final step. Civic behavior before elections determines the quality of options."
    ],
    'pvc': [
        "Elections work better when citizens already have data: roads, housing, projects, and outcomes—not promises.",
        "Voting is the final step. Civic behavior before elections determines the quality of options."
    ],
    'inec': [
        "Elections work better when citizens already have data: roads, housing, projects, and outcomes—not promises.",
        "Voting is the final step. Civic behavior before elections determines the quality of options."
    ],
    'bbn': [
        "What society rewards eventually governs it. Fame is a rehearsal for power.",
        "Muting noise is not apathy. It's discipline."
    ],
    'viral drama': [
        "What society rewards eventually governs it. Fame is a rehearsal for power.",
        "Muting noise is not apathy. It's discipline."
    ],
    'skits': [
        "What society rewards eventually governs it. Fame is a rehearsal for power.",
        "Muting noise is not apathy. It's discipline."
    ],
    'outrage': [
        "What society rewards eventually governs it. Fame is a rehearsal for power.",
        "Muting noise is not apathy. It's discipline."
    ],
    'build': [
        "Looking to build with people who value alignment over ego. Partnerships work best when incentives are shared.",
        "The strongest outcomes come from collaboration, not control."
    ],
    'alignment': [
        "Looking to build with people who value alignment over ego. Partnerships work best when incentives are shared.",
        "The strongest outcomes come from collaboration, not control."
    ],
    'collaboration': [
        "Looking to build with people who value alignment over ego. Partnerships work best when incentives are shared.",
        "The strongest outcomes come from collaboration, not control."
    ],
    'shared': [
        "Looking to build with people who value alignment over ego. Partnerships work best when incentives are shared.",
        "The strongest outcomes come from collaboration, not control."
    ],
    'long-term': [
        "Joint ownership creates long-term thinking. Short-term wins matter less than shared outcomes.",
        "When everyone has skin in the game, execution gets sharper."
    ],
    'skin in the game': [
        "Joint ownership creates long-term thinking. Short-term wins matter less than shared outcomes.",
        "When everyone has skin in the game, execution gets sharper."
    ],
    'outcomes': [
        "Joint ownership creates long-term thinking. Short-term wins matter less than shared outcomes.",
        "When everyone has skin in the game, execution gets sharper."
    ],
    'ownership': [
        "Joint ownership creates long-term thinking. Short-term wins matter less than shared outcomes.",
        "When everyone has skin in the game, execution gets sharper."
    ],
    'trust': [
        "Not interested in transactional partnerships. Looking for trust, transparency, and shared responsibility.",
        "The best partnerships aren't loud — they're durable."
    ],
    'transparency': [
        "Not interested in transactional partnerships. Looking for trust, transparency, and shared responsibility.",
        "The best partnerships aren't loud — they're durable."
    ],
    'accountability': [
        "Not interested in transactional partnerships. Looking for trust, transparency, and shared responsibility.",
        "The best partnerships aren't loud — they're durable."
    ],
    'durable': [
        "Not interested in transactional partnerships. Looking for trust, transparency, and shared responsibility.",
        "The best partnerships aren't loud — they're durable."
    ],
    'operators': [
        "Building is easier when incentives point in the same direction. Exploring joint ownership models.",
        "Operators partnering with operators > vanity collaborations."
    ],
    'incentives': [
        "Building is easier when incentives point in the same direction. Exploring joint ownership models.",
        "Operators partnering with operators > vanity collaborations."
    ],
    'shared risk': [
        "Building is easier when incentives point in the same direction. Exploring joint ownership models.",
        "Operators partnering with operators > vanity collaborations."
    ],
    'upside': [
        "Building is easier when incentives point in the same direction. Exploring joint ownership models.",
        "Operators partnering with operators > vanity collaborations."
    ],
    'conversations': [
        "Always open to conversations with people who believe in partnership over hierarchy.",
        "If you're building something interesting and value shared ownership, let's compare notes."
    ],
    'compare notes': [
        "Always open to conversations with people who believe in partnership over hierarchy.",
        "If you're building something interesting and value shared ownership, let's compare notes."
    ],
    'contributes': [
        "Always open to conversations with people who believe in partnership over hierarchy.",
        "Exploring partnerships where everyone contributes and everyone owns the result."
    ]
}

# Ripple Effect general replies
RIPPLE_EFFECT_REPLIES = [
    "Ripple Effect theory: society trains its leaders long before elections. Change what we reward, and leadership quality changes over time.",
    "If 20% of Nigerians focus on productive discourse—agriculture, tech, real estate, governance—the system tilts.",
    "Nigeria doesn't lack ideas. It lacks execution, accountability, and civic discipline. Development begins when society changes what it celebrates."
]

# Community link for beautiful places posts
COMMUNITY_LINK = "https://x.com/i/communities/1951416110240149783"


class BotData:
    """Manages persistent bot data"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.user_dir = Path('users') / user_id
        self.user_dir.mkdir(parents=True, exist_ok=True)
        self.filepath = self.user_dir / 'bot_data.json'
        self.data = self.load()
    
    def load(self):
        """Load bot data from file"""
        if Path(self.filepath).exists():
            with open(self.filepath, 'r') as f:
                return json.load(f)
        return {
            'current_tweet_index': 0,
            'replied_tweets': [],
            'daily_stats': {},
            'total_tweets_posted': 0,
            'total_replies_sent': 0,
            'last_reset': datetime.now().strftime('%Y-%m-%d')
        }
    
    def save(self):
        """Save bot data to file"""
        with open(self.filepath, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def add_replied_tweet(self, tweet_id):
        """Track replied tweets (keep last 1000)"""
        self.data['replied_tweets'].append(str(tweet_id))
        if len(self.data['replied_tweets']) > 1000:
            self.data['replied_tweets'] = self.data['replied_tweets'][-1000:]
        self.save()
    
    def has_replied(self, tweet_id):
        """Check if we've already replied to this tweet"""
        return str(tweet_id) in self.data['replied_tweets']
    
    def increment_stat(self, stat_name):
        """Increment a statistic counter"""
        self.data[stat_name] = self.data.get(stat_name, 0) + 1
        
        # Daily stats
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.data['daily_stats']:
            self.data['daily_stats'][today] = {}
        self.data['daily_stats'][today][stat_name] = \
            self.data['daily_stats'][today].get(stat_name, 0) + 1
        
        self.save()
    
    def reset_daily_limits(self):
        """Reset rate limits daily"""
        today = datetime.now().strftime('%Y-%m-%d')
        if self.data['last_reset'] != today:
            self.data['last_reset'] = today
            self.save()
            return True
        return False


class TwitterBot:
    """Main bot class with multi-user support"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.data = BotData(user_id)
        self.tweet_queue = self.load_tweet_queue()
        
        # Load user configuration
        user_manager = UserManager()
        user_config = user_manager.get_user_config(user_id)
        self.config = {
            'tweets_per_day': user_config.get('tweets_per_day', DEFAULT_CONFIG['tweets_per_day']),
            'posting_times': user_config.get('posting_times', DEFAULT_CONFIG['posting_times']),
            'engagement_interval': user_config.get('engagement_interval', DEFAULT_CONFIG['engagement_interval']),
            'max_replies_per_hour': user_config.get('max_replies_per_hour', DEFAULT_CONFIG['max_replies_per_hour']),
            'keywords': user_config.get('keywords', {})
        }
        
        # Load user-specific reply templates
        self.reply_templates = self.load_reply_templates()
        
        # Load and initialize Twitter client
        self.client = self._initialize_client()
        
        # Setup scheduling
        self._setup_schedule()
    
    def _initialize_client(self):
        """Initialize Twitter client with user's credentials"""
        try:
            cred_manager = CredentialManager(self.user_id)
            credentials = cred_manager.load_credentials()
            
            return tweepy.Client(
                bearer_token=credentials.get('bearer_token', ''),
                consumer_key=credentials.get('api_key', ''),
                consumer_secret=credentials.get('api_secret', ''),
                access_token=credentials.get('access_token', ''),
                access_token_secret=credentials.get('access_token_secret', ''),
                wait_on_rate_limit=True
            )
        except Exception as e:
            print(f"❌ Error initializing Twitter client for {self.user_id}: {e}")
            raise
    
    def load_tweet_queue(self):
        """Load pre-written tweets from user-specific file"""
        queue_file = Path('users') / self.user_id / 'tweet_queue.json'
        if queue_file.exists():
            with open(queue_file, 'r') as f:
                return json.load(f)
        # Fallback to default queue if user-specific doesn't exist
        default_queue = Path('tweet_queue.json')
        if default_queue.exists():
            with open(default_queue, 'r') as f:
                return json.load(f)
        return []
    
    def load_reply_templates(self):
        """Load user-specific reply templates, fallback to defaults"""
        templates_file = Path('users') / self.user_id / 'reply_templates.json'
        if templates_file.exists():
            with open(templates_file, 'r') as f:
                return json.load(f)
        # Fallback to default templates
        return REPLY_TEMPLATES
    
    def _setup_schedule(self):
        """Setup scheduled tasks for this bot instance"""
        # Note: schedule uses a global scheduler, but each bot's methods
        # are bound to self, so they'll use the correct bot instance
        
        # Check for scheduled tweets every minute
        schedule.every(1).minutes.do(self.check_scheduled_tweets)
        
        # Schedule tweets
        for post_time in self.config['posting_times']:
            schedule.every().day.at(post_time).do(self.post_scheduled_tweet)
        
        # Schedule engagement scans
        schedule.every(self.config['engagement_interval']).minutes.do(self.search_and_engage)
        
        # Schedule Ripple Effect trigger searches (every 30 minutes)
        schedule.every(30).minutes.do(self.search_ripple_triggers)
        
        # Schedule economic news every 5 hours
        schedule.every().day.at("17:00").do(self.post_economic_news)
        schedule.every().day.at("22:00").do(self.post_economic_news)
        schedule.every().day.at("03:00").do(self.post_economic_news)
        schedule.every().day.at("08:00").do(self.post_economic_news)
        schedule.every().day.at("13:00").do(self.post_economic_news)
        
        # Schedule beautiful places posts (twice daily)
        schedule.every().day.at("10:00").do(self.post_beautiful_place)
        schedule.every().day.at("18:00").do(self.post_beautiful_place)
        
        # Schedule daily stats
        schedule.every().day.at("23:59").do(self.print_stats)
        schedule.every().day.at("00:01").do(self.data.reset_daily_limits)
    
    def check_scheduled_tweets(self):
        """Check for scheduled tweets that should be posted now"""
        scheduled_file = Path('users') / self.user_id / 'scheduled_tweets.json'
        if not scheduled_file.exists():
            return
        
        with open(scheduled_file, 'r') as f:
            scheduled_tweets = json.load(f)
        
        now = datetime.now()
        updated = False
        
        # Find tweets scheduled for this exact time (within 1 minute window)
        for scheduled in scheduled_tweets:
            if scheduled['status'] == 'pending':
                scheduled_dt_str = scheduled['datetime']
                # Parse scheduled datetime (format: "YYYY-MM-DD HH:MM")
                try:
                    scheduled_dt = datetime.strptime(scheduled_dt_str, '%Y-%m-%d %H:%M')
                    # Check if it's time to post (within 1 minute window)
                    time_diff = abs((now - scheduled_dt).total_seconds())
                    if time_diff <= 60:  # Within 1 minute
                        tweet_text = scheduled['tweet']
                        try:
                            response = self.client.create_tweet(text=tweet_text)
                            scheduled['status'] = 'posted'
                            scheduled['posted_at'] = now.strftime('%Y-%m-%d %H:%M:%S')
                            updated = True
                            self.data.increment_stat('total_tweets_posted')
                            print(f"✅ Posted scheduled tweet: {tweet_text[:50]}...")
                        except Exception as e:
                            print(f"❌ Error posting scheduled tweet: {e}")
                            scheduled['status'] = 'error'
                            scheduled['error'] = str(e)
                            updated = True
                except ValueError:
                    # Invalid datetime format, skip
                    continue
        
        if updated:
            with open(scheduled_file, 'w') as f:
                json.dump(scheduled_tweets, f, indent=2)
    
    def post_scheduled_tweet(self):
        """Post next tweet from queue or generate new one"""
        
        # Mix: 60% pre-written, 40% generated (to avoid repetition)
        use_generator = random.random() < 0.4
        
        if use_generator:
            # Generate a new tweet
            max_attempts = 10
            for attempt in range(max_attempts):
                try:
                    tweet_text = generate_tweet()
                    
                    # Check if we've posted something very similar recently
                    if 'posted_tweets' not in self.data.data:
                        self.data.data['posted_tweets'] = []
                    
                    # Check for exact duplicates and high similarity
                    is_duplicate = False
                    for posted in self.data.data['posted_tweets'][-100:]:  # Check last 100
                        if tweet_text == posted:
                            is_duplicate = True
                            break
                        # Check similarity (if 80%+ same words, consider duplicate)
                        words1 = set(tweet_text.lower().split())
                        words2 = set(posted.lower().split())
                        if len(words1) > 0 and len(words2) > 0:
                            similarity = len(words1 & words2) / max(len(words1), len(words2))
                            if similarity > 0.8:
                                is_duplicate = True
                                break
                    
                    if not is_duplicate:
                        break
                    
                    if attempt == max_attempts - 1:
                        # Fall back to queue if can't generate unique
                        use_generator = False
                        break
                except Exception as e:
                    print(f"⚠️  Error generating tweet: {e}")
                    use_generator = False
                    break
        else:
            # Use pre-written queue
            if not self.tweet_queue:
                print("❌ No tweets in queue!")
                return
            
            # Get current tweet with some randomization
            index = self.data.data['current_tweet_index']
            
            # 20% chance to skip ahead for more variety
            if random.random() < 0.2 and len(self.tweet_queue) > 10:
                skip = random.randint(1, min(5, len(self.tweet_queue) // 10))
                index = (index + skip) % len(self.tweet_queue)
            
            if index >= len(self.tweet_queue):
                index = 0  # Loop back to start
            
            tweet_text = self.tweet_queue[index]
            self.data.data['current_tweet_index'] = (index + 1) % len(self.tweet_queue)
        
        try:
            # Post tweet
            response = self.client.create_tweet(text=tweet_text)
            
            # Track posted tweets (keep last 200)
            if 'posted_tweets' not in self.data.data:
                self.data.data['posted_tweets'] = []
            self.data.data['posted_tweets'].append(tweet_text)
            if len(self.data.data['posted_tweets']) > 200:
                self.data.data['posted_tweets'] = self.data.data['posted_tweets'][-200:]
            
            self.data.increment_stat('total_tweets_posted')
            
            source = "GENERATED" if use_generator else f"QUEUE ({index + 1}/{len(self.tweet_queue)})"
            print(f"✅ Posted tweet ({source})")
            print(f"   Content: {tweet_text[:50]}...")
            
        except Exception as e:
            print(f"❌ Error posting tweet: {e}")
    
    def search_and_engage(self):
        """Search for keywords and engage with relevant tweets"""
        
        # Check rate limits
        today_stats = self.data.data['daily_stats'].get(
            datetime.now().strftime('%Y-%m-%d'), {}
        )
        replies_today = today_stats.get('total_replies_sent', 0)
        
        if replies_today >= self.config['max_replies_per_hour'] * 24:
            print(f"⚠️  Daily reply limit reached ({replies_today})")
            return
        
        keywords = self.config.get('keywords', {})
        if not keywords:
            # Fallback to default keywords if user config doesn't have them
            # KEYWORDS is already defined in this file
            keywords = KEYWORDS
        
        for category, keyword_list in keywords.items():
            for keyword in keyword_list:
                try:
                    # Search recent tweets
                    tweets = self.client.search_recent_tweets(
                        query=f"{keyword} -is:retweet -is:reply lang:en",
                        max_results=10,
                        tweet_fields=['created_at', 'author_id', 'public_metrics']
                    )
                    
                    if not tweets.data:
                        continue
                    
                    for tweet in tweets.data:
                        # Skip if already replied
                        if self.data.has_replied(tweet.id):
                            continue
                        
                        # Skip low-engagement accounts (likely bots)
                        # if tweet.public_metrics['followers_count'] < 50:
                        #     continue
                        
                        # Check if tweet contains engagement triggers or Ripple Effect triggers
                        tweet_text = tweet.text.lower()
                        is_relevant = any(
                            trigger in tweet_text 
                            for trigger in ENGAGEMENT_TRIGGERS
                        )
                        
                        # Check for Ripple Effect triggers
                        has_ripple_trigger = any(
                            trigger in tweet_text
                            for trigger in RIPPLE_TRIGGERS.keys()
                        )
                        
                        if is_relevant or has_ripple_trigger or random.random() < 0.3:  # 30% of all matches
                            self.reply_to_tweet(tweet.id, category, tweet.text)
                            time.sleep(120)  # 2 min between replies
                    
                    time.sleep(10)  # Pause between keyword searches
                    
                except Exception as e:
                    print(f"❌ Error searching '{keyword}': {e}")
                    time.sleep(60)
    
    def search_ripple_triggers(self):
        """Search for Ripple Effect trigger words and reply intelligently"""
        try:
            # Check rate limits
            today_stats = self.data.data['daily_stats'].get(
                datetime.now().strftime('%Y-%m-%d'), {}
            )
            replies_today = today_stats.get('total_replies_sent', 0)
            
            if replies_today >= self.config['max_replies_per_hour'] * 24:
                return
            
            # Search for key Ripple Effect triggers
            ripple_keywords = [
                'Nigeria development',
                'building Nigeria',
                'nation building',
                'government bad',
                'leaders useless',
                'politicians problem',
                'inflation Nigeria',
                'food prices',
                'cost of living',
                'real estate Nigeria',
                'youth Nigeria',
                'unity Nigeria',
                'corruption Nigeria'
            ]
            
            for keyword in random.sample(ripple_keywords, min(3, len(ripple_keywords))):  # Search 3 random ones
                try:
                    tweets = self.client.search_recent_tweets(
                        query=f"{keyword} -is:retweet -is:reply lang:en",
                        max_results=5,
                        tweet_fields=['created_at', 'author_id', 'public_metrics', 'text']
                    )
                    
                    if not tweets.data:
                        continue
                    
                    for tweet in tweets.data:
                        if self.data.has_replied(tweet.id):
                            continue
                        
                        tweet_text_lower = tweet.text.lower()
                        
                        # Check for matching Ripple trigger
                        for trigger, replies in RIPPLE_TRIGGERS.items():
                            if trigger in tweet_text_lower:
                                # Initialize reply tracking if needed
                                if 'recent_replies' not in self.data.data:
                                    self.data.data['recent_replies'] = []
                                
                                # Filter out recently used replies (last 50)
                                recent_replies = self.data.data['recent_replies'][-50:]
                                unused_replies = [r for r in replies if r not in recent_replies]
                                
                                # If all replies were used recently, use all available (but shuffle)
                                if not unused_replies:
                                    unused_replies = replies.copy()
                                    random.shuffle(unused_replies)
                                
                                reply_text = random.choice(unused_replies)
                                
                                # Track this reply
                                self.data.data['recent_replies'].append(reply_text)
                                if len(self.data.data['recent_replies']) > 100:  # Keep last 100
                                    self.data.data['recent_replies'] = self.data.data['recent_replies'][-100:]
                                self.data.save()
                                
                                try:
                                    self.client.create_tweet(
                                        text=reply_text,
                                        in_reply_to_tweet_id=tweet.id
                                    )
                                    
                                    self.data.add_replied_tweet(tweet.id)
                                    self.data.increment_stat('total_replies_sent')
                                    
                                    print(f"✅ Ripple reply to tweet {tweet.id}")
                                    print(f"   Trigger: {trigger}")
                                    print(f"   Reply: {reply_text[:50]}...")
                                    
                                    time.sleep(180)  # 3 min between Ripple replies
                                    break  # Only one reply per tweet
                                    
                                except Exception as e:
                                    print(f"❌ Error replying: {e}")
                        
                        time.sleep(10)
                    
                    time.sleep(30)  # Pause between keyword searches
                    
                except Exception as e:
                    print(f"❌ Error searching Ripple triggers '{keyword}': {e}")
                    time.sleep(60)
                    
        except Exception as e:
            print(f"❌ Error in search_ripple_triggers: {e}")
    
    def reply_to_tweet(self, tweet_id, category, tweet_text=""):
        """Reply to a specific tweet with duplicate prevention"""
        
        # Initialize reply tracking if needed
        if 'recent_replies' not in self.data.data:
            self.data.data['recent_replies'] = []
        
        # Check for Ripple Effect triggers first
        reply_text = None
        available_replies = []
        
        if tweet_text:
            tweet_lower = tweet_text.lower()
            for trigger, replies in RIPPLE_TRIGGERS.items():
                if trigger in tweet_lower:
                    available_replies = replies
                    break
        
        # Fall back to category-based replies
        if not available_replies:
            available_replies = self.reply_templates.get(category, self.reply_templates.get('land', []))
        
        # Filter out recently used replies (last 50)
        recent_replies = self.data.data['recent_replies'][-50:]
        unused_replies = [r for r in available_replies if r not in recent_replies]
        
        # If all replies were used recently, use all available (but shuffle)
        if not unused_replies:
            unused_replies = available_replies.copy()
            random.shuffle(unused_replies)
        
        # Select reply
        reply_text = random.choice(unused_replies)
        
        # Track this reply
        self.data.data['recent_replies'].append(reply_text)
        if len(self.data.data['recent_replies']) > 100:  # Keep last 100
            self.data.data['recent_replies'] = self.data.data['recent_replies'][-100:]
        self.data.save()
        
        try:
            self.client.create_tweet(
                text=reply_text,
                in_reply_to_tweet_id=tweet_id
            )
            
            self.data.add_replied_tweet(tweet_id)
            self.data.increment_stat('total_replies_sent')
            
            print(f"✅ Replied to tweet {tweet_id}")
            print(f"   Category: {category}")
            print(f"   Reply: {reply_text[:50]}...")
            
        except Exception as e:
            print(f"❌ Error replying to {tweet_id}: {e}")
    
    def auto_like_mentions(self):
        """Like tweets mentioning @1Subx or related terms"""
        try:
            # Get mentions (requires user context auth)
            # This is a placeholder - you'll need to implement with user context
            print("ℹ️  Auto-like feature requires additional OAuth setup")
            
        except Exception as e:
            print(f"❌ Error in auto-like: {e}")
    
    def post_economic_news(self):
        """Fetch and post economic news from NGX Group"""
        try:
            print("📰 Fetching economic news from NGX...")
            
            # Fetch news from NGX Group
            url = "https://ngxgroup.com"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find news articles (adjust selectors based on actual site structure)
            news_items = []
            
            # Look for common news patterns
            for article in soup.find_all(['article', 'div'], class_=re.compile(r'news|article|post|update', re.I)):
                title_elem = article.find(['h1', 'h2', 'h3', 'h4', 'a'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href') or article.find('a', href=True)
                    if link and isinstance(link, dict):
                        link = link.get('href', '')
                    elif hasattr(link, 'get'):
                        link = link.get('href', '')
                    else:
                        link = str(link) if link else ''
                    
                    if title and len(title) > 20:
                        news_items.append({
                            'title': title[:200],
                            'link': link if link.startswith('http') else f"{url}{link}" if link else url
                        })
            
            # If no structured news found, try alternative approach
            if not news_items:
                # Look for any headlines
                for heading in soup.find_all(['h1', 'h2', 'h3']):
                    text = heading.get_text(strip=True)
                    if len(text) > 30 and any(word in text.lower() for word in ['stock', 'market', 'ngx', 'index', 'trading', 'equity']):
                        news_items.append({
                            'title': text[:200],
                            'link': url
                        })
            
            if news_items:
                # Select a random news item
                news = random.choice(news_items[:5])  # Take first 5 to avoid stale news
                
                tweet_text = f"📊 {news['title']}\n\n{news['link']}"
                
                # Post tweet
                response = self.client.create_tweet(text=tweet_text)
                
                self.data.increment_stat('total_tweets_posted')
                print(f"✅ Posted economic news")
                print(f"   Title: {news['title'][:50]}...")
                print(f"   Tweet ID: {response.data['id']}")
            else:
                # Fallback: post general market update
                tweet_text = f"📊 Nigerian Stock Market Update\n\nStay informed about NGX market movements: {url}\n\n#NGX #NigeriaStocks"
                response = self.client.create_tweet(text=tweet_text)
                self.data.increment_stat('total_tweets_posted')
                print(f"✅ Posted general market update")
                
        except Exception as e:
            print(f"❌ Error posting economic news: {e}")
            # Fallback tweet
            try:
                tweet_text = f"📊 Nigerian Stock Market News\n\nFollow market updates: https://ngxgroup.com\n\n#NGX #NigeriaStocks"
                self.client.create_tweet(text=tweet_text)
                self.data.increment_stat('total_tweets_posted')
            except:
                pass
    
    def post_beautiful_place(self):
        """Search for and post beautiful places around the world"""
        try:
            print("🌍 Searching for beautiful places...")
            
            # List of beautiful places with descriptions
            beautiful_places = [
                {
                    'name': 'Santorini, Greece',
                    'description': 'White-washed buildings against blue Aegean waters',
                    'image_url': 'https://images.unsplash.com/photo-1613395877344-13d4a8e0d49e',
                    'source': 'https://unsplash.com/s/photos/santorini'
                },
                {
                    'name': 'Bali, Indonesia',
                    'description': 'Tropical paradise with rice terraces and temples',
                    'image_url': 'https://images.unsplash.com/photo-1518548419970-58e3b4079ab2',
                    'source': 'https://unsplash.com/s/photos/bali'
                },
                {
                    'name': 'Maldives',
                    'description': 'Crystal clear waters and overwater bungalows',
                    'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4',
                    'source': 'https://unsplash.com/s/photos/maldives'
                },
                {
                    'name': 'Swiss Alps',
                    'description': 'Majestic mountains and pristine lakes',
                    'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4',
                    'source': 'https://unsplash.com/s/photos/swiss-alps'
                },
                {
                    'name': 'Iceland',
                    'description': 'Northern lights and dramatic landscapes',
                    'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4',
                    'source': 'https://unsplash.com/s/photos/iceland'
                },
                {
                    'name': 'Machu Picchu, Peru',
                    'description': 'Ancient Incan citadel in the clouds',
                    'image_url': 'https://images.unsplash.com/photo-1526392060635-9d6019884377',
                    'source': 'https://unsplash.com/s/photos/machu-picchu'
                },
                {
                    'name': 'Bora Bora, French Polynesia',
                    'description': 'Turquoise lagoons and luxury resorts',
                    'image_url': 'https://images.unsplash.com/photo-1544551763-46a013bb70d5',
                    'source': 'https://unsplash.com/s/photos/bora-bora'
                },
                {
                    'name': 'Kyoto, Japan',
                    'description': 'Traditional temples and cherry blossoms',
                    'image_url': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e',
                    'source': 'https://unsplash.com/s/photos/kyoto'
                }
            ]
            
            # Select a random place
            place = random.choice(beautiful_places)
            
            # Create tweet text
            tweet_text = f"🌍 {place['name']}\n\n{place['description']}\n\nJoin our community to discover more beautiful places:\n{COMMUNITY_LINK}\n\n📸 {place['source']}"
            
            # Post tweet (without image for now - requires media upload API)
            # To add images later, use tweepy media upload
            response = self.client.create_tweet(text=tweet_text)
            
            self.data.increment_stat('total_tweets_posted')
            print(f"✅ Posted beautiful place: {place['name']}")
            print(f"   Tweet ID: {response.data['id']}")
            
        except Exception as e:
            print(f"❌ Error posting beautiful place: {e}")
    
    def print_stats(self):
        """Print bot statistics"""
        print("\n" + "="*50)
        print("📊 BOT STATISTICS")
        print("="*50)
        print(f"Total tweets posted: {self.data.data['total_tweets_posted']}")
        print(f"Total replies sent: {self.data.data['total_replies_sent']}")
        print(f"Current queue position: {self.data.data['current_tweet_index']}/{len(self.tweet_queue)}")
        
        # Today's stats
        today = datetime.now().strftime('%Y-%m-%d')
        today_stats = self.data.data['daily_stats'].get(today, {})
        print(f"\nToday ({today}):")
        for key, value in today_stats.items():
            print(f"  {key}: {value}")
        print("="*50 + "\n")


    def initialize(self):
        """Initialize bot - print stats, check missed times, run initial scan"""
        print(f"🤖 SubX Twitter Bot Started for user {self.user_id}")
        print(f"📅 Scheduled tweets: {self.config['posting_times']}")
        print(f"🔍 Engagement scans: Every {self.config['engagement_interval']} minutes")
        print(f"💬 Max replies/hour: {self.config['max_replies_per_hour']}")
        print()
    
    # Print initial stats
        self.print_stats()
    
    # Check if we missed any scheduled times today and post if needed
    now = datetime.now()
    current_time = now.strftime('%H:%M')
    current_hour = now.hour
    current_minute = now.minute
    
    print(f"⏰ Current time: {current_time}")
    
    # Check if any scheduled times have passed today
    missed_times = []
        for post_time in self.config['posting_times']:
        hour, minute = map(int, post_time.split(':'))
        # If scheduled time has passed today, we missed it
        if hour < current_hour or (hour == current_hour and minute <= current_minute):
            missed_times.append(post_time)
    
    if missed_times:
        print(f"⚠️  Missed scheduled times today: {missed_times}")
        print("📝 Posting now to catch up...")
            self.post_scheduled_tweet()
        print("✅ Caught up!\n")
    
    # Run initial engagement scan
    print("🔍 Running initial engagement scan...")
        self.search_and_engage()
