# JSON2XMind AI提示词指南

## 工具概述

JSON2XMind是一个将JSON数据转换为XMind思维导图的Dify插件工具。它支持丰富的元数据标记，可以创建具有优先级、标签、备注、星标等丰富格式的思维导图。

## 核心功能

- 将JSON数据结构转换为XMind思维导图
- 支持丰富的视觉元数据（优先级、星标、旗帜、任务进度等）
- 自动处理嵌套结构和数组
- 生成可下载的.xmind文件

## JSON格式规范

### 基础结构

```json
{
  "主题名称": "内容或子结构",
  "数组主题": ["项目1", "项目2", "项目3"],
  "嵌套主题": {
    "子主题1": "内容",
    "子主题2": {
      "孙主题": "深层内容"
    }
  }
}
```

### 元数据标记

所有元数据字段以下划线`_`开头，用于控制节点的视觉样式：

#### 优先级标记
- `_priority`: 1-6的整数，表示优先级等级

#### 视觉标记
- `_label`: 字符串，添加描述标签
- `_note`: 字符串，添加备注信息
- `_star`: 颜色名称，添加彩色星标
- `_flag`: 颜色名称，添加彩色旗帜

#### 任务标记
- `_task`: 任务进度状态
- `_emotion`: 表情标记
- `_symbol`: 符号标记
- `_arrow`: 箭头标记

#### 链接和位置
- `_url`: 超链接地址
- `_file`: 文件链接
- `_topic`: 主题链接
- `_folded`: 布尔值，是否折叠
- `_position`: 数组[x, y]，节点位置

## AI提示词模板

### 基础提示词模板

```xml
<system_instruction>
你是一个专业的思维导图JSON生成器，专门为JSON2XMind工具创建结构化数据。

## 输出要求
1. 必须输出有效的JSON格式
2. 使用中文作为主要语言
3. 结构要清晰、层次分明
4. 合理使用元数据增强视觉效果

## 元数据使用规范
- _priority: 1-6 (1=最高优先级)
- _star: red/orange/yellow/blue/green/purple
- _flag: red/orange/yellow/blue/green/purple  
- _task: start/oct/quarter/3oct/half/5oct/3quar/7oct/done
- _emotion: smile/laugh/angry/cry/surprise/boring
- _symbol: plus/minus/question/exclam/info/wrong/right
- _arrow: up/up-right/right/down-right/down/down-left/left/up-left/refresh
- _label: 文本标签
- _note: 备注信息
- _url: 网址链接
- _folded: true/false

## 任务要求
根据用户输入的主题或内容，生成适合的JSON结构供JSON2XMind工具使用。
</system_instruction>

<user_input>
[用户输入内容]
</user_input>

<expected_output>
请为以上内容生成JSON2XMind格式的思维导图数据：

```json
{
  // 在这里生成JSON结构
}
```
</expected_output>
```

### 学习计划生成模板

```xml
<prompt_template name="learning_plan">
<system_instruction>
你是一个学习规划专家，使用JSON2XMind格式创建详细的学习计划思维导图。

## 生成规则
1. 主分支：学习阶段或知识模块
2. 子分支：具体学习内容
3. 叶子节点：学习要点或资源
4. 使用优先级标记重要程度
5. 使用任务标记学习进度
6. 使用星标标记重点内容

## 元数据使用策略
- 基础知识: _priority=3, _star="blue"
- 重点难点: _priority=1, _star="red" 
- 实践项目: _priority=2, _flag="green"
- 复习内容: _task="half", _symbol="refresh"
- 参考资源: _symbol="info", _note="详细信息"
</system_instruction>

<user_input>
学习主题：[用户输入的学习主题]
学习周期：[学习时间安排]
学习目标：[具体学习目标]
</user_input>

<expected_output>
基于以上信息，生成学习计划的JSON2XMind数据：

```json
{
  "学习计划": {
    "_priority": 1,
    "_star": "yellow",
    "_note": "完整学习路径规划"
  }
}
```
</expected_output>
</prompt_template>
```

### 项目管理模板

