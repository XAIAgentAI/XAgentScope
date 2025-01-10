# Browser Automation API Design

## 1. WebBrowser Service Integration

### Current Implementation
The WebBrowser class provides core browser automation capabilities:
```python
class WebBrowser:
    _actions = [
        "action_click",
        "action_type",
        "action_scroll_up",
        "action_scroll_down",
        "action_press_key",
        "action_visit_url",
    ]
```

### REST API Endpoints

#### Action Endpoints
```typescript
interface BrowserEndpoints {
  // Execute browser actions
  POST /api/browser/action
  {
    action: "click" | "type" | "scroll_up" | "scroll_down" | "press_key" | "visit_url",
    params: {
      element_id?: number,
      text?: string,
      url?: string,
      key?: string
    }
  }

  // Get page state
  GET /api/browser/state
  Response: {
    url: string,
    title: string,
    screenshot: string,
    interactive_elements: WebElementInfo[]
  }

  // Set interactive marks
  POST /api/browser/marks
  Response: {
    elements: WebElementInfo[]
  }

  // Remove interactive marks
  DELETE /api/browser/marks
}
```

### WebSocket Events
```typescript
interface BrowserEvents {
  // Browser state updates
  browser_state_update: {
    url: string,
    title: string,
    interactive_elements: WebElementInfo[]
  }

  // Action results
  browser_action_result: {
    status: "success" | "error",
    action: string,
    message: string
  }

  // Page load events
  browser_page_loaded: {
    url: string
  }
}
```

## 2. Backend Service Implementation

### BrowserController Class
```python
class BrowserController:
    def __init__(self):
        self.browser = WebBrowser()
        self.active_sessions = {}

    async def handle_action(self, action: str, params: dict) -> ServiceResponse:
        """Handle browser action requests"""
        if action not in self.browser._actions:
            return ServiceResponse(
                status=ServiceExecStatus.ERROR,
                content=f"Unknown action: {action}"
            )
        
        method = getattr(self.browser, f"action_{action}")
        return await method(**params)

    async def get_page_state(self) -> dict:
        """Get current page state"""
        return {
            "url": self.browser.url,
            "title": self.browser.page_title,
            "screenshot": self.browser.page_screenshot,
            "interactive_elements": self.browser.set_interactive_marks()
        }
```

### Flask Route Integration
```python
@app.route("/api/browser/action", methods=["POST"])
async def browser_action():
    data = request.json
    action = data.get("action")
    params = data.get("params", {})
    
    response = await browser_controller.handle_action(action, params)
    return jsonify(response.dict())

@app.route("/api/browser/state", methods=["GET"])
async def browser_state():
    state = await browser_controller.get_page_state()
    return jsonify(state)
```

## 3. Error Handling

### Error Types
```python
class BrowserError(Exception):
    """Base class for browser automation errors"""
    pass

class ElementNotFoundError(BrowserError):
    """Element not found or invalid element ID"""
    pass

class ActionTimeoutError(BrowserError):
    """Action execution timeout"""
    pass

class InvalidActionError(BrowserError):
    """Invalid or unsupported action"""
    pass
```

### Error Responses
```typescript
interface ErrorResponse {
  status: "error";
  error: {
    type: string;
    message: string;
    details?: any;
  }
}
```

## 4. Session Management

### Browser Session
```python
class BrowserSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.browser = WebBrowser()
        self.last_activity = datetime.now()
        self.active = True

    async def cleanup(self):
        """Clean up browser resources"""
        if self.active:
            self.browser.close()
            self.active = False
```

### Session Manager
```python
class BrowserSessionManager:
    def __init__(self):
        self.sessions = {}
        self.cleanup_interval = 300  # 5 minutes

    async def get_session(self, session_id: str) -> BrowserSession:
        """Get or create browser session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = BrowserSession(session_id)
        return self.sessions[session_id]

    async def cleanup_inactive_sessions(self):
        """Clean up inactive sessions"""
        current_time = datetime.now()
        for session_id, session in list(self.sessions.items()):
            if (current_time - session.last_activity).seconds > self.cleanup_interval:
                await session.cleanup()
                del self.sessions[session_id]
```

## 5. Integration Strategy

### Phase 1: API Layer
1. Implement BrowserController class
2. Add REST endpoints
3. Set up WebSocket events
4. Implement error handling

### Phase 2: Session Management
1. Implement BrowserSession class
2. Add session manager
3. Configure cleanup tasks
4. Add session middleware

### Phase 3: Testing
1. Unit tests for controller
2. Integration tests for endpoints
3. Load testing for sessions
4. Error handling verification

### Phase 4: Documentation
1. API documentation
2. Integration guide
3. Error handling guide
4. Example implementations

## 6. Security Considerations

### Access Control
- Session-based authentication
- Rate limiting for actions
- Origin validation
- CORS configuration

### Input Validation
- Action parameter validation
- URL validation
- Element ID validation
- Session ID validation

### Resource Management
- Browser instance limits
- Session timeout controls
- Memory usage monitoring
- Error rate monitoring

This design document outlines how to expose the WebBrowser service functionality through a REST API while maintaining all existing capabilities and adding proper session management and error handling.
