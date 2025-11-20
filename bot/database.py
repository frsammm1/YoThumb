import json
import os
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        self.db_file = 'database.json'
        self.data = self.load_data()
    
    def load_data(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except:
                return self.get_default_data()
        return self.get_default_data()
    
    def get_default_data(self):
        return {
            'subscriptions': {},
            'auth_keys': {},
            'stats': {
                'total_users': 0,
                'total_videos': 0,
                'total_keys_generated': 0
            }
        }
    
    def save_data(self):
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving database: {e}")
    
    def create_auth_key(self, key, duration_seconds):
        self.data['auth_keys'][key] = {
            'duration_seconds': duration_seconds,
            'created_at': datetime.now().isoformat(),
            'used': False,
            'used_by': None,
            'used_at': None
        }
        self.data['stats']['total_keys_generated'] += 1
        self.save_data()
    
    def verify_auth_key(self, key):
        if key in self.data['auth_keys'] and not self.data['auth_keys'][key]['used']:
            self.data['auth_keys'][key]['used'] = True
            self.data['auth_keys'][key]['used_at'] = datetime.now().isoformat()
            self.save_data()
            return self.data['auth_keys'][key]
        return None
    
    def activate_subscription(self, user_id, duration_seconds):
        user_id_str = str(user_id)
        
        if user_id_str in self.data['subscriptions']:
            current_expires = datetime.fromisoformat(
                self.data['subscriptions'][user_id_str]['expires_at']
            )
            if current_expires > datetime.now():
                new_expires = current_expires + timedelta(seconds=duration_seconds)
            else:
                new_expires = datetime.now() + timedelta(seconds=duration_seconds)
        else:
            new_expires = datetime.now() + timedelta(seconds=duration_seconds)
            self.data['stats']['total_users'] += 1
        
        self.data['subscriptions'][user_id_str] = {
            'expires_at': new_expires.isoformat(),
            'activated_at': datetime.now().isoformat(),
            'videos_processed': self.data['subscriptions'].get(user_id_str, {}).get('videos_processed', 0)
        }
        
        for key, key_data in self.data['auth_keys'].items():
            if key_data.get('used') and not key_data.get('used_by'):
                key_data['used_by'] = user_id_str
                break
        
        self.save_data()
    
    def get_subscription(self, user_id):
        user_id_str = str(user_id)
        return self.data['subscriptions'].get(user_id_str)
    
    def has_active_subscription(self, user_id):
        subscription = self.get_subscription(user_id)
        if not subscription:
            return False
        expires_at = datetime.fromisoformat(subscription['expires_at'])
        return expires_at > datetime.now()
    
    def increment_videos_processed(self, user_id):
        user_id_str = str(user_id)
        if user_id_str in self.data['subscriptions']:
            self.data['subscriptions'][user_id_str]['videos_processed'] = \
                self.data['subscriptions'][user_id_str].get('videos_processed', 0) + 1
            self.data['stats']['total_videos'] += 1
            self.save_data()
    
    def get_stats(self):
        return self.data['stats']
