# Gradio UI迁移策略

## 1. 当前Gradio组件

### 核心UI组件
```python
# 来自studio.py
with gr.Blocks() as demo:
    # 警告HTML
    gr.HTML(warning_html_code)
    
    # 会话ID
    uuid = gr.Textbox(label="modelscope_uuid", visible=False)
    
    # 聊天界面
    with gr.Row():
        chatbot = mgr.Chatbot(
            label="Dialog",
            show_label=False,
            bubble_full_width=False,
            visible=True,
        )
    
    # 输入区域
    with gr.Column():
        user_chat_input = gr.Textbox(
            label="user_chat_input",
            placeholder="Say something here",
            show_label=False,
        )
        send_button = gr.Button(value="📣Send")
    
    # 文件上传组件
    with gr.Row():
        # 音频输入
        audio = gr.Accordion("Audio input", open=False)
        with audio:
            audio_term = gr.Audio(
                visible=True,
                type="filepath",
                format="wav",
            )
            submit_audio_button = gr.Button(value="Send Audio")
        
        # 图片输入
        image = gr.Accordion("Image input", open=False)
        with image:
            image_term = gr.Image(
                visible=True,
                height=300,
                interactive=True,
                type="filepath",
            )
            submit_image_button = gr.Button(value="Send Image")
    
    # 重置按钮
    with gr.Column():
        reset_button = gr.Button(value="Reset")
```

### Socket.IO事件处理器

#### 传入事件
```python
# 来自_app.py
@_app.route("/api/messages/push", methods=["POST"])
def _push_message():
    """在Web UI上显示消息"""
    _socketio.emit(
        "display_message",
        data,
        room=run_id,
    )

@_app.route("/api/messages/run/<run_id>", methods=["GET"])
def _get_messages(run_id: str):
    """获取消息历史"""
    messages = _MessageTable.query.filter_by(run_id=run_id).all()
    return jsonify([msg.to_dict() for msg in messages])
```

#### 传出事件
```python
# 来自studio.py
def send_message(msg: str, uid: str):
    """发送用户消息"""
    send_player_input(msg, uid=uid)
    send_msg(msg, is_player=True, role="Me", uid=uid)

def send_audio(audio_term: str, uid: str):
    """发送音频消息"""
    content = audio2text(audio_path=audio_term)
    send_player_input(content, uid=uid)
    send_msg(f"{content}\n<audio src='{audio_term}'></audio>",
            is_player=True, role="Me", uid=uid)

def send_image(image_term: str, uid: str):
    """发送图片消息"""
    send_player_input(image_term, uid=uid)
    send_msg(f"<img src='{image_term}'></img>",
            is_player=True, role="Me", uid=uid)
```

## 2. 迁移策略

### 第一阶段：组件隔离
1. 识别独立的Gradio组件：
   - 聊天显示（Chatbot）
   - 文本输入（Textbox）
   - 文件上传（Audio/Image）
   - 重置功能
   - 会话管理

2. 提取事件处理器：
   - 消息显示
   - 用户输入
   - 文件上传
   - 重置处理

### 第二阶段：React组件开发
1. 创建等效React组件：
   ```typescript
   // 聊天显示
   const ChatDisplay: React.FC<ChatDisplayProps> = ({ messages }) => {
     return <MessageList messages={messages} />;
   };

   // 文本输入
   const TextInput: React.FC<TextInputProps> = ({ onSend }) => {
     return <InputArea onSubmit={onSend} />;
   };

   // 文件上传
   const FileUpload: React.FC<FileUploadProps> = ({ onUpload }) => {
     return <UploadArea onFileSelect={onUpload} />;
   };
   ```

2. 实现事件处理器：
   ```typescript
   // Socket.IO事件处理器
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

### 第三阶段：并行测试
1. 同时运行两个UI：
   - Gradio UI在原始路由
   - React UI在新路由
   - 相同的后端端点
   - 共享Socket.IO事件

2. 验证功能：
   - 消息发送/接收
   - 文件上传
   - 会话管理
   - 重置功能

### 第四阶段：迁移
1. 用户会话处理：
   ```typescript
   // 会话管理
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

2. 消息处理：
   ```typescript
   // 消息管理
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

### 第五阶段：Gradio移除
1. 组件移除顺序：
   - 文件上传组件
   - 输入组件
   - 聊天显示
   - 会话管理
   - 重置功能

2. 路由更新：
   - 重定向旧路由到React UI
   - 移除Gradio路由
   - 更新文档

## 3. 需要保留的Socket.IO事件

### 传入事件
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

### 传出事件
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

## 4. 测试策略

### 功能测试
1. 消息流：
   - 文本消息
   - 文件上传
   - 系统消息
   - 错误处理

2. 会话管理：
   - 创建
   - 持久化
   - 清理

3. 事件处理：
   - Socket.IO事件
   - 用户交互
   - 错误条件

### 集成测试
1. 后端集成：
   - API端点
   - Socket.IO事件
   - 文件处理
   - 会话管理

2. 浏览器自动化：
   - 操作执行
   - 状态管理
   - 错误处理

### 性能测试
1. 负载测试：
   - 多个会话
   - 并发用户
   - 消息量

2. 资源使用：
   - 内存使用
   - CPU利用率
   - 网络流量

## 5. 回滚计划

### 即时回滚
1. 路由配置：
   ```nginx
   location /ui {
     # 在React和Gradio之间切换
     set $ui_backend "react";  # 或 "gradio"
     
     if ($ui_backend = "gradio") {
       proxy_pass http://localhost:7860;
     }
     
     if ($ui_backend = "react") {
       proxy_pass http://localhost:3000;
     }
   }
   ```

2. 会话处理：
   - 保留Gradio会话
   - 维护兼容性
   - 启用快速切换

### 监控
1. 错误追踪：
   - UI错误
   - 后端错误
   - Socket.IO问题

2. 性能指标：
   - 响应时间
   - 错误率
   - 用户满意度

该策略确保从Gradio到React的平稳过渡，同时保持所有功能并提供必要的回滚选项。
