# Dify插件开发完整指南（Mac M芯片版本）

## 环境准备

### 1. Python环境配置（Apple Silicon优化）

```bash
# 安装Homebrew（Apple Silicon版本）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装pyenv（推荐用于Python版本管理）
brew install pyenv

# 配置shell环境（zsh）
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc

# 安装Python 3.12+（针对Apple Silicon优化）
env PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.12.0
pyenv global 3.12.0

# 验证Python版本和架构
python --version
python -c "import platform; print(f'架构: {platform.machine()}')"
# 应显示: 架构: arm64
```

### 2. 安装官方CLI工具（Apple Silicon版本）

```bash
# 下载Apple Silicon专用版本
curl -L -o dify-plugin-daemon https://github.com/langgenius/dify-plugin-daemon/releases/latest/download/dify-plugin-darwin-arm64

# 赋予执行权限
chmod +x dify-plugin-daemon

# 移除macOS隔离属性
sudo xattr -rd com.apple.quarantine dify-plugin-daemon

# 移动到系统路径
sudo mv dify-plugin-daemon /usr/local/bin/dify-plugin

# 验证安装
dify-plugin --version
```

### 3. Apple Silicon特定环境配置

```bash
# 安装Apple Silicon优化的依赖工具
brew install pkg-config libffi openssl

# 配置编译环境变量
echo 'export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig"' >> ~/.zshrc
echo 'export LDFLAGS="-L/opt/homebrew/lib"' >> ~/.zshrc
echo 'export CPPFLAGS="-I/opt/homebrew/include"' >> ~/.zshrc
source ~/.zshrc

# 验证CLI工具
dify-plugin --help
```

## 项目初始化

### 使用官方CLI创建新项目

```bash
# 创建工作目录
mkdir ~/dify-plugins-workspace
cd ~/dify-plugins-workspace

# 创建新插件项目
dify-plugin new

# 按提示输入信息：
# - Plugin Type: Tool (选择插件类型)
# - Plugin Name: mac-m-system-tool
# - Author: your-name
# - Description: Mac M芯片系统工具
```

**自动生成的项目结构：**
```
mac-m-system-tool/
├── manifest.yaml          # 插件配置文件
├── main.py                # 入口文件
├── requirements.txt       # Python依赖
├── PRIVACY.md            # 隐私政策
├── _assets/              # 资源文件
│   ├── icon.svg
│   └── icon-dark.svg
├── provider/             # 提供商配置
│   ├── mac_m_system_tool.py
│   └── mac_m_system_tool.yaml
└── tools/               # 工具配置
    ├── system_monitor.py
    └── system_monitor.yaml
```

## 核心代码开发（Apple Silicon优化）

### 1. 系统监控工具 (tools/system_monitor.py)

