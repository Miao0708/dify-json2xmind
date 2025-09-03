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
        """应用元数据到XMind主题"""
        
        # 优先级 (1-6)
        if '_priority' in data:
            priority = data['_priority']
            if isinstance(priority, int) and 1 <= priority <= 6:
                topic.addMarker(f'priority-{priority}')
        
        # 描述标签
        if '_label' in data:
            current_title = topic.getTitle() or ""
            label = data['_label']
            if label:
                topic.setTitle(f"{current_title} ({label})")
        
        # 备注
        if '_note' in data:
            topic.setPlainNotes(str(data['_note']))
        
        # 星标
        if '_star' in data:
            star_color = data['_star'].lower()
            if star_color in ['red', 'orange', 'yellow', 'blue', 'green', 'purple']:
                topic.addMarker(f'star-{star_color}')
        
        # 旗帜
        if '_flag' in data:
            flag_color = data['_flag'].lower()
            if flag_color in ['red', 'orange', 'yellow', 'blue', 'green', 'purple']:
                topic.addMarker(f'flag-{flag_color}')
        
        # 任务进度
        if '_task' in data:
            task_progress = data['_task']
            valid_tasks = ['start', 'oct', 'quarter', '3oct', 'half', '5oct', '3quar', '7oct', 'done']
            if task_progress in valid_tasks:
                topic.addMarker(f'task-{task_progress}')
        
        # 表情
        if '_emotion' in data:
            emotion = data['_emotion']
            valid_emotions = ['smile', 'laugh', 'angry', 'cry', 'surprise', 'boring']
            if emotion in valid_emotions:
                topic.addMarker(f'smiley-{emotion}')
        
        # 符号
        if '_symbol' in data:
            symbol = data['_symbol']
            valid_symbols = ['plus', 'minus', 'question', 'exclam', 'info', 'wrong', 'right']
            if symbol in valid_symbols:
                topic.addMarker(f'symbol-{symbol}')
        
        # 箭头
        if '_arrow' in data:
            arrow = data['_arrow']
            valid_arrows = ['up', 'up-right', 'right', 'down-right', 'down', 'down-left', 'left', 'up-left', 'refresh']
            if arrow in valid_arrows:
                topic.addMarker(f'arrow-{arrow}')
        
        # 超链接
        if '_url' in data:
            topic.setURLHyperlink(str(data['_url']))
        elif '_file' in data:
            topic.setFileHyperlink(str(data['_file']))
        elif '_topic' in data:
            topic.setTopicHyperlink(str(data['_topic']))
        
        # 折叠状态
        if '_folded' in data and data['_folded']:
            topic.setFolded()
        
        # 位置设置
        if '_position' in data:
            position = data['_position']
            if isinstance(position, list) and len(position) == 2:
                try:
                    x, y = float(position[0]), float(position[1])
                    topic.setPosition(int(x), int(y))
                except (ValueError, TypeError):
                    pass
    
    def _convert_json_to_xmind(self, data: Any, parent_topic: TopicElement, max_depth: int = 10, current_depth: int = 0):
        """递归转换JSON为XMind主题结构"""
        
        if current_depth >= max_depth or data is None:
            return
            
        if isinstance(data, dict):
            # 分离元数据和内容数据
            metadata = {k: v for k, v in data.items() if k.startswith('_')}
            content = {k: v for k, v in data.items() if not k.startswith('_')}
            
            # 如果有元数据，应用到当前主题
            if metadata:
                self._apply_metadata(parent_topic, metadata)
            
            # 处理内容数据
            for key, value in content.items():
                child_topic = parent_topic.addSubTopic()
                child_topic.setTitle(str(key))
                
                if value is None:
                    # null值：只创建节点，不展开
                    continue
                elif isinstance(value, (dict, list)):
                    # 复杂类型：继续递归
                    self._convert_json_to_xmind(value, child_topic, max_depth, current_depth + 1)
                else:
                    # 基础类型：创建子节点
                    leaf_topic = child_topic.addSubTopic()
                    leaf_topic.setTitle(str(value))
        
        elif isinstance(data, list):
            # 数组：为每个元素创建同级子主题
            for i, item in enumerate(data):
                child_topic = parent_topic.addSubTopic()
                
                if isinstance(item, (dict, list)):
                    child_topic.setTitle(f"项目 {i+1}")
                    self._convert_json_to_xmind(item, child_topic, max_depth, current_depth + 1)
                else:
                    child_topic.setTitle(str(item))
        
        else:
            # 基础类型：直接创建叶子节点
            child_topic = parent_topic.addSubTopic()
            child_topic.setTitle(str(data))
    
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
            
            
            # 智能解析JSON数据 - 支持字符串、字典、列表等多种输入格式
            plugin_logger.info("🔍 开始解析JSON数据")
            try:
                if isinstance(json_data, str):
                    # 处理空值和特殊值
                    json_str = json_data.strip()
                    if not json_str or json_str.lower() in ['null', 'none', 'undefined']:
                        yield self.create_json_message({
                            "success": False,
                            "error": "输入数据为空或无效",
                            "message": "请提供有效的JSON数据。支持JSON字符串、对象或数组格式。"
                        })
                        return
                    
                    # 字符串输入：尝试解析为JSON
                    data = json.loads(json_str)
                elif isinstance(json_data, (dict, list)):
                    # 已经是字典或列表：直接使用
                    data = json_data
                else:
                    # 其他类型：转为字符串后再解析
                    data = json.loads(str(json_data))
                
                # 验证数据不为空
                if not data:
                    raise ValueError("输入数据不能为空")
                
                yield self.create_text_message(f"✅ 数据解析成功! 数据类型: {type(data).__name__}")
                plugin_logger.info(f"✅ 数据解析成功: 数据类型={type(data)}, 数据长度={len(str(data))}")
                    
            except json.JSONDecodeError as e:
                plugin_logger.error(f"❌ JSON解析失败: {e}")
                yield self.create_json_message({
                    "success": False,
                    "error": f"JSON解析失败: {str(e)}",
                    "message": "请检查JSON格式是否正确。支持JSON字符串、对象或数组格式。"
                })
                return
            except Exception as e:
                yield self.create_json_message({
                    "success": False,
                    "error": f"数据处理失败: {str(e)}",
                    "message": "数据解析失败，请提供有效的JSON数据。"
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
