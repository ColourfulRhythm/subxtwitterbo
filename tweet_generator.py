#!/usr/bin/env python3
"""
Dynamic Tweet Generator - Creates unlimited variations to avoid repetition
Uses templates with variables and multiple phrasing options
"""

import random
from datetime import datetime

# Template categories with multiple variations
TWEET_TEMPLATES = {
    'betting_vs_land': [
        {
            'openers': [
                "Did you know",
                "Here's a fact",
                "Real numbers",
                "Let's talk numbers",
                "Quick math",
                "The data shows",
                "Statistics reveal",
                "Here's the truth"
            ],
            'stats': [
                ("₦3.2 TRILLION", "was spent on betting in 2023"),
                ("₦450 BILLION", "is what betting companies made in profit from Nigerians in 2024"),
                ("₦2.8 TRILLION", "was the combined revenue from top 3 betting companies (2023)"),
                ("₦87 BILLION", "is processed monthly in the Nigerian betting market"),
                ("₦150 BILLION", "was spent on betting ads in 2024")
            ],
            'comparisons': [
                "That's enough to buy land for {people} million people",
                "Enough for {sqm} sqm of land appreciating 15-25% annually",
                "That's {sqm} sqm of land you could own instead",
                "Enough to own {sqm} sqm in 2 Seasons, Abeokuta",
                "That could buy {sqm} sqm of appreciating land",
                "Enough to purchase {sqm} sqm in premium locations"
            ],
            'closers': [
                "The math doesn't lie. @1Subx starts at ₦1k.",
                "Choose differently. Start from ₦1k. @1Subx",
                "Build instead of feed. From ₦1k. www.subxhq.com",
                "The choice is clear. @1Subx · From ₦1k",
                "Still betting? The data doesn't lie. @1Subx"
            ]
        }
    ],
    
    'betting_losses': [
        {
            'openers': [
                "Your ₦{amount} {frequency} betting habit",
                "That ₦{amount} you {action} on betting",
                "Every ₦{amount} you {action} betting",
                "Your ₦{amount} {frequency} losses"
            ],
            'calculations': [
                "= ₦{yearly} in 1 year. Returns: -₦{yearly} (you lose it all)",
                "= ₦{yearly}/year. That's ₦{yearly} GONE",
                "= ₦{yearly} yearly. All lost. Zero returns",
                "= ₦{yearly} annually. Your share: ₦0"
            ],
            'land_comparison': [
                "₦{amount} {frequency} land buying = {sqm} sqm in 1 year. Returns: +₦{appreciation} appreciation (15%) PLUS you own ₦{yearly} in land",
                "Same ₦{amount} in land = {sqm} sqm + 15-25% appreciation. Your share: 100%",
                "That ₦{amount} in land = {sqm} sqm appreciating 15-25% annually. You own it forever",
                "₦{amount} {frequency} land = {sqm} sqm + ₦{appreciation} appreciation. Build wealth instead"
            ],
            'closers': [
                "Math is brutal. Choose wisely. @1Subx",
                "Same money. Opposite outcomes. Choose. @1Subx",
                "The difference is clear. Start from ₦1k. www.subxhq.com",
                "Build instead of lose. From ₦1k. @1Subx"
            ]
        }
    ],
    
    'success_rates': [
        {
            'openers': [
                "Research shows",
                "Studies reveal",
                "The data proves",
                "Statistics show",
                "Industry reports confirm",
                "Real facts"
            ],
            'betting_stats': [
                "Only 1 in 100 bettors profit long-term",
                "Just 1% of bettors make profit over time",
                "90% of bettors lose money over 12 months",
                "Only 1-11% of bettors profit long-term",
                "89-90% lose money wagered over 12 months"
            ],
            'land_stats': [
                "Land appreciation success rate in Lagos/Ogun last 10 years? 100%. Every single landowner gained",
                "Land owners in Nigeria: 100% success rate. Every. Single. One gained",
                "Land appreciation in Lagos/Ogun: 15-25% annually. 100% success rate",
                "Land owners in Abeokuta: 18% annual returns. 100% success rate"
            ],
            'closers': [
                "Still think betting is the 'smart risk'? 🤔 @1Subx",
                "The choice is clear. Start from ₦1k. www.subxhq.com",
                "1% vs 100%. Which side are you on? @1Subx",
                "Choose the 100% success rate. From ₦1k. @1Subx"
            ]
        }
    ],
    
    'land_appreciation': [
        {
            'openers': [
                "2 Seasons land was",
                "Land in 2 Seasons started at",
                "2 Seasons Phase 1 began at",
                "When 2 Seasons launched, prices were"
            ],
            'price_history': [
                ("₦5k/sqm", "6 months ago", "₦5,750/sqm", "15%"),
                ("₦5k/sqm", "last year", "₦5,750/sqm", "15%"),
                ("₦5k/sqm", "in January", "₦5,750/sqm", "15%"),
                ("₦5,000/sqm", "6 months back", "₦5,750/sqm", "15%")
            ],
            'projections': [
                "Projected: ₦8k-₦10k/sqm in 12 months (40-75% gain)",
                "Next year: ₦8k-₦10k/sqm expected (40-75% gain)",
                "12 months from now: ₦8k-₦10k/sqm (40-75% gain)",
                "By next year: ₦8k-₦10k/sqm (40-75% gain)"
            ],
            'closers': [
                "Early buyers win. That's you. Start from ₦1k. @1Subx",
                "Lock in current prices NOW. From ₦1k. www.subxhq.com",
                "Buy before prices rise. Start from ₦1k. @1Subx",
                "Don't wait. Prices only go up. From ₦1k. @1Subx"
            ]
        }
    ],
    
    'demographics': [
        {
            'openers': [
                "Industry report",
                "Research shows",
                "Data reveals",
                "Statistics indicate",
                "Studies confirm"
            ],
            'age_stats': [
                "76% of Nigerian bettors are under 35 years old",
                "Three-quarters of bettors are under 35",
                "Most bettors (76%) are in their prime earning years (under 35)",
                "76% of bettors haven't hit 35 yet"
            ],
            'loss_stats': [
                "Average loss = ₦18k/month = ₦216k/year",
                "Average monthly loss: ₦18k = ₦216k annually",
                "They lose ₦18k monthly on average = ₦216k yearly",
                "₦18k/month average loss = ₦216k/year"
            ],
            'land_comparison': [
                "That's the PRIME land-buying age losing generational wealth",
                "Prime age for land ownership, but losing wealth to betting",
                "Best time to buy land, but choosing to lose money instead",
                "Perfect age for building wealth, but destroying it instead"
            ],
            'closers': [
                "Wake up. 💯 Start from ₦1k. @1Subx",
                "Choose differently. From ₦1k. www.subxhq.com",
                "Build wealth instead. From ₦1k. @1Subx",
                "Stop the cycle. Start from ₦1k. @1Subx"
            ]
        }
    ],
    
    'house_edge': [
        {
            'openers': [
                "Mathematics lesson",
                "Here's the math",
                "Let's do the math",
                "Quick calculation",
                "The numbers"
            ],
            'betting_edge': [
                "Betting house edge = 5-15%. Your ₦100 bet returns ₦85-₦95 on average",
                "House edge: 5-15%. ₦100 bet = ₦85-₦95 average return",
                "Betting edge: 5-15%. ₦100 becomes ₦85-₦95 (you lose)",
                "House takes 5-15%. Your ₦100 = ₦85-₦95 back"
            ],
            'land_appreciation': [
                "Land appreciation = 15-25% annually. Your ₦100 land becomes ₦115-₦125",
                "Land: 15-25% annual gain. ₦100 becomes ₦115-₦125",
                "Land appreciation: 15-25% yearly. ₦100 = ₦115-₦125",
                "Land gains: 15-25% annually. ₦100 becomes ₦115-₦125"
            ],
            'closers': [
                "One guarantees loss. One guarantees gain. Still betting? You failed the math test. @1Subx",
                "One loses. One gains. Choose wisely. From ₦1k. www.subxhq.com",
                "The math is clear. Choose the gain. Start from ₦1k. @1Subx",
                "Numbers don't lie. Choose land. From ₦1k. @1Subx"
            ]
        }
    ]
}

