"""
超分辨率模块测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
import cv2
from app.processing.super_resolution import SuperResolution


class TestSuperResolution:
    """超分辨率处理器测试"""

    def setup_method(self):
        """测试前设置"""
        self.sr = SuperResolution(model_name="realesr_anime", device="cpu")

    def test_init(self):
        """测试初始化"""
        assert self.sr.model_name == "realesr_anime"
        assert self.sr.device == "cpu"
        assert self.sr.model is None
        assert self.sr.upsampler is None

    def test_load_model(self):
        """测试模型加载"""
        self.sr.load_model()
        assert self.sr.model is not None
        assert self.sr.upsampler is not None

    def test_enhance_small_image(self):
        """测试小图像增强"""
        self.sr.load_model()

        # 创建小测试图像
        image = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)

        # 增强图像
        enhanced, alpha = self.sr.enhance(image, outscale=2)

        # 检查输出尺寸
        assert enhanced.shape[0] == 100  # 50 * 2
        assert enhanced.shape[1] == 100
        assert enhanced.shape[2] == 3

    def test_enhance_returns_uint8(self):
        """测试输出格式"""
        self.sr.load_model()

        image = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
        enhanced, _ = self.sr.enhance(image, outscale=2)

        assert enhanced.dtype == np.uint8

    def test_get_model_info(self):
        """测试获取模型信息"""
        info = self.sr.get_model_info()

        assert 'model_name' in info
        assert 'device' in info
        assert 'loaded' in info
        assert 'scale' in info
        assert info['model_name'] == "realesr_anime"

    def test_enhance_without_model(self):
        """测试未加载模型时的行为"""
        # 不加载模型，直接尝试增强
        image = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)

        # 应该会自动加载模型或报错
        try:
            enhanced, _ = self.sr.enhance(image, outscale=2)
            # 如果成功，检查输出
            assert enhanced.shape[0] == 100
        except Exception as e:
            # 如果失败，应该是模型相关的错误
            assert "model" in str(e).lower() or "load" in str(e).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