```xml
<prompt_template name="project_management">
<system_instruction>
你是一个项目管理专家，使用JSON2XMind格式创建项目管理思维导图。

## 项目结构规范
1. 项目概述：目标、范围、时间线
2. 工作分解：主要里程碑和任务
3. 资源配置：人员、工具、预算
4. 风险管理：识别、评估、应对
5. 质量控制：标准、检查点、验收

## 元数据策略
- 里程碑: _priority=1, _flag="red"
- 关键任务: _priority=2, _star="orange"
- 一般任务: _priority=3, _task="start"
- 已完成: _task="done", _symbol="right"
- 风险项: _symbol="exclam", _flag="yellow"
- 重要资源: _symbol="info", _star="blue"
</system_instruction>

<user_input>
项目名称：[项目名称]
项目周期：[项目时间安排]
主要目标：[项目目标]
团队规模：[团队信息]
</user_input>

<expected_output>
生成项目管理的JSON2XMind结构：

```json
{
  "[项目名称]管理计划": {
    "_priority": 1,
    "_star": "red",
    "_note": "项目整体规划"
  }
}
```
</expected_output>
</prompt_template>
```

### 知识总结模板

```xml
<prompt_template name="knowledge_summary">
<system_instruction>
你是一个知识整理专家，将复杂内容转换为JSON2XMind格式的结构化思维导图。

## 知识整理原则
1. 主题分类：按逻辑关系组织
2. 层次清晰：核心概念→具体内容→细节要点
3. 关联标记：使用箭头表示关系
4. 重点突出：用星标和优先级标记
5. 补充说明：用备注添加详细信息

## 视觉增强策略
- 核心概念: _priority=1, _star="red"
- 重要概念: _priority=2, _star="orange"  
- 支撑要点: _priority=3, _symbol="plus"
- 案例示例: _flag="green", _emotion="smile"
- 注意事项: _symbol="exclam", _flag="yellow"
- 相关链接: _symbol="info", _url="链接地址"
</system_instruction>

<user_input>
知识主题：[要整理的知识主题]
内容来源：[学习材料或内容]
整理目的：[学习或应用目标]
</user_input>

<expected_output>
生成知识总结的JSON2XMind数据：

```json
{
  "[知识主题]知识图谱": {
    "_priority": 1,
    "_star": "purple",
    "_note": "系统化知识整理"
  }
}
```
</expected_output>
</prompt_template>
```

### 会议记录模板

```xml
<prompt_template name="meeting_minutes">
<system_instruction>
你是一个会议记录专家，将会议内容转换为JSON2XMind格式的结构化记录。

## 会议记录结构
1. 会议基本信息（时间、参与者、议题）
2. 讨论要点（按议题分组）
3. 决策事项（明确的决定）
4. 行动计划（任务分配和时间节点）
5. 后续跟进（下次会议安排）

## 状态标记策略
- 重要决策: _priority=1, _flag="red"
- 行动项: _task="start", _symbol="right"
- 已完成: _task="done", _star="green"
- 待跟进: _task="quarter", _symbol="question"
- 风险提示: _symbol="exclam", _flag="yellow"
- 参考资料: _symbol="info", _note="详细说明"
</system_instruction>

<user_input>
会议主题：[会议主题]
参与人员：[参会人员]
讨论内容：[会议讨论的具体内容]
决策结果：[会议达成的决策]
</user_input>

<expected_output>
生成会议记录的JSON2XMind格式：

```json
{
  "[会议主题]会议纪要": {
    "_priority": 1,
    "_star": "blue",
    "_note": "会议时间：[时间]"
  }
}
```
</expected_output>
</prompt_template>
```

### 问题分析模板