```python
from dify_plugin import Tool
from dify_plugin.entities import ToolInvokeMessage
import platform
import psutil
import subprocess
import json

class MacMSystemTool(Tool):
    def _invoke(self, tool_parameters: dict) -> ToolInvokeMessage:
        """
        Mac M芯片系统监控工具
        """
        action = tool_parameters.get('action', 'system_info')
        
        try:
            if action == 'system_info':
                result = self.get_apple_silicon_info()
            elif action == 'cpu_info':
                result = self.get_cpu_info()
            elif action == 'memory_pressure':
                result = self.get_memory_pressure()
            elif action == 'thermal_state':
                result = self.get_thermal_state()
            elif action == 'power_metrics':
                result = self.get_power_metrics()
            else:
                result = "不支持的操作"
            
            return self.create_text_message(result)
        except Exception as e:
            return self.create_text_message(f"执行失败: {str(e)}")
    
    def get_apple_silicon_info(self):
        """获取Apple Silicon特定信息"""
        try:
            # 获取芯片信息
            chip_info = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], 
                                     capture_output=True, text=True)
            
            # 获取架构信息
            arch_info = platform.machine()
            
            # 获取macOS版本
            macos_version = platform.mac_ver()[0]
            
            # 获取性能核心和效率核心数量
            perf_cores = subprocess.run(['sysctl', '-n', 'hw.perflevel0.logicalcpu'], 
                                      capture_output=True, text=True)
            effi_cores = subprocess.run(['sysctl', '-n', 'hw.perflevel1.logicalcpu'], 
                                      capture_output=True, text=True)
            
            info = {
                "芯片型号": chip_info.stdout.strip(),
                "架构": arch_info,
                "macOS版本": macos_version,
                "性能核心": perf_cores.stdout.strip() if perf_cores.stdout else "未知",
                "效率核心": effi_cores.stdout.strip() if effi_cores.stdout else "未知",
                "总CPU核心": psutil.cpu_count(logical=False),
                "逻辑CPU数": psutil.cpu_count(logical=True)
            }
            
            return "\n".join([f"{k}: {v}" for k, v in info.items()])
        except Exception as e:
            return f"获取系统信息失败: {str(e)}"
    
    def get_cpu_info(self):
        """获取CPU详细信息"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            avg_cpu = sum(cpu_percent) / len(cpu_percent)
            
            # CPU频率信息
            cpu_freq = psutil.cpu_freq()
            
            # 负载平均值
            load_avg = subprocess.run(['sysctl', '-n', 'vm.loadavg'], 
                                    capture_output=True, text=True)
            
            result = [
                f"平均CPU使用率: {avg_cpu:.2f}%",
                f"各核心使用率: {', '.join([f'{cpu:.1f}%' for cpu in cpu_percent])}",
                f"当前频率: {cpu_freq.current:.0f} MHz" if cpu_freq else "频率信息不可用",
                f"系统负载: {load_avg.stdout.strip()}" if load_avg.stdout else "负载信息不可用"
            ]
            
            return "\n".join(result)
        except Exception as e:
            return f"获取CPU信息失败: {str(e)}"
    
    def get_memory_pressure(self):
        """获取内存压力信息（macOS特有）"""
        try:
            # 基本内存信息
            memory = psutil.virtual_memory()
            
            # macOS内存压力信息
            memory_pressure = subprocess.run(['memory_pressure'], 
                                           capture_output=True, text=True, timeout=5)
            
            # Swap使用情况
            swap = psutil.swap_memory()
            
            result = [
                f"物理内存总计: {memory.total // (1024**3)} GB",
                f"已用内存: {memory.used // (1024**3)} GB ({memory.percent:.1f}%)",
                f"可用内存: {memory.available // (1024**3)} GB",
                f"Swap总计: {swap.total // (1024**3)} GB",
                f"Swap已用: {swap.used // (1024**3)} GB",
                "",
                "内存压力信息:",
                memory_pressure.stdout if memory_pressure.stdout else "无法获取内存压力详情"
            ]
            
            return "\n".join(result)
        except Exception as e:
            return f"获取内存信息失败: {str(e)}"
    
    def get_thermal_state(self):
        """获取热状态信息"""
        try:
            # 系统热状态
            thermal_state = subprocess.run(['pmset', '-g', 'thermlog'], 
                                         capture_output=True, text=True)
            
            # 温度传感器信息（需要额外工具，这里模拟）
            sensors_info = "温度传感器信息需要额外工具支持"
            
            result = [
                "系统热状态:",
                thermal_state.stdout if thermal_state.stdout else "无法获取热状态信息",
                "",
                sensors_info
            ]
            
            return "\n".join(result)
        except Exception as e:
            return f"获取热状态失败: {str(e)}"
    
    def get_power_metrics(self):
        """获取电源和功耗信息"""
        try:
            # 电池信息
            battery = psutil.sensors_battery()
            
            # 电源管理信息
            power_info = subprocess.run(['pmset', '-g', 'ps'], 
                                      capture_output=True, text=True)
            
            # 功耗历史
            power_history = subprocess.run(['pmset', '-g', 'pslog'], 
                                         capture_output=True, text=True)
            
            result = []
            
            if battery:
                result.extend([
                    f"电池电量: {battery.percent:.1f}%",
                    f"电源连接: {'是' if battery.power_plugged else '否'}",
                    f"剩余时间: {battery.secsleft // 3600}小时{(battery.secsleft % 3600) // 60}分钟" if battery.secsleft != psutil.POWER_TIME_UNLIMITED else "无限制",
                    ""
                ])
            
            result.extend([
                "电源状态:",
                power_info.stdout if power_info.stdout else "无法获取电源信息"
            ])
            
            return "\n".join(result)
        except Exception as e:
            return f"获取电源信息失败: {str(e)}"
```

