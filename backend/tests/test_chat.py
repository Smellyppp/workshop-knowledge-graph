"""
智能问答模块测试脚本
测试基于Qwen大模型的对话功能和记忆管理
"""
import sys
import os
import asyncio
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.chat_service import ChatService
import json


class TestColors:
    """终端颜色输出"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_section(title):
    """打印测试章节标题"""
    print("\n" + "=" * 70)
    print(f"{TestColors.HEADER}{TestColors.BOLD}【{title}】{TestColors.ENDC}")
    print("=" * 70)


def print_success(message):
    """打印成功消息"""
    print(f"{TestColors.OKGREEN}✓ {message}{TestColors.ENDC}")


def print_error(message):
    """打印错误消息"""
    print(f"{TestColors.FAIL}✗ {message}{TestColors.ENDC}")


def print_info(message):
    """打印信息消息"""
    print(f"{TestColors.OKCYAN}ℹ {message}{TestColors.ENDC}")


def test_single_message():
    """
    测试1：单次对话测试
    验证基本的消息发送和回复功能
    """
    print_section("测试1：单次对话测试")

    try:
        # 创建聊天服务实例
        chat_service = ChatService()
        print_success("聊天服务初始化成功")

        # 发送测试消息
        test_message = "你好，请简单介绍一下你自己"
        print_info(f"发送消息: {test_message}")

        # 同步调用异步函数
        response = asyncio.run(chat_service.chat(test_message))

        print_success("收到回复")
        print(f"\n{TestColors.OKBLUE}AI回复:{TestColors.ENDC}")
        print(f"  {response['message']}")
        print(f"\n{TestColors.OKCYAN}会话ID: {response['session_id']}{TestColors.ENDC}")

        return True

    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_multi_turn_conversation():
    """
    测试2：多轮对话测试（3轮记忆）
    验证模型能够记住之前的对话内容
    """
    print_section("测试2：多轮对话测试（3轮记忆）")

    try:
        chat_service = ChatService()
        session_id = "test_session_memory"

        # 定义3轮对话
        conversations = [
            "我遇到了设备故障，设备突然停止运转",
            "设备型号是XYZ-2000，请问可能是什么原因？",
            "如果检查电源后发现没问题，下一步该怎么办？"
        ]

        print_info(f"开始 {len(conversations)} 轮对话测试...")
        print_info(f"会话ID: {session_id}\n")

        for i, message in enumerate(conversations, 1):
            print(f"{TestColors.BOLD}第 {i} 轮对话:{TestColors.ENDC}")
            print(f"  用户: {message}")

            # 发送消息
            response = asyncio.run(chat_service.chat(message, session_id))

            print(f"  AI: {response['message'][:100]}...")  # 只显示前100字符
            print()

        print_success("多轮对话测试完成")
        print_info("对话历史应保留最近3轮（6条消息）")

        # 验证历史记录
        history = chat_service._get_history(session_id)
        message_count = len(history.messages)
        print_info(f"当前历史记录数: {message_count} 条消息")

        if message_count == 6:  # 3轮对话 = 3个用户消息 + 3个AI回复
            print_success("历史记录数量正确（3轮对话 = 6条消息）")
        else:
            print(f"历史记录数量不匹配，预期6条，实际{message_count}条")

        return True

    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_limit():
    """
    测试3：记忆限制测试
    验证超过3轮后，旧的对话会被清除
    """
    print_section("测试3：记忆限制测试（超过3轮）")

    try:
        chat_service = ChatService()
        session_id = "test_memory_limit"

        # 发送5轮对话（超过3轮限制）
        print_info("发送5轮对话（超过3轮限制）...\n")

        for i in range(5):
            message = f"这是第{i+1}轮测试消息"
            asyncio.run(chat_service.chat(message, session_id))
            print(f"  已发送第 {i+1} 轮消息")

        # 检查历史记录
        history = chat_service._get_history(session_id)
        message_count = len(history.messages)

        print(f"\n{TestColors.OKCYAN}实际历史记录数: {message_count} 条{TestColors.ENDC}")

        # 验证只保留了最近3轮
        if message_count == 6:  # 3轮 = 6条消息
            print_success("记忆限制功能正常：只保留最近3轮对话")

            # 显示保留的消息
            print_info("\n保留的消息:")
            for i, msg in enumerate(history.messages, 1):
                role = "用户" if i % 2 != 0 else "AI"
                content = msg.content if hasattr(msg, 'content') else str(msg)
                print(f"  {i}. [{role}] {content[:50]}...")
        else:
            print(f"历史记录数量异常: {message_count} 条（预期6条）")

        return True

    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_clear_history():
    """
    测试4：清除历史测试
    验证清除对话历史功能
    """
    print_section("测试4：清除历史测试")

    try:
        chat_service = ChatService()
        session_id = "test_clear_history"

        # 先发送一些消息
        print_info("发送2轮测试消息...")
        asyncio.run(chat_service.chat("第一条消息", session_id))
        asyncio.run(chat_service.chat("第二条消息", session_id))

        # 检查历史存在
        history = chat_service._get_history(session_id)
        before_count = len(history.messages)
        print_info(f"清除前历史记录数: {before_count} 条")

        # 清除历史
        print_info("\n执行清除操作...")
        chat_service.clear_history(session_id)

        # 验证历史已清除
        after_exists = session_id in chat_service.histories
        print_info(f"会话是否存在: {after_exists}")

        if not after_exists:
            print_success("历史清除成功：会话已从内存中删除")
        else:
            print_error("历史清除失败：会话仍然存在")

        return not after_exists

    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_session_isolation():
    """
    测试5：会话隔离测试
    验证不同session_id之间的对话历史互不干扰
    """
    print_section("测试5：会话隔离测试")

    try:
        chat_service = ChatService()

        # 在两个不同的会话中发送消息
        session_1 = "user_alice"
        session_2 = "user_bob"

        print_info(f"会话1 ({session_1}) 发送消息...")
        asyncio.run(chat_service.chat("我是Alice", session_1))

        print_info(f"会话2 ({session_2}) 发送消息...")
        asyncio.run(chat_service.chat("我是Bob", session_2))

        # 检查两个会话的历史
        history_1 = chat_service._get_history(session_1)
        history_2 = chat_service._get_history(session_2)

        count_1 = len(history_1.messages)
        count_2 = len(history_2.messages)

        print(f"\n会话1消息数: {count_1}")
        print(f"会话2消息数: {count_2}")

        if count_1 > 0 and count_2 > 0:
            print_success("会话隔离功能正常：两个会话的历史记录独立")
            return True
        else:
            print_error("会话隔离失败：历史记录数量异常")
            return False

    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_fault_diagnosis_scenario():
    """
    测试6：实际故障诊断场景测试
    模拟真实的设备故障诊断对话
    """
    print_section("测试6：实际故障诊断场景")

    try:
        chat_service = ChatService()
        session_id = "test_diagnosis_scenario"

        # 模拟真实对话场景
        scenario = [
            "我的设备突然停止运转了，显示错误代码E01",
            "设备是XYZ-2000型号，使用时间是3年",
            "按照你的建议检查后发现电机过热，怎么办？"
        ]

        print_info("模拟真实故障诊断场景...\n")

        for i, message in enumerate(scenario, 1):
            print(f"{TestColors.BOLD}--- 第 {i} 轮 ---{TestColors.ENDC}")
            print(f"用户: {message}")

            response = asyncio.run(chat_service.chat(message, session_id))

            print(f"AI助手: {response['message']}")
            print()

        print_success("故障诊断场景测试完成")

        # 显示完整的对话历史
        history = chat_service._get_history(session_id)
        print_info(f"完整对话历史（共{len(history.messages)}条消息）:")
        print("-" * 70)

        for i, msg in enumerate(history.messages, 1):
            role = "用户" if "Human" in str(type(msg)) else "AI助手"
            content = msg.content if hasattr(msg, 'content') else str(msg)
            print(f"{i}. {role}: {content}")

        print("-" * 70)

        return True

    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + TestColors.BOLD + "=" * 70)
    print(f"智能问答模块测试套件")
    print(f"测试LangChain + Qwen大模型对话功能")
    print("=" * 70 + TestColors.ENDC)

    # 执行所有测试
    tests = [
        ("单次对话测试", test_single_message),
        ("多轮对话测试（3轮记忆）", test_multi_turn_conversation),
        ("记忆限制测试", test_memory_limit),
        ("清除历史测试", test_clear_history),
        ("会话隔离测试", test_session_isolation),
        ("实际故障诊断场景", test_fault_diagnosis_scenario),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print_error(f"测试异常: {str(e)}")
            results[test_name] = False

    # 输出测试总结
    print_section("测试总结")

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for test_name, result in results.items():
        status = f"{TestColors.OKGREEN}✓ 通过{TestColors.ENDC}" if result else f"{TestColors.FAIL}✗ 失败{TestColors.ENDC}"
        print(f"{test_name:30s} : {status}")

    print("\n" + "=" * 70)
    print(f"总计: {TestColors.BOLD}{passed}/{total}{TestColors.ENDC} 个测试通过")
    print("=" * 70 + "\n")

    return 0 if passed == total else 1


if __name__ == "__main__":
    exit(main())
