from collections.abc import Generator
from typing import Any
import json
import os
import tempfile
import logging
import mimetypes

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.config.logger_format import plugin_logger_handler

import xmind
from xmind.core.topic import TopicElement
from xmind.core.markerref import MarkerId

# 设置插件专用日志
plugin_logger = logging.getLogger(__name__)
plugin_logger.setLevel(logging.INFO)
plugin_logger.addHandler(plugin_logger_handler)

# 插件加载时的日志
plugin_logger.info("🔧 Json2xmindTool 类正在加载")

class Json2xmindTool(Tool):
    def _apply_metadata(self, topic: TopicElement, data: dict):
        """应用元数据到XMind主题，支持完整的元数据标记系统"""
        
        # 优先级 (1-6) - 增强兼容性
        if '_priority' in data:
            priority = data['_priority']
            # 支持字符串和整数输入
            try:
                priority_int = int(priority)
                if 1 <= priority_int <= 6:
                    topic.addMarker(f'priority-{priority_int}')
            except (ValueError, TypeError):
                pass
        
        # 描述标签 - 增强格式处理
        if '_label' in data:
            current_title = topic.getTitle() or ""
            label = str(data['_label']).strip()
            if label:
                # 避免重复添加标签
                if f"({label})" not in current_title:
                    topic.setTitle(f"{current_title} ({label})")
        
        # 备注 - 支持多行和富文本
        if '_note' in data:
            note_content = str(data['_note']).strip()
            if note_content:
                topic.setPlainNotes(note_content)
        
        # 星标 - 增加兼容性和默认值
        if '_star' in data:
            star_color = str(data['_star']).lower().strip()
            valid_star_colors = ['red', 'orange', 'yellow', 'blue', 'green', 'purple', 'default']
            if star_color in valid_star_colors:
                topic.addMarker(f'star-{star_color}')
            elif star_color == 'true' or star_color == '1':  # 兼容布尔值
                topic.addMarker('star-yellow')  # 默认黄色星标
        
        # 旗帜 - 增加兼容性
        if '_flag' in data:
            flag_color = str(data['_flag']).lower().strip()
            valid_flag_colors = ['red', 'orange', 'yellow', 'blue', 'green', 'purple', 'default']
            if flag_color in valid_flag_colors:
                topic.addMarker(f'flag-{flag_color}')
            elif flag_color == 'true' or flag_color == '1':  # 兼容布尔值
                topic.addMarker('flag-red')  # 默认红色旗帜
        
        # 任务进度 - 增加别名支持
        if '_task' in data:
            task_progress = str(data['_task']).lower().strip()
            # 支持多种表达方式
            task_mapping = {
                'start': 'start', 'begin': 'start', '0%': 'start', '开始': 'start',
                'oct': 'oct', '12.5%': 'oct', '1/8': 'oct',
                'quarter': 'quarter', '25%': 'quarter', '1/4': 'quarter', '四分之一': 'quarter',
                '3oct': '3oct', '37.5%': '3oct', '3/8': '3oct',
                'half': 'half', '50%': 'half', '1/2': 'half', '一半': 'half',
                '5oct': '5oct', '62.5%': '5oct', '5/8': '5oct',
                '3quar': '3quar', '75%': '3quar', '3/4': '3quar', '四分之三': '3quar',
                '7oct': '7oct', '87.5%': '7oct', '7/8': '7oct',
                'done': 'done', 'complete': 'done', '100%': 'done', '完成': 'done'
            }
            if task_progress in task_mapping:
                topic.addMarker(f'task-{task_mapping[task_progress]}')
        
        # 表情 - 增加别名支持
        if '_emotion' in data:
            emotion = str(data['_emotion']).lower().strip()
            emotion_mapping = {
                'smile': 'smile', 'happy': 'smile', '😊': 'smile', '微笑': 'smile',
                'laugh': 'laugh', 'joy': 'laugh', '😂': 'laugh', '大笑': 'laugh',
                'angry': 'angry', 'mad': 'angry', '😠': 'angry', '生气': 'angry',
                'cry': 'cry', 'sad': 'cry', '😢': 'cry', '哭泣': 'cry',
                'surprise': 'surprise', 'shocked': 'surprise', '😲': 'surprise', '惊讶': 'surprise',
                'boring': 'boring', 'tired': 'boring', '😴': 'boring', '无聊': 'boring'
            }
            if emotion in emotion_mapping:
                topic.addMarker(f'smiley-{emotion_mapping[emotion]}')
        
        # 符号 - 增加别名支持
        if '_symbol' in data:
            symbol = str(data['_symbol']).lower().strip()
            symbol_mapping = {
                'plus': 'plus', 'add': 'plus', '+': 'plus', '加号': 'plus',
                'minus': 'minus', 'subtract': 'minus', '-': 'minus', '减号': 'minus',
                'question': 'question', '?': 'question', '问号': 'question',
                'exclam': 'exclam', 'exclamation': 'exclam', '!': 'exclam', '感叹号': 'exclam',
                'info': 'info', 'information': 'info', 'i': 'info', '信息': 'info',
                'wrong': 'wrong', 'error': 'wrong', 'x': 'wrong', '错误': 'wrong',
                'right': 'right', 'correct': 'right', 'check': 'right', '正确': 'right'
            }
            if symbol in symbol_mapping:
                topic.addMarker(f'symbol-{symbol_mapping[symbol]}')
        
        # 箭头 - 增加更多方向支持
        if '_arrow' in data:
            arrow = str(data['_arrow']).lower().strip()
            arrow_mapping = {
                'up': 'up', 'north': 'up', '↑': 'up', '上': 'up',
                'up-right': 'up-right', 'northeast': 'up-right', '↗': 'up-right', '右上': 'up-right',
                'right': 'right', 'east': 'right', '→': 'right', '右': 'right',
                'down-right': 'down-right', 'southeast': 'down-right', '↘': 'down-right', '右下': 'down-right',
                'down': 'down', 'south': 'down', '↓': 'down', '下': 'down',
                'down-left': 'down-left', 'southwest': 'down-left', '↙': 'down-left', '左下': 'down-left',
                'left': 'left', 'west': 'left', '←': 'left', '左': 'left',
                'up-left': 'up-left', 'northwest': 'up-left', '↖': 'up-left', '左上': 'up-left',
                'refresh': 'refresh', 'reload': 'refresh', '🔄': 'refresh', '刷新': 'refresh'
            }
            if arrow in arrow_mapping:
                topic.addMarker(f'arrow-{arrow_mapping[arrow]}')
        
        # 超链接 - 增强URL验证和处理
        if '_url' in data:
            url = str(data['_url']).strip()
            if url:
                # 简单URL格式验证和修正
                if not url.startswith(('http://', 'https://', 'ftp://', 'file://')):
                    if '.' in url:  # 看起来像域名
                        url = 'https://' + url
                topic.setURLHyperlink(url)
        elif '_file' in data:
            file_path = str(data['_file']).strip()
            if file_path:
                topic.setFileHyperlink(file_path)
        elif '_topic' in data:
            topic_link = str(data['_topic']).strip()
            if topic_link:
                topic.setTopicHyperlink(topic_link)
        
        # 折叠状态 - 支持多种表达方式
        if '_folded' in data:
            folded_value = data['_folded']
            # 支持布尔值、字符串、数字
            if isinstance(folded_value, bool):
                is_folded = folded_value
            elif isinstance(folded_value, str):
                is_folded = folded_value.lower() in ['true', '1', 'yes', 'on', '是', '折叠']
            elif isinstance(folded_value, (int, float)):
                is_folded = bool(folded_value)
            else:
                is_folded = False
            
            if is_folded:
                topic.setFolded()
        
        # 位置设置 - 增强格式兼容性
        if '_position' in data:
            position = data['_position']
            x, y = None, None
            
            try:
                if isinstance(position, (list, tuple)) and len(position) >= 2:
                    x, y = float(position[0]), float(position[1])
                elif isinstance(position, str):
                    # 支持 "x,y" 格式
                    if ',' in position:
                        coords = position.split(',')
                        if len(coords) >= 2:
                            x, y = float(coords[0].strip()), float(coords[1].strip())
                elif isinstance(position, dict):
                    # 支持 {"x": 100, "y": 200} 格式
                    if 'x' in position and 'y' in position:
                        x, y = float(position['x']), float(position['y'])
                
                if x is not None and y is not None:
                    topic.setPosition(int(x), int(y))
            except (ValueError, TypeError, IndexError):
                pass  # 忽略无效的位置数据
        
        # 新增：样式支持
        if '_style' in data:
            style = str(data['_style']).lower().strip()
            # 虽然XMind库可能不直接支持，但为未来扩展预留
            if style in ['bold', 'italic', 'underline']:
                # 可以通过修改标题来实现简单样式
                current_title = topic.getTitle() or ""
                if style == 'bold' and not current_title.startswith('**'):
                    topic.setTitle(f"**{current_title}**")
                elif style == 'italic' and not current_title.startswith('*'):
                    topic.setTitle(f"*{current_title}*")
        
        # 新增：颜色支持（用于主题着色）
        if '_color' in data:
            color = str(data['_color']).lower().strip()
            # XMind支持的基本颜色标记
            valid_colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'gray', 'black']
            if color in valid_colors:
                # 通过添加颜色相关的标记来实现
                topic.addMarker(f'color-{color}')  # 注意：这可能需要XMind库的具体支持
    
    def _parse_input_data(self, input_data: Any) -> Any:
        """智能解析各种格式的输入数据，大幅提升兼容性"""
        import re
        
        # 如果已经是字典或列表，直接返回
        if isinstance(input_data, (dict, list)):
            return input_data
        
        # 如果是空值，返回None
        if input_data is None:
            return None
        
        # 转换为字符串进行处理
        if not isinstance(input_data, str):
            input_data = str(input_data)
        
        # 清理输入字符串
        data_str = input_data.strip()
        
        # 处理明确的空值
        if not data_str or data_str.lower() in ['null', 'none', 'undefined', 'nil', '空']:
            return None
        
        # 尝试JSON解析
        try:
            return json.loads(data_str)
        except json.JSONDecodeError:
            pass
        
        # 尝试修复常见JSON格式问题
        try:
            # 修复单引号问题
            fixed_json = data_str.replace("'", '"')
            # 修复Python字典格式
            fixed_json = re.sub(r'\b(True|False|None)\b', lambda m: {
                'True': 'true', 'False': 'false', 'None': 'null'
            }[m.group()], fixed_json)
            return json.loads(fixed_json)
        except json.JSONDecodeError:
            pass
        
        # 尝试解析为YAML格式（简单支持）
        try:
            # 检测YAML格式特征
            if ':' in data_str and (data_str.count('\n') > 0 or data_str.count('  ') > 0):
                return self._parse_simple_yaml(data_str)
        except:
            pass
        
        # 尝试解析为CSV格式
        try:
            if ',' in data_str and '\n' in data_str:
                return self._parse_csv_to_dict(data_str)
        except:
            pass
        
        # 尝试解析为键值对格式
        try:
            if '=' in data_str or ':' in data_str:
                return self._parse_key_value_pairs(data_str)
        except:
            pass
        
        # 尝试解析为列表格式
        try:
            if data_str.startswith(('[', '(')) or '\n' in data_str:
                return self._parse_as_list(data_str)
        except:
            pass
        
        # 如果所有解析都失败，创建一个简单的结构
        return {"内容": data_str}
    
    def _parse_simple_yaml(self, yaml_str: str) -> dict:
        """简单的YAML解析器，支持基本的键值对结构"""
        result = {}
        lines = yaml_str.strip().split('\n')
        current_dict = result
        indent_stack = [result]
        
        for line in lines:
            if not line.strip() or line.strip().startswith('#'):
                continue
            
            # 计算缩进级别
            indent = len(line) - len(line.lstrip())
            content = line.strip()
            
            if ':' in content:
                key, value = content.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # 处理值
                if not value:
                    current_dict[key] = {}
                    indent_stack.append(current_dict[key])
                else:
                    # 尝试转换值类型
                    if value.lower() in ['true', 'yes']:
                        value = True
                    elif value.lower() in ['false', 'no']:
                        value = False
                    elif value.lower() in ['null', 'none']:
                        value = None
                    elif value.isdigit():
                        value = int(value)
                    elif value.replace('.', '').isdigit():
                        value = float(value)
                    
                    current_dict[key] = value
        
        return result
    
    def _parse_csv_to_dict(self, csv_str: str) -> dict:
        """将CSV格式转换为字典结构"""
        lines = csv_str.strip().split('\n')
        if len(lines) < 2:
            return {"数据": csv_str}
        
        headers = [h.strip() for h in lines[0].split(',')]
        result = {}
        
        for i, line in enumerate(lines[1:], 1):
            values = [v.strip() for v in line.split(',')]
            row_data = {}
            for j, header in enumerate(headers):
                if j < len(values):
                    row_data[header] = values[j]
            result[f"行{i}"] = row_data
        
        return result
    
    def _parse_key_value_pairs(self, kv_str: str) -> dict:
        """解析键值对格式的字符串"""
        result = {}
        
        # 支持多种分隔符
        separators = ['=', ':', '->', '=>']
        line_separators = ['\n', ';', ',']
        
        # 选择合适的分隔符
        separator = '='
        for sep in separators:
            if sep in kv_str:
                separator = sep
                break
        
        # 选择行分隔符
        line_sep = '\n'
        for lsep in line_separators:
            if lsep in kv_str:
                line_sep = lsep
                break
        
        # 解析每一行
        lines = kv_str.split(line_sep)
        for line in lines:
            line = line.strip()
            if separator in line:
                key, value = line.split(separator, 1)
                key = key.strip()
                value = value.strip()
                
                # 清理引号
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                result[key] = value
        
        return result
    
    def _parse_as_list(self, list_str: str) -> list:
        """将字符串解析为列表结构"""
        # 移除括号
        content = list_str.strip()
        if content.startswith('[') and content.endswith(']'):
            content = content[1:-1]
        elif content.startswith('(') and content.endswith(')'):
            content = content[1:-1]
        
        # 按行或逗号分割
        if '\n' in content:
            items = [item.strip() for item in content.split('\n') if item.strip()]
        else:
            items = [item.strip() for item in content.split(',') if item.strip()]
        
        # 清理引号和处理数据类型
        result = []
        for item in items:
            item = item.strip()
            if item.startswith('"') and item.endswith('"'):
                item = item[1:-1]
            elif item.startswith("'") and item.endswith("'"):
                item = item[1:-1]
            elif item.isdigit():
                item = int(item)
            elif item.replace('.', '').isdigit():
                item = float(item)
            elif item.lower() in ['true', 'false']:
                item = item.lower() == 'true'
            
            result.append(item)
        
        return result
    
    def _convert_json_to_xmind(self, data: Any, parent_topic: TopicElement, max_depth: int = 10, current_depth: int = 0):
        """递归转换JSON为XMind主题结构，增强错误处理和格式兼容性"""
        
        # 安全检查
        if current_depth >= max_depth:
            plugin_logger.warning(f"达到最大递归深度 {max_depth}，停止处理")
            return
            
        if data is None:
            return
        
        try:
            if isinstance(data, dict):
                # 分离元数据和内容数据
                metadata = {k: v for k, v in data.items() if k.startswith('_')}
                content = {k: v for k, v in data.items() if not k.startswith('_')}
                
                # 如果有元数据，安全地应用到当前主题
                if metadata:
                    try:
                        self._apply_metadata(parent_topic, metadata)
                    except Exception as e:
                        plugin_logger.warning(f"应用元数据失败: {e}")
                
                # 处理内容数据
                for key, value in content.items():
                    try:
                        # 清理和验证键名
                        clean_key = self._clean_node_title(str(key))
                        if not clean_key:
                            clean_key = f"节点{len(parent_topic.getSubTopics()) + 1}"
                        
                        child_topic = parent_topic.addSubTopic()
                        child_topic.setTitle(clean_key)
                        
                        if value is None:
                            # null值：只创建节点，添加特殊标记
                            child_topic.setPlainNotes("空值")
                            continue
                        elif isinstance(value, (dict, list)):
                            # 复杂类型：继续递归
                            self._convert_json_to_xmind(value, child_topic, max_depth, current_depth + 1)
                        else:
                            # 基础类型：创建子节点或直接设置内容
                            self._handle_leaf_value(child_topic, value)
                    except Exception as e:
                        plugin_logger.error(f"处理键 '{key}' 时出错: {e}")
                        # 创建错误节点以保持数据完整性
                        error_topic = parent_topic.addSubTopic()
                        error_topic.setTitle(f"错误: {key}")
                        error_topic.setPlainNotes(f"处理失败: {str(e)}")
            
            elif isinstance(data, list):
                # 数组：为每个元素创建同级子主题
                for i, item in enumerate(data):
                    try:
                        child_topic = parent_topic.addSubTopic()
                        
                        # 智能命名数组项
                        if isinstance(item, dict) and item:
                            # 尝试从字典中提取有意义的标题
                            title = self._extract_meaningful_title(item, i)
                        elif isinstance(item, str) and len(item) <= 50:
                            # 短字符串直接作为标题
                            title = self._clean_node_title(item)
                        else:
                            # 默认编号
                            title = f"项目 {i+1}"
                        
                        child_topic.setTitle(title)
                        
                        if isinstance(item, (dict, list)):
                            self._convert_json_to_xmind(item, child_topic, max_depth, current_depth + 1)
                        else:
                            self._handle_leaf_value(child_topic, item)
                    except Exception as e:
                        plugin_logger.error(f"处理数组项 {i} 时出错: {e}")
                        # 创建错误节点
                        error_topic = parent_topic.addSubTopic()
                        error_topic.setTitle(f"错误项目 {i+1}")
                        error_topic.setPlainNotes(f"处理失败: {str(e)}")
            
            else:
                # 基础类型：直接处理
                self._handle_leaf_value(parent_topic, data)
                
        except Exception as e:
            plugin_logger.error(f"转换过程中发生严重错误: {e}")
            # 添加错误信息到思维导图中
            error_topic = parent_topic.addSubTopic()
            error_topic.setTitle("转换错误")
            error_topic.setPlainNotes(f"数据转换失败: {str(e)}")
    
    def _clean_node_title(self, title: str) -> str:
        """清理节点标题，确保XMind兼容性"""
        if not title:
            return ""
        
        # 移除控制字符和特殊字符
        import re
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', str(title))
        
        # 限制长度，避免显示问题
        if len(cleaned) > 100:
            cleaned = cleaned[:97] + "..."
        
        # 移除首尾空白
        return cleaned.strip()
    
    def _extract_meaningful_title(self, item: dict, index: int) -> str:
        """从字典中提取有意义的标题"""
        # 常见的标题字段
        title_fields = ['title', 'name', 'label', '标题', '名称', '名字', 'id', 'key']
        
        for field in title_fields:
            if field in item:
                title = self._clean_node_title(str(item[field]))
                if title:
                    return title
        
        # 如果没有找到标题字段，使用第一个字符串值
        for key, value in item.items():
            if isinstance(value, str) and len(value) <= 50:
                title = self._clean_node_title(value)
                if title:
                    return f"{title}"
        
        # 默认编号
        return f"项目 {index+1}"
    
    def _handle_leaf_value(self, topic: TopicElement, value: Any):
        """处理叶子节点的值，增强类型支持"""
        try:
            if value is None:
                topic.setPlainNotes("空值")
                return
            
            # 转换为字符串
            str_value = str(value)
            
            # 对于简短的值，直接作为子节点
            if len(str_value) <= 100:
                leaf_topic = topic.addSubTopic()
                leaf_topic.setTitle(self._clean_node_title(str_value))
            else:
                # 对于长文本，放在备注中
                topic.setPlainNotes(str_value[:500] + ("..." if len(str_value) > 500 else ""))
                
            # 根据值类型添加额外信息
            if isinstance(value, bool):
                topic.addMarker('symbol-right' if value else 'symbol-wrong')
            elif isinstance(value, (int, float)):
                if isinstance(value, int) and value > 0:
                    # 为正数添加正面标记
                    topic.addMarker('symbol-plus')
                elif isinstance(value, (int, float)) and value < 0:
                    # 为负数添加负面标记
                    topic.addMarker('symbol-minus')
            elif isinstance(value, str):
                # 检测URL
                if value.startswith(('http://', 'https://', 'ftp://')):
                    topic.setURLHyperlink(value)
                    topic.addMarker('symbol-info')
                # 检测邮箱
                elif '@' in value and '.' in value:
                    topic.addMarker('symbol-info')
                    
        except Exception as e:
            plugin_logger.error(f"处理叶子值时出错: {e}")
            # 安全处理：至少创建一个节点
            try:
                leaf_topic = topic.addSubTopic()
                leaf_topic.setTitle("数据处理错误")
                leaf_topic.setPlainNotes(f"原值: {str(value)[:100]}, 错误: {str(e)}")
            except:
                pass  # 如果连错误节点都创建不了，就忽略
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        plugin_logger.info("🚀 JSON2XMind工具开始执行")
        plugin_logger.info(f"📋 接收到的参数: {tool_parameters}")
        plugin_logger.info(f"🔧 参数类型: {[(k, type(v).__name__) for k, v in tool_parameters.items()]}")
        
        try:
            # 获取参数
            json_data = tool_parameters.get('json_data', '{}')
            root_title = tool_parameters.get('root_title', '思维导图')
            max_depth = tool_parameters.get('max_depth', 10)
            
            plugin_logger.info(f"✅ 参数解析完成: json_data类型={type(json_data)}, root_title={root_title}, max_depth={max_depth}")
            
            # 调试信息
            yield self.create_text_message(f"🔧 开始处理JSON转XMind转换...")
            yield self.create_text_message(f"📝 参数信息: 根标题={root_title}, 最大深度={max_depth}")
            yield self.create_text_message(f"📊 输入数据类型: {type(json_data).__name__}")
            
            
            # 智能解析JSON数据 - 大幅增强格式兼容性
            plugin_logger.info("🔍 开始解析JSON数据")
            try:
                data = self._parse_input_data(json_data)
                
                # 验证数据不为空
                if data is None:
                    yield self.create_json_message({
                        "success": False,
                        "error": "输入数据为空或无效",
                        "message": "请提供有效的数据。支持JSON字符串、对象、数组、YAML格式或任意结构化数据。"
                    })
                    return
                
                yield self.create_text_message(f"✅ 数据解析成功! 数据类型: {type(data).__name__}")
                plugin_logger.info(f"✅ 数据解析成功: 数据类型={type(data)}, 数据长度={len(str(data))}")
                    
            except Exception as e:
                plugin_logger.error(f"❌ 数据解析失败: {e}")
                yield self.create_json_message({
                    "success": False,
                    "error": f"数据解析失败: {str(e)}",
                    "message": "数据格式无法识别。支持JSON、YAML、CSV或其他结构化数据格式。"
                })
                return
            
            # 创建XMind工作簿
            yield self.create_text_message(f"🏗️ 正在创建XMind工作簿...")
            plugin_logger.info("🏗️ 开始创建XMind工作簿")
            
            # 直接使用WorkbookDocument创建新的工作簿
            try:
                from xmind.core.workbook import WorkbookDocument
                from xmind.core.styles import StylesBookDocument
                from xmind.core.comments import CommentsBookDocument
                
                workbook = WorkbookDocument()
                # 初始化必要的子文档
                workbook.stylesbook = StylesBookDocument()
                workbook.commentsbook = CommentsBookDocument()
                # 设置一个临时路径以避免 None 路径问题
                workbook.set_path("/tmp/temp.xmind")
                
                sheet = workbook.getPrimarySheet()
                if sheet is None:
                    raise ValueError("无法获取主工作表")
                sheet.setTitle("JSON转换结果")
                
                root_topic = sheet.getRootTopic()
                if root_topic is None:
                    raise ValueError("无法获取根主题")
                root_topic.setTitle(root_title)
            except ImportError as e:
                raise Exception(f"XMind库导入失败，请确保已正确安装xmind库: {str(e)}")
            except Exception as e:
                raise Exception(f"创建XMind工作簿失败: {str(e)}")
            yield self.create_text_message(f"📋 工作簿创建完成，根节点: {root_title}")
            plugin_logger.info(f"✅ XMind工作簿创建完成: 根节点={root_title}")
            
            # 转换JSON数据到XMind
            yield self.create_text_message(f"🔄 开始转换JSON数据到XMind结构...")
            plugin_logger.info("🔄 开始转换JSON到XMind结构")
            self._convert_json_to_xmind(data, root_topic, max_depth)
            yield self.create_text_message(f"✅ JSON结构转换完成!")
            plugin_logger.info("✅ JSON到XMind结构转换完成")
            
            # 计算统计信息
            def count_nodes(topic: TopicElement):
                count = 1
                sub_topics = topic.getSubTopics()
                if sub_topics:
                    for sub_topic in sub_topics:
                        count += count_nodes(sub_topic)
                return count
            
            total_nodes = count_nodes(root_topic)
            filename = f"{root_title}.xmind"
            
            yield self.create_text_message(f"📊 统计信息: 总节点数={total_nodes}, 文件名={filename}")
            yield self.create_text_message(f"💾 正在生成XMind文件...")
            
            # 生成XMind文件
            plugin_logger.info("📄 开始生成临时XMind文件")
            temp_file = tempfile.NamedTemporaryFile(suffix='.xmind', delete=False)
            temp_path = temp_file.name
            temp_file.close()  # 关闭文件句柄，但保留文件
            
            if temp_path is None:
                raise ValueError("无法创建临时文件")
            
            # 保存XMind文件
            plugin_logger.info(f"💾 保存XMind文件到: {temp_path}")
            try:
                xmind.save(workbook, temp_path)
            except Exception as e:
                # 清理可能创建的临时文件
                try:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                except:
                    pass
                raise Exception(f"保存XMind文件失败: {str(e)}")
            
            # 读取文件内容
            plugin_logger.info("📖 读取XMind文件内容")
            try:
                with open(temp_path, 'rb') as f:
                    file_content = f.read()
                plugin_logger.info(f"✅ 文件读取成功，大小: {len(file_content)} bytes")
            except Exception as e:
                # 清理临时文件
                try:
                    os.unlink(temp_path)
                except:
                    pass
                raise Exception(f"读取文件内容失败: {str(e)}")
            
            file_size = len(file_content)
            
            # 清理临时文件
            try:
                os.unlink(temp_path)
            except Exception as e:
                plugin_logger.warning(f"⚠️ 清理临时文件失败: {e}")
            
            # 智能推断MIME类型并返回文件
            # 确保XMind类型已注册
            mimetypes.add_type('application/vnd.xmind.workbook', '.xmind')
            
            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type:
                # 如果无法推断，使用XMind的标准MIME类型
                mime_type = "application/vnd.xmind.workbook"
            
            plugin_logger.info(f"📁 使用MIME类型: {mime_type} 用于文件: {filename}")
            
            yield self.create_blob_message(
                blob=file_content,
                meta={
                    "mime_type": mime_type,
                    "filename": filename
                }
            )
            
            # 同时返回成功信息
            yield self.create_json_message({
                "success": True,
                "message": f"XMind文件已生成，可直接下载使用",
                "filename": filename,
                "file_size": file_size,
                "instructions": "📥 点击下载按钮即可获取 XMind 文件，可直接在 XMind 软件中打开使用",
                "statistics": {
                    "total_nodes": total_nodes,
                    "max_depth_used": min(max_depth, self._calculate_depth(data)),
                    "root_title": root_title
                }
            })
            
        except Exception as e:
            plugin_logger.error(f"💥 JSON2XMind转换出错: {str(e)}", exc_info=True)
            yield self.create_json_message({
                "success": False,
                "error": str(e),
                "message": "转换过程中发生错误，请检查输入数据",
                "error_type": type(e).__name__
            })
    
    def _calculate_depth(self, data: Any, current_depth: int = 0) -> int:
        """计算JSON数据的最大深度"""
        if not isinstance(data, (dict, list)):
            return current_depth
        
        max_child_depth = current_depth
        
        if isinstance(data, dict):
            for value in data.values():
                if not str(value).startswith('_'):  # 忽略元数据字段
                    child_depth = self._calculate_depth(value, current_depth + 1)
                    max_child_depth = max(max_child_depth, child_depth)
        elif isinstance(data, list):
            for item in data:
                child_depth = self._calculate_depth(item, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth

# 模块加载完成日志
plugin_logger.info("✅ Json2xmind 工具模块加载完成")