### 2. 工具配置 (tools/system_monitor.yaml)

```yaml
identity:
  name: "mac_m_system_monitor"
  author: "your-name"
  label:
    en_US: "Mac M Chip System Monitor"
    zh_Hans: "Mac M芯片系统监控器"

description:
  human:
    en_US: "Advanced system monitoring tool optimized for Apple Silicon Macs"
    zh_Hans: "专为Apple Silicon Mac优化的高级系统监控工具"
  llm: "A comprehensive system monitoring tool designed specifically for Apple Silicon Macs, providing detailed information about CPU, memory, thermal state, and power metrics"

parameters:
  - name: action
    type: string
    required: true
    label:
      en_US: Action Type
      zh_Hans: 监控类型
    human_description:
      en_US: "Type of system information to monitor"
      zh_Hans: "要监控的系统信息类型"
    llm_description: "Specify the monitoring action: system_info, cpu_info, memory_pressure, thermal_state, or power_metrics"
    form: form
    options:
      - value: "system_info"
        label:
          en_US: "Apple Silicon System Info"
          zh_Hans: "Apple Silicon系统信息"
      - value: "cpu_info"
        label:
          en_US: "CPU Performance"
          zh_Hans: "CPU性能信息"
      - value: "memory_pressure"
        label:
          en_US: "Memory Pressure"
          zh_Hans: "内存压力"
      - value: "thermal_state"
        label:
          en_US: "Thermal State"
          zh_Hans: "热状态"
      - value: "power_metrics"
        label:
          en_US: "Power & Battery"
          zh_Hans: "电源和电池"

extra:
  python:
    source: tools/system_monitor.py
```

### 3. Apple Silicon优化的依赖 (requirements.txt)

```txt
dify_plugin>=0.2.0,<0.3.0
psutil>=5.9.0
# Apple Silicon优化的数据处理库
numpy>=1.24.0
# 如需要机器学习功能
# tensorflow-macos>=2.13.0
# torch>=2.0.0
```

## 本地调试（Apple Silicon优化）

### 使用官方CLI调试

```bash
# 进入项目目录
cd mac-m-system-tool

# 创建Apple Silicon优化的虚拟环境
python -m venv venv --prompt "mac-m-plugin"
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 使用CLI运行插件
dify-plugin run
```

### 性能测试脚本

```python
# test_performance.py
import requests
import json
import time
import concurrent.futures

def test_mac_m_performance():
    """测试Mac M芯片性能"""
    url = "http://localhost:5003/tools/mac_m_system_monitor/invoke"
    
    test_cases = [
        {"action": "system_info"},
        {"action": "cpu_info"},
        {"action": "memory_pressure"},
        {"action": "thermal_state"},
        {"action": "power_metrics"}
    ]
    
    print("=== Mac M芯片系统监控测试 ===\n")
    
    # 顺序测试
    for case in test_cases:
        start_time = time.time()
        data = {"tool_parameters": case}
        response = requests.post(url, json=data)
        end_time = time.time()
        
        print(f"测试 {case['action']}:")
        print(f"响应时间: {(end_time - start_time)*1000:.2f}ms")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"结果预览: {str(result)[:100]}...")
        print("-" * 60)
    
    # 并发性能测试
    print("\n=== 并发性能测试 ===")
    def concurrent_test(action):
        data = {"tool_parameters": {"action": action}}
        start_time = time.time()
        response = requests.post(url, json=data)
        end_time = time.time()
        return action, (end_time - start_time) * 1000, response.status_code
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        actions = ["cpu_info"] * 5
        futures = [executor.submit(concurrent_test, action) for action in actions]
        
        for future in concurrent.futures.as_completed(futures):
            action, response_time, status = future.result()
            print(f"并发测试 {action}: {response_time:.2f}ms, 状态: {status}")

if __name__ == "__main__":
    test_mac_m_performance()
```

