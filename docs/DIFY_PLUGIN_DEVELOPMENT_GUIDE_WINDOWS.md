# Dify插件开发完整指南（Windows版本）

## 环境准备

### 1. Python环境配置

```powershell
# 下载并安装Python 3.12+ (推荐使用官方安装程序)
# 访问 https://www.python.org/downloads/windows/

# 验证安装
python --version
pip --version

# 如果需要多版本管理，安装pyenv-win
git clone https://github.com/pyenv-win/pyenv-win.git %USERPROFILE%\.pyenv
```

### 2. 安装官方CLI工具

```powershell
# 下载Windows版本的dify-plugin-daemon
# 对于64位Windows系统
curl -L -o dify-plugin-daemon.exe https://github.com/langgenius/dify-plugin-daemon/releases/latest/download/dify-plugin-windows-amd64.exe

# 重命名为简短名称
rename dify-plugin-daemon.exe dify-plugin.exe

# 移动到系统路径（可选）
move dify-plugin.exe C:\Windows\System32\

# 验证安装
dify-plugin --version
```

### 3. 开发环境验证

```powershell
# 验证CLI工具
dify-plugin --help

# 创建测试项目
mkdir dify-plugin-workspace
cd dify-plugin-workspace
dify-plugin new
```

## 项目初始化

### 使用官方CLI创建新项目

```powershell
# 创建新插件项目
dify-plugin new

# 按提示输入信息：
# - Plugin Type: Tool (选择插件类型)
# - Plugin Name: my-windows-plugin
# - Author: your-name
# - Description: My first Windows Dify plugin
```

**自动生成的项目结构：**
```
my-windows-plugin/
├── manifest.yaml          # 插件配置文件
├── main.py                # 入口文件
├── requirements.txt       # Python依赖
├── PRIVACY.md            # 隐私政策
├── _assets/              # 资源文件
│   ├── icon.svg
│   └── icon-dark.svg
├── provider/             # 提供商配置
│   ├── my_windows_plugin.py
│   └── my_windows_plugin.yaml
└── tools/               # 工具配置
    ├── my_tool.py
    └── my_tool.yaml
```

## 核心代码开发

### 1. 工具实现 (tools/my_tool.py)

```python
from dify_plugin import Tool
from dify_plugin.entities import ToolInvokeMessage
import platform
import psutil

class WindowsSystemTool(Tool):
    def _invoke(self, tool_parameters: dict) -> ToolInvokeMessage:
        """
        Windows系统信息工具
        """
        action = tool_parameters.get('action', 'system_info')
        
        try:
            if action == 'system_info':
                result = self.get_system_info()
            elif action == 'disk_usage':
                result = self.get_disk_usage()
            elif action == 'memory_info':
                result = self.get_memory_info()
            else:
                result = "不支持的操作"
            
            return self.create_text_message(result)
        except Exception as e:
            return self.create_text_message(f"执行失败: {str(e)}")
    
    def get_system_info(self):
        """获取Windows系统信息"""
        info = {
            "操作系统": platform.system(),
            "系统版本": platform.release(),
            "架构": platform.machine(),
            "处理器": platform.processor(),
            "主机名": platform.node()
        }
        return "\n".join([f"{k}: {v}" for k, v in info.items()])
    
    def get_disk_usage(self):
        """获取磁盘使用情况"""
        partitions = psutil.disk_partitions()
        result = []
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                result.append(f"盘符 {partition.device}: "
                            f"总计 {usage.total // (1024**3)}GB, "
                            f"已用 {usage.used // (1024**3)}GB, "
                            f"可用 {usage.free // (1024**3)}GB")
            except PermissionError:
                result.append(f"盘符 {partition.device}: 无权限访问")
        return "\n".join(result)
    
    def get_memory_info(self):
        """获取内存信息"""
        memory = psutil.virtual_memory()
        return (f"总内存: {memory.total // (1024**3)}GB\n"
                f"已用内存: {memory.used // (1024**3)}GB\n"
                f"可用内存: {memory.available // (1024**3)}GB\n"
                f"使用率: {memory.percent}%")
```

### 2. 工具配置 (tools/my_tool.yaml)

```yaml
identity:
  name: "windows_system_tool"
  author: "your-name"
  label:
    en_US: "Windows System Tool"
    zh_Hans: "Windows系统工具"

description:
  human:
    en_US: "Get Windows system information including disk usage, memory status"
    zh_Hans: "获取Windows系统信息，包括磁盘使用情况、内存状态等"
  llm: "A tool to retrieve Windows system information including OS details, disk usage, and memory statistics"

parameters:
  - name: action
    type: string
    required: true
    label:
      en_US: Action Type
      zh_Hans: 操作类型
    human_description:
      en_US: "Type of system information to retrieve"
      zh_Hans: "要获取的系统信息类型"
    llm_description: "Specify the type of information: system_info, disk_usage, or memory_info"
    form: form
    options:
      - value: "system_info"
        label:
          en_US: "System Information"
          zh_Hans: "系统信息"
      - value: "disk_usage"
        label:
          en_US: "Disk Usage"
          zh_Hans: "磁盘使用情况"
      - value: "memory_info"
        label:
          en_US: "Memory Information"
          zh_Hans: "内存信息"

extra:
  python:
    source: tools/my_tool.py
```

