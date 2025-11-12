import cv2 as cv
from ultralytics import YOLO
import time
import yaml
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()


model = YOLO("yolov8n.pt")

# Notification Configuration from environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
EMAIL_FROM = os.getenv('EMAIL_FROM', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
EMAIL_TO = os.getenv('EMAIL_TO', '')

# Check if notifications are configured
telegram_configured = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
email_configured = bool(EMAIL_FROM and EMAIL_PASSWORD and EMAIL_TO)

if telegram_configured:
    print("📱 Telegram notifications enabled")
if email_configured:
    print("� Email notifications enabled")
if not telegram_configured and not email_configured:
    print("📱 No remote notifications configured - check your .env file")

#Security categories with their coco IDs
SECURITY_CLASSES = {
    #people
    'person': [0],

    #all common animals that could be intruders
    'animal': [14, 15, 16, 17, 18, 19, 20, 21, 22, 23],

    #common vehicles
    'vehicle': [1, 2, 3, 5, 7]
}

#Load configuration from YAML file
with open("coco.yaml", "r") as f: 
    coco_data = yaml.safe_load(f)
    CLASS_NAMES = coco_data["names"]

#alert settings
ALERT_COOLDOWN = 3  # seconds between alerts for the same category
last_alert_time = {} #track last alert times for each category

#colors for bounding boxes
COLORS = {
    'person': (0, 255, 0),   # Green -- highest threat
    'animal': (0, 165, 255),   # Orange -- medium threat
    'vehicle': (0, 255, 255)   # Yellow -- low threat
}

#alert priority. higher index means higher priority
ALERT_PRIORITY = {
    'person': 3,
    'animal': 2,
    'vehicle': 1
}

#function to play alert sound (prominent alerts)
def play_alert_sound(category):
    """Play an urgent alert sound based on the threat level."""
    try:
        #urgent sound alerts for security
        if category == 'person':
            # High priority - urgent multiple alarms
            os.system('say -v "Alex" -r 200 "SECURITY ALERT! PERSON DETECTED!" &')
            for _ in range(3):
                os.system('afplay /System/Library/Sounds/Sosumi.aiff &')
                time.sleep(0.1)
        elif category == 'animal':
            # Medium priority - moderate alert
            os.system('say -v "Alex" -r 180 "Animal detected in security zone!" &')
            for _ in range(2):
                os.system('afplay /System/Library/Sounds/Ping.aiff &')
                time.sleep(0.2)
        elif category == 'vehicle':
            # Low priority - single alert
            os.system('say -v "Alex" -r 160 "Vehicle detected!" &')
            os.system('afplay /System/Library/Sounds/Purr.aiff &')
    except Exception as e:
        # Fallback to system bell if audio fails
        for _ in range(3):
            print(f"\a", end="", flush=True)  # Multiple system bells
            time.sleep(0.1)
        print(f"\nAudio alert failed: {e}")

#function to send Telegram notification
def send_telegram_alert(message):
    """Send alert via Telegram bot."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram not configured - check your .env file")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        print(f"🔄 Sending Telegram alert...")
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print("Telegram alert sent successfully!")
            return True
        else:
            print(f"Telegram API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("Telegram notification timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("No internet connection for Telegram")
        return False
    except Exception as e:
        print(f"Telegram notification failed: {e}")
        return False

#function to send Email notification
def send_email_alert(message):
    """Send alert via Email using SMTP."""
    if not all([EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO]):
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = "🚨 Security Alert - Intrusion Detected"
        
        # Add body to email
        msg.attach(MIMEText(message, 'plain'))
        
        # Gmail SMTP configuration
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Enable security
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        
        # Send email
        text = msg.as_string()
        server.sendmail(EMAIL_FROM, EMAIL_TO, text)
        server.quit()
        return True
        
    except Exception as e:
        print(f"Email notification failed: {e}")
        return False

#function to test notifications on startup
def test_notifications():
    """Test notification systems on startup."""
    print("\nTesting notification systems...")
    
    test_message = " Security system started successfully!\nAll notifications are working."
    
    # Test Telegram
    if telegram_configured:
        if send_telegram_alert(test_message):
            print(" Telegram test: SUCCESS")
        else:
            print(" Telegram test: FAILED")
    
    # Test Email  
    if email_configured:
        if send_email_alert(test_message):
            print("Email test: SUCCESS")
        else:
            print("Email test: FAILED")
    
    if not telegram_configured and not email_configured:
        print("No remote notifications configured")
    
    print("-" * 60)

#function to log alerts
def send_notification(category, object_name):
    """Send a notification for the detected threat."""
    current_time = time.time()

    #check cooldown period
    if category in last_alert_time:
        if current_time - last_alert_time[category] < ALERT_COOLDOWN:
            return
    
    #update last alert time
    last_alert_time[category] = current_time

    #trigger subtle alert sound
    play_alert_sound(category)

    #create alert message
    priority = ALERT_PRIORITY[category]
    emoji = '🚨' if priority == 3 else '⚠️' if priority == 2 else '📢'
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert_message = f"{emoji} SECURITY ALERT [{timestamp}]\n{category.upper()}: {object_name} detected!"
    
    #display alert in console
    print(alert_message)
    
    #send remote notifications for all threats
    # Format notification message based on threat type
    if category == 'person':
        notification_msg = f"🚨 SECURITY BREACH!\n{timestamp}\nPerson detected: {object_name}\nLocation: Security Camera\nPriority: HIGH ALERT"
        
    elif category == 'animal':
        notification_msg = f"⚠️ ANIMAL INTRUSION!\n{timestamp}\n{object_name.title()} detected in security zone!\nLocation: Security Camera\nPriority: MEDIUM ALERT"
        
    elif category == 'vehicle':
        notification_msg = f"🚙 VEHICLE DETECTED!\n{timestamp}\n{object_name.title()} spotted in monitored area!\nLocation: Security Camera\nPriority: LOW ALERT"
    
    else:
        notification_msg = f"{emoji} SECURITY ALERT!\n{timestamp}\n{object_name} detected!\nLocation: Security Camera"
    
    # Send notifications 
    notification_sent = False
    
    if send_telegram_alert(notification_msg):
        print("📱 Telegram alert sent")
        notification_sent = True
    elif send_email_alert(notification_msg):
        print("📧 Email alert sent") 
        notification_sent = True
    
    if not notification_sent:
        print("📱 Remote notifications not configured")
        
    print(f"📝 {category.capitalize()} detection logged and processed")

#get category of detected object
def get_category(class_id):
    """Determine the security category of a detected object based on its class ID."""
    for category, class_ids in SECURITY_CLASSES.items():
        if class_id in class_ids:
            return category
    return None

#draw bounding boxes and labels
def draw_detections(frame, results):
    """Draw bounding boxes and labels on the frame for detected objects."""
    detected_objects = {'person': [], 'animal': [], 'vehicle': [] }
    for result in results:
        boxes = result.boxes
        for box in boxes:
            #get box cordinates
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            #get class and confidence
            cls = int(box.cls[0])
            conf = float(box.conf[0])

            #check if it's a security relevant object
            if conf > 0.5:
                category = get_category(cls)
                if category:
                    object_name = CLASS_NAMES.get(cls, f'class_{cls}')
                    detected_objects[category].append(object_name)

                    #draw bounding box
                    color = COLORS[category]
                    cv.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    #draw label background
                    label = f"{object_name} {conf:.2f}"
                    (w,h), _ = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                    cv.rectangle(frame, (x1, y1 - 20), (x1 + w, y1), color, -1)
                    #draw label text
                    cv.putText(frame, label, (x1, y1 - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    #draw category badge
                    badge = category.upper()
                    cv.putText(frame, badge, (x1, y1 - 40), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame, detected_objects

def main():
    #initialize video capture
    cap = cv.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    print("=" * 60)
    print("🛡️  SECURITY SURVEILLANCE SYSTEM ACTIVATED")
    print("=" * 60)
    print("📋 Monitoring Categories:")
    print("   🚨 PERSONS (High Priority)")
    print("   ⚠️  ANIMALS (Medium Priority)")
    print("   📢 VEHICLES (Low Priority)")
    
    # Test notifications on startup
    test_notifications()
    
    print("\nPress 'q' to quit")
    print("-" * 60)

    fps_start_time = time.time()
    fps_counter = 0
    fps = 0

    total_detections = {'person': 0, 'animal': 0, 'vehicle': 0}

    while True:
        ret, frame = cap.read()
        #flip frame horizontally for mirror effect
        frame = cv.flip(frame, 1)
        if not ret:
            print("Error: Could not read frame.")
            break

        #perform detection
        results = model(frame, verbose=False)

        #draw detections
        frame, detected_objects = draw_detections(frame, results)

        #send notifications for detected objects
        for category in ['person', 'animal', 'vehicle']:
            if detected_objects[category]:
                #send notification for the category
                send_notification(category, detected_objects[category][0])
                total_detections[category] += len(detected_objects[category])

                # Calculate FPS
        fps_counter += 1
        if time.time() - fps_start_time > 1:
            fps = fps_counter
            fps_counter = 0
            fps_start_time = time.time()

        # Draw status panel
        panel_height = 120
        overlay = frame.copy()
        cv.rectangle(overlay, (0, 0), (frame.shape[1], panel_height), (0, 0, 0), -1)
        cv.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Display FPS
        cv.putText(frame, f"FPS: {fps}", (10, 25), 
                   cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Display current detections with icons
        y_pos = 55
        # Check if any threats are detected
        any_threats = any(detected_objects[category] for category in ['person', 'animal', 'vehicle'])
        status_text = "🔴 BREACH" if any_threats else "🟢 SECURE"
        cv.putText(frame, f"Status: {status_text}", (10, y_pos),
                   cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        y_pos += 30
        for category, color in COLORS.items():
            count = len(detected_objects[category])
            if count > 0:
                objects_str = ', '.join(detected_objects[category][:3])  # Show first 3
                if len(detected_objects[category]) > 3:
                    objects_str += f" +{len(detected_objects[category])-3}"
                text = f"{category.upper()}: {objects_str}"
            else:
                text = f"{category.upper()}: None"
            cv.putText(frame, text, (10, y_pos),
                       cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            y_pos += 25
        
        # Show frame
        cv.imshow('Security Surveillance System', frame)
        
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    

    cap.release()
    cv.destroyAllWindows()
    
if __name__ == "__main__":
    main()