## Apple Silicon特定优化

### 1. 内存管理优化

```python
# memory_optimization.py
import gc
import psutil
from functools import wraps

def memory_efficient(func):
    """内存优化装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 获取执行前内存
        process = psutil.Process()
        memory_before = process.memory_info().rss
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # 强制垃圾回收
            gc.collect()
            
            # 获取执行后内存
            memory_after = process.memory_info().rss
            memory_diff = (memory_after - memory_before) / 1024 / 1024  # MB
            
            if memory_diff > 100:  # 如果内存增长超过100MB
                print(f"警告: 函数 {func.__name__} 内存使用增长 {memory_diff:.2f} MB")
    
    return wrapper

class AppleSiliconOptimizer:
    """Apple Silicon特定优化"""
    
    @staticmethod
    def optimize_numpy():
        """优化NumPy for Apple Silicon"""
        import numpy as np
        # 启用Apple Silicon加速
        import os
        os.environ['OPENBLAS_NUM_THREADS'] = '1'
        os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
    
    @staticmethod
    def get_metal_info():
        """获取Metal GPU信息"""
        try:
            import subprocess
            result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                  capture_output=True, text=True)
            return result.stdout
        except:
            return "无法获取Metal信息"
```

### 2. 多进程处理优化

```python
# multiprocessing_optimization.py
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import psutil

def get_optimal_workers():
    """获取最优工作进程数"""
    # Apple Silicon通常有8个性能核心 + 2-4个效率核心
    cpu_count = psutil.cpu_count(logical=False)
    
    # 为系统保留一些核心
    optimal_workers = max(1, cpu_count - 2)
    return optimal_workers

def parallel_task(data_chunk):
    """并行处理任务"""
    # 处理数据块
    return len(data_chunk)

class AppleSiliconParallelProcessor:
    """Apple Silicon并行处理器"""
    
    def __init__(self):
        self.workers = get_optimal_workers()
    
    def process_data(self, data):
        """并行处理数据"""
        chunk_size = len(data) // self.workers
        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
        
        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            results = list(executor.map(parallel_task, chunks))
        
        return results
```

## 打包和部署

### Apple Silicon特定打包

```bash
# 确保使用Apple Silicon优化的Python环境
python -c "import platform; print(f'当前架构: {platform.machine()}')"

# 打包插件
dify-plugin package .

# 验证包内容
tar -tzf mac-m-system-tool.difypkg | head -20
```

### 性能基准测试

```bash
# 创建性能测试脚本
cat > benchmark.py << 'EOF'
import time
import psutil
import subprocess

def benchmark_apple_silicon():
    """Apple Silicon性能基准测试"""
    print("=== Apple Silicon性能基准测试 ===")
    
    # CPU基准测试
    start_time = time.time()
    result = sum(i * i for i in range(1000000))
    cpu_time = time.time() - start_time
    print(f"CPU计算测试: {cpu_time:.4f}秒")
    
    # 内存访问测试
    start_time = time.time()
    data = [i for i in range(1000000)]
    memory_time = time.time() - start_time
    print(f"内存访问测试: {memory_time:.4f}秒")
    
    # 系统信息
    print(f"CPU核心数: {psutil.cpu_count()}")
    print(f"内存总量: {psutil.virtual_memory().total // (1024**3)} GB")
    
    return {"cpu_time": cpu_time, "memory_time": memory_time}

if __name__ == "__main__":
    benchmark_apple_silicon()
EOF

python benchmark.py
```