# Betting amount variations
BETTING_AMOUNTS = {
    'daily': [
        ('₦5k', 1825000, 365, 273750),
        ('₦3k', 1095000, 219, 164250),
        ('₦10k', 3650000, 730, 547500),
        ('₦2k', 730000, 146, 109500)
    ],
    'weekly': [
        ('₦5k', 260000, 52, 39000),
        ('₦10k', 520000, 104, 78000),
        ('₦20k', 1040000, 208, 156000),
        ('₦3k', 156000, 31, 23400)
    ],
    'monthly': [
        ('₦20k', 240000, 48, 36000),
        ('₦15k', 180000, 36, 27000),
        ('₦30k', 360000, 72, 54000),
        ('₦50k', 600000, 120, 90000)
    ]
}

# Action words for variation
ACTIONS = ['spend', 'lose', 'waste', 'throw away', 'gamble away']


def generate_betting_vs_land_tweet():
    """Generate a betting vs land comparison tweet"""
    template = random.choice(TWEET_TEMPLATES['betting_vs_land'])
    
    opener = random.choice(template['openers'])
    stat_amount, stat_desc = random.choice(template['stats'])
    comparison = random.choice(template['comparisons'])
    closer = random.choice(template['closers'])
    
    # Calculate people/sqm based on stat
    if '3.2 TRILLION' in stat_amount:
        people = 6.4
        sqm = 640000
    elif '450 BILLION' in stat_amount:
        people = 0.9
        sqm = 90000
    elif '2.8 TRILLION' in stat_amount:
        people = 5.6
        sqm = 560000
    elif '87 BILLION' in stat_amount:
        people = 0.17
        sqm = 17400
    elif '150 BILLION' in stat_amount:
        people = 0.3
        sqm = 30000
    else:
        people = 1.0
        sqm = 100000
    
    comparison_text = comparison.format(people=int(people), sqm=int(sqm))
    
    # Vary the phrasing
    phrasing_options = [
        f"{opener}: {stat_amount} {stat_desc}. {comparison_text}. {closer}",
        f"{opener}: Nigerians {stat_desc} {stat_amount}. {comparison_text}. {closer}",
        f"{opener}: {stat_amount} {stat_desc}. {comparison_text}. {closer}",
    ]
    
    tweet = random.choice(phrasing_options)
    return tweet


