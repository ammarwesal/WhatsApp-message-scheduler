import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sqlite3
import threading
import schedule
import time
import pywhatkit as pwk
import pyautogui

class WhatsAppSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Scheduler - Professional")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize database
        self.db_path = "scheduler.db"
        self.init_database()
        
        # Scheduler state
        self.scheduler_running = False
        self.scheduler_thread = None
        
        # Create GUI
        self.create_widgets()
        self.load_data()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def init_database(self):
        """Initialize SQLite database"""
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
    
    def create_widgets(self):
        """Create the main GUI components"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="WhatsApp Message Scheduler", 
                              font=('Arial', 24, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Status frame
        status_frame = tk.Frame(main_frame, bg='#f0f0f0')
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.status_label = tk.Label(status_frame, text="Scheduler: STOPPED", 
                                   font=('Arial', 12, 'bold'), bg='#e74c3c', fg='white', 
                                   padx=10, pady=5)
        self.status_label.pack(side=tk.LEFT)
        
        self.toggle_button = tk.Button(status_frame, text="Start Scheduler", 
                                     command=self.toggle_scheduler,
                                     bg='#27ae60', fg='white', font=('Arial', 10, 'bold'),
                                     padx=20, pady=5)
        self.toggle_button.pack(side=tk.RIGHT)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_schedule_tab()
        self.create_contacts_tab()
        self.create_messages_tab()
    
    def create_schedule_tab(self):
        """Create the schedule message tab"""
        schedule_frame = ttk.Frame(self.notebook)
        self.notebook.add(schedule_frame, text="Schedule Message")
        
        # Left panel for form
        left_frame = tk.Frame(schedule_frame, bg='white', relief=tk.RAISED, bd=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)
        
        tk.Label(left_frame, text="Schedule New Message", font=('Arial', 16, 'bold'), 
                bg='white').pack(pady=10)
        
        # Contact selection
        tk.Label(left_frame, text="Select Contact:", font=('Arial', 10), 
                bg='white').pack(pady=(10, 5), anchor='w', padx=20)
        
        self.contact_var = tk.StringVar()
        self.contact_combo = ttk.Combobox(left_frame, textvariable=self.contact_var, 
                                        state='readonly', width=40)
        self.contact_combo.pack(pady=(0, 10), padx=20)
        
        # Message input
        tk.Label(left_frame, text="Message:", font=('Arial', 10), 
                bg='white').pack(pady=(10, 5), anchor='w', padx=20)
        
        self.message_text = tk.Text(left_frame, height=4, width=50, wrap=tk.WORD)
        self.message_text.pack(pady=(0, 10), padx=20)
        
        # Schedule type
        tk.Label(left_frame, text="Schedule Type:", font=('Arial', 10), 
                bg='white').pack(pady=(10, 5), anchor='w', padx=20)
        
        self.schedule_type_var = tk.StringVar(value="minutes")
        schedule_frame_radio = tk.Frame(left_frame, bg='white')
        schedule_frame_radio.pack(pady=(0, 10), padx=20, anchor='w')
        
        tk.Radiobutton(schedule_frame_radio, text="Minutes", variable=self.schedule_type_var,
                      value="minutes", bg='white', command=self.on_schedule_type_change).pack(side=tk.LEFT)
        tk.Radiobutton(schedule_frame_radio, text="Hours", variable=self.schedule_type_var,
                      value="hours", bg='white', command=self.on_schedule_type_change).pack(side=tk.LEFT)
        tk.Radiobutton(schedule_frame_radio, text="Days", variable=self.schedule_type_var,
                      value="days", bg='white', command=self.on_schedule_type_change).pack(side=tk.LEFT)
        tk.Radiobutton(schedule_frame_radio, text="Custom", variable=self.schedule_type_var,
                      value="custom", bg='white', command=self.on_schedule_type_change).pack(side=tk.LEFT)
        
        # Delay input frame
        self.delay_frame = tk.Frame(left_frame, bg='white')
        self.delay_frame.pack(pady=(0, 10), padx=20, fill='x')
        
        self.delay_label = tk.Label(self.delay_frame, text="Delay (minutes):", 
                                   font=('Arial', 10), bg='white')
        self.delay_label.pack(anchor='w')
        
        self.delay_var = tk.StringVar(value="5")
        self.delay_entry = tk.Entry(self.delay_frame, textvariable=self.delay_var, width=10)
        self.delay_entry.pack(anchor='w')
        
        # Custom datetime frame (initially hidden)
        self.custom_frame = tk.Frame(left_frame, bg='white')
        
        tk.Label(self.custom_frame, text="Date (YYYY-MM-DD):", 
                font=('Arial', 10), bg='white').pack(anchor='w')
        self.custom_date_var = tk.StringVar()
        tk.Entry(self.custom_frame, textvariable=self.custom_date_var, width=15).pack(anchor='w')
        
        tk.Label(self.custom_frame, text="Time (HH:MM):", 
                font=('Arial', 10), bg='white').pack(anchor='w')
        self.custom_time_var = tk.StringVar()
        tk.Entry(self.custom_frame, textvariable=self.custom_time_var, width=15).pack(anchor='w')
        
        # Schedule button
        schedule_btn = tk.Button(left_frame, text="Schedule Message", 
                               command=self.schedule_message,
                               bg='#3498db', fg='white', font=('Arial', 12, 'bold'),
                               padx=20, pady=10)
        schedule_btn.pack(pady=20)
        
        # Right panel for preview
        right_frame = tk.Frame(schedule_frame, bg='white', relief=tk.RAISED, bd=1)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        
        tk.Label(right_frame, text="Quick Actions", font=('Arial', 16, 'bold'), 
                bg='white').pack(pady=10)
        
        # Quick schedule buttons
        quick_frame = tk.Frame(right_frame, bg='white')
        quick_frame.pack(pady=10)
        
        tk.Button(quick_frame, text="Send in 1 min", 
                 command=lambda: self.quick_schedule(1, "minutes"),
                 bg='#e67e22', fg='white', padx=10).pack(pady=2, fill='x')
        tk.Button(quick_frame, text="Send in 5 min", 
                 command=lambda: self.quick_schedule(5, "minutes"),
                 bg='#e67e22', fg='white', padx=10).pack(pady=2, fill='x')
        tk.Button(quick_frame, text="Send in 1 hour", 
                 command=lambda: self.quick_schedule(1, "hours"),
                 bg='#e67e22', fg='white', padx=10).pack(pady=2, fill='x')
        tk.Button(quick_frame, text="Send tomorrow", 
                 command=lambda: self.quick_schedule(1, "days"),
                 bg='#e67e22', fg='white', padx=10).pack(pady=2, fill='x')
    
    def create_contacts_tab(self):
        """Create the contacts management tab"""
        contacts_frame = ttk.Frame(self.notebook)
        self.notebook.add(contacts_frame, text="Contacts")
        
        # Left panel for adding contacts
        left_frame = tk.Frame(contacts_frame, bg='white', relief=tk.RAISED, bd=1)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=10)
        
        tk.Label(left_frame, text="Add New Contact", font=('Arial', 16, 'bold'), 
                bg='white').pack(pady=10)
        
        tk.Label(left_frame, text="Name:", font=('Arial', 10), bg='white').pack(pady=(10, 5))
        self.contact_name_var = tk.StringVar()
        tk.Entry(left_frame, textvariable=self.contact_name_var, width=30).pack()
        
        tk.Label(left_frame, text="Phone Number:", font=('Arial', 10), bg='white').pack(pady=(10, 5))
        self.contact_phone_var = tk.StringVar()
        tk.Entry(left_frame, textvariable=self.contact_phone_var, width=30).pack()
        
        tk.Button(left_frame, text="Add Contact", command=self.add_contact,
                 bg='#27ae60', fg='white', font=('Arial', 10, 'bold'), 
                 padx=20, pady=5).pack(pady=20)
        
        # Right panel for contacts list
        right_frame = tk.Frame(contacts_frame, bg='white', relief=tk.RAISED, bd=1)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        
        tk.Label(right_frame, text="Contacts List", font=('Arial', 16, 'bold'), 
                bg='white').pack(pady=10)
        
        # Treeview for contacts
        self.contacts_tree = ttk.Treeview(right_frame, columns=('Name', 'Phone'), show='headings')
        self.contacts_tree.heading('Name', text='Name')
        self.contacts_tree.heading('Phone', text='Phone Number')
        self.contacts_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Delete button
        tk.Button(right_frame, text="Delete Selected", command=self.delete_contact,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(pady=10)
    
    def create_messages_tab(self):
        """Create the scheduled messages tab"""
        messages_frame = ttk.Frame(self.notebook)
        self.notebook.add(messages_frame, text="Scheduled Messages")
        
        # Header
        header_frame = tk.Frame(messages_frame, bg='white')
        header_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(header_frame, text="Scheduled Messages", font=('Arial', 16, 'bold'), 
                bg='white').pack(side=tk.LEFT, padx=10)
        
        tk.Button(header_frame, text="Refresh", command=self.refresh_messages,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.RIGHT, padx=10)
        
        # Messages treeview
        self.messages_tree = ttk.Treeview(messages_frame, 
                                        columns=('Recipient', 'Message', 'Scheduled Time', 'Status'), 
                                        show='headings')
        self.messages_tree.heading('Recipient', text='Recipient')
        self.messages_tree.heading('Message', text='Message')
        self.messages_tree.heading('Scheduled Time', text='Scheduled Time')
        self.messages_tree.heading('Status', text='Status')
        
        # Configure column widths
        self.messages_tree.column('Recipient', width=120)
        self.messages_tree.column('Message', width=300)
        self.messages_tree.column('Scheduled Time', width=150)
        self.messages_tree.column('Status', width=100)
        
        self.messages_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Buttons frame
        buttons_frame = tk.Frame(messages_frame, bg='white')
        buttons_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(buttons_frame, text="Delete Selected", command=self.delete_message,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)
        
        tk.Button(buttons_frame, text="Send Now", command=self.send_now,
                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)
    
    def on_schedule_type_change(self):
        """Handle schedule type change"""
        if self.schedule_type_var.get() == "custom":
            self.delay_frame.pack_forget()
            self.custom_frame.pack(pady=(0, 10), padx=20, fill='x')
        else:
            self.custom_frame.pack_forget()
            self.delay_frame.pack(pady=(0, 10), padx=20, fill='x')
            
            # Update delay label
            schedule_type = self.schedule_type_var.get()
            self.delay_label.config(text=f"Delay ({schedule_type}):")
    
    def quick_schedule(self, delay, unit):
        """Quick schedule with predefined delay"""
        if not self.contact_var.get() or not self.message_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Missing Information", "Please select a contact and enter a message")
            return
        
        self.schedule_type_var.set(unit)
        self.delay_var.set(str(delay))
        self.on_schedule_type_change()
        self.schedule_message()
    
    def add_contact(self):
        """Add a new contact"""
        name = self.contact_name_var.get().strip()
        phone = self.contact_phone_var.get().strip()
        
        if not name or not phone:
            messagebox.showwarning("Missing Information", "Please enter both name and phone number")
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT OR REPLACE INTO contacts (name, phone_number) VALUES (?, ?)",
                         (name.lower(), phone))
            conn.commit()
            messagebox.showinfo("Success", f"Contact {name} added successfully!")
            
            # Clear fields
            self.contact_name_var.set("")
            self.contact_phone_var.set("")
            
            # Refresh displays
            self.load_contacts()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add contact: {e}")
        finally:
            conn.close()
    
    def delete_contact(self):
        """Delete selected contact"""
        selection = self.contacts_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a contact to delete")
            return
        
        item = self.contacts_tree.item(selection[0])
        name = item['values'][0]
        
        if messagebox.askyesno("Confirm Delete", f"Delete contact {name}?"):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute("DELETE FROM contacts WHERE name = ?", (name.lower(),))
                conn.commit()
                messagebox.showinfo("Success", f"Contact {name} deleted successfully!")
                self.load_contacts()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete contact: {e}")
            finally:
                conn.close()
    
    def schedule_message(self):
        """Schedule a new message"""
        contact_name = self.contact_var.get()
        message = self.message_text.get(1.0, tk.END).strip()
        
        if not contact_name or not message:
            messagebox.showwarning("Missing Information", "Please select a contact and enter a message")
            return
        
        # Get contact phone number
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT phone_number FROM contacts WHERE name = ?", (contact_name.lower(),))
        result = cursor.fetchone()
        
        if not result:
            messagebox.showerror("Error", f"Contact {contact_name} not found")
            conn.close()
            return
        
        phone_number = result[0]
        
        # Calculate scheduled time
        try:
            if self.schedule_type_var.get() == "custom":
                date_str = self.custom_date_var.get()
                time_str = self.custom_time_var.get()
                scheduled_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            else:
                delay = int(self.delay_var.get())
                schedule_type = self.schedule_type_var.get()
                
                multiplier = {"minutes": 1, "hours": 60, "days": 1440}[schedule_type]
                scheduled_time = datetime.now() + timedelta(minutes=delay * multiplier)
        
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please check your date/time format: {e}")
            conn.close()
            return
        
        # Save to database
        try:
            cursor.execute('''
                INSERT INTO scheduled_messages 
                (recipient_name, phone_number, message, scheduled_time)
                VALUES (?, ?, ?, ?)
            ''', (contact_name, phone_number, message, scheduled_time))
            
            conn.commit()
            messagebox.showinfo("Success", 
                              f"Message scheduled for {contact_name} at {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Clear form
            self.message_text.delete(1.0, tk.END)
            self.contact_var.set("")
            
            # Refresh messages list
            self.refresh_messages()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to schedule message: {e}")
        finally:
            conn.close()
    
    def delete_message(self):
        """Delete selected scheduled message"""
        selection = self.messages_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a message to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Delete selected message?"):
            item = self.messages_tree.item(selection[0])
            # We need to get the message ID somehow - let's store it in tags
            message_id = self.messages_tree.item(selection[0])['tags'][0] if self.messages_tree.item(selection[0])['tags'] else None
            
            if message_id:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                try:
                    cursor.execute("DELETE FROM scheduled_messages WHERE id = ?", (message_id,))
                    conn.commit()
                    messagebox.showinfo("Success", "Message deleted successfully!")
                    self.refresh_messages()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete message: {e}")
                finally:
                    conn.close()
    
    def send_now(self):
        """Send selected message immediately"""
        selection = self.messages_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a message to send")
            return
        
        message_id = self.messages_tree.item(selection[0])['tags'][0] if self.messages_tree.item(selection[0])['tags'] else None
        
        if message_id:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute("SELECT phone_number, message FROM scheduled_messages WHERE id = ?", (message_id,))
                result = cursor.fetchone()
                
                if result:
                    phone_number, message = result
                    
                    # Send message
                    if self.send_whatsapp_message(phone_number, message):
                        cursor.execute("UPDATE scheduled_messages SET status = 'sent', sent_at = ? WHERE id = ?",
                                     (datetime.now(), message_id))
                        conn.commit()
                        messagebox.showinfo("Success", "Message sent successfully!")
                        self.refresh_messages()
                    else:
                        messagebox.showerror("Error", "Failed to send message")
                        
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send message: {e}")
            finally:
                conn.close()
    
    def send_whatsapp_message(self, phone_number, message):
        """Send WhatsApp message"""
        try:
            import pyautogui
            import time as time_module
            
            phone_number = phone_number.replace('+', '').replace('-', '').replace(' ', '')
            
            if not phone_number.startswith('91') and len(phone_number) == 10:
                phone_number = '91' + phone_number
            
            now = datetime.now()
            send_hour = now.hour
            send_minute = now.minute + 2
            
            if send_minute >= 60:
                send_minute -= 60
                send_hour += 1
                if send_hour >= 24:
                    send_hour = 0
            
            pwk.sendwhatmsg(f"+{phone_number}", message, send_hour, send_minute, 
                          wait_time=15, tab_close=False, close_time=2)
            
            time_module.sleep(3)
            pyautogui.press('enter')
            time_module.sleep(2)
            pyautogui.hotkey('ctrl', 'w')
            
            return True
            
        except Exception as e:
            print(f"Failed to send message: {e}")
            return False
    
    def load_contacts(self):
        """Load contacts into combo box and tree view"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, phone_number FROM contacts ORDER BY name")
        contacts = cursor.fetchall()
        conn.close()
        
        # Update combo box
        contact_names = [contact[0].title() for contact in contacts]
        self.contact_combo['values'] = contact_names
        
        # Update tree view
        for item in self.contacts_tree.get_children():
            self.contacts_tree.delete(item)
        
        for name, phone in contacts:
            self.contacts_tree.insert('', 'end', values=(name.title(), phone))
    
    def refresh_messages(self):
        """Refresh the messages list"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, recipient_name, message, scheduled_time, status 
            FROM scheduled_messages 
            ORDER BY scheduled_time DESC
        ''')
        messages = cursor.fetchall()
        conn.close()
        
        # Clear existing items
        for item in self.messages_tree.get_children():
            self.messages_tree.delete(item)
        
        # Add messages
        for msg_id, recipient, message, scheduled_time, status in messages:
            # Truncate long messages
            display_message = message[:50] + "..." if len(message) > 50 else message
            
            # Format datetime
            try:
                dt = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                dt = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M:%S")
            
            formatted_time = dt.strftime("%Y-%m-%d %H:%M")
            
            self.messages_tree.insert('', 'end', 
                                    values=(recipient.title(), display_message, formatted_time, status.title()),
                                    tags=(str(msg_id),))
    
    def load_data(self):
        """Load initial data"""
        self.load_contacts()
        self.refresh_messages()
    
    def toggle_scheduler(self):
        """Start or stop the scheduler"""
        if self.scheduler_running:
            self.stop_scheduler()
        else:
            self.start_scheduler()
    
    def start_scheduler(self):
        """Start the background scheduler"""
        if not self.scheduler_running:
            self.scheduler_running = True
            self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
            self.scheduler_thread.start()
            
            self.status_label.config(text="Scheduler: RUNNING", bg='#27ae60')
            self.toggle_button.config(text="Stop Scheduler", bg='#e74c3c')
            
            messagebox.showinfo("Scheduler Started", "Message scheduler is now running in the background!")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.scheduler_running = False
        schedule.clear()
        
        self.status_label.config(text="Scheduler: STOPPED", bg='#e74c3c')
        self.toggle_button.config(text="Start Scheduler", bg='#27ae60')
        
        messagebox.showinfo("Scheduler Stopped", "Message scheduler has been stopped.")
    
    def run_scheduler(self):
        """Run the scheduler in background"""
        schedule.every(1).minutes.do(self.check_and_send_messages)
        
        while self.scheduler_running:
            schedule.run_pending()
            time.sleep(1)
    
    def check_and_send_messages(self):
        """Check for pending messages and send them"""
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
        
        # Refresh the GUI if messages were processed
        if pending_messages:
            self.root.after(0, self.refresh_messages)
    
    def on_closing(self):
        """Handle window closing"""
        if self.scheduler_running:
            if messagebox.askokcancel("Quit", "Scheduler is running. Do you want to quit?"):
                self.stop_scheduler()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    root = tk.Tk()
    app = WhatsAppSchedulerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()