## 常见问题解决

### Q1: Rosetta兼容性问题

```bash
# 检查是否在Rosetta模式下运行
if [[ $(sysctl -n sysctl.proc_translated) == 1 ]]; then
    echo "警告: 正在Rosetta模式下运行，性能可能受影响"
    echo "建议使用原生Apple Silicon Python环境"
fi

# 强制使用原生arm64
arch -arm64 python your_script.py
```

### Q2: 权限和安全问题

```bash
# 授予终端完全磁盘访问权限
# 系统偏好设置 -> 安全性与隐私 -> 隐私 -> 完全磁盘访问权限

# 代码签名（用于分发）
codesign --force --deep --sign - dify-plugin-daemon

# 检查安全设置
spctl --assess --verbose dify-plugin-daemon
```

### Q3: 依赖包编译问题

```bash
# 安装编译工具
xcode-select --install

# 设置正确的架构
export ARCHFLAGS="-arch arm64"

# 为Apple Silicon优化编译
pip install --no-binary :all: --force-reinstall psutil
```

### Q4: 性能优化问题

```python
# 启用Apple Silicon特定优化
import os
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'  # PyTorch Metal性能优化
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '1'        # TensorFlow优化

# 检查Metal性能状态
def check_metal_performance():
    try:
        import tensorflow as tf
        print(f"Metal支持: {tf.config.list_physical_devices('GPU')}")
    except ImportError:
        print("TensorFlow未安装")
    
    try:
        import torch
        print(f"MPS可用: {torch.backends.mps.is_available()}")
    except ImportError:
        print("PyTorch未安装")
```

### Q5: 监控和调试

```bash
# 实时监控系统资源
sudo powermetrics --samplers smc -n 1 -i 1000

# 查看详细的CPU信息
sysctl -a | grep machdep.cpu

# 监控内存压力
memory_pressure

# 查看热状态
pmset -g thermlog
```

## 最佳实践

### 1. 代码优化

```python
# 利用Apple Silicon优势
def apple_silicon_optimized_function():
    # 使用向量化操作
    import numpy as np
    
    # 利用统一内存架构
    data = np.random.random((10000, 1000))
    result = np.dot(data, data.T)
    
    return result

# 异步处理
import asyncio

async def async_system_monitor():
    """异步系统监控"""
    tasks = [
        get_cpu_info_async(),
        get_memory_info_async(),
        get_thermal_info_async()
    ]
    
    results = await asyncio.gather(*tasks)
    return results
```

### 2. 资源管理

```python
# 智能资源管理
class ResourceManager:
    def __init__(self):
        self.cpu_cores = psutil.cpu_count()
        self.memory_gb = psutil.virtual_memory().total // (1024**3)
    
    def get_optimal_config(self):
        """根据硬件配置返回最优设置"""
        if self.memory_gb >= 16:
            return {"workers": self.cpu_cores, "batch_size": 1000}
        else:
            return {"workers": self.cpu_cores // 2, "batch_size": 500}
```

### 3. 错误处理

```python
# Apple Silicon特定错误处理
def handle_apple_silicon_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OSError as e:
            if "arm64" in str(e):
                return "Apple Silicon架构相关错误，请检查依赖兼容性"
            raise
        except ImportError as e:
            if "Metal" in str(e) or "MPS" in str(e):
                return "Metal GPU支持不可用，使用CPU模式"
            raise
    return wrapper
```

---

*本指南专为Apple Silicon Mac（M1/M2/M3芯片）优化，基于macOS 13.0+和Python 3.12+环境编写*