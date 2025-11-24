# 🎅 Santa's Workshop AI - Interactive Voice Assistant

An enchanting AI-powered Santa experience that allows children (and adults!) to have real-time voice conversations with Santa Claus. Built with SignalWire's AI Agent technology, this application features dynamic gift searching, real-time product displays, and a magical Christmas atmosphere.

![Santa's Workshop](https://img.shields.io/badge/SignalWire-AI%20Agent-red?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9%2B-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

## 🎄 Features

### Voice Interaction
- **Real-time conversations** with Santa using SignalWire's AI Agent
- **ElevenLabs voice synthesis** for authentic Santa voice
- **Natural language processing** for understanding gift requests
- **WebRTC video/audio** streaming with festive backgrounds

### Dynamic Gift Search
- **Real-time Amazon product search** via RapidAPI
- **Visual gift gallery** with product images and details
- **Interactive gift selection** with 3D card effects
- **Smart product recommendations** based on conversation context

### Festive UI Elements
- **Animated snowfall** with accumulation effect
- **Twinkling Christmas lights** with individual bulb animations
- **Aurora Borealis** background effects
- **Christmas countdown** timer
- **Background holiday music** with volume controls

### Interactive Features
- **Nice list checker** with animated results
- **Gift selection confirmation** with confetti effects
- **Responsive design** for all devices

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- SignalWire account with AI Agent access
- RapidAPI account for Amazon product search

### Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/signalwire/santa.git
cd santa
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
# RapidAPI Configuration
RAPIDAPI_KEY=your_rapidapi_key
RAPIDAPI_HOST=real-time-amazon-data.p.rapidapi.com

# Basic Auth for SWML endpoints (optional, but recommended for production)
SWML_BASIC_AUTH_USER=your_username
SWML_BASIC_AUTH_PASSWORD=your_password

# Server Configuration
PORT=5000
HOST=0.0.0.0
```

### Running Locally

1. Start the application:
```bash
python santa_ai.py
```

2. Access the application:
   - Open your browser to `http://localhost:5000`
   - Click "Talk to Santa!" to begin

3. Configure SignalWire phone number:
   - Point your SignalWire number to: `https://your-domain.com/santa`
   - Set the webhook type to "Voice"

## 🎁 Usage Guide

### Starting a Conversation
1. Click the green "Talk to Santa!" button
2. Allow microphone/camera permissions when prompted
3. Santa will greet you with his jolly voice
4. Tell Santa what gifts you'd like for Christmas

### Searching for Gifts
- Say something like: "I want a toy robot"
- Santa will search his workshop catalog
- 4 gift options will appear with images and details
- Say "option 1", "option 2", "option 3", or "option 4" to select

### Interactive Elements
- **Mute Button**: Toggle your microphone during the call
- **Snow Effect**: Watch snow accumulate at the bottom
- **Christmas Lights**: Individual bulbs twinkle independently
- **Gift Cards**: Hover for 3D effects, click to select

## 🛠️ Architecture

### Backend (Python/SignalWire Agents SDK)
```
santa_ai.py
├── SantaAIAgent class (AgentBase)
│   ├── search_gifts()      # SWAIG function
│   ├── select_gift()       # SWAIG function
│   └── check_nice_list()   # SWAIG function
├── create_server()         # AgentServer setup
└── RapidAPI Integration
```

### Frontend (HTML/CSS/JavaScript)
```
web/
├── index.html          # Main application page
├── app.js             # SignalWire SDK integration
├── styles.css         # Festive styling & animations
└── media/             # Audio/video assets
```

### State Management
- **Gift State**: Tracks search results and selections
- **Conversation Context**: Manages dialogue flow
- **Frontend Events**: Real-time UI updates via WebSocket

## 📱 Deployment

### Dokku Deployment

1. Create a Dokku app:
```bash
dokku apps:create santa-ai
```

2. Set environment variables:
```bash
dokku config:set santa-ai RAPIDAPI_KEY=xxx
dokku config:set santa-ai SWML_BASIC_AUTH_USER=xxx
dokku config:set santa-ai SWML_BASIC_AUTH_PASSWORD=xxx
```

3. Deploy:
```bash
git remote add dokku dokku@your-server:santa-ai
git push dokku main
```

### Production Considerations

- **SSL/TLS**: Required for WebRTC connections
- **CORS**: Configure for your domain
- **Rate Limiting**: Implement for API endpoints
- **Monitoring**: Add logging and error tracking
- **Scaling**: Use load balancer for multiple instances

## 🎨 Customization

### Voice Options
Edit voice ID in `santa_ai.py`:
```python
voice_id = 'uDsPstFWFBUXjIBimV7s'  # Santa voice
```

### Visual Theme
Modify CSS variables in `styles.css`:
```css
--christmas-red: #C41E3A;
--christmas-green: #165B33;
--christmas-gold: #FFD700;
```

### Search Behavior
Adjust product count in `santa_ai.py`:
```python
for i, product in enumerate(products[:4], 1):  # Shows 4 products
```

## 🐛 Troubleshooting

### Common Issues

**No Audio/Video**
- Ensure HTTPS is enabled (required for WebRTC)
- Check browser permissions for microphone/camera
- Verify SignalWire credentials

**Search Not Working**
- Confirm RapidAPI key is valid
- Check API rate limits
- Verify network connectivity

**Mute Button Issues**
- Refresh browser to clear cache
- Check console for WebRTC errors

## 📊 API Documentation

### API Endpoints

**POST /santa**
- Receives SignalWire AI Agent requests
- Returns SWML instructions

**GET /santa**
- Alternative webhook endpoint for SignalWire

**GET /health**
- Health check endpoint (provided by AgentServer)
- Returns: `{"status": "healthy"}`

### Frontend Events

Events sent via WebSocket:
- `gifts_found`: Products found from search
- `gift_selected`: User selected a gift
- `nice_list_checked`: Nice list verification complete
- `searching`: Search in progress
- `search_failed`: Search encountered an error

## 🤝 Contributing

We welcome contributions!

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **SignalWire** - AI Agent platform and WebRTC infrastructure
- **ElevenLabs** - Voice synthesis technology
- **RapidAPI** - Real-time Amazon product data
- **Open Source Community** - Various libraries and tools

## 🔗 Links

- [Live Demo](https://santa.signalwire.me/) - Try Santa's Workshop
- [SignalWire Documentation](https://developer.signalwire.com)
- [Project Repository](https://github.com/signalwire/santa)
- [Report Issues](https://github.com/signalwire/santa/issues)

## 📞 Support

For questions and support:
- Open an issue on [GitHub](https://github.com/signalwire/santa/issues)
- Join our [Discord Community](https://discord.com/invite/F2WNYTNjuF)
- Contact SignalWire support

---

🎄 **Happy Holidays from SignalWire!** 🎅

Built with ❤️ and holiday magic by the SignalWire team.