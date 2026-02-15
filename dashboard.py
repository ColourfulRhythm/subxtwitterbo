#!/usr/bin/env python3
"""
SubX Twitter Bot Dashboard
View statistics, manage queue, and control bot
"""

import json
from pathlib import Path
from datetime import datetime
import sys

class Dashboard:
    def __init__(self):
        self.load_data()
        self.load_queue()
    
    def load_data(self):
        """Load bot data"""
        data_file = Path('bot_data.json')
        if data_file.exists():
            with open(data_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = None
            print("⚠️  No bot data found. Bot hasn't run yet.")
    
    def load_queue(self):
        """Load tweet queue"""
        queue_file = Path('tweet_queue.json')
        if queue_file.exists():
            with open(queue_file, 'r') as f:
                self.queue = json.load(f)
        else:
            self.queue = []
            print("⚠️  No tweet queue found.")
    
    def show_stats(self):
        """Display bot statistics"""
        if not self.data:
            print("No data available yet.")
            return
        
        print("\n" + "="*60)
        print("📊 SUBX TWITTER BOT STATISTICS")
        print("="*60)
        
        print(f"\n📈 Overall Performance:")
        print(f"   Total Tweets Posted: {self.data.get('total_tweets_posted', 0)}")
        print(f"   Total Replies Sent: {self.data.get('total_replies_sent', 0)}")
        print(f"   Tweets Replied To: {len(self.data.get('replied_tweets', []))}")
        
        print(f"\n📅 Queue Status:")
        print(f"   Current Position: {self.data.get('current_tweet_index', 0)}/{len(self.queue)}")
        print(f"   Remaining Tweets: {len(self.queue) - self.data.get('current_tweet_index', 0)}")
        
        if self.queue:
            next_tweet = self.queue[self.data.get('current_tweet_index', 0) % len(self.queue)]
            print(f"\n📝 Next Scheduled Tweet:")
            print(f"   {next_tweet[:100]}...")
        
        print(f"\n📆 Daily Statistics:")
        daily_stats = self.data.get('daily_stats', {})
        if daily_stats:
            for date in sorted(daily_stats.keys(), reverse=True)[:7]:  # Last 7 days
                stats = daily_stats[date]
                print(f"\n   {date}:")
                for key, value in stats.items():
                    print(f"      {key}: {value}")
        
        print("\n" + "="*60 + "\n")
    
    def show_queue(self):
        """Display tweet queue"""
        if not self.queue:
            print("No tweets in queue.")
            return
        
        print("\n" + "="*60)
        print(f"📝 TWEET QUEUE ({len(self.queue)} tweets)")
        print("="*60)
        
        current_index = self.data.get('current_tweet_index', 0) if self.data else 0
        
        for i, tweet in enumerate(self.queue[:10]):  # Show first 10
            marker = "➡️ " if i == current_index else "   "
            print(f"\n{marker}[{i+1}] {tweet[:80]}...")
        
        if len(self.queue) > 10:
            print(f"\n   ... and {len(self.queue) - 10} more tweets")
        
        print("\n" + "="*60 + "\n")
    
    def add_tweet(self, tweet_text):
        """Add a new tweet to the queue"""
        self.queue.append(tweet_text)
        with open('tweet_queue.json', 'w') as f:
            json.dump(self.queue, f, indent=2)
        print(f"✅ Added tweet to queue (position {len(self.queue)})")
    
    def remove_tweet(self, index):
        """Remove a tweet from the queue"""
        if 0 <= index < len(self.queue):
            removed = self.queue.pop(index)
            with open('tweet_queue.json', 'w') as f:
                json.dump(self.queue, f, indent=2)
            print(f"✅ Removed: {removed[:50]}...")
        else:
            print(f"❌ Invalid index. Queue has {len(self.queue)} tweets.")
    
    def reset_index(self):
        """Reset queue to beginning"""
        if self.data:
            self.data['current_tweet_index'] = 0
            with open('bot_data.json', 'w') as f:
                json.dump(self.data, f, indent=2)
            print("✅ Reset queue to beginning")
        else:
            print("❌ No bot data to reset")
    
    def export_stats(self):
        """Export statistics to CSV"""
        if not self.data:
            print("No data to export")
            return
        
        filename = f"bot_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w') as f:
            f.write("Date,Metric,Value\n")
            
            # Overall stats
            f.write(f"Overall,Total Tweets Posted,{self.data.get('total_tweets_posted', 0)}\n")
            f.write(f"Overall,Total Replies Sent,{self.data.get('total_replies_sent', 0)}\n")
            
            # Daily stats
            for date, stats in self.data.get('daily_stats', {}).items():
                for metric, value in stats.items():
                    f.write(f"{date},{metric},{value}\n")
        
        print(f"✅ Exported stats to {filename}")
    
    def menu(self):
        """Interactive menu"""
        while True:
            print("\n" + "="*60)
            print("🤖 SUBX TWITTER BOT DASHBOARD")
            print("="*60)
            print("\n1. View Statistics")
            print("2. View Tweet Queue")
            print("3. Add Tweet to Queue")
            print("4. Remove Tweet from Queue")
            print("5. Reset Queue to Beginning")
            print("6. Export Statistics (CSV)")
            print("7. Exit")
            
            choice = input("\nEnter choice (1-7): ").strip()
            
            if choice == '1':
                self.show_stats()
            elif choice == '2':
                self.show_queue()
            elif choice == '3':
                print("\nEnter tweet text (max 280 characters):")
                tweet = input("> ").strip()
                if len(tweet) <= 280:
                    self.add_tweet(tweet)
                else:
                    print(f"❌ Too long! ({len(tweet)} characters)")
            elif choice == '4':
                self.show_queue()
                try:
                    index = int(input("\nEnter tweet number to remove: ")) - 1
                    self.remove_tweet(index)
                except ValueError:
                    print("❌ Invalid number")
            elif choice == '5':
                confirm = input("Reset queue to beginning? (y/n): ").lower()
                if confirm == 'y':
                    self.reset_index()
            elif choice == '6':
                self.export_stats()
            elif choice == '7':
                print("\n👋 Goodbye!\n")
                break
            else:
                print("❌ Invalid choice")

if __name__ == "__main__":
    dashboard = Dashboard()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'stats':
            dashboard.show_stats()
        elif sys.argv[1] == 'queue':
            dashboard.show_queue()
        elif sys.argv[1] == 'export':
            dashboard.export_stats()
        else:
            print("Usage: python3 dashboard.py [stats|queue|export]")
    else:
        dashboard.menu()
