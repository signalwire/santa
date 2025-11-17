# 🎅 Santa AI Setup & Testing Guide

## Quick Start

### 1. Install Dependencies
```bash
# Activate your Python virtual environment (as per your note)
source venv/bin/activate  # or use your container

# Install Python packages
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit the `.env` file with your actual credentials:

```env
# SignalWire Configuration (REQUIRED)
SIGNALWIRE_PROJECT_ID=your_actual_project_id
SIGNALWIRE_TOKEN=your_actual_token
SIGNALWIRE_SPACE=your_space.signalwire.com

# RapidAPI Configuration (REQUIRED)
# Get your key from: https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-amazon-data
RAPIDAPI_KEY=your_rapidapi_key_here
```

### 3. Update Frontend Token

Edit `/web/app.js` line 6:
```javascript
const STATIC_TOKEN = 'YOUR_SIGNALWIRE_TOKEN_HERE'; // Replace with your guest token
```

To get a guest token, use the SignalWire Guest Token API as documented in the Holyguacamole project.

### 4. Add Santa Videos (Optional)

Place these files in the `/web` directory:
- `santa_idle.mp4` - Santa waiting/listening animation
- `santa_talking.mp4` - Santa speaking animation

For testing, you can use placeholder videos or animated GIFs.

### 5. Run the Application

```bash
python santa_ai.py
```

The server will start on `http://localhost:5000`

## Features Implemented

### ✅ Backend Features
- **Dynamic Gift Search**: Real-time Amazon product search via RapidAPI
- **Santa Persona**: Jolly, warm personality with Christmas-themed responses
- **Voice Configuration**: ElevenLabs Santa voice with natural speech patterns
- **SWAIG Functions**:
  - `search_gifts()` - Search Amazon for gift ideas
  - `select_gift()` - Confirm gift selection
  - `send_gift_sms()` - Send details via SMS
  - `check_nice_list()` - Fun nice list checker
- **Mock Data Fallback**: Works without RapidAPI for testing

### ✅ Frontend Features
- **Festive UI Elements**:
  - Animated snowfall effect
  - Aurora borealis background animation
  - Christmas countdown timer
  - Magic meter animation
  - Confetti on gift selection

- **Dynamic Gift Display**:
  - Real-time product cards from API
  - Hover effects and animations
  - Gift showcase for selected item
  - Option numbering (1, 2, 3)

- **Interactive Elements**:
  - Santa video/avatar area
  - Speech bubble for Santa's messages
  - Workshop scene with animated elves
  - Nice list checker display

### ✅ Visual Effects
- Snow particles falling continuously
- Northern lights in background
- Floating gift boxes and elves
- Sparkle animations on headers
- Pulse effects on buttons
- Slide-in animations for gift cards
- 3D hover effects on selection

## Testing the Application

### Test Without Phone Call
1. Open `http://localhost:5000` in browser
2. The UI will load with all visual effects
3. Gift cards can be tested with mock data

### Test Voice Interaction
1. Configure SignalWire phone number to point to your SWML endpoint
2. Call the configured number
3. Or use the web interface with proper guest token

### Test Conversation Flow
```
Santa: "Ho ho ho! What's your name?"
Child: "My name is Emma"
Santa: "What would you like for Christmas?"
Child: "I want a doll"
Santa: [Searches and presents 3 doll options]
Child: "I want number 2"
Santa: [Confirms selection and sends SMS]
```

### API Test Commands

Test the backend directly:
```bash
# Check health
curl http://localhost:5000/health

# Get system info
curl http://localhost:5000/api/info
```

## Troubleshooting

### RapidAPI Not Working?
- The app includes mock data fallback
- Check your API key is correct
- Verify you're subscribed to the Real-Time Amazon Data API

### No Audio/Video?
- Add placeholder videos in `/web` directory
- Audio files are optional (jingle_bells.mp3, hohoho.mp3)

### SignalWire Connection Issues?
- Verify your credentials in `.env`
- Check guest token in `app.js`
- Ensure port 5000 is not blocked

## Next Steps

### To Complete:
1. **Add Santa Videos**: Create or find Santa avatar videos
2. **Test with Real API**: Subscribe to RapidAPI and test real searches
3. **Deploy to Production**: Use HTTPS domain for WebRTC
4. **Customize Further**: Add more animations, sound effects, or features

### Production Deployment:
```bash
# Use a process manager
pm2 start santa_ai.py --name santa-ai

# Or with systemd service
# Or deploy to cloud (Heroku, AWS, etc.)
```

## Customization Ideas

- Add more holiday music/sounds
- Create gift wrapping animation
- Add reindeer flying across screen
- Implement gift categories (toys, books, games)
- Add parent notification system
- Create gift history tracking
- Add multi-language support

## Resources

- [SignalWire Docs](https://developer.signalwire.com)
- [RapidAPI Amazon Data](https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-amazon-data)
- [ElevenLabs Voices](https://elevenlabs.io)

---

🎄 **Ready to spread Christmas joy!** 🎅

Start the app and watch the magic happen!