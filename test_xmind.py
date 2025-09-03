#!/usr/bin/env python3
import tempfile
import xmind

# 测试xmind库基本功能
try:
    # 创建临时文件
    with tempfile.NamedTemporaryFile(suffix='.xmind', delete=False) as temp_file:
        temp_path = temp_file.name
    
    print(f"创建临时文件: {temp_path}")
    
    # 使用WorkbookDocument直接创建新工作簿
    from xmind.core.workbook import WorkbookDocument
    workbook = WorkbookDocument()
    
    # 初始化stylesbook
    from xmind.core.styles import StylesBookDocument
    workbook.stylesbook = StylesBookDocument()
    
    print("工作簿加载成功")
    
    # 获取主sheet
    sheet = workbook.getPrimarySheet()
    print("获取主sheet成功")
    
    # 获取根主题
    root_topic = sheet.getRootTopic()
    root_topic.setTitle("测试根节点")
    print("设置根节点标题成功")
    
    # 添加子主题
    child = root_topic.addSubTopic()
    child.setTitle("子节点1")
    print("添加子节点成功")
    
    # 保存文件
    xmind.save(workbook, temp_path)
    print("保存XMind文件成功")
    
    # 检查文件大小
    import os
    file_size = os.path.getsize(temp_path)
    print(f"文件大小: {file_size} bytes")
    
    if file_size > 0:
        print("✅ XMind库测试成功!")
    else:
        print("❌ XMind文件为空")
    
    # 清理
    os.unlink(temp_path)
    
except Exception as e:
    print(f"❌ XMind库测试失败: {e}")
    import traceback
    traceback.print_exc()