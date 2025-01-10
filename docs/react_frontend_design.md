# React Frontend Design Document

## 1. Component Architecture

### Core Components

#### ChatInterface
- **Purpose**: Main chat interface replacing Gradio's chat implementation
- **Features**:
  - Real-time message display
  - Message history management
  - User input handling
  - File upload support (audio/image)
  - Reset functionality
- **State Management**:
  ```typescript
  interface ChatState {
    messages: Message[];
    isTyping: boolean;
    currentInput: string;
    sessionId: string;
  }
  ```

#### MessageList
- **Purpose**: Display chat messages
- **Features**:
  - Message grouping by sender
  - Support for text/audio/image content
  - Auto-scroll to latest message
  - Loading states
- **Props**:
  ```typescript
  interface MessageListProps {
    messages: Message[];
    isTyping: boolean;
    onMessageAction?: (messageId: string, action: string) => void;
  }
  ```

#### InputArea
- **Purpose**: User input handling
- **Features**:
  - Text input
  - File upload buttons
  - Send button
  - Input validation
- **Props**:
  ```typescript
  interface InputAreaProps {
    onSendMessage: (content: string) => void;
    onFileUpload: (file: File) => void;
    disabled?: boolean;
  }
  ```

#### FileUploadModal
- **Purpose**: Handle file uploads (audio/image)
- **Features**:
  - File type validation
  - Upload progress
  - Preview capability
- **Props**:
  ```typescript
  interface FileUploadModalProps {
    isOpen: boolean;
    onClose: () => void;
    onUpload: (file: File) => void;
    acceptedTypes: string[];
  }
  ```

### Socket.IO Integration

#### WebSocket Service
```typescript
class WebSocketService {
  private socket: Socket;

  constructor(url: string) {
    this.socket = io(url);
    this.setupEventListeners();
  }

  private setupEventListeners() {
    this.socket.on('display_message', this.handleMessage);
    this.socket.on('enable_user_input', this.handleUserInput);
    this.socket.on('fetch_user_input', this.handleFetchInput);
  }

  public sendMessage(data: MessageData) {
    this.socket.emit('user_input_ready', data);
  }
}
```

### Browser Automation Integration

#### BrowserService
```typescript
class BrowserService {
  private apiClient: AxiosInstance;

  public async executeAction(action: BrowserAction) {
    return this.apiClient.post('/api/browser/action', action);
  }

  public async getPageState() {
    return this.apiClient.get('/api/browser/state');
  }
}

interface BrowserAction {
  type: 'click' | 'type' | 'scroll' | 'visit';
  payload: any;
}
```

## 2. State Management

### Redux Store Structure
```typescript
interface RootState {
  chat: {
    messages: Message[];
    isTyping: boolean;
    currentInput: string;
    sessionId: string;
  };
  browser: {
    currentUrl: string;
    interactiveElements: InteractiveElement[];
    isLoading: boolean;
  };
  ui: {
    activeModals: string[];
    theme: 'light' | 'dark';
    notifications: Notification[];
  };
}
```

### Actions
```typescript
enum ActionTypes {
  SEND_MESSAGE = 'chat/sendMessage',
  RECEIVE_MESSAGE = 'chat/receiveMessage',
  SET_TYPING = 'chat/setTyping',
  EXECUTE_BROWSER_ACTION = 'browser/executeAction',
  UPDATE_BROWSER_STATE = 'browser/updateState',
  TOGGLE_MODAL = 'ui/toggleModal',
}
```

## 3. API Integration

### REST Endpoints
```typescript
interface ApiEndpoints {
  messages: {
    get: '/api/messages/run/:runId',
    push: '/api/messages/push',
  };
  browser: {
    action: '/api/browser/action',
    state: '/api/browser/state',
  };
  session: {
    create: '/api/runs/register',
    status: '/api/runs/get/:runId',
  };
}
```

### WebSocket Events
```typescript
interface WebSocketEvents {
  incoming: {
    DISPLAY_MESSAGE: 'display_message',
    ENABLE_USER_INPUT: 'enable_user_input',
    FETCH_USER_INPUT: 'fetch_user_input',
  };
  outgoing: {
    USER_INPUT_READY: 'user_input_ready',
    JOIN_ROOM: 'join',
    LEAVE_ROOM: 'leave',
  };
}
```

## 4. Migration Strategy

### Phase 1: Setup React Project
1. Initialize React project with TypeScript
2. Set up Socket.IO client
3. Configure Redux store
4. Create basic component structure

### Phase 2: Core Components
1. Implement ChatInterface
2. Develop MessageList
3. Create InputArea
4. Add FileUploadModal

### Phase 3: Integration
1. Connect Socket.IO events
2. Implement browser automation API
3. Add state management
4. Set up API client

### Phase 4: Testing
1. Unit tests for components
2. Integration tests for Socket.IO
3. E2E tests for chat flow
4. Browser automation testing

### Phase 5: Deployment
1. Build configuration
2. Environment setup
3. Documentation
4. Performance optimization

## 5. Dependencies

### Core Dependencies
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@reduxjs/toolkit": "^1.9.0",
    "socket.io-client": "^4.7.0",
    "axios": "^1.6.0",
    "typescript": "^5.0.0"
  }
}
```

### UI Components
```json
{
  "dependencies": {
    "@mui/material": "^5.14.0",
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0",
    "react-virtualized": "^9.22.0"
  }
}
```

## 6. Browser Automation Integration

### Backend API Structure
```typescript
interface BrowserEndpoints {
  click: '/api/browser/click',
  type: '/api/browser/type',
  scroll: '/api/browser/scroll',
  visit: '/api/browser/visit',
  state: '/api/browser/state',
}

interface BrowserResponse {
  status: 'success' | 'error';
  content: string;
  data?: any;
}
```

This design document provides a comprehensive plan for migrating the current Gradio-based UI to a React frontend while maintaining compatibility with the existing backend services and browser automation functionality.
