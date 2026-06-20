"""
马赛克区域检测模块
基于方差分析和边缘检测识别图像中的马赛克区域
"""
import logging
import cv2
import numpy as np
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class MosaicDetector:
    """马赛克区域检测器"""

    def __init__(self, block_size: int = 10, threshold: float = 15.0):
        """
        初始化检测器

        Args:
            block_size: 马赛克块大小估计值
            threshold: 方差阈值，低于此值认为是马赛克区域
        """
        self.block_size = block_size
        self.threshold = threshold

    def detect(self, image: np.ndarray) -> np.ndarray:
        """
        检测图像中的马赛克区域

        Args:
            image: 输入图像 (BGR格式)

        Returns:
            二值mask，马赛克区域为255，其他区域为0
        """
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        h, w = gray.shape
        mask = np.zeros((h, w), dtype=np.uint8)

        # 方法1: 基于方差的检测
        variance_mask = self._detect_by_variance(gray)

        # 方法2: 基于边缘的检测
        edge_mask = self._detect_by_edges(gray)

        # 组合两种方法的结果
        mask = cv2.bitwise_or(variance_mask, edge_mask)

        # 形态学操作优化mask
        mask = self._refine_mask(mask)

        return mask

    def _detect_by_variance(self, gray: np.ndarray) -> np.ndarray:
        """
        基于方差检测马赛克区域
        马赛克块内像素值方差较低
        """
        h, w = gray.shape
        mask = np.zeros((h, w), dtype=np.uint8)
        bs = self.block_size

        for i in range(0, h - bs, bs):
            for j in range(0, w - bs, bs):
                block = gray[i:i+bs, j:j+bs].astype(np.float32)
                # 计算块内标准差
                std = np.std(block)
                # 低方差区域可能是马赛克
                if std < self.threshold:
                    mask[i:i+bs, j:j+bs] = 255

        return mask

    def _detect_by_edges(self, gray: np.ndarray) -> np.ndarray:
        """
        基于边缘检测马赛克区域
        马赛克边界会产生规律性的强边缘
        """
        # Sobel边缘检测
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        edges = cv2.magnitude(sobelx, sobely)
        edges = np.uint8(np.clip(edges, 0, 255))

        # 二值化
        _, binary = cv2.threshold(edges, 30, 255, cv2.THRESH_BINARY)

        # 膨胀操作连接边缘
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(binary, kernel, iterations=2)

        # 寻找轮廓并分析规律性
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        mask = np.zeros_like(gray)
        for contour in contours:
            # 计算轮廓面积和矩形度
            area = cv2.contourArea(contour)
            if area < 100:  # 忽略小区域
                continue

            # 检查是否是近似矩形（马赛克块通常是矩形）
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
            if len(approx) == 4:  # 四边形
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h
                # 马赛克块通常接近正方形
                if 0.5 < aspect_ratio < 2.0:
                    mask[y:y+h, x:x+w] = 255

        return mask

    def _refine_mask(self, mask: np.ndarray) -> np.ndarray:
        """
        优化mask，去除噪点并平滑边缘
        """
        # 形态学闭操作填充小空洞
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        # 形态学开操作去除小噪点
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

        # 高斯模糊平滑边缘
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

        return mask

    def detect_with_info(self, image: np.ndarray) -> Tuple[np.ndarray, dict]:
        """
        检测马赛克区域并返回详细信息

        Args:
            image: 输入图像

        Returns:
            mask: 二值mask
            info: 检测信息字典
        """
        mask = self.detect(image)

        # 计算马赛克区域占比
        total_pixels = mask.shape[0] * mask.shape[1]
        mosaic_pixels = np.sum(mask > 0)
        mosaic_ratio = mosaic_pixels / total_pixels

        info = {
            "has_mosaic": mosaic_ratio > 0.01,  # 超过1%认为有马赛克
            "mosaic_ratio": float(mosaic_ratio),
            "mosaic_area": int(mosaic_pixels),
            "total_area": total_pixels,
        }

        return mask, info
