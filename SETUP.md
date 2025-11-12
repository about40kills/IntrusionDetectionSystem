# Security Intrusion Detection System

An intelligent security monitoring system using YOLOv8 computer vision with real-time alerts via Telegram and Email.

## Features

- 🔍 **Real-time Detection**: Monitors for persons, animals, and vehicles using YOLOv8
- 📱 **Smart Notifications**: Telegram and Email alerts for security breaches
- 🔊 **Audio Alerts**: Priority-based sound notifications (macOS compatible)
- ⏰ **Cooldown Protection**: Prevents notification spam with configurable cooldowns
- 📊 **Live Statistics**: Real-time detection counters and FPS monitoring
- 🎥 **Live Video Feed**: Real-time camera feed with bounding boxes and status overlay

## Requirements

- Python 3.8+
- Webcam or video capture device
- macOS (for audio alerts) or compatible system

## Installation

1. **Clone the repository**

```bash
git clone <your-repo-url>
cd IntrusionDetectionSystem
```

2. **Create virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure notifications (optional)**

```bash
cp .env.example .env
# Edit .env with your Telegram/Email credentials
```

## Notification Setup

### Telegram (Free & Recommended)

1. **Create a Telegram Bot**:

   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot` and follow the instructions
   - Copy the bot token

2. **Get your Chat ID**:

   - Send a message to your bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your chat ID in the JSON response

3. **Update .env file**:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

### Email (Optional - Gmail Recommended)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:

   - Go to [Google Account Settings](https://myaccount.google.com/apppasswords)
   - Generate a new app password for "Mail"
   - Use this password (not your regular password)

3. **Update .env file**:

```env
EMAIL_FROM=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password_here
EMAIL_TO=recipient_email@example.com
```

## Usage

```bash
python3 main.py
```

### Controls

- **Press 'q'** to quit the application
- **Real-time display** shows live camera feed with detections
- **Status panel** displays FPS, security status, and current detections

### Alert Behavior

- 🚨 **Persons** (High Priority): Immediate remote notifications + urgent audio alerts
- ⚠️ **Animals** (Medium Priority): Remote notifications + moderate audio alerts
- 📢 **Vehicles** (Low Priority): Remote notifications + subtle audio alerts

## Security Categories

| Category    | Priority | Alert Type              | COCO Classes                                                              |
| ----------- | -------- | ----------------------- | ------------------------------------------------------------------------- |
| **Person**  | High     | Remote + Urgent Audio   | person (0)                                                                |
| **Animal**  | Medium   | Remote + Moderate Audio | bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe (14-23) |
| **Vehicle** | Low      | Remote + Subtle Audio   | bicycle, car, motorcycle, bus, truck (1-3, 5, 7)                          |

## Configuration

### Environment Variables (.env)

All sensitive credentials are stored in `.env` file (not tracked by git).

```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Email Configuration
EMAIL_FROM=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
EMAIL_TO=alert_recipient@example.com
```

### Detection Settings

- **Confidence Threshold**: 0.5 (configurable in code)
- **Alert Cooldown**: 3 seconds between alerts for same category
- **Audio Alerts**: macOS system sounds and text-to-speech

## Project Structure

```
IntrusionDetectionSystem/
├── main.py                 # Main application script
├── coco.yaml              # COCO dataset class names
├── yolov8n.pt             # YOLOv8 nano model weights
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── .env                   # Environment variables (not tracked)
├── .gitignore            # Git ignore rules
└── SETUP.md              # This setup guide
```

## Troubleshooting

### Common Issues

1. **"Could not open video"**

   - Ensure your webcam is connected and not used by other applications
   - Try changing camera index in `cv.VideoCapture(0)` to `cv.VideoCapture(1)`

2. **Telegram notifications not working**

   - Verify bot token and chat ID in `.env`
   - Ensure internet connection is available
   - Check bot permissions and chat ID

3. **Email notifications failing**

   - Use Gmail app password, not regular password
   - Enable "Less secure app access" or use app passwords
   - Check SMTP settings for your email provider

4. **Audio alerts not working**
   - Ensure you're on macOS for `say` and `afplay` commands
   - Check system audio settings

### Performance Tips

- Use YOLOv8 nano model for better performance on lower-end hardware
- Adjust confidence threshold in `draw_detections()` function
- Close other applications using the camera
- Ensure good lighting for better detection accuracy

## Dependencies

- **opencv-python**: Computer vision and video processing
- **ultralytics**: YOLOv8 object detection
- **pyyaml**: Configuration file parsing
- **requests**: HTTP requests for Telegram API
- **python-dotenv**: Environment variable management

## License

This project is open-source. Please refer to the repository for licensing information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:

- Check the troubleshooting section above
- Review the code comments in `main.py`
- Ensure all dependencies are properly installed