```xml
<prompt_template name="problem_analysis">
<system_instruction>
你是一个问题分析专家，使用JSON2XMind格式进行系统性问题分析和解决方案设计。

## 问题分析框架
1. 问题描述：现状、影响、紧急程度
2. 原因分析：根本原因、直接原因、诱发因素
3. 解决方案：多个备选方案比较
4. 实施计划：步骤、资源、时间安排
5. 风险评估：可能的风险和应对措施

## 分析标记规范
- 核心问题: _priority=1, _flag="red", _symbol="exclam"
- 根本原因: _priority=2, _star="orange", _arrow="down"
- 推荐方案: _priority=1, _star="green", _symbol="right"
- 备选方案: _priority=3, _flag="blue"
- 实施步骤: _task="start", _symbol="plus"
- 风险点: _symbol="exclam", _flag="yellow"
</system_instruction>

<user_input>
问题描述：[具体问题描述]
问题影响：[问题造成的影响]
期望结果：[希望达到的目标]
约束条件：[现有的限制条件]
</user_input>

<expected_output>
生成问题分析的JSON2XMind结构：

```json
{
  "问题分析：[问题标题]": {
    "_priority": 1,
    "_flag": "red",
    "_note": "系统性问题分析"
  }
}
```
</expected_output>
</prompt_template>
```

## 使用示例

### 示例1：技术学习路径

**用户输入：**
```
学习主题：Python Web开发
学习周期：3个月
学习目标：能够独立开发Web应用
```

**AI生成的JSON：**
```json
{
  "Python Web开发学习路径": {
    "_priority": 1,
    "_star": "purple",
    "_note": "3个月完整学习计划",
    "第一阶段：基础准备": {
      "_priority": 2,
      "_star": "blue",
      "_task": "start",
      "Python基础回顾": {
        "_priority": 3,
        "_task": "quarter",
        "语法基础": "变量、函数、类",
        "数据结构": "列表、字典、集合",
        "文件操作": "读写、异常处理"
      },
      "Web基础知识": {
        "_priority": 2,
        "_star": "orange",
        "HTTP协议": {
          "_note": "请求响应机制",
          "GET请求": "获取数据",
          "POST请求": "提交数据",
          "状态码": "200, 404, 500等"
        },
        "HTML/CSS": "页面结构和样式",
        "JavaScript": "基础交互逻辑"
      }
    },
    "第二阶段：框架学习": {
      "_priority": 1,
      "_star": "red",
      "_task": "start",
      "Django框架": {
        "_priority": 1,
        "_flag": "green",
        "MVC架构": "模型视图控制器",
        "路由系统": "URL映射",
        "模板引擎": "动态页面生成",
        "ORM操作": {
          "_note": "数据库操作",
          "_symbol": "info",
          "模型定义": "数据结构设计",
          "查询操作": "增删改查",
          "关联关系": "一对多、多对多"
        }
      },
      "Flask框架": {
        "_priority": 2,
        "_flag": "blue",
        "轻量级特性": "微框架概念",
        "扩展系统": "插件机制"
      }
    },
    "第三阶段：实战项目": {
      "_priority": 1,
      "_star": "green",
      "_task": "start",
      "博客系统": {
        "_priority": 2,
        "_flag": "orange",
        "_task": "half",
        "功能模块": [
          "用户注册登录",
          "文章发布编辑", 
          "评论系统",
          "标签分类"
        ],
        "技术要点": {
          "_symbol": "plus",
          "用户认证": "Session/JWT",
          "富文本编辑": "编辑器集成",
          "文件上传": "图片处理"
        }
      },
      "电商网站": {
        "_priority": 1,
        "_star": "red",
        "_task": "start",
        "核心功能": [
          "商品管理",
          "购物车",
          "订单处理",
          "支付集成"
        ],
        "高级特性": {
          "_priority": 3,
          "_symbol": "exclam",
          "缓存优化": "Redis集成",
          "消息队列": "异步处理",
          "API设计": "RESTful接口"
        }
      }
    },
    "学习资源": {
      "_symbol": "info",
      "_star": "yellow",
      "官方文档": {
        "_url": "https://docs.djangoproject.com",
        "_note": "最权威的学习资料"
      },
      "实战教程": "在线视频课程",
      "社区论坛": "问题讨论交流",
      "开源项目": {
        "_symbol": "plus",
        "_note": "学习优秀代码"
      }
    }
  }
}
```

### 示例2：项目风险管理

**用户输入：**
```
项目名称：移动APP开发
项目周期：6个月
主要风险：技术难度高、时间紧迫、团队经验不足
```

