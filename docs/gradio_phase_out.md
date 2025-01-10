# Gradio UI Phase-Out Strategy

## 1. Current Gradio Components

### Core UI Components
```python
# From studio.py
with gr.Blocks() as demo:
    # Warning HTML
    gr.HTML(warning_html_code)
    
    # Session ID
    uuid = gr.Textbox(label="modelscope_uuid", visible=False)
    
    # Chat Interface
    with gr.Row():
        chatbot = mgr.Chatbot(
            label="Dialog",
            show_label=False,
            bubble_full_width=False,
            visible=True,
        )
    
    # Input Area
    with gr.Column():
        user_chat_input = gr.Textbox(
            label="user_chat_input",
            placeholder="Say something here",
            show_label=False,
        )
        send_button = gr.Button(value="📣Send")
    
    # File Upload Components
    with gr.Row():
        # Audio Input
        audio = gr.Accordion("Audio input", open=False)
        with audio:
            audio_term = gr.Audio(
                visible=True,
                type="filepath",
                format="wav",
            )
            submit_audio_button = gr.Button(value="Send Audio")
        
        # Image Input
        image = gr.Accordion("Image input", open=False)
        with image:
            image_term = gr.Image(
                visible=True,
                height=300,
                interactive=True,
                type="filepath",
            )
            submit_image_button = gr.Button(value="Send Image")
    
    # Reset Button
    with gr.Column():
        reset_button = gr.Button(value="Reset")
```

### Socket.IO Event Handlers

#### Incoming Events
```python
# From _app.py
@_app.route("/api/messages/push", methods=["POST"])
def _push_message():
    """Display message on web UI"""
    _socketio.emit(
        "display_message",
        data,
        room=run_id,
    )

@_app.route("/api/messages/run/<run_id>", methods=["GET"])
def _get_messages(run_id: str):
    """Get message history"""
    messages = _MessageTable.query.filter_by(run_id=run_id).all()
    return jsonify([msg.to_dict() for msg in messages])
```

#### Outgoing Events
```python
# From studio.py
def send_message(msg: str, uid: str):
    """Send user message"""
    send_player_input(msg, uid=uid)
    send_msg(msg, is_player=True, role="Me", uid=uid)

def send_audio(audio_term: str, uid: str):
    """Send audio message"""
    content = audio2text(audio_path=audio_term)
    send_player_input(content, uid=uid)
    send_msg(f"{content}\n<audio src='{audio_term}'></audio>",
            is_player=True, role="Me", uid=uid)

def send_image(image_term: str, uid: str):
    """Send image message"""
    send_player_input(image_term, uid=uid)
    send_msg(f"<img src='{image_term}'></img>",
            is_player=True, role="Me", uid=uid)
```

## 2. Phase-Out Strategy

### Phase 1: Component Isolation
1. Identify independent Gradio components:
   - Chat display (Chatbot)
   - Text input (Textbox)
   - File upload (Audio/Image)
   - Reset functionality
   - Session management

2. Extract event handlers:
   - Message display
   - User input
   - File upload
   - Reset handling

### Phase 2: React Component Development
1. Create equivalent React components:
   ```typescript
   // Chat display
   const ChatDisplay: React.FC<ChatDisplayProps> = ({ messages }) => {
     return <MessageList messages={messages} />;
   };

   // Text input
   const TextInput: React.FC<TextInputProps> = ({ onSend }) => {
     return <InputArea onSubmit={onSend} />;
   };

   // File upload
   const FileUpload: React.FC<FileUploadProps> = ({ onUpload }) => {
     return <UploadArea onFileSelect={onUpload} />;
   };
   ```

2. Implement event handlers:
   ```typescript
   // Socket.IO event handlers
   const useSocketEvents = () => {
     useEffect(() => {
       socket.on('display_message', handleMessage);
       socket.on('enable_user_input', handleUserInput);
       socket.on('fetch_user_input', handleFetchInput);
       
       return () => {
         socket.off('display_message');
         socket.off('enable_user_input');
         socket.off('fetch_user_input');
       };
     }, []);
   };
   ```

### Phase 3: Parallel Testing
1. Run both UIs simultaneously:
   - Gradio UI on original route
   - React UI on new route
   - Same backend endpoints
   - Shared Socket.IO events

2. Verify functionality:
   - Message sending/receiving
   - File uploads
   - Session management
   - Reset functionality

### Phase 4: Migration
1. User session handling:
   ```typescript
   // Session management
   const useSession = () => {
     const [session, setSession] = useState<Session | null>(null);
     
     useEffect(() => {
       const initSession = async () => {
         const newSession = await createSession();
         setSession(newSession);
       };
       
       initSession();
     }, []);
     
     return session;
   };
   ```

2. Message handling:
   ```typescript
   // Message management
   const useMessages = (sessionId: string) => {
     const [messages, setMessages] = useState<Message[]>([]);
     
     useEffect(() => {
       const loadMessages = async () => {
         const history = await fetchMessages(sessionId);
         setMessages(history);
       };
       
       loadMessages();
     }, [sessionId]);
     
     return messages;
   };
   ```

### Phase 5: Gradio Removal
1. Component removal sequence:
   - File upload components
   - Input components
   - Chat display
   - Session management
   - Reset functionality

2. Route updates:
   - Redirect old routes to React UI
   - Remove Gradio routes
   - Update documentation

## 3. Socket.IO Events to Preserve

### Incoming Events
```typescript
interface IncomingEvents {
  display_message: {
    id: string;
    run_id: string;
    name: string;
    role: string;
    content: string;
    url: string | null;
    metadata: any;
    timestamp: string;
  };
  
  enable_user_input: {
    run_id: string;
    agent_id: string;
    data: any;
  };
  
  fetch_user_input: {
    run_id: string;
    agent_id: string;
  };
}
```

### Outgoing Events
```typescript
interface OutgoingEvents {
  user_input_ready: {
    run_id: string;
    agent_id: string;
    content: string;
    url?: string;
  };
  
  join: {
    run_id: string;
  };
  
  leave: {
    run_id: string;
  };
}
```

## 4. Testing Strategy

### Functional Testing
1. Message flow:
   - Text messages
   - File uploads
   - System messages
   - Error handling

2. Session management:
   - Creation
   - Persistence
   - Cleanup

3. Event handling:
   - Socket.IO events
   - User interactions
   - Error conditions

### Integration Testing
1. Backend integration:
   - API endpoints
   - Socket.IO events
   - File handling
   - Session management

2. Browser automation:
   - Action execution
   - State management
   - Error handling

### Performance Testing
1. Load testing:
   - Multiple sessions
   - Concurrent users
   - Message volume

2. Resource usage:
   - Memory usage
   - CPU utilization
   - Network traffic

## 5. Rollback Plan

### Immediate Rollback
1. Route configuration:
   ```nginx
   location /ui {
     # Switch between React and Gradio
     set $ui_backend "react";  # or "gradio"
     
     if ($ui_backend = "gradio") {
       proxy_pass http://localhost:7860;
     }
     
     if ($ui_backend = "react") {
       proxy_pass http://localhost:3000;
     }
   }
   ```

2. Session handling:
   - Preserve Gradio sessions
   - Maintain compatibility
   - Enable quick switching

### Monitoring
1. Error tracking:
   - UI errors
   - Backend errors
   - Socket.IO issues

2. Performance metrics:
   - Response times
   - Error rates
   - User satisfaction

This strategy ensures a smooth transition from Gradio to React while maintaining all functionality and providing fallback options if needed.
