# React前端设计文档

## 1. 组件架构

### 核心组件

#### ChatInterface
- **目的**: 替代Gradio聊天实现的主聊天界面
- **功能**:
  - 实时消息显示
  - 消息历史管理
  - 用户输入处理
  - 文件上传支持（音频/图片）
  - 重置功能
- **状态管理**:
  ```typescript
  interface ChatState {
    messages: Message[];
    isTyping: boolean;
    currentInput: string;
    sessionId: string;
  }
  ```

#### MessageList
- **目的**: 显示聊天消息
- **功能**:
  - 按发送者分组消息
  - 支持文本/音频/图片内容
  - 自动滚动到最新消息
  - 加载状态
- **属性**:
  ```typescript
  interface MessageListProps {
    messages: Message[];
    isTyping: boolean;
    onMessageAction?: (messageId: string, action: string) => void;
  }
  ```

#### InputArea
- **目的**: 用户输入处理
- **功能**:
  - 文本输入
  - 文件上传按钮
  - 发送按钮
  - 输入验证
- **属性**:
  ```typescript
  interface InputAreaProps {
    onSendMessage: (content: string) => void;
    onFileUpload: (file: File) => void;
    disabled?: boolean;
  }
  ```

#### FileUploadModal
- **目的**: 处理文件上传（音频/图片）
- **功能**:
  - 文件类型验证
  - 上传进度
  - 预览功能
- **属性**:
  ```typescript
  interface FileUploadModalProps {
    isOpen: boolean;
    onClose: () => void;
    onUpload: (file: File) => void;
    acceptedTypes: string[];
  }
  ```

### Socket.IO集成

#### WebSocket服务
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

### 浏览器自动化集成

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

## 2. 状态管理

### Redux存储结构
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

### 操作
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

## 3. API集成

### REST端点
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

### WebSocket事件
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

## 4. 迁移策略

### 第一阶段：设置React项目
1. 使用TypeScript初始化React项目
2. 设置Socket.IO客户端
3. 配置Redux存储
4. 创建基本组件结构

### 第二阶段：核心组件
1. 实现ChatInterface
2. 开发MessageList
3. 创建InputArea
4. 添加FileUploadModal

### 第三阶段：集成
1. 连接Socket.IO事件
2. 实现浏览器自动化API
3. 添加状态管理
4. 设置API客户端

### 第四阶段：测试
1. 组件单元测试
2. Socket.IO集成测试
3. 聊天流程E2E测试
4. 浏览器自动化测试

### 第五阶段：部署
1. 构建配置
2. 环境设置
3. 文档编写
4. 性能优化

## 5. 依赖

### 核心依赖
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

### UI组件
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

## 6. 浏览器自动化集成

### 后端API结构
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

本设计文档提供了从Gradio迁移到React前端的完整计划，同时保持与现有后端服务和浏览器自动化功能的兼容性。