**AI生成的JSON：**
```json
{
  "移动APP项目风险管理": {
    "_priority": 1,
    "_flag": "red",
    "_note": "6个月项目周期风险控制",
    "技术风险": {
      "_priority": 1,
      "_star": "red",
      "_symbol": "exclam",
      "跨平台兼容": {
        "_priority": 2,
        "_flag": "orange",
        "风险描述": "iOS/Android差异导致功能实现困难",
        "影响程度": "高",
        "发生概率": "中等",
        "应对措施": {
          "_star": "green",
          "_symbol": "right",
          "技术选型": "React Native统一开发",
          "原型验证": "核心功能提前测试",
          "技术储备": "提前学习相关技术"
        }
      },
      "性能优化": {
        "_priority": 2,
        "_flag": "yellow",
        "内存管理": "避免内存泄漏",
        "网络优化": "离线缓存机制",
        "UI流畅度": {
          "_task": "start",
          "_note": "60fps目标"
        }
      }
    },
    "进度风险": {
      "_priority": 1,
      "_star": "orange",
      "_arrow": "up",
      "时间压力": {
        "_priority": 1,
        "_flag": "red",
        "风险因素": [
          "需求变更频繁",
          "技术难点预估不足", 
          "测试时间压缩"
        ],
        "缓解策略": {
          "_star": "blue",
          "_task": "quarter",
          "敏捷开发": "2周迭代周期",
          "MVP策略": "最小可行产品优先",
          "并行开发": "前后端同步进行"
        }
      },
      "里程碑管控": {
        "_priority": 2,
        "_task": "start",
        "月度检查": "进度评估会议",
        "关键节点": {
          "_symbol": "info",
          "原型完成": "第1个月",
          "核心功能": "第3个月",
          "测试完成": "第5个月",
          "上线准备": "第6个月"
        }
      }
    },
    "团队风险": {
      "_priority": 2,
      "_star": "yellow",
      "_symbol": "question",
      "经验不足": {
        "_priority": 1,
        "_flag": "orange",
        "技能差距": "移动开发经验缺乏",
        "学习成本": "影响开发效率",
        "解决方案": {
          "_star": "green",
          "_task": "start",
          "技术培训": "外部专家指导",
          "导师制度": "经验丰富的顾问",
          "知识分享": "团队内部交流"
        }
      },
      "人员流动": {
        "_priority": 3,
        "_symbol": "exclam",
        "核心成员": "关键人员离职风险",
        "知识传承": "文档化管理",
        "备用方案": {
          "_task": "start",
          "_note": "人员替补计划"
        }
      }
    },
    "应急预案": {
      "_priority": 1,
      "_star": "purple",
      "_symbol": "refresh",
      "技术方案B": {
        "_priority": 2,
        "_flag": "blue",
        "原生开发": "放弃跨平台方案",
        "功能裁减": "核心功能优先",
        "外包支持": "技术难点外包"
      },
      "进度调整": {
        "_priority": 2,
        "_task": "quarter",
        "延期申请": "合理调整时间线",
        "资源增配": "增加开发人员",
        "范围缩减": "减少非核心功能"
      }
    }
  }
}
```

## 最佳实践建议

### 1. 结构设计原则
- **层次清晰**：不超过5层深度
- **内容平衡**：避免单一分支过深
- **命名一致**：使用统一的命名规范
- **逻辑性强**：分类合理，关联明确

### 2. 元数据使用技巧
- **优先级**：只对关键内容使用1-2级优先级
- **颜色标记**：建立一致的颜色语义体系
- **任务状态**：反映真实的进展情况
- **备注信息**：提供必要的补充说明

### 3. 视觉优化策略
- **重点突出**：使用星标和旗帜标记重要内容
- **状态清晰**：用任务进度显示完成情况
- **关系明确**：用箭头表示流程和因果关系
- **信息丰富**：合理使用链接和备注

### 4. 常见问题避免
- **过度装饰**：不要滥用元数据标记
- **结构混乱**：保持清晰的层次关系
- **信息冗余**：避免重复和无效信息
- **格式错误**：确保JSON语法正确

---

*使用本指南可以帮助AI更好地理解和使用JSON2XMind工具，生成高质量的思维导图数据*