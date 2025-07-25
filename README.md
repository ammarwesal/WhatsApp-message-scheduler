# WhatsApp Message Scheduler

An intelligent WhatsApp message scheduler that allows you to schedule and send WhatsApp messages automatically. The application features both a command-line interface and a professional GUI, with natural language processing for easy message scheduling.

## Features

### Core Features
- **Automated Message Scheduling**: Schedule WhatsApp messages for future delivery
- **Natural Language Processing**: Use conversational commands like "Send john 'meeting reminder' in 2 hours"
- **Contact Management**: Store and manage contacts with names and phone numbers
- **Multiple Interfaces**: Choose between CLI and GUI versions
- **SQLite Database**: Persistent storage for contacts and scheduled messages
- **Background Scheduler**: Automatic message sending when scheduled time arrives
- **Message Status Tracking**: Track pending, sent, and failed messages

### GUI Features (Professional Interface)
- **Tabbed Interface**: Separate tabs for scheduling, contacts, and message management
- **Quick Schedule Buttons**: One-click scheduling for common time intervals
- **Real-time Status Updates**: Live scheduler status and message tracking
- **Contact Management**: Add, edit, and delete contacts through GUI
- **Message History**: View all scheduled messages with status updates
- **Send Now Option**: Instantly send scheduled messages

### CLI Features (Command-line Interface)
- **Natural Language Commands**: Intuitive text-based scheduling
- **Interactive Commands**: Easy-to-use command structure
- **Real-time Feedback**: Immediate confirmation and status updates

## Prerequisites

- Python 3.7 or higher
- Google Chrome browser (for WhatsApp Web)
- Active WhatsApp account
- Internet connection

## Installation

1. **Clone or download the project files**
   ```bash
   git clone <repository-url>
   cd whatsapp-scheduler
   ```

2. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure WhatsApp Web Access**
   - Open Google Chrome
   - Go to [WhatsApp Web](https://web.whatsapp.com)
   - Scan QR code with your phone to log in
   - Keep the browser tab open while using the application

## Usage

### GUI Version (Recommended)

Run the GUI application:
```bash
python whatsapp_scheduler_gui.py
```

**Features:**
1. **Schedule Tab**: Create new scheduled messages
   - Select contact from dropdown
   - Enter your message
   - Choose schedule type (minutes, hours, days, or custom date/time)
   - Use quick schedule buttons for common intervals

2. **Contacts Tab**: Manage your contacts
   - Add new contacts with name and phone number
   - View all contacts in a list
   - Delete unwanted contacts

3. **Messages Tab**: View and manage scheduled messages
   - See all scheduled messages with status
   - Delete pending messages
   - Send messages immediately

4. **Scheduler Control**
   - Start/stop the background scheduler
   - Monitor scheduler status in real-time

### CLI Version

Run the command-line application:
```bash
python main.py
```

**Available Commands:**
- `add contact <name> <phone>` - Add a new contact
- `schedule <natural_language_command>` - Schedule a message
- `send now <contact> "<message>"` - Send immediate message
- `list` - Show all scheduled messages
- `start` - Start the background scheduler
- `stop` - Stop the scheduler
- `quit` - Exit the application

**Natural Language Examples:**
```bash
schedule Send john "meeting at 3pm" in 2 hours
schedule Message sarah "happy birthday" tomorrow  
schedule Remind alex "call mom" in 30 minutes
schedule Send you "take medicine" in 1 hour
```

## Phone Number Format

Use international format with country code:
- **India**: +919876543210 or 919876543210
- **US**: +11234567890
- **UK**: +447123456789

The application automatically adds India's country code (+91) if not specified.

## File Structure

```
whatsapp-scheduler/
│
├── main.py                     # CLI version of the application
├── whatsapp_scheduler_gui.py   # GUI version of the application
├── requirements.txt            # Python dependencies
├── scheduler.db               # SQLite database (auto-created)
├── PyWhatKit_DB.txt          # Message log (auto-created)
└── README.md                 # Project documentation
```

## Database Schema

The application uses SQLite with two main tables:

### contacts
- `Id`: Primary key
- `name`: Contact name (stored in lowercase)
- `phone_number`: Phone number with country code

### scheduled_messages  
- `id`: Primary key
- `recipient_name`: Contact name
- `phone_number`: Recipient's phone number
- `message`: Message content
- `scheduled_time`: When to send the message
- `created_at`: When the message was scheduled
- `status`: pending/sent/failed
- `sent_at`: When the message was actually sent

## Dependencies

### Core Dependencies
- **pywhatkit**: WhatsApp Web automation
- **schedule**: Task scheduling
- **pyautogui**: GUI automation for message sending
- **sqlite3**: Database management (built-in)

### GUI Dependencies  
- **tkinter**: GUI framework (built-in)
- **threading**: Background task management (built-in)

### Additional Modules
- **datetime**: Date and time handling (built-in)
- **re**: Regular expressions for parsing (built-in)
- **typing**: Type hints (built-in)
- **json**: JSON handling (built-in)

## How It Works

1. **Message Scheduling**: Messages are stored in SQLite database with scheduled time
2. **Background Monitoring**: Scheduler runs every minute checking for due messages  
3. **WhatsApp Integration**: Uses pywhatkit to open WhatsApp Web and send messages
4. **Auto-typing**: Automatically types message and presses Enter
5. **Status Updates**: Database updated with delivery status

## Troubleshooting

### Common Issues

1. **WhatsApp Web not logged in**
   - Ensure you're logged into WhatsApp Web in Chrome
   - Keep the browser tab open during operation

2. **Message sending fails**
   - Check internet connection
   - Verify WhatsApp Web is responsive
   - Ensure phone number format is correct

3. **GUI not opening**
   - Check if tkinter is installed: `python -m tkinter`
   - Try running CLI version instead

4. **Natural language parsing fails**
   - Use quotes around messages: `"your message"`
   - Include timing: `in X minutes/hours/days`
   - Specify contact name clearly

5. **Database errors**
   - Delete `scheduler.db` to reset database
   - Check file permissions in application directory

### Error Solutions

**"Contact not found"**
- Add contact first using GUI or CLI
- Check spelling of contact name

**"Could not parse request"**
- Follow the command format examples
- Use quotes around message text
- Include proper timing keywords

**"Failed to send message"**
- Restart Chrome browser
- Re-login to WhatsApp Web
- Check recipient's phone number

## Advanced Features

### Custom Scheduling
- **Flexible timing**: Minutes, hours, days, or specific date/time
- **Multiple formats**: Natural language or precise datetime
- **Recurring options**: Modify code to add recurring messages

### Contact Management
- **Bulk import**: Extend to import contacts from CSV
- **Groups**: Add support for WhatsApp groups
- **Backup**: Export/import contact database

### Message Templates
- **Pre-defined messages**: Create common message templates
- **Variables**: Use placeholders for personalized messages
- **Rich content**: Add emoji and formatting support

## Security Considerations

- **Local storage**: All data stored locally in SQLite
- **No cloud sync**: Messages and contacts remain on your device
- **Browser automation**: Requires WhatsApp Web access
- **Phone verification**: Uses your WhatsApp account credentials

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test thoroughly with different scenarios
5. Submit a pull request

## Future Enhancements

- **Rich media support**: Images, documents, videos
- **Group messaging**: Send to WhatsApp groups
- **Message templates**: Pre-defined message formats
- **Recurring messages**: Daily/weekly/monthly schedules
- **Multiple accounts**: Support for multiple WhatsApp accounts
- **Analytics**: Message delivery statistics
- **Mobile app**: Android/iOS companion app

## License

This project is open source. Please check the repository for specific license information.

## Disclaimer

This application automates WhatsApp Web using browser automation. Use responsibly and in accordance with WhatsApp's Terms of Service. The developers are not responsible for any misuse or violations of WhatsApp's policies.

## Support

For issues and questions:
- Check the troubleshooting section above
- Ensure all dependencies are installed correctly
- Verify WhatsApp Web is accessible and logged in
- Test with simple messages first before complex scheduling

---

**Note**: This application requires WhatsApp Web to be accessible and may need adjustments based on WhatsApp Web updates. Always test with non-critical messages first.
