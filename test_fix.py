#!/usr/bin/env python3
"""
测试修复后的JSON2XMind工具
"""
import json
import sys
import os
import logging

# 添加项目目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.json2xmind import Json2xmindTool

class MockRuntime:
    """模拟运行时环境"""
    def __init__(self):
        self.credentials = {}

class MockSession:
    """模拟会话"""
    def __init__(self):
        pass

def test_simple_json():
    """测试简单JSON转换"""
    print("🧪 开始测试简单JSON转换...")
    
    # 创建工具实例
    runtime = MockRuntime()
    session = MockSession()
    tool = Json2xmindTool(runtime=runtime, session=session)
    
    # 测试数据
    test_data = {
        "根节点": {
            "子节点1": ["项目1", "项目2"],
            "子节点2": None,
            "子节点3": "单个值"
        }
    }
    
    # 测试参数
    tool_parameters = {
        "json_data": json.dumps(test_data, ensure_ascii=False),
        "root_title": "测试思维导图",
        "max_depth": 10,
        "output_format": "file"  # 使用file格式方便查看结果
    }
    
    try:
        # 调用工具
        messages = list(tool._invoke(tool_parameters))
        
        print(f"✅ 工具调用完成，返回了 {len(messages)} 条消息")
        
        for i, message in enumerate(messages):
            print(f"消息 {i+1}: {message}")
            
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_with_metadata():
    """测试带元数据的JSON转换"""
    print("\n🧪 开始测试带元数据的JSON转换...")
    
    runtime = MockRuntime()
    session = MockSession()
    tool = Json2xmindTool(runtime=runtime, session=session)
    
    test_data = {
        "_priority": 1,
        "_label": "软件开发项目",
        "_note": "2024年重点项目",
        "开发阶段": {
            "_star": "red",
            "_task": "half",
            "需求分析": {
                "_priority": 2,
                "_flag": "green",
                "功能需求": ["用户登录", "数据展示", "权限管理"],
                "非功能需求": None
            },
            "技术实现": {
                "_priority": 1,
                "_emotion": "smile",
                "_url": "https://github.com/project",
                "前端技术": ["React", "TypeScript", "Tailwind"],
                "后端技术": {
                    "_symbol": "right",
                    "编程语言": ["Python", "JavaScript"],
                    "数据库": None
                }
            }
        }
    }
    
    tool_parameters = {
        "json_data": json.dumps(test_data, ensure_ascii=False),
        "root_title": "元数据测试导图",
        "max_depth": 10,
        "output_format": "file"
    }
    
    try:
        messages = list(tool._invoke(tool_parameters))
        
        print(f"✅ 元数据测试完成，返回了 {len(messages)} 条消息")
        
        for i, message in enumerate(messages):
            print(f"消息 {i+1}: {message}")
            
        return True
        
    except Exception as e:
        print(f"❌ 元数据测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_different_formats():
    """测试不同输出格式"""
    print("\n🧪 开始测试不同输出格式...")
    
    runtime = MockRuntime()
    session = MockSession()
    tool = Json2xmindTool(runtime=runtime, session=session)
    
    test_data = {"简单测试": {"子项": ["A", "B", "C"]}}
    
    formats = ["file", "base64", "blob", "zip"]
    
    for format_name in formats:
        print(f"\n测试格式: {format_name}")
        
        tool_parameters = {
            "json_data": json.dumps(test_data, ensure_ascii=False),
            "root_title": f"格式测试-{format_name}",
            "max_depth": 5,
            "output_format": format_name
        }
        
        try:
            messages = list(tool._invoke(tool_parameters))
            print(f"✅ 格式 {format_name} 测试成功，返回 {len(messages)} 条消息")
            
        except Exception as e:
            print(f"❌ 格式 {format_name} 测试失败: {str(e)}")
            return False
            
    return True

def main():
    """主测试函数"""
    print("🚀 开始JSON2XMind修复验证测试\n")
    
    # 设置日志级别
    logging.basicConfig(level=logging.INFO)
    
    tests = [
        ("简单JSON转换", test_simple_json),
        ("元数据JSON转换", test_with_metadata), 
        ("不同输出格式", test_different_formats)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"执行测试: {test_name}")
        print('='*50)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} 通过")
        else:
            print(f"❌ {test_name} 失败")
    
    print(f"\n{'='*50}")
    print(f"测试总结: {passed}/{total} 项测试通过")
    print('='*50)
    
    if passed == total:
        print("🎉 所有测试通过！修复成功！")
        return 0
    else:
        print("⚠️  部分测试失败，需要进一步检查")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)