def generate_betting_loss_tweet():
    """Generate a betting loss calculation tweet"""
    template = random.choice(TWEET_TEMPLATES['betting_losses'])
    
    frequency = random.choice(['daily', 'weekly', 'monthly'])
    amount, yearly, sqm, appreciation = random.choice(BETTING_AMOUNTS[frequency])
    action = random.choice(ACTIONS)
    
    opener = random.choice(template['openers']).format(
        amount=amount, frequency=frequency, action=action
    )
    calculation = random.choice(template['calculations']).format(
        yearly=f"{yearly:,}"
    )
    land_comp = random.choice(template['land_comparison']).format(
        amount=amount, frequency=frequency, sqm=sqm, 
        appreciation=f"{appreciation:,}", yearly=f"{yearly:,}"
    )
    closer = random.choice(template['closers'])
    
    # Fix double currency symbol issue
    opener = opener.replace('₦₦', '₦')
    land_comp = land_comp.replace('₦₦', '₦')
    
    tweet = f"{opener} {calculation}. {land_comp}. {closer}"
    return tweet


def generate_success_rate_tweet():
    """Generate a success rate comparison tweet"""
    template = random.choice(TWEET_TEMPLATES['success_rates'])
    
    opener = random.choice(template['openers'])
    betting_stat = random.choice(template['betting_stats'])
    land_stat = random.choice(template['land_stats'])
    closer = random.choice(template['closers'])
    
    tweet = f"{opener}: {betting_stat}. {land_stat}. {closer}"
    return tweet


def generate_land_appreciation_tweet():
    """Generate a land appreciation tweet"""
    template = random.choice(TWEET_TEMPLATES['land_appreciation'])
    
    opener = random.choice(template['openers'])
    old_price, time_ago, new_price, percent = random.choice(template['price_history'])
    projection = random.choice(template['projections'])
    closer = random.choice(template['closers'])
    
    tweet = f"{opener} {old_price} {time_ago}. Today it's worth {new_price}. That's {percent} appreciation. {projection}. {closer}"
    return tweet


def generate_demographics_tweet():
    """Generate a demographics-focused tweet"""
    template = random.choice(TWEET_TEMPLATES['demographics'])
    
    opener = random.choice(template['openers'])
    age_stat = random.choice(template['age_stats'])
    loss_stat = random.choice(template['loss_stats'])
    comparison = random.choice(template['land_comparison'])
    closer = random.choice(template['closers'])
    
    tweet = f"{opener}: {age_stat}. {loss_stat}. {comparison} to betting companies. Meanwhile, 500 sqm in 2 Seasons = ₦2.5M today, ₦4M+ in 3 years. {closer}"
    return tweet


def generate_house_edge_tweet():
    """Generate a house edge comparison tweet"""
    template = random.choice(TWEET_TEMPLATES['house_edge'])
    
    opener = random.choice(template['openers'])
    betting_edge = random.choice(template['betting_edge'])
    land_app = random.choice(template['land_appreciation'])
    closer = random.choice(template['closers'])
    
    tweet = f"{opener}: {betting_edge}. {land_app}. {closer}"
    return tweet


# Main generator function
def generate_tweet(category=None):
    """Generate a random tweet from specified category or random"""
    generators = {
        'betting_vs_land': generate_betting_vs_land_tweet,
        'betting_losses': generate_betting_loss_tweet,
        'success_rates': generate_success_rate_tweet,
        'land_appreciation': generate_land_appreciation_tweet,
        'demographics': generate_demographics_tweet,
        'house_edge': generate_house_edge_tweet
    }
    
    if category and category in generators:
        return generators[category]()
    else:
        return random.choice(list(generators.values()))()


# Test function
if __name__ == "__main__":
    print("Generating sample tweets...\n")
    for i in range(5):
        print(f"{i+1}. {generate_tweet()}\n")

