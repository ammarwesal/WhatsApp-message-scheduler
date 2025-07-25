import sqlite3
import schedule
import time
import threading
from datetime import datetime, timedelta
import re
import pywhatkit as pwk
from typing import Optional, Dict, List
import json

class WhatsAppScheduler:
    def __init__(self, db_path: str = "scheduler.db"):
        self.db_path = db_path
        self.init_database()
        self.running = False
        
    def init_database(self):
        """Initialize SQLite database for storing scheduled messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                message TEXT NOT NULL,
                scheduled_time DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                sent_at DATETIME NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                phone_number TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_contact(self, name: str, phone_number: str):
        """Add a contact to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO contacts (name, phone_number) VALUES (?, ?)",
                (name.lower(), phone_number)
            )
            conn.commit()
            print(f"Contact {name} added successfully!")
        except Exception as e:
            print(f"Error adding contact: {e}")
        finally:
            conn.close()
    
    def get_contact_number(self, name: str) -> Optional[str]:
        """Get phone number for a contact name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT phone_number FROM contacts WHERE name = ?",
            (name.lower(),)
        )
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def parse_natural_language(self, user_input: str) -> Dict:
        """Parse natural language input to extract scheduling information"""
        # Enhanced pattern matching with better flexibility
        patterns = {
            'time_patterns': [
                (r'in (\d+) days?', lambda x: int(x) * 24 * 60),
                (r'in (\d+) hours?', lambda x: int(x) * 60),
                (r'in (\d+) minutes?', lambda x: int(x)),
                (r'tomorrow', lambda x: 24 * 60),
                (r'after (\d+) days?', lambda x: int(x) * 24 * 60),
                (r'after (\d+) hours?', lambda x: int(x) * 60),
                (r'after (\d+) minutes?', lambda x: int(x)),
            ],
            'contact_patterns': [
                r'(?:to|send|message|remind)\s+([A-Za-z]+)',
                r'send\s+([A-Za-z]+)\s+',
                r'^([A-Za-z]+)\s+',  # Name at the beginning
                r'\s+([A-Za-z]+)\s+["\']',  # Name before quoted message
            ],
            'message_patterns': [
                r'["\'](.+?)["\']',  # Quoted message
                r'(?:saying|asking|about|that)\s+(.+?)(?:\s+in|\s+after|$)',
                r'message\s+(.+?)(?:\s+in|\s+after|$)',
            ]
        }
        
        result = {
            'recipient': None,
            'message': None,
            'delay_minutes': None
        }
        
        # Extract time delay
        for pattern, converter in patterns['time_patterns']:
            match = re.search(pattern, user_input.lower())
            if match:
                if match.group(1).isdigit():
                    result['delay_minutes'] = converter(match.group(1))
                else:
                    result['delay_minutes'] = converter(1)
                break
        
        # Extract recipient - try multiple patterns
        for pattern in patterns['contact_patterns']:
            contact_match = re.search(pattern, user_input.lower())
            if contact_match:
                result['recipient'] = contact_match.group(1)
                break
        
        # Extract message - try multiple patterns
        for pattern in patterns['message_patterns']:
            message_match = re.search(pattern, user_input)
            if message_match:
                result['message'] = message_match.group(1).strip()
                break
        
        # Debug output
        print(f"DEBUG - Parsed: recipient='{result['recipient']}', message='{result['message']}', delay={result['delay_minutes']}")
        
        return result
    
    def schedule_message(self, user_input: str) -> bool:
        """Schedule a message based on natural language input"""
        parsed = self.parse_natural_language(user_input)
        
        if not all([parsed['recipient'], parsed['message'], parsed['delay_minutes']]):
            print("\n❌ Could not parse the request. Here are some examples:")
            print("✅ 'Send john \"test message\" in 2 minutes'")
            print("✅ 'Message sarah \"meeting reminder\" tomorrow'")
            print("✅ 'Remind you \"call back\" in 1 hour'")
            print("✅ 'Send alex \"happy birthday\" in 2 days'")
            print("\nMake sure to:")
            print("- Use quotes around the message")
            print("- Specify a contact name")
            print("- Include timing (in X minutes/hours/days)")
            return False
        
        # Handle "you" as a special case - ask for phone number
        if parsed['recipient'].lower() == 'you':
            phone_input = input("Enter your phone number (with country code, e.g., +919876543210): ")
            if phone_input.strip():
                # Add temporary contact
                self.add_contact("me", phone_input.strip())
                parsed['recipient'] = "me"
            else:
                print("Phone number required to send message to 'you'")
                return False
        
        # Get contact number
        phone_number = self.get_contact_number(parsed['recipient'])
        if not phone_number:
            print(f"❌ Contact '{parsed['recipient']}' not found.")
            add_now = input(f"Would you like to add {parsed['recipient']} now? (y/n): ")
            if add_now.lower() == 'y':
                phone_input = input(f"Enter phone number for {parsed['recipient']} (with country code): ")
                if phone_input.strip():
                    self.add_contact(parsed['recipient'], phone_input.strip())
                    phone_number = phone_input.strip()
                else:
                    return False
            else:
                return False
        
        # Calculate scheduled time
        scheduled_time = datetime.now() + timedelta(minutes=parsed['delay_minutes'])
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scheduled_messages 
            (recipient_name, phone_number, message, scheduled_time)
            VALUES (?, ?, ?, ?)
        ''', (parsed['recipient'], phone_number, parsed['message'], scheduled_time))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Message scheduled!")
        print(f"📱 To: {parsed['recipient']} ({phone_number})")
        print(f"💬 Message: {parsed['message']}")
        print(f"⏰ Scheduled for: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
        return True
    
    def send_whatsapp_message_alternative(self, phone_number: str, message: str) -> bool:
        """Alternative method using instant send for more reliable sending"""
        try:
            # Use the instant send method from pywhatkit
            phone_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
            if not phone_number.startswith('91') and len(phone_number) == 10:
                phone_number = '91' + phone_number
            
            print(f"Using instant send to +{phone_number}")
            
            # Use sendwhatmsg_instantly which is more reliable
            pwk.sendwhatmsg_instantly(f"+{phone_number}", message, 
                                    wait_time=10,  # Wait for page load
                                    tab_close=True,  # Close after sending
                                    close_time=3)
            
            return True
            
        except Exception as e:
            print(f"Alternative method failed: {e}")
            return False
    
    def send_whatsapp_message(self, phone_number: str, message: str) -> bool:
        """Send WhatsApp message using pywhatkit with auto-send fix"""
        try:
            import pyautogui
            import time as time_module
            
            # Remove '+' from phone number if present
            phone_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
            # Add country code if not present (assuming India +91)
            if not phone_number.startswith('91') and len(phone_number) == 10:
                phone_number = '91' + phone_number
            
            # Calculate send time with proper buffer
            now = datetime.now()
            send_hour = now.hour
            send_minute = now.minute + 2  # Add 2 minutes buffer for WhatsApp Web to load
            
            # Handle minute overflow
            if send_minute >= 60:
                send_minute -= 60
                send_hour += 1
                if send_hour >= 24:
                    send_hour = 0
            
            print(f"Sending WhatsApp message to +{phone_number} at {send_hour:02d}:{send_minute:02d}")
            
            # Send message with proper timing - but don't close tab yet
            pwk.sendwhatmsg(f"+{phone_number}", message, send_hour, send_minute, 
                          wait_time=15,  # Wait 15 seconds for WhatsApp Web to load
                          tab_close=False,  # Don't close tab yet - we need to press Enter
                          close_time=2)
            
            # Wait a bit more for the message to be typed
            time_module.sleep(3)
            
            # Press Enter to send the message
            print("Pressing Enter to send the message...")
            pyautogui.press('enter')
            
            # Wait a moment to confirm sending
            time_module.sleep(2)
            
            # Now close the tab
            pyautogui.hotkey('ctrl', 'w')
            
            print("✅ Message sent and tab closed!")
            return True
            
        except Exception as e:
            print(f"Failed to send message: {e}")
            print("💡 Tip: Make sure WhatsApp Web is accessible and you're logged in")
            return False
    
    def check_and_send_messages(self):
        """Check for pending messages and send them if it's time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        current_time = datetime.now()
        
        cursor.execute('''
            SELECT id, recipient_name, phone_number, message 
            FROM scheduled_messages 
            WHERE status = 'pending' AND scheduled_time <= ?
        ''', (current_time,))
        
        pending_messages = cursor.fetchall()
        
        for msg_id, recipient, phone_number, message in pending_messages:
            print(f"Sending message to {recipient}: {message}")
            
            # Try both methods
            success = False
            try:
                success = self.send_whatsapp_message_alternative(phone_number, message)
            except:
                success = self.send_whatsapp_message(phone_number, message)
            
            if success:
                cursor.execute('''
                    UPDATE scheduled_messages 
                    SET status = 'sent', sent_at = ? 
                    WHERE id = ?
                ''', (current_time, msg_id))
                print(f"Message sent successfully to {recipient}")
            else:
                cursor.execute('''
                    UPDATE scheduled_messages 
                    SET status = 'failed' 
                    WHERE id = ?
                ''', (msg_id,))
                print(f"Failed to send message to {recipient}")
        
        conn.commit()
        conn.close()
    
    def start_scheduler(self):
        """Start the background scheduler"""
        def run_scheduler():
            schedule.every(1).minutes.do(self.check_and_send_messages)
            
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        
        self.running = True
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        print("Scheduler started! Checking for messages every minute.")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        print("Scheduler stopped.")
    
    def list_scheduled_messages(self):
        """List all scheduled messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT recipient_name, message, scheduled_time, status 
            FROM scheduled_messages 
            ORDER BY scheduled_time
        ''')
        
        messages = cursor.fetchall()
        conn.close()
        
        if not messages:
            print("No scheduled messages found.")
            return
        
        print("\n=== Scheduled Messages ===")
        for recipient, message, scheduled_time, status in messages:
            print(f"To: {recipient}")
            print(f"Message: {message}")
            print(f"Scheduled: {scheduled_time}")
            print(f"Status: {status}")
            print("-" * 30)

def main():
    scheduler = WhatsAppScheduler()
    
    print("WhatsApp Message Scheduler AI Agent")
    print("====================================")
    print("Commands:")
    print("1. 'add contact <n> <phone>' - Add a contact")
    print("2. 'schedule <message>' - Schedule a message")
    print("3. 'send now <contact> <message>' - Send immediately")
    print("4. 'list' - List scheduled messages")
    print("5. 'start' - Start the scheduler")
    print("6. 'stop' - Stop the scheduler")
    print("7. 'quit' - Exit the program")
    print()
    
    while True:
        try:
            user_input = input("Enter command: ").strip()
            
            if user_input.lower() == 'quit':
                scheduler.stop_scheduler()
                break
            
            elif user_input.lower().startswith('add contact'):
                parts = user_input.split()
                if len(parts) >= 4:
                    name = parts[2]
                    phone = parts[3]
                    scheduler.add_contact(name, phone)
                else:
                    print("Usage: add contact <n> <phone>")
            
            elif user_input.lower().startswith('send now'):
                # Extract contact and message for immediate sending
                parts = user_input[8:].strip().split('"')
                if len(parts) >= 2:
                    contact = parts[0].strip()
                    message = parts[1]
                    phone_number = scheduler.get_contact_number(contact)
                    if phone_number:
                        print(f"Sending immediate message to {contact}...")
                        if scheduler.send_whatsapp_message_alternative(phone_number, message):
                            print(f"✅ Message sent to {contact}")
                        else:
                            print(f"❌ Failed to send message to {contact}")
                    else:
                        print(f"Contact '{contact}' not found")
                else:
                    print("Usage: send now <contact> \"<message>\"")
            
            elif user_input.lower().startswith('schedule'):
                message_text = user_input[8:].strip()  # Remove 'schedule' prefix
                scheduler.schedule_message(message_text)
            
            elif user_input.lower() == 'list':
                scheduler.list_scheduled_messages()
            
            elif user_input.lower() == 'start':
                scheduler.start_scheduler()
            
            elif user_input.lower() == 'stop':
                scheduler.stop_scheduler()
            
            else:
                print("Unknown command. Try 'help' for available commands.")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            scheduler.stop_scheduler()
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()