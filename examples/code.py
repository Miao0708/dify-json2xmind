# code节点参考，输入为 json list字符串，loads 后为 list(dict),然后转换为 xmind 结构
def _get_field_value(case: dict, *field_names: str, default: str = "") -> str:
    """获取字段值，支持多个字段名的回退机制"""
    for field_name in field_names:
        value = case.get(field_name)
        if value:
            return value
    return default


def _parse_priority(priority_str: str) -> int:
    """解析优先级字符串，转换为 XMind 优先级数字"""
    if not priority_str or not priority_str.startswith('P'):
        return 2
    try:
        return min(int(priority_str[1:]), 6)
    except (ValueError, IndexError):
        return 2


def _format_list_with_numbers(data, default: str = "") -> str:
    """将列表或字符串格式化为带序号的文本"""
    if not data:
        return default
    if isinstance(data, str) and data.strip():
        return data
    elif isinstance(data, list):
        return '\n'.join([f"{i+1}. {item}" for i, item in enumerate(data)])
    return default


def main(test_cases: str) -> dict:
    """
    将测试用例数据转换为符合 json2xmind 格式的数据结构
    
    Args:
        test_cases (str): JSON 字符串格式的测试用例数据，或者已解析的字典/列表
        
    Returns:
        dict: 包含转换结果的字典，格式为 {'xmind_json': JSON字符串}
              如果转换失败，返回包含错误信息的结构
              
    功能说明：
        - 支持单个或多个测试用例的转换
        - 支持中英文字段名称（如 'module'/'一级分组', 'title'/'标题' 等）
        - 将测试用例按模块分组组织
        - 转换优先级格式（P1->1, P2->2 等）
        - 格式化前置条件、测试步骤和预期结果为带序号的列表
    """
    import json

    try:
        # 解析输入的测试用例数据
        # 如果输入是字符串则进行 JSON 解析，否则直接使用（支持传入已解析的数据）
        cases_data = json.loads(test_cases) if isinstance(test_cases, str) else test_cases

        # 确保输入是列表格式
        # 如果传入单个测试用例（字典），则转换为包含一个元素的列表
        if not isinstance(cases_data, list):
            cases_data = [cases_data]

        # 按模块分组测试用例 - 使用正确的字段名
        # 创建模块字典，用于按模块名称分组测试用例
        modules = {}
        for case in cases_data:
            # 获取模块名称，支持中英文字段名：'module' 或 '一级分组'
            module_name = _get_field_value(case, 'module', '一级分组', default='未分类模块')
            # 如果模块不存在则创建新的模块列表
            if module_name not in modules:
                modules[module_name] = []
            # 将当前测试用例添加到对应模块中
            modules[module_name].append(case)

        # 构建符合 json2xmind 格式的数据结构
        # 这是最终输出的主数据结构，每个模块作为一级节点
        xmind_structure = {}

        # 遍历每个模块
        # 为每个模块创建对应的节点结构
        for module_name, module_cases in modules.items():
            # 创建模块节点，用于存储该模块下的所有测试用例
            module_node: dict = {}

            # 为每个测试用例创建节点
            # 遍历当前模块下的所有测试用例
            for case in module_cases:
                # 获取测试用例标题，支持多种字段名：'title'、'标题'、'用例ID'
                case_title = _get_field_value(case, 'title', '标题', '用例ID', default='未命名用例')

                # 转换优先级格式 (P1->1, P2->2, etc.)
                # XMind 中优先级使用数字表示，默认为中等优先级 2
                priority_str = _get_field_value(case, 'priority', '优先级')
                priority_value = _parse_priority(priority_str)

                # 处理前置条件 - 带序号换行
                # 将前置条件格式化为带序号的文本
                preconditions = case.get('preconditions', case.get('前置条件', ""))
                condition_text = _format_list_with_numbers(preconditions)

                # 处理测试步骤 - 带序号换行
                # 将测试步骤格式化为带序号的文本
                steps = case.get('steps', case.get('步骤', []))
                steps_text = _format_list_with_numbers(steps)

                # 处理预期结果 - 带序号换行
                # 将预期结果格式化为带序号的文本
                expected = case.get('expected', case.get('预期结果', []))
                expected_text = _format_list_with_numbers(expected)
                
                # 处理测试项
                # 获取测试项名称，支持中英文字段名
                testing_item = _get_field_value(case, '测试项', 'testing_item', default='未命名测试项')
                # 处理备注
                # 获取备注信息，支持 'remark' 或 '备注' 字段
                note = _get_field_value(case, 'remark', '备注')

                # 构建用例节点结构
                # 创建测试用例节点，设置优先级（XMind 的特殊属性以 _ 开头）
                case_node: dict = {
                    "_priority": priority_value,  # XMind 优先级属性
                }

                # 构建各个子节点的键值对
                # 格式化各个字段为 XMind 节点的键名
                condition_key = f"前置条件：\n{condition_text}"  # 前置条件节点
                note_key = f"备注：{note}"  # 备注节点
                steps_key = f"步骤：\n{steps_text}"  # 测试步骤节点
                steps_value = f"预期结果：\n{expected_text}"  # 预期结果作为步骤的子节点
                testing_item_key = f"测试项：{testing_item}"  # 测试项节点

                # 将各个信息作为子节点添加到用例节点中
                # None 值表示该节点没有子节点，纯文本显示
                case_node[testing_item_key] = None  # 测试项子节点
                case_node[condition_key] = None     # 前置条件子节点
                case_node[steps_key] = steps_value  # 步骤子节点（包含预期结果）
                case_node[note_key] = None          # 备注子节点


                # 将用例添加到模块中
                # 以测试用例标题为键，用例节点结构为值
                module_node[case_title] = case_node

            # 将模块添加到主结构中
            # 以模块名称为键，模块节点结构为值，构成完整的 XMind 数据结构
            xmind_structure[module_name] = module_node

        # 返回转换后的JSON字符串
        # 将数据结构序列化为 JSON 字符串，保持中文字符显示，使用缩进格式化
        result_json = json.dumps(xmind_structure, ensure_ascii=False, indent=2)

        # 返回包含转换结果的字典
        return {
            'xmind_json': result_json
        }

    except Exception as e:
        # 异常处理：当转换过程中出现错误时，返回包含错误信息的 XMind 结构
        return {
            'xmind_json': json.dumps({
                "错误": {  # 错误节点
                    "_priority": 6,                    # 最高优先级
                    "_star": "red",                   # 红色星标标记
                    "_note": f"转换失败：{str(e)}",      # 添加错误注释
                    "错误信息": str(e)                  # 具体错误信息
                }
            }, ensure_ascii=False)  # 保持中文字符显示
        }
    
# 测试数据示例
# 包含完整测试用例信息的 JSON 字符串，用于演示函数功能
s = '[{"case_id":"c-ep-management-001","module_id":"m-ep-management","point_id":"p-ep-management-001","module":"EP管理优化","testing_item":"开关配置","priority":"P1","is_negative":"否","title":"配置并保存EP的AutoLink、TouchStart和摇一摇开关","preconditions":["用户已登录并具备EP管理权限","进入新增EP页面"],"steps":["选择开启AutoLink功能开关","选择开启TouchStart功能开关","选择开启摇一摇功能开关","填写EP基本信息并点击保存"],"expected":["AutoLink开关状态被正确记录为开启","TouchStart开关状态被正确记录为开启","摇一摇开关状态被正确记录为开启","EP创建成功并显示在列表中"],"remark":"无"}]'
# 主程序入口
if __name__ == '__main__':
    # 运行测试：使用示例数据调用主函数并打印转换结果
    print(main(s).get("xmind_json"))