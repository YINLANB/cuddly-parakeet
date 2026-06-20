"""
pytest 配置文件
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# pytest 配置
def pytest_configure(config):
    """配置pytest"""
    config.addinivalue_line("markers", "slow: 标记慢速测试")
    config.addinivalue_line("markers", "gpu: 标记需要GPU的测试")

def pytest_collection_modifyitems(items):
    """修改测试收集"""
    for item in items:
        # 添加慢速测试标记
        if "slow" in item.nodeid:
            item.add_marker(pytest.mark.slow)
