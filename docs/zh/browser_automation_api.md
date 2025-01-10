# 浏览器自动化API设计

## 1. WebBrowser服务集成

### 当前实现
WebBrowser类提供核心浏览器自动化功能：
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

### REST API端点

#### 操作端点
```typescript
interface BrowserEndpoints {
  // 执行浏览器操作
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

  // 获取页面状态
  GET /api/browser/state
  Response: {
    url: string,
    title: string,
    screenshot: string,
    interactive_elements: WebElementInfo[]
  }

  // 设置交互标记
  POST /api/browser/marks
  Response: {
    elements: WebElementInfo[]
  }

  // 移除交互标记
  DELETE /api/browser/marks
}
```

### WebSocket事件
```typescript
interface BrowserEvents {
  // 浏览器状态更新
  browser_state_update: {
    url: string,
    title: string,
    interactive_elements: WebElementInfo[]
  }

  // 操作结果
  browser_action_result: {
    status: "success" | "error",
    action: string,
    message: string
  }

  // 页面加载事件
  browser_page_loaded: {
    url: string
  }
}
```

## 2. 后端服务实现

### BrowserController类
```python
class BrowserController:
    def __init__(self):
        self.browser = WebBrowser()
        self.active_sessions = {}

    async def handle_action(self, action: str, params: dict) -> ServiceResponse:
        """处理浏览器操作请求"""
        if action not in self.browser._actions:
            return ServiceResponse(
                status=ServiceExecStatus.ERROR,
                content=f"未知操作: {action}"
            )
        
        method = getattr(self.browser, f"action_{action}")
        return await method(**params)

    async def get_page_state(self) -> dict:
        """获取当前页面状态"""
        return {
            "url": self.browser.url,
            "title": self.browser.page_title,
            "screenshot": self.browser.page_screenshot,
            "interactive_elements": self.browser.set_interactive_marks()
        }
```

### Flask路由集成
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

## 3. 错误处理

### 错误类型
```python
class BrowserError(Exception):
    """浏览器自动化错误基类"""
    pass

class ElementNotFoundError(BrowserError):
    """元素未找到或无效元素ID"""
    pass

class ActionTimeoutError(BrowserError):
    """操作执行超时"""
    pass

class InvalidActionError(BrowserError):
    """无效或不支持的操作"""
    pass
```

### 错误响应
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

## 4. 会话管理

### 浏览器会话
```python
class BrowserSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.browser = WebBrowser()
        self.last_activity = datetime.now()
        self.active = True

    async def cleanup(self):
        """清理浏览器资源"""
        if self.active:
            self.browser.close()
            self.active = False
```

### 会话管理器
```python
class BrowserSessionManager:
    def __init__(self):
        self.sessions = {}
        self.cleanup_interval = 300  # 5分钟

    async def get_session(self, session_id: str) -> BrowserSession:
        """获取或创建浏览器会话"""
        if session_id not in self.sessions:
            self.sessions[session_id] = BrowserSession(session_id)
        return self.sessions[session_id]

    async def cleanup_inactive_sessions(self):
        """清理不活跃的会话"""
        current_time = datetime.now()
        for session_id, session in list(self.sessions.items()):
            if (current_time - session.last_activity).seconds > self.cleanup_interval:
                await session.cleanup()
                del self.sessions[session_id]
```

## 5. 集成策略

### 第一阶段：API层
1. 实现BrowserController类
2. 添加REST端点
3. 设置WebSocket事件
4. 实现错误处理

### 第二阶段：会话管理
1. 实现BrowserSession类
2. 添加会话管理器
3. 配置清理任务
4. 添加会话中间件

### 第三阶段：测试
1. 控制器单元测试
2. 端点集成测试
3. 会话负载测试
4. 错误处理验证

### 第四阶段：文档
1. API文档
2. 集成指南
3. 错误处理指南
4. 示例实现

## 6. 安全考虑

### 访问控制
- 基于会话的认证
- 操作速率限制
- 来源验证
- CORS配置

### 输入验证
- 操作参数验证
- URL验证
- 元素ID验证
- 会话ID验证

### 资源管理
- 浏览器实例限制
- 会话超时控制
- 内存使用监控
- 错误率监控

本设计文档概述了如何通过REST API暴露WebBrowser服务功能，同时保持所有现有功能并添加适当的会话管理和错误处理。