### 3. 依赖配置 (requirements.txt)

```txt
dify_plugin>=0.2.0,<0.3.0
psutil>=5.9.0
```

## 本地调试

### 使用官方CLI调试

```powershell
# 进入项目目录
cd my-windows-plugin

# 安装依赖
pip install -r requirements.txt

# 使用CLI运行插件
dify-plugin run

# 插件启动后会显示：
# Plugin started successfully
# Listening on port 5003
```

### 测试插件功能

```powershell
# 在新的PowerShell窗口中测试
curl -X POST http://localhost:5003/tools/windows_system_tool/invoke `
  -H "Content-Type: application/json" `
  -d '{\"tool_parameters\": {\"action\": \"system_info\"}}'
```

### Python测试脚本

```python
# test_plugin.py
import requests
import json

def test_windows_tool():
    url = "http://localhost:5003/tools/windows_system_tool/invoke"
    
    # 测试系统信息
    test_cases = [
        {"action": "system_info"},
        {"action": "disk_usage"},
        {"action": "memory_info"}
    ]
    
    for case in test_cases:
        data = {"tool_parameters": case}
        response = requests.post(url, json=data)
        print(f"测试 {case['action']}:")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print("-" * 50)

if __name__ == "__main__":
    test_windows_tool()
```

## 打包和发布

### 使用官方CLI打包

```powershell
# 确保在项目根目录
dify-plugin package .

# 成功后生成 my-windows-plugin.difypkg 文件
```

### 手动打包

```powershell
# 创建压缩包（需要7-Zip或其他压缩工具）
tar -czf my-windows-plugin.difypkg --exclude=venv --exclude=.git --exclude=__pycache__ --exclude=*.pyc .
```

## Windows特定注意事项

### 1. 路径处理

```python
import os
import pathlib

# 使用pathlib处理Windows路径
def get_windows_path():
    # 正确的Windows路径处理
    path = pathlib.Path("C:/Users/username/Documents")
    return path.resolve()

# 避免硬编码路径分隔符
def safe_path_join(*args):
    return os.path.join(*args)
```

### 2. 权限管理

```python
import ctypes

def is_admin():
    """检查是否具有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """以管理员身份运行"""
    if not is_admin():
        # 重新以管理员身份启动
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
```

### 3. Windows服务集成

```python
import win32serviceutil
import win32service

class DifyPluginService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DifyPluginService"
    _svc_display_name_ = "Dify Plugin Service"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        
    def SvcDoRun(self):
        # 运行插件服务
        pass
```

## 常见问题解决

### Q1: PowerShell执行策略限制

```powershell
# 查看当前执行策略
Get-ExecutionPolicy

# 设置允许本地脚本执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 或者临时绕过
PowerShell -ExecutionPolicy Bypass -File script.ps1
```

### Q2: 端口占用问题

```powershell
# 查看端口占用
netstat -ano | findstr :5003

# 结束占用进程
taskkill /PID [进程ID] /F
```

### Q3: 依赖安装失败

```powershell
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ dify_plugin

# 安装Visual C++构建工具（如果需要编译扩展）
# 下载并安装 Microsoft C++ Build Tools
```

### Q4: 防火墙和安全软件

```powershell
# 添加防火墙例外
netsh advfirewall firewall add rule name="Dify Plugin" dir=in action=allow protocol=TCP localport=5003

# 检查Windows Defender排除项
# 在Windows安全中心添加项目文件夹为排除项
```

### Q5: 文件路径问题

```python
# 正确处理Windows文件路径
import os
from pathlib import Path

# 使用原始字符串
config_path = r"C:\Users\username\AppData\Local\dify-plugin\config.json"

# 或使用Path对象
config_path = Path.home() / "AppData" / "Local" / "dify-plugin" / "config.json"

# 确保目录存在
config_path.parent.mkdir(parents=True, exist_ok=True)
```

## 部署建议

### 1. 开发环境

```powershell
# 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装开发依赖
pip install -r requirements.txt
pip install pytest black flake8
```

### 2. 生产环境

```powershell
# 使用Windows服务方式运行
# 安装pywin32
pip install pywin32

# 注册为Windows服务
python setup.py install
python plugin_service.py install
python plugin_service.py start
```

### 3. 自动启动配置

```bat
@echo off
cd /d "C:\path\to\your\plugin"
call venv\Scripts\activate
dify-plugin run
pause
```

## 最佳实践

1. **错误处理**: 使用try-except捕获Windows特定异常
2. **日志记录**: 使用Windows事件日志或文件日志
3. **配置管理**: 使用Windows注册表或配置文件
4. **安全考虑**: 遵循Windows安全最佳实践
5. **性能优化**: 考虑Windows内存管理特性

---

*本指南基于Windows 10/11系统和Python 3.12+环境编写*