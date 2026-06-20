"""
马赛克检测模块测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
import cv2
from app.processing.detector import MosaicDetector


class TestMosaicDetector:
    """马赛克检测器测试"""

    def setup_method(self):
        """测试前设置"""
        self.detector = MosaicDetector(block_size=10, threshold=15.0)

    def test_init(self):
        """测试初始化"""
        assert self.detector.block_size == 10
        assert self.detector.threshold == 15.0

    def test_detect_with_clean_image(self):
        """测试干净图像（无马赛克）"""
        # 创建一个随机噪声图像（无马赛克，高方差）
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

        mask = self.detector.detect(image)
        assert mask.shape == (100, 100)
        # 检测结果应该是有效的mask
        assert set(np.unique(mask)).issubset({0, 255})

    def test_detect_with_mosaic_image(self):
        """测试有马赛克的图像"""
        # 创建一个带有马赛克块的图像
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

        # 添加马赛克块（低方差区域）
        for i in range(0, 100, 10):
            for j in range(0, 100, 10):
                # 每个块使用相同的颜色
                block_color = np.random.randint(0, 255, 3)
                image[i:i+10, j:j+10, :] = block_color

        mask = self.detector.detect(image)
        assert mask.shape == (100, 100)
        # 检测到的mask应该是二值的
        assert set(np.unique(mask)).issubset({0, 255})

    def test_detect_with_grayscale(self):
        """测试灰度图像"""
        # 创建灰度马赛克图像
        gray = np.zeros((100, 100), dtype=np.uint8)
        for i in range(0, 100, 10):
            for j in range(0, 100, 10):
                gray[i:i+10, j:j+10] = np.random.randint(0, 255)

        mask = self.detector.detect(gray)
        assert mask.shape == (100, 100)

    def test_detect_with_info(self):
        """测试带信息的检测"""
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        mask, info = self.detector.detect_with_info(image)

        assert 'has_mosaic' in info
        assert 'mosaic_ratio' in info
        assert 'mosaic_area' in info
        assert 'total_area' in info
        assert info['total_area'] == 100 * 100

    def test_refine_mask(self):
        """测试mask优化"""
        # 创建一个有噪点的mask
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[20:80, 20:80] = 255
        # 添加一些噪点
        mask[10, 10] = 255
        mask[90, 90] = 255

        refined = self.detector._refine_mask(mask)
        # 优化后的mask应该更平滑
        assert refined.shape == mask.shape


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
