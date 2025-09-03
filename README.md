# JSON to XMind 转换插件

**作者:** chyax  
**版本:** 0.0.1  
**类型:** Dify 工具插件

## 功能介绍

这是一个功能强大的 Dify 插件，能够将 JSON 数据转换为 XMind 思维导图格式，支持丰富的格式化和标记功能。

### 核心特性

- ✅ **完整的 JSON 结构支持** - 支持任意复杂的嵌套 JSON 数据结构
- ✅ **层级不一致处理** - 优雅处理不同深度的数据分支  
- ✅ **丰富的元数据支持** - 支持优先级、标签、备注、标记等多种属性
- ✅ **XMind 原生功能** - 基于官方 XMind SDK，支持所有标准功能
- ✅ **灵活配置** - 可自定义根节点标题、最大深度等参数

## 安装方式

1. 将插件文件放置到 Dify 插件目录
2. 插件会自动安装所需依赖：
   - `dify_plugin>=0.2.0,<0.3.0`
   - `xmind-sdk-python` (从官方GitHub安装)

## 使用方法

### 输入格式说明

插件支持多种 JSON 输入格式，自动智能识别：

#### 1. JSON 字符串格式（推荐）
```json
{
  "json_data": "{\"项目管理\": {\"前端开发\": [\"React组件\", \"CSS样式\"], \"后端开发\": null}}"
}
```

#### 2. Python 字典格式
```json
{
  "json_data": {
    "项目管理": {
      "前端开发": ["React组件", "CSS样式", "测试用例"],
      "后端开发": ["API设计", "数据库设计", "性能优化"],
      "项目部署": null
    }
  }
}
```

#### 3. 数组格式
```json
{
  "json_data": ["项目1", "项目2", {"复杂项目": {"子任务": ["任务A", "任务B"]}}]
}
```

### 基本用法示例

```json
{
  "项目管理": {
    "前端开发": ["React组件", "CSS样式", "测试用例"],
    "后端开发": ["API设计", "数据库设计", "性能优化"],
    "项目部署": null
  }
}
```

### 带元数据的高级用法

```json
{
  "_priority": 1,
  "_label": "软件开发项目规划",
  "_note": "2024年第一季度重点项目",
  "项目管理": {
    "_star": "red",
    "_task": "half",
    "前端开发": {
      "_priority": 2,
      "_flag": "green",
      "React组件": {
        "_priority": 3,
        "_symbol": "right",
        "功能组件": ["useState", "useEffect"],
        "类组件": ["生命周期", "state管理"]
      },
      "CSS样式": null,
      "测试用例": ["单元测试", "集成测试"]
    },
    "后端开发": {
      "_priority": 1,
      "_emotion": "smile",
      "_url": "https://github.com/project/backend",
      "API设计": ["REST接口", "GraphQL"],
      "数据库设计": {
        "_note": "考虑分库分表方案",
        "MySQL": {
          "_priority": 1,
          "版本": ["5.7", "8.0"],
          "特性": ["事务支持", "索引优化"]
        },
        "Redis": null
      }
    }
  }
}
```

## 支持的元数据字段

使用下划线 `_` 前缀来定义节点的特殊属性：

### 基础属性
- `_priority`: 优先级标记 (1-6)
- `_label`: 节点描述文字 
- `_note`: 详细备注信息

### 视觉标记  
- `_star`: 星标颜色 (`red`, `orange`, `yellow`, `blue`, `green`, `purple`)
- `_flag`: 旗帜颜色 (同上)
- `_task`: 任务进度 (`start`, `quarter`, `half`, `3quar`, `done` 等)
- `_emotion`: 表情符号 (`smile`, `laugh`, `angry`, `cry`, `surprise`, `boring`)
- `_symbol`: 符号标记 (`plus`, `minus`, `question`, `right`, `wrong` 等)
- `_arrow`: 箭头方向 (`up`, `down`, `left`, `right` 等)

### 功能属性
- `_url`: 网页链接
- `_file`: 文件链接  
- `_topic`: 主题内部链接
- `_folded`: 折叠状态 (`true`/`false`)
- `_position`: 自定义位置 `[x, y]`

