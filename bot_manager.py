#!/usr/bin/env python3
"""
Bot Manager - Manages multiple bot instances running concurrently
"""

import threading
from typing import Dict, Optional
from bot_core import TwitterBot
import time

class BotManager:
    """Manages multiple bot instances"""
    
    def __init__(self):
        self.bots: Dict[str, TwitterBot] = {}
        self.threads: Dict[str, threading.Thread] = {}
        self.running: Dict[str, bool] = {}
    
    def start_bot(self, user_id: str) -> bool:
        """
        Start a bot instance for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            True if started successfully, False otherwise
        """
        if user_id in self.bots and self.running.get(user_id, False):
            return False  # Already running
        
        try:
            # Create bot instance
            bot = TwitterBot(user_id)
            self.bots[user_id] = bot
            self.running[user_id] = True
            
            # Start bot in a separate thread
            thread = threading.Thread(
                target=self._run_bot,
                args=(user_id,),
                daemon=True
            )
            thread.start()
            self.threads[user_id] = thread
            
            return True
        
        except Exception as e:
            print(f"❌ Error starting bot for {user_id}: {e}")
            if user_id in self.bots:
                del self.bots[user_id]
            if user_id in self.running:
                del self.running[user_id]
            return False
    
    def stop_bot(self, user_id: str) -> bool:
        """
        Stop a bot instance for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            True if stopped successfully, False otherwise
        """
        if user_id not in self.bots:
            return False
        
        # Mark as not running
        self.running[user_id] = False
        
        # Wait for thread to finish (with timeout)
        if user_id in self.threads:
            thread = self.threads[user_id]
            thread.join(timeout=5)
            del self.threads[user_id]
        
        # Remove bot instance
        if user_id in self.bots:
            del self.bots[user_id]
        
        return True
    
    def _run_bot(self, user_id: str):
        """Internal method to run bot in a thread"""
        try:
            bot = self.bots[user_id]
            
            # Initialize bot (print stats, check missed times, etc.)
            bot.initialize()
            
            # Run bot loop
            import schedule
            while self.running.get(user_id, False):
                try:
                    # Run pending scheduled tasks
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    print(f"❌ Error in bot loop for {user_id}: {e}")
                    time.sleep(60)
        except Exception as e:
            print(f"❌ Error in bot thread for {user_id}: {e}")
            self.running[user_id] = False
    
    def get_bot_status(self, user_id: str) -> dict:
        """
        Get status of a bot instance
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with bot status information
        """
        if user_id not in self.bots:
            return {
                'running': False,
                'exists': False
            }
        
        return {
            'running': self.running.get(user_id, False),
            'exists': True,
            'thread_alive': user_id in self.threads and self.threads[user_id].is_alive()
        }
    
    def list_active_bots(self) -> list:
        """
        List all active bot instances
        
        Returns:
            List of user_ids with active bots
        """
        return [
            user_id for user_id, running in self.running.items()
            if running
        ]
    
    def restart_bot(self, user_id: str) -> bool:
        """
        Restart a bot instance
        
        Args:
            user_id: User identifier
            
        Returns:
            True if restarted successfully
        """
        self.stop_bot(user_id)
        time.sleep(1)  # Brief pause
        return self.start_bot(user_id)

