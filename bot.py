#!/usr/bin/env python3
"""
SubX Twitter Bot - Automated Scheduling & Engagement
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
from difflib import SequenceMatcher

# Load environment variables
load_dotenv()

# Twitter API credentials (from .env file)
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')

# Initialize Twitter client
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    wait_on_rate_limit=True
)

# Configuration
CONFIG = {
    'tweets_per_day': 24,  # Hourly tweets
    'posting_times': [f'{i:02d}:00' for i in range(24)],  # Every hour (00:00 to 23:00)
    'engagement_interval': 60,  # minutes between engagement scans (reduced frequency to avoid spam)
    'max_replies_per_hour': 2,  # Reduced from 5 to avoid spam flags
    'max_replies_per_day': 20,  # Daily limit to prevent spam
    'data_file': 'bot_data.json'
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
        'small money investment',
        'Nigeria tax laws',
        'tax planning Nigeria',
        'investor tax',
        'tax breaks Nigeria',
        'investment incentives',
        'corporate tax relief',
        'Nigeria tax incentives',
        'tax efficiency',
        'legal tax reduction',
        'production incentives',
        'real sector investment'
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
        'property investment Nigeria',
        'property rights Nigeria',
        'land registration',
        'collateral value',
        'untitled land',
        'economic loss',
        'dead capital',
        'register land',
        'agriculture Nigeria',
        'agribusiness incentives',
        'food security policy',
        'pioneer status',
        'agro-processing incentives',
        'government policy support',
        'investment risk',
        'GDP contribution',
        'sector data',
        'import duty incentive',
        'tariff breaks',
        'tax holiday Nigeria',
        'agric investment support',
        'tax-free loans',
        'jobs creation',
        'investment reform'
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

# Reply templates by category - Educational and helpful, not salesy
REPLY_TEMPLATES = {
    'betting': [
        "The math of betting: Bookmakers set odds with a built-in margin (usually 5-10%). Over time, this guarantees they profit. It's not about luck—it's about probability. The house edge means long-term losses for bettors.",
        "Understanding betting psychology: The occasional win reinforces the behavior, even when losses outweigh gains. This is called 'variable ratio reinforcement'—the same mechanism slot machines use.",
        "Betting vs investing: Betting transfers wealth from you to the bookmaker. Investing transfers wealth from the economy to you. One is zero-sum (you win, they lose). One is positive-sum (both can grow).",
        "The true cost of betting isn't just the money lost. It's opportunity cost—what that money could have become if invested in appreciating assets over the same period.",
        "Why betting feels accessible: Low entry barriers (₦100) make it seem democratic. But the exit barriers (consistent losses) make it expensive. Real wealth-building often requires higher entry but lower long-term cost.",
        "Betting companies aren't in the prediction business. They're in the probability business. They don't need to be right—they just need the math to work in their favor over time.",
        "The 'near miss' in betting is designed to keep you playing. Losing by one goal feels like you were close, but a loss is a loss. This psychological trick costs bettors millions annually.",
        "If you track your betting over 6 months honestly, you'll likely find you've lost more than you think. Small losses (₦5k here, ₦10k there) compound into significant amounts without feeling significant.",
        "The accessibility paradox: Betting is accessible because it's designed to extract value. Real investments often have higher barriers because they're designed to create value. Understanding this changes your strategy.",
        "Betting loss isn't a character flaw—it's math. The system is designed so most participants lose. Recognizing this is the first step toward redirecting that risk tolerance into asset-building.",
        "The psychology of 'one more bet': After losses, the brain seeks to recover (loss aversion). This often leads to larger bets, chasing losses, and deeper holes. It's a predictable pattern.",
        "Betting companies use your money to buy assets (land, stocks, businesses). They're essentially pooling your losses into their investments. Understanding this dynamic helps you see the alternative path.",
    ],
    'investment': [
        "Investment basics: An asset is something that puts money in your pocket. A liability takes money out. Your car? Liability (depreciates, costs money). Land? Asset (appreciates, can generate income). Focus on acquiring assets.",
        "The power of compound interest: ₦100k at 15% annual return becomes ₦200k in ~5 years, ₦400k in ~10 years. Time is your greatest asset in investing. Start early, even with small amounts.",
        "Understanding risk vs return: Higher potential returns usually mean higher risk. But 'risk' isn't just volatility—it's also the risk of not keeping up with inflation. Sometimes 'safe' investments are risky in real terms.",
        "Investment diversification: Don't put all your money in one asset class. Real estate, stocks, bonds, and alternative investments each serve different purposes in a portfolio. Balance is key.",
        "The inflation trap: If inflation is 28% and your savings earn 5%, you're losing 23% of purchasing power annually. This is why 'safe' savings can be risky. Assets that appreciate with or above inflation protect wealth.",
        "Passive income requires upfront work: Either you work to build systems (businesses, rental properties) or you work to accumulate capital to buy into existing systems. There's no truly passive path—just delayed gratification.",
        "Investment entry barriers exist for a reason: High minimums often indicate institutional-grade opportunities. But they also exclude many people. Understanding this helps you evaluate alternative structures (co-ownership, fractional shares, etc.).",
        "The difference between speculation and investment: Speculation bets on price movements. Investment bets on underlying value creation. Real estate can be either—buying for quick flips is speculation; buying for long-term income is investment.",
        "Due diligence in investing: Always ask: Where does the return come from? If it's not clear, it's likely unsustainable. Real assets generate returns from real economic activity (rent, crops, business profits).",
        "Investment psychology: Fear and greed drive poor decisions. Having a clear strategy and sticking to it (regardless of emotions) is what separates successful investors from those who lose money.",
        "The time value of money: ₦100k today is worth more than ₦100k next year because of inflation and opportunity cost. This is why delaying investment decisions has a real cost.",
        "Asset allocation matters more than individual picks: A balanced portfolio of mediocre assets often outperforms a concentrated bet on one 'great' asset. Diversification reduces risk without necessarily reducing returns.",
        "Many Nigerians fear tax, but smart investors study it. Nigeria tax laws reward production more than consumption—especially in real sectors. Understanding tax incentives can significantly improve investment returns.",
        "Tax breaks in Nigeria exist, but only for those operating formally. Incentives don't reward noise—they reward structure, compliance, and scale. Formalization unlocks access to tax benefits.",
        "Tax is not the enemy of wealth—ignorance is. Nigeria tax incentives reduce liability legally for investors who understand the system. Knowledge of tax law is an investment advantage.",
        "Tax breaks Nigeria are designed to encourage production, not speculation. If your income depends on real output, the system quietly works in your favor. Production-based investments get preferential treatment.",
        "Under Nigeria's new tax law, new agribusinesses can get up to 5 years of income tax exemption—a major break for crop, livestock, dairy, and cocoa processing startups. Policy supports real sector growth.",
        "The Economic Development Tax Incentive (EDTI) offers ~5% annual tax credit for up to 5 years on qualifying capital expenditure—replacing the old Pioneer Status system. This rewards productive investment.",
        "In 2022 the Federal Government granted about ₦1.8 trillion in tax incentives to businesses, including VAT exemptions and pioneer incentives—a huge slice aimed at growth, not giveaways. The system rewards structured investment.",
    ],
    'land': [
        "Why land appreciates: It's a finite resource with growing demand. As population increases and urbanization expands, well-located land becomes scarcer. This creates natural appreciation pressure over time.",
        "Land vs buildings: Buildings depreciate (they age, need maintenance, become outdated). Land appreciates (location value increases with development). Smart investors focus on the appreciating component.",
        "The power of location: Land value comes from what's around it—infrastructure, development, economic activity. Buying land before these factors arrive (but when they're planned) captures maximum appreciation.",
        "Land title clarity matters: Clear, documented ownership reduces risk and increases value. Unclear titles create legal uncertainty that depresses prices and limits investment. Always verify documentation.",
        "Urbanization and land value: As cities expand, land on the periphery becomes more valuable. Understanding development patterns helps identify areas with appreciation potential before prices reflect it.",
        "Land as an inflation hedge: When currency loses value, real assets (like land) maintain purchasing power. This is why land ownership has historically preserved wealth during high inflation periods.",
        "The entry barrier problem: Traditional land ownership requires large capital (₦10M-₦50M+). This excludes most people. Alternative structures (co-ownership, fractional shares) can lower barriers while maintaining ownership benefits.",
        "Land investment timeline: Unlike stocks (can trade daily), land is illiquid. This is actually a feature—it forces long-term thinking and prevents emotional selling. Patience is rewarded.",
        "Infrastructure impact on land value: When roads, utilities, or commercial development arrives nearby, land values typically increase 30-50% or more. Understanding planned infrastructure helps identify opportunities.",
        "Generational wealth through land: Land ownership can be passed down, creating multi-generational wealth. Unlike businesses (can fail) or stocks (can crash), land tends to persist and appreciate over decades.",
        "The rent vs own equation: Renters transfer wealth to landlords. Owners build equity. Over 20-30 years, the difference is substantial. But ownership requires capital—understanding alternative entry methods helps.",
        "Land use and value: Agricultural land, residential land, and commercial land serve different purposes and have different value drivers. Understanding zoning and use potential affects investment decisions.",
        "Weak property rights Nigeria creates informal wealth. Strong property documentation turns land into collateral, income, and long-term security. Formalization transforms dead capital into active assets.",
        "Property rights Nigeria determine whether land is an asset or a liability. Unregistered land invites disputes; registered land attracts capital. Documentation is the difference between wealth and risk.",
        "Only about 10% of Nigeria's ~40 million households have formal land titles—meaning 36 million properties are untitled, costing the economy roughly ₦36 trillion annually in lost revenue. Formal property rights unlock capital & tax base.",
        "Nigeria's government estimates over 90% of land is unregistered, representing roughly $300 billion in 'dead capital' that can't be used as loans or investments until property rights are secured. Registration transforms value.",
        "Without solid property rights, land can't be taxed effectively—weakening local government revenue streams and stalling investment in housing and infrastructure. National land reform aims to boost formal ownership and unlock value.",
        "Agriculture in Nigeria isn't charity—it's policy-backed business. Food security incentives and import substitution make farming one of the most protected sectors. Policy alignment reduces investment risk.",
        "Agriculture Nigeria remains one of the few sectors with government-aligned policy support. That alignment lowers risk for long-term investors. When policy and investment align, returns improve.",
        "The agricultural sector contributes about 25% of Nigeria's GDP and employs nearly 48% of the labour force, yet policy and incentives are key to scaling beyond subsistence farming. Understanding policy unlocks scale.",
        "Agriculture equipment and machinery—from tractors to processing tools—qualify for 0% import duty under Nigeria's tariff incentive regime, lowering the cost of modernising farms. Policy reduces capital barriers.",
        "Nigeria previously approved five-year tax and duty-free holidays for agricultural production and processing, plus tax-free agro loans with extended repayment terms. Policy creates favorable conditions for agribusiness.",
        "The agricultural policy push is tied to job creation and food security—reforms unveiled in Abuja aim to create millions of rural jobs through investment incentives and modern farming support. Policy supports long-term investment.",
        "Agriculture Nigeria benefits from pioneer status incentives in some value chains. Processing beats raw production when it comes to tax relief and access to funding. Value addition unlocks more incentives.",
    ],
    'co_ownership': [
        "Fractional ownership explained: Instead of one person owning 100% of an asset, multiple people own percentages. Like company shares, but for real estate. Each owner's returns are proportional to their ownership stake.",
        "Why co-ownership exists: It solves the capital barrier problem. A ₦50M property is out of reach for most. But 100 people contributing ₦500k each makes it accessible. Same asset, lower individual entry.",
        "Co-ownership vs sole ownership: Sole ownership gives you 100% control but requires 100% capital. Co-ownership gives you proportional benefits with fractional capital. Trade-off: less control, more accessibility.",
        "The economics of shared ownership: When multiple people pool capital, they can access larger, often better-performing assets than any could individually. This can improve returns through better asset selection.",
        "Risk distribution in co-ownership: If one person owns a property and it fails, they lose 100%. If 100 people co-own, each loses proportionally. Diversification reduces individual risk exposure.",
        "Management in co-ownership: Professional management is often necessary when multiple owners are involved. This adds cost but also expertise. The trade-off is worth it when individual owners lack management capacity.",
        "Legal structure matters: Co-ownership requires clear documentation—who owns what percentage, how decisions are made, how income is distributed, exit procedures. Without this, disputes are inevitable.",
        "The liquidity question: Co-owned assets are typically less liquid than sole ownership (more people to coordinate). But they're more liquid than trying to sell a property you can't afford to own alone.",
        "Co-ownership democratizes access: What was once only available to high-net-worth individuals becomes accessible to more people. This is the core value proposition—democratizing asset ownership.",
        "Understanding your ownership: In co-ownership, you own a percentage of the asset's economic value, not a specific physical space. This is similar to owning stock—you own part of the company, not a specific office.",
        "The scalability of co-ownership: As more people participate, larger assets become accessible. This can unlock opportunities (commercial real estate, large developments) that individual investors couldn't access.",
        "Co-ownership requires trust and transparency: Since you're not in direct control, you need confidence in the structure, management, and other participants. Due diligence is essential before participating.",
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
    'nigeria tax laws': [
        "Many Nigerians fear tax, but smart investors study it. Nigeria tax laws reward production more than consumption—especially in real sectors. Understanding tax incentives can significantly improve investment returns.",
        "Tax is not the enemy of wealth—ignorance is. Nigeria tax incentives reduce liability legally for investors who understand the system. Knowledge of tax law is an investment advantage."
    ],
    'tax planning nigeria': [
        "Tax breaks in Nigeria exist, but only for those operating formally. Incentives don't reward noise—they reward structure, compliance, and scale. Formalization unlocks access to tax benefits.",
        "The Economic Development Tax Incentive (EDTI) offers ~5% annual tax credit for up to 5 years on qualifying capital expenditure—replacing the old Pioneer Status system. This rewards productive investment."
    ],
    'tax breaks nigeria': [
        "Tax breaks Nigeria are designed to encourage production, not speculation. If your income depends on real output, the system quietly works in your favor. Production-based investments get preferential treatment.",
        "In 2022 the Federal Government granted about ₦1.8 trillion in tax incentives to businesses, including VAT exemptions and pioneer incentives—a huge slice aimed at growth, not giveaways. The system rewards structured investment."
    ],
    'agriculture nigeria': [
        "Agriculture in Nigeria isn't charity—it's policy-backed business. Food security incentives and import substitution make farming one of the most protected sectors. Policy alignment reduces investment risk.",
        "The agricultural sector contributes about 25% of Nigeria's GDP and employs nearly 48% of the labour force, yet policy and incentives are key to scaling beyond subsistence farming. Understanding policy unlocks scale.",
        "Agriculture Nigeria remains one of the few sectors with government-aligned policy support. That alignment lowers risk for long-term investors. When policy and investment align, returns improve."
    ],
    'property rights nigeria': [
        "Weak property rights Nigeria creates informal wealth. Strong property documentation turns land into collateral, income, and long-term security. Formalization transforms dead capital into active assets.",
        "Property rights Nigeria determine whether land is an asset or a liability. Unregistered land invites disputes; registered land attracts capital. Documentation is the difference between wealth and risk.",
        "Only about 10% of Nigeria's ~40 million households have formal land titles—meaning 36 million properties are untitled, costing the economy roughly ₦36 trillion annually in lost revenue. Formal property rights unlock capital & tax base."
    ],
    'untitled land': [
        "Nigeria's government estimates over 90% of land is unregistered, representing roughly $300 billion in 'dead capital' that can't be used as loans or investments until property rights are secured. Registration transforms value.",
        "Without solid property rights, land can't be taxed effectively—weakening local government revenue streams and stalling investment in housing and infrastructure. National land reform aims to boost formal ownership and unlock value."
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
    
    def __init__(self, filepath='bot_data.json'):
        self.filepath = filepath
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
    """Main bot class"""
    
    def __init__(self):
        self.data = BotData()
        self.tweet_queue = self.load_tweet_queue()
    
    def is_contextually_relevant(self, tweet_text, category, trigger_word=""):
        """
        Check if a tweet is contextually relevant before replying.
        Returns True only if the tweet is actually about the topic.
        """
        tweet_lower = tweet_text.lower()
        
        # Context indicators that suggest the tweet is NOT about our topic
        false_positives = {
            'land': [
                'landed', 'landing', 'airport', 'flight', 'plane', 'travel', 
                'visiting', 'arrived', 'touched down', 'disembarked'
            ],
            'property': [
                'property of', 'belongs to', 'owned by', 'copyright', 'intellectual property'
            ],
            'housing': [
                'housing estate', 'housing complex', 'housing unit', 'housing project'
            ],
            'investment': [
                'investment banking', 'investment firm', 'investment company', 
                'investment advisor', 'investment manager'
            ],
            'betting': [
                'betting odds', 'betting line', 'betting spread', 'betting market'
            ]
        }
        
        # Check for false positives
        if category in false_positives:
            for fp in false_positives[category]:
                if fp in tweet_lower:
                    # If it's a false positive, check if there are also relevant words
                    relevant_words = {
                        'land': ['buy', 'sell', 'own', 'purchase', 'invest', 'plot', 'acre', 'hectare', 'property', 'real estate'],
                        'property': ['buy', 'sell', 'own', 'purchase', 'invest', 'real estate', 'land', 'house'],
                        'housing': ['buy', 'sell', 'own', 'purchase', 'affordable', 'home', 'house'],
                        'investment': ['buy', 'sell', 'invest', 'money', 'wealth', 'passive income', 'returns'],
                        'betting': ['loss', 'lost', 'waste', 'regret', 'addiction', 'stop', 'quit']
                    }
                    
                    # If no relevant words found, it's likely a false positive
                    if category in relevant_words:
                        has_relevant = any(word in tweet_lower for word in relevant_words[category])
                        if not has_relevant:
                            return False
        
        # Context indicators that suggest the tweet IS about our topic
        positive_indicators = {
            'betting': [
                'lost money', 'betting loss', 'stop betting', 'gambling', 'waste', 
                'regret', 'addiction', 'quit betting', 'lost on', 'lost to'
            ],
            'investment': [
                'how to invest', 'where to invest', 'passive income', 'wealth building',
                'investment opportunity', 'invest money', 'make money', 'earn money'
            ],
            'land': [
                'buy land', 'sell land', 'own land', 'land ownership', 'land investment',
                'affordable land', 'land for sale', 'real estate', 'property investment',
                'land price', 'land value', 'plot of land'
            ],
            'co_ownership': [
                'fractional ownership', 'co-ownership', 'shared ownership', 'group purchase',
                'syndication', 'joint ownership', 'split ownership'
            ]
        }
        
        # Check for positive indicators
        if category in positive_indicators:
            has_positive = any(indicator in tweet_lower for indicator in positive_indicators[category])
            if has_positive:
                return True
        
        # For Ripple triggers, check if the trigger word appears in a relevant context
        if trigger_word:
            # Check if trigger appears with relevant surrounding words
            trigger_index = tweet_lower.find(trigger_word)
            if trigger_index != -1:
                # Extract context around the trigger (50 chars before and after)
                start = max(0, trigger_index - 50)
                end = min(len(tweet_lower), trigger_index + len(trigger_word) + 50)
                context = tweet_lower[start:end]
                
                # Check for context words that suggest relevance
                context_words = {
                    'nigeria development': ['build', 'develop', 'growth', 'progress', 'nation', 'country'],
                    'real estate nigeria': ['buy', 'sell', 'own', 'property', 'land', 'house', 'investment'],
                    'land': ['buy', 'sell', 'own', 'property', 'investment', 'plot', 'acre'],
                    'housing': ['buy', 'sell', 'own', 'affordable', 'home', 'house', 'rent'],
                    'youth': ['young', 'generation', 'future', 'opportunity', 'access', 'need'],
                    'inflation': ['price', 'cost', 'money', 'economy', 'nigerian', 'naira'],
                    'corruption': ['government', 'politician', 'leader', 'accountability', 'transparency']
                }
                
                if trigger_word in context_words:
                    has_context = any(word in context for word in context_words[trigger_word])
                    if not has_context:
                        return False
        
        # If we have a trigger word match but no clear context, be conservative
        # Only reply if there are multiple relevant words or phrases
        if trigger_word:
            # Count relevant words/phrases
            relevant_count = 0
            if category == 'betting' and any(word in tweet_lower for word in ['money', 'loss', 'waste', 'regret']):
                relevant_count += 1
            if category == 'investment' and any(word in tweet_lower for word in ['money', 'invest', 'wealth', 'income']):
                relevant_count += 1
            if category == 'land' and any(word in tweet_lower for word in ['buy', 'sell', 'own', 'property', 'real estate']):
                relevant_count += 1
            if category == 'co_ownership' and any(word in tweet_lower for word in ['own', 'share', 'group', 'together']):
                relevant_count += 1
            
            # Require at least 2 relevant indicators for ambiguous matches
            if relevant_count < 2:
                return False
        
        return True
    
    def load_tweet_queue(self):
        """Load pre-written tweets from file"""
        queue_file = Path('tweet_queue.json')
        if queue_file.exists():
            with open(queue_file, 'r') as f:
                return json.load(f)
        return []
    
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
            pass
        
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
            response = client.create_tweet(text=tweet_text)
            
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
        
        # Check daily limit first
        if replies_today >= CONFIG.get('max_replies_per_day', 20):
            print(f"⚠️  Daily reply limit reached ({replies_today})")
            return
        
        # Check hourly limit
        current_hour = datetime.now().hour
        hour_key = f"replies_hour_{current_hour}"
        replies_this_hour = today_stats.get(hour_key, 0)
        
        if replies_this_hour >= CONFIG['max_replies_per_hour']:
            print(f"⚠️  Hourly reply limit reached ({replies_this_hour})")
            return
        
        for category, keyword_list in KEYWORDS.items():
            for keyword in keyword_list:
                try:
                    # Search recent tweets
                    tweets = client.search_recent_tweets(
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
                        original_tweet_text = tweet.text  # Keep original for context checking
                        
                        is_relevant = any(
                            trigger in tweet_text 
                            for trigger in ENGAGEMENT_TRIGGERS
                        )
                        
                        # Check for Ripple Effect triggers
                        has_ripple_trigger = any(
                            trigger in tweet_text
                            for trigger in RIPPLE_TRIGGERS.keys()
                        )
                        
                        # Validate context before replying
                        should_reply = False
                        if is_relevant:
                            # Engagement triggers found - high relevance
                            should_reply = self.is_contextually_relevant(original_tweet_text, category)
                        elif has_ripple_trigger:
                            # Ripple trigger found - check context
                            matching_trigger = next(
                                (trigger for trigger in RIPPLE_TRIGGERS.keys() if trigger in tweet_text),
                                None
                            )
                            should_reply = self.is_contextually_relevant(original_tweet_text, category, matching_trigger)
                        elif random.random() < 0.1:  # 10% of keyword matches (reduced from 30% to avoid spam)
                            # Random match - require strong context validation
                            should_reply = self.is_contextually_relevant(original_tweet_text, category)
                        
                        if should_reply:
                            # Check daily limit
                            today_stats = self.data.data['daily_stats'].get(
                                datetime.now().strftime('%Y-%m-%d'), {}
                            )
                            replies_today = today_stats.get('total_replies_sent', 0)
                            
                            if replies_today >= CONFIG.get('max_replies_per_day', 20):
                                print(f"⚠️  Daily reply limit reached ({replies_today})")
                                break
                            
                            # Check hourly limit
                            current_hour = datetime.now().hour
                            hour_key = f"replies_hour_{current_hour}"
                            replies_this_hour = today_stats.get(hour_key, 0)
                            
                            if replies_this_hour >= CONFIG['max_replies_per_hour']:
                                print(f"⚠️  Hourly reply limit reached ({replies_this_hour})")
                                break
                            
                            self.reply_to_tweet(tweet.id, category, tweet.text)
                            
                            # Update hourly counter
                            if hour_key not in today_stats:
                                today_stats[hour_key] = 0
                            today_stats[hour_key] += 1
                            self.data.save()
                            
                            time.sleep(300)  # 5 min between replies (increased from 2 min to avoid spam)
                    
                    time.sleep(30)  # Pause between keyword searches (increased from 10 to 30 seconds)
                    
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
            
            if replies_today >= CONFIG['max_replies_per_hour'] * 24:
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
                    tweets = client.search_recent_tweets(
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
                        original_tweet_text = tweet.text  # Keep original for context checking
                        
                        # Check for matching Ripple trigger
                        for trigger, replies in RIPPLE_TRIGGERS.items():
                            if trigger in tweet_text_lower:
                                # Validate context before replying
                                # Determine category from trigger
                                category = 'land'  # Default
                                if 'betting' in trigger or 'gambling' in trigger:
                                    category = 'betting'
                                elif 'investment' in trigger or 'invest' in trigger:
                                    category = 'investment'
                                elif 'land' in trigger or 'property' in trigger or 'real estate' in trigger or 'housing' in trigger:
                                    category = 'land'
                                
                                # Check if tweet is contextually relevant
                                if not self.is_contextually_relevant(original_tweet_text, category, trigger):
                                    print(f"⏭️  Skipping tweet {tweet.id} - not contextually relevant")
                                    print(f"   Trigger: {trigger}")
                                    print(f"   Tweet: {original_tweet_text[:80]}...")
                                    continue
                                
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
                                    client.create_tweet(
                                        text=reply_text,
                                        in_reply_to_tweet_id=tweet.id
                                    )
                                    
                                    self.data.add_replied_tweet(tweet.id)
                                    self.data.increment_stat('total_replies_sent')
                                    
                                    # Update hourly counter
                                    today_stats = self.data.data['daily_stats'].get(
                                        datetime.now().strftime('%Y-%m-%d'), {}
                                    )
                                    current_hour = datetime.now().hour
                                    hour_key = f"replies_hour_{current_hour}"
                                    if hour_key not in today_stats:
                                        today_stats[hour_key] = 0
                                    today_stats[hour_key] += 1
                                    self.data.save()
                                    
                                    print(f"✅ Ripple reply to tweet {tweet.id}")
                                    print(f"   Trigger: {trigger}")
                                    print(f"   Tweet context: {original_tweet_text[:60]}...")
                                    print(f"   Reply: {reply_text[:50]}...")
                                    
                                    time.sleep(600)  # 10 min between Ripple replies (increased from 3 min to avoid spam)
                                    break  # Only one reply per tweet
                                    
                                except Exception as e:
                                    print(f"❌ Error replying: {e}")
                        
                        time.sleep(30)  # Increased from 10 to 30 seconds
                    
                    time.sleep(60)  # Pause between keyword searches (increased from 30 to 60 seconds)
                    
                except Exception as e:
                    print(f"❌ Error searching Ripple triggers '{keyword}': {e}")
                    time.sleep(60)
                    
        except Exception as e:
            print(f"❌ Error in search_ripple_triggers: {e}")
    
    def reply_to_tweet(self, tweet_id, category, tweet_text=""):
        """Reply to a specific tweet with duplicate prevention and context validation"""
        
        # Validate context before proceeding (if tweet text provided)
        if tweet_text and not self.is_contextually_relevant(tweet_text, category):
            print(f"⏭️  Skipping reply to {tweet_id} - not contextually relevant")
            print(f"   Category: {category}")
            print(f"   Tweet: {tweet_text[:80]}...")
            return
        
        # Initialize reply tracking if needed
        if 'recent_replies' not in self.data.data:
            self.data.data['recent_replies'] = []
        
        # Check for Ripple Effect triggers first
        reply_text = None
        available_replies = []
        matching_trigger = None
        
        if tweet_text:
            tweet_lower = tweet_text.lower()
            for trigger, replies in RIPPLE_TRIGGERS.items():
                if trigger in tweet_lower:
                    available_replies = replies
                    matching_trigger = trigger
                    break
        
        # Fall back to category-based replies
        if not available_replies:
            available_replies = REPLY_TEMPLATES.get(category, REPLY_TEMPLATES['land'])
        
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
            client.create_tweet(
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
                response = client.create_tweet(text=tweet_text)
                
                self.data.increment_stat('total_tweets_posted')
                print(f"✅ Posted economic news")
                print(f"   Title: {news['title'][:50]}...")
                print(f"   Tweet ID: {response.data['id']}")
            else:
                # Fallback: post general market update
                tweet_text = f"📊 Nigerian Stock Market Update\n\nStay informed about NGX market movements: {url}\n\n#NGX #NigeriaStocks"
                response = client.create_tweet(text=tweet_text)
                self.data.increment_stat('total_tweets_posted')
                print(f"✅ Posted general market update")
                
        except Exception as e:
            print(f"❌ Error posting economic news: {e}")
            # Fallback tweet
            try:
                tweet_text = f"📊 Nigerian Stock Market News\n\nFollow market updates: https://ngxgroup.com\n\n#NGX #NigeriaStocks"
                client.create_tweet(text=tweet_text)
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
            response = client.create_tweet(text=tweet_text)
            
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


# Initialize bot
bot = TwitterBot()

# Schedule tweets
for post_time in CONFIG['posting_times']:
    schedule.every().day.at(post_time).do(bot.post_scheduled_tweet)

# Schedule engagement scans
schedule.every(CONFIG['engagement_interval']).minutes.do(bot.search_and_engage)

# Schedule Ripple Effect trigger searches (every 2 hours - reduced frequency to avoid spam)
schedule.every(120).minutes.do(bot.search_ripple_triggers)

# Schedule economic news every 5 hours (starting at 5pm)
schedule.every().day.at("17:00").do(bot.post_economic_news)
schedule.every().day.at("22:00").do(bot.post_economic_news)
schedule.every().day.at("03:00").do(bot.post_economic_news)
schedule.every().day.at("08:00").do(bot.post_economic_news)
schedule.every().day.at("13:00").do(bot.post_economic_news)

# Schedule beautiful places posts (twice daily)
schedule.every().day.at("10:00").do(bot.post_beautiful_place)
schedule.every().day.at("18:00").do(bot.post_beautiful_place)

# Schedule daily stats
schedule.every().day.at("23:59").do(bot.print_stats)
schedule.every().day.at("00:01").do(bot.data.reset_daily_limits)


def main():
    """Main bot loop"""
    print("🤖 SubX Twitter Bot Started")
    print(f"📅 Scheduled tweets: {CONFIG['posting_times']}")
    print(f"🔍 Engagement scans: Every {CONFIG['engagement_interval']} minutes")
    print(f"💬 Max replies/hour: {CONFIG['max_replies_per_hour']}")
    print(f"📊 Max replies/day: {CONFIG.get('max_replies_per_day', 20)}")
    print(f"🌊 Ripple trigger scans: Every 120 minutes")
    print("\nPress Ctrl+C to stop\n")
    
    # Print initial stats
    bot.print_stats()
    
    # Check if we missed any scheduled times today and post if needed
    now = datetime.now()
    current_time = now.strftime('%H:%M')
    current_hour = now.hour
    current_minute = now.minute
    
    print(f"⏰ Current time: {current_time}")
    
    # Check if any scheduled times have passed today
    missed_times = []
    for post_time in CONFIG['posting_times']:
        hour, minute = map(int, post_time.split(':'))
        # If scheduled time has passed today, we missed it
        if hour < current_hour or (hour == current_hour and minute <= current_minute):
            missed_times.append(post_time)
    
    if missed_times:
        print(f"⚠️  Missed scheduled times today: {missed_times}")
        print("📝 Posting now to catch up...")
        bot.post_scheduled_tweet()
        print("✅ Caught up!\n")
    
    # Run initial engagement scan
    print("🔍 Running initial engagement scan...")
    bot.search_and_engage()
    
    # Main loop
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped by user")
        bot.print_stats()
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        bot.print_stats()