## 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `json_data` | string/dict | ✅ | - | 要转换的JSON数据（支持JSON字符串或Python字典） |
| `root_title` | string | ❌ | "思维导图" | 根节点标题 |
| `max_depth` | number | ❌ | 10 | 最大转换深度 (1-20) |
| `output_format` | string | ❌ | "base64" | 输出格式："base64"、"file"、"blob" 或 "zip" |

## 输出格式

### Base64 格式输出（默认）
```json
{
  "success": true,
  "message": "JSON成功转换为XMind思维导图",
  "file_base64": "UEsDBBQACAAI...",
  "filename": "思维导图.xmind",
  "file_size": 12345,
  "output_format": "base64",
  "statistics": {
    "total_nodes": 25,
    "max_depth_used": 4,
    "root_title": "项目规划"
  }
}
```

### 文件格式输出
```json
{
  "success": true,
  "message": "XMind文件已生成: 思维导图.xmind",
  "file_path": "/path/to/思维导图.xmind",
  "filename": "思维导图.xmind",
  "file_size": 12345,
  "output_format": "file",
  "statistics": {
    "total_nodes": 25,
    "max_depth_used": 4,
    "root_title": "项目规划"
  }
}
```

### Blob 格式输出（🌟推荐 - 直接 XMind 下载）
```json
{
  "success": true,
  "message": "XMind文件已生成，可直接下载",
  "filename": "思维导图.xmind",
  "file_size": 12345,
  "output_format": "blob",
  "statistics": {
    "total_nodes": 25,
    "max_depth_used": 4,
    "root_title": "项目规划"
  }
}
```
*注：浏览器直接下载 .xmind 文件，无需任何额外操作*

### ZIP 格式输出（需要改扩展名）
```json
{
  "success": true,
  "message": "文件已生成为 ZIP 格式，下载后请将扩展名改为 .xmind",
  "filename": "思维导图.zip",
  "original_filename": "思维导图.xmind",
  "file_size": 12345,
  "output_format": "zip",
  "instructions": "下载后请将文件扩展名从 .zip 改为 .xmind",
  "statistics": {
    "total_nodes": 25,
    "max_depth_used": 4,
    "root_title": "项目规划"
  }
}
```
*注：下载为 .zip 文件，用户需手动改扩展名为 .xmind*

## 使用示例

### 1. 简单项目结构

**输入：**
```json
{
  "项目": {
    "前端": ["页面", "组件", "样式"],
    "后端": ["接口", "数据库"],
    "测试": null
  }
}
```

**输出思维导图结构：**
```
项目
├── 前端
│   ├── 页面
│   ├── 组件  
│   └── 样式
├── 后端
│   ├── 接口
│   └── 数据库
└── 测试
```

### 2. 复杂的团队管理结构

**输入：**
```json
{
  "_priority": 1,
  "_label": "团队协作管理系统",
  "团队管理": {
    "_star": "red",
    "_note": "核心业务模块",
    "人员管理": {
      "_priority": 1,
      "_flag": "green", 
      "开发团队": {
        "前端工程师": ["React专家", "Vue专家"],
        "后端工程师": ["Java", "Python", "Go"],
        "测试工程师": null
      },
      "产品团队": ["产品经理", "UI设计师", "UX设计师"]
    },
    "项目管理": {
      "_priority": 2,
      "_task": "half",
      "_url": "https://project-management.com",
      "敏捷开发": ["Sprint规划", "每日站会", "回顾会议"],
      "工具平台": {
        "_symbol": "right",
        "协作工具": ["Slack", "Teams", "钉钉"],
        "项目跟踪": ["Jira", "Trello", "Asana"]
      }
    }
  }
}
```

## 错误处理

插件具备完善的错误处理机制：

- **JSON解析错误** - 提供具体的语法错误位置
- **深度限制保护** - 防止无限递归导致的性能问题  
- **类型安全** - 自动处理各种数据类型转换
- **资源管理** - 自动清理临时文件

## 技术实现

