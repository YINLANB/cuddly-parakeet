"""
处理流水线测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
import cv2
from app.processing.pipeline import ProcessingPipeline, ProcessingOptions, ProcessingResult


class TestProcessingPipeline:
    """处理流水线测试"""

    def setup_method(self):
        """测试前设置"""
        self.pipeline = ProcessingPipeline(device="cpu")

    def test_init(self):
        """测试初始化"""
        assert self.pipeline.device == "cpu"
        assert self.pipeline.detector is not None
        assert self.pipeline.super_resolution is not None
        assert self.pipeline.inpainting is not None

    def test_process_full_mode(self):
        """测试全图处理模式"""
        # 创建测试图像
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        options = ProcessingOptions(mode="full", scale=2, face_enhance=False)

        result = self.pipeline.process(image, options)

        assert result.success is True
        assert result.image is not None
        # 检查输出尺寸
        assert result.image.shape[0] == 200  # 100 * 2
        assert result.image.shape[1] == 200

    def test_process_partial_mode(self):
        """测试局部处理模式"""
        # 创建测试图像
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        options = ProcessingOptions(mode="partial", scale=2, face_enhance=False)

        result = self.pipeline.process(image, options)

        assert result.success is True
        assert result.image is not None
        assert result.mask is not None
        assert result.detection_info is not None

    def test_processing_options_default(self):
        """测试默认处理选项"""
        options = ProcessingOptions()
        assert options.mode == "full"
        assert options.scale == 4
        assert options.face_enhance is True
        assert options.enhance_result is True

    def test_processing_result(self):
        """测试处理结果"""
        result = ProcessingResult(success=True)
        assert result.success is True
        assert result.image is None
        assert result.error is None

    def test_processing_result_with_error(self):
        """测试带错误的处理结果"""
        result = ProcessingResult(success=False, error="Test error")
        assert result.success is False
        assert result.error == "Test error"


class TestInpainting:
    """图像修复测试"""

    def setup_method(self):
        """测试前设置"""
        from app.processing.inpainting import Inpainting
        self.inpainting = Inpainting()

    def test_inpaint_opencv(self):
        """测试OpenCV修复"""
        # 创建测试图像和mask
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[30:70, 30:70] = 255  # 修复区域

        result = self.inpainting.inpaint(image, mask, method="opencv")

        assert result.shape == image.shape
        assert result.dtype == np.uint8

    def test_inpaint_with_blend(self):
        """测试带融合的修复"""
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[30:70, 30:70] = 255

        result = self.inpainting.inpaint_with_blend(image, mask)

        assert result.shape == image.shape

    def test_get_method_info(self):
        """测试获取方法信息"""
        info = self.inpainting.get_method_info()
        assert "method" in info
        assert "available_methods" in info
        assert "opencv" in info["available_methods"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
