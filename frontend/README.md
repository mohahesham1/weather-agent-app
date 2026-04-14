# Weather Agent - Frontend Chat UI

A modern, dark-themed chat interface for the Weather Agent application built with plain HTML, CSS, and JavaScript (no frameworks).

## Features

✨ **Modern Dark Theme** - Sleek, professional appearance optimized for readability
🎨 **Message Bubbles** - Blue bubbles for user messages, dark gray for agent responses
⚡ **Real-time Chat** - Instant communication with the backend agent
🔄 **Auto-scroll** - Automatically scrolls to the latest message
⌨️ **Keyboard Support** - Press Enter to send messages
🔌 **Status Indicator** - Shows connection status to backend
⚠️ **Error Handling** - Graceful error messages and toast notifications
📱 **Responsive Design** - Works on desktop, tablet, and mobile

## File Structure

```
frontend/
├── index.html       # Chat UI structure
├── style.css        # Dark theme styling
├── app.js          # Chat logic and API integration
└── README.md       # This file
```

## How It Works

### HTML (index.html)
- Chat container with header, chat area, input, and status indicator
- Welcome message shown on first load
- Scrollable message container
- Text input with rounded send button

### CSS (style.css)
- **Color Variables**: CSS custom properties for theming
  - Blue (`#2196F3`) for user messages
  - Dark gray (`#1E1E2E`) for agent messages  
  - Cyan accent (`#00D4FF`) for highlights
  
- **Animations**:
  - Message fade-in effect
  - Loading dots bounce animation
  - Send button hover scale
  - Error toast slide-in

- **Responsive**: Adapts to mobile, tablet, and desktop

### JavaScript (app.js)

**Main Functions**:
- `sendMessage()` - Sends message to backend, handles loading state
- `fetchChatResponse(message)` - Makes POST request to `/chat` endpoint
- `displayUserMessage(text)` - Renders user message bubble
- `displayAgentMessage(text)` - Renders agent response bubble
- `displayLoadingMessage()` - Shows "Thinking..." indicator
- `handleError(error)` - Displays error messages gracefully
- `scrollToBottom()` - Auto-scrolls to latest message
- `checkBackendStatus()` - Verifies backend connectivity on startup

**Chat State**:
- `chatHistory` - Array of previous messages for context
- `isWaitingForResponse` - Prevents double-sending

**Error Handling**:
- Network errors show in chat with explanation
- Toast notifications for critical errors
- Console logging for debugging
- Graceful fallbacks if backend unavailable

## Running the Frontend

### Quick Start

1. **Open in Browser**:
   ```bash
   # macOS
   open frontend/index.html
   
   # Windows
   start frontend/index.html
   
   # Linux
   firefox frontend/index.html
   ```

2. **Or use a local server** (recommended):
   ```bash
   # Python 3
   python -m http.server 3000 -d frontend
   
   # Then visit: http://localhost:3000
   ```

3. **Make sure the backend is running**:
   ```bash
   cd agent-backend
   python main.py  # Should run on http://localhost:8001
   ```

## API Integration

### Backend Connection

The frontend POSTs to `http://localhost:8001/chat`:

```javascript
{
  "query": "What's the weather in London?",
  "chat_history": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ]
}
```

### Response Format

Expected response:
```json
{
  "response": "The weather in London is...",
  "query": "What's the weather in London?",
  "timestamp": "2024-04-14T10:30:45.123456",
  "tools_used": ["get_weather_forecast"]
}
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Enter` | Send message |
| `Shift+Enter` | New line in input |
| Click send button | Send message |

## Debugging

### Console Functions

Open DevTools (F12) and use:

```javascript
// Get chat history
chatDebug.getHistory()

// Clear chat history
chatDebug.clearHistory()

// Get backend URL
chatDebug.backendURL

// Manually scroll to bottom
chatDebug.resizeChat()
```

### Check Backend Status

The UI automatically checks backend health on load. Look for green "Connected" indicator at the bottom, or check browser console for:
- ✅ `Backend is online and ready`
- ⚠️ `Unable to connect to backend`

## Error Messages

### "Backend error: 500"
- Backend crashed or threw an exception
- Check agent-backend terminal for error details

### "Empty response from backend"
- Backend returned a response without the `response` field
- Verify backend response format matches expected schema

### "Unable to connect to backend"
- Backend not running on localhost:8001
- Check if `python agent-backend/main.py` is running
- Verify no firewall blocking localhost:8001

## Styling Customization

### Dark Mode Colors

Edit CSS variables in `style.css`:

```css
:root {
    --bg-primary: #0f1419;        /* Main background */
    --color-user: #2196F3;         /* User message blue */
    --color-agent: #1E1E2E;        /* Agent message dark */
    --color-accent: #00D4FF;       /* Accent cyan */
}
```

### Message Bubble Width

The max-width of bubbles is responsive:
- Desktop: 70% (user), 80% (agent)
- Tablet: 85%
- Mobile: 90%

Edit in `@media` queries if needed.

## Browser Compatibility

✓ Chrome/Edge 90+
✓ Firefox 88+
✓ Safari 14+
✓ Mobile browsers (iOS Safari, Chrome Mobile)

Uses standard ES6+ features and CSS3 (no polyfills needed for modern browsers).

## Performance

- **Zero dependencies** - No npm packages or frameworks
- **Lightweight** - ~50KB total (HTML + CSS + JS uncompressed)
- **Fast startup** - Instant load, no build step required
- **Efficient scrolling** - Uses native scroll-behavior CSS

## Troubleshooting

### Messages not sending
1. Check backend is running: `curl http://localhost:8001/health`
2. Check browser console (F12) for error details
3. Verify `Content-Type: application/json` header is being sent

### Wrong layout on mobile
- Double-check `<meta name="viewport">` tag in HTML
- Try refreshing page or clearing cache

### Past messages not persisting
- Chat history is in-memory only (resets on page refresh)
- To persist: Store `chatHistory` in localStorage or backend database

### Slow responses
- Check network tab (F12 → Network) for request/response times
- May indicate backend is slow or MCP server unreachable
- Check backend logs for errors

## Next Steps

1. ✅ Frontend UI complete
2. Connect to running backend
3. Test end-to-end flow
4. Add persistent local storage with localStorage
5. Add typing indicators
6. Add weather icons and card layouts
7. Deploy to production

## License

Part of the Weather Agent application.