- 基于官方 **XMind SDK Python** 实现
- 支持 **XMind Legacy** 和 **XMind Zen** 两种格式
- 递归算法处理任意深度的 JSON 结构
- 完整的元数据映射到 XMind 原生功能

## 注意事项

1. JSON数据请确保格式正确
2. 元数据字段名必须以下划线 `_` 开头
3. 优先级范围为 1-6，超出范围将被忽略
4. 颜色值必须为预定义的颜色名称
5. 建议控制数据深度在合理范围内以获得最佳体验

## Dify 工作流集成

### 方式一：Blob 格式（🌟推荐用于直接下载）

最简单的文件下载方式，用户可直接下载：

```yaml
# 工作流配置
steps:
  - name: json_to_xmind
    type: tool
    tool: json2xmind
    parameters:
      json_data: "{{input.json_data}}"
      root_title: "{{input.title}}"
      output_format: "blob"
```
**优势**：用户在浏览器中会自动获得下载提示，无需额外处理。

### 方式二：Base64 格式（用于数据传递）

适用于需要在工作流中进一步处理文件的场景：

```yaml
# 工作流配置
steps:
  - name: json_to_xmind
    type: tool
    tool: json2xmind
    parameters:
      json_data: "{{input.json_data}}"
      root_title: "{{input.title}}"
      output_format: "base64"
  
  - name: process_file
    type: code
    code: |
      import base64
      
      # 获取 base64 数据
      file_data = {{json_to_xmind.file_base64}}
      filename = {{json_to_xmind.filename}}
      
      # 解码并保存文件
      with open(filename, 'wb') as f:
          f.write(base64.b64decode(file_data))
      
      # 或者发送到其他服务
      # upload_to_cloud(file_data, filename)
```

### 方式三：文件格式（用于服务器端）

适用于服务器端文件管理的场景：

```yaml
# 工作流配置  
steps:
  - name: json_to_xmind
    type: tool
    tool: json2xmind
    parameters:
      json_data: "{{input.json_data}}"
      root_title: "{{input.title}}"
      output_format: "file"
  
  - name: return_download_link
    type: template
    template: |
      XMind 文件已生成成功！
      
      📁 文件名：{{json_to_xmind.filename}}
      📊 节点数量：{{json_to_xmind.statistics.total_nodes}}
      💾 文件大小：{{json_to_xmind.file_size}} bytes
      📂 文件路径：{{json_to_xmind.file_path}}
      
      请从生成的路径下载文件。
```

### 四种方式详细对比

| 格式 | 下载文件 | 优势 | 适用场景 | 用户体验 |
|------|----------|------|----------|----------|
| **Blob** | 📁 `.xmind` | 🌟 直接下载 XMind<br>📱 移动端友好<br>⚡ 无需额外操作 | 直接提供给最终用户 | ⭐⭐⭐⭐⭐ |
| **ZIP** | 📦 `.zip` | 📥 兼容性最强<br>🔧 明确的格式<br>⚠️ 需要改扩展名 | 兼容性要求高的环境 | ⭐⭐⭐ |
| **Base64** | 💾 数据传递 | 🔄 便于数据传递<br>🔧 工作流集成<br>☁️ 云服务兼容 | 复杂工作流处理 | ⭐⭐⭐⭐ |
| **File** | 📂 服务器路径 | 💾 服务器端管理<br>📂 文件系统集成<br>🚀 性能最高 | 服务器端应用 | ⭐⭐⭐ |

### 集成优势

1. **四重选择**：满足所有使用场景的输出需求
2. **无缝集成**：完全兼容 Dify 工作流语法  
3. **用户友好**：Blob 格式提供完美的 XMind 下载体验
4. **兼容性强**：ZIP 格式确保在任何环境下都能正常工作
5. **开发便利**：Base64 格式便于二次开发和集成

## 更新日志

### v0.0.1 (2024-01-XX)
- 🎉 首次发布
- ✅ 支持基础 JSON 到 XMind 转换
- ✅ 支持完整的元数据功能
- ✅ 支持优先级、标记、备注等功能
- ✅ 支持自定义根节点和深度限制
- ✅ 支持双输出格式（base64 和文件）
- ✅ 完整的 Dify 工作流集成支持
