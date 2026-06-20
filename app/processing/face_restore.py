"""
GFPGAN 人脸恢复模块
专门用于修复图像中的人脸区域
"""
import logging
import os
import cv2
import numpy as np
import torch
from pathlib import Path
from typing import Optional, Tuple

from ..config import WEIGHTS_DIR, WEIGHTS, MODEL_URLS

logger = logging.getLogger(__name__)


class FaceRestore:
    """GFPGAN 人脸恢复处理器"""

    def __init__(self, device: Optional[str] = None):
        """
        初始化人脸恢复处理器

        Args:
            device: 计算设备 ('cuda' 或 'cpu')
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.face_enhancer = None
        self.upsampler = None

    def load_model(self, bg_upsampler=None) -> None:
        """
        加载 GFPGAN 模型

        Args:
            bg_upsampler: 背景上采样器 (Real-ESRGAN)
        """
        if self.face_enhancer is not None:
            return

        try:
            from gfpgan import GFPGANer

            # 模型权重路径
            model_path = WEIGHTS_DIR / WEIGHTS["gfpgan"]

            # 如果模型不存在，提示下载
            if not model_path.exists():
                self._download_model(model_path)

            # 初始化人脸增强器
            # 设置 model_rootpath 到 weights 目录
            self.face_enhancer = GFPGANer(
                model_path=str(model_path),
                upscale=4,
                arch="clean",
                channel_multiplier=2,
                bg_upsampler=bg_upsampler,
                model_rootpath=str(WEIGHTS_DIR)
            )
            self.upsampler = bg_upsampler
            logger.info("GFPGAN 模型加载成功")

        except Exception as e:
            logger.warning(f"GFPGAN 模型加载失败: {e}")
            logger.info("人脸增强功能将不可用")
            self.face_enhancer = None

    def _download_model(self, model_path: Path) -> None:
        """下载模型权重"""
        import urllib.request

        url = MODEL_URLS["gfpgan"]
        logger.info("正在下载 GFPGAN 模型...")
        logger.info(f"下载地址: {url}")

        try:
            urllib.request.urlretrieve(url, str(model_path))
            logger.info(f"模型下载完成: {model_path}")
        except Exception as e:
            logger.error(f"模型下载失败: {e}")
            raise

    def enhance(
        self,
        image: np.ndarray,
        has_aligned: bool = False,
        only_center_face: bool = False,
        paste_back: bool = True
    ) -> Tuple[np.ndarray, Optional[list], Optional[list]]:
        """
        增强图像中的人脸

        Args:
            image: 输入图像 (BGR格式)
            has_aligned: 是否是已对齐的人脸图
            only_center_face: 是否只处理中心人脸
            paste_back: 是否将增强后的人脸贴回原图

        Returns:
            cropped_faces: 裁剪的人脸列表
            restored_faces: 恢复的人脸列表
            restored_img: 完整的恢复后图像
        """
        if self.face_enhancer is None:
            try:
                self.load_model()
            except Exception:
                logger.info("跳过人脸增强，返回原图")
                return [], [], image

        # 如果模型加载失败，直接返回原图
        if self.face_enhancer is None:
            return [], [], image

        # 确保图像是uint8格式
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)

        try:
            cropped_faces, restored_faces, restored_img = self.face_enhancer.enhance(
                image,
                has_aligned=has_aligned,
                only_center_face=only_center_face,
                paste_back=paste_back
            )
            return cropped_faces, restored_faces, restored_img
        except Exception as e:
            logger.warning(f"人脸增强失败: {e}")
            # 返回原图
            return [], [], image

    def enhance_file(
        self,
        input_path: str,
        output_path: str
    ) -> str:
        """
        增强图像文件中的人脸

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径

        Returns:
            输出文件路径
        """
        # 读取图像
        image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            raise ValueError(f"无法读取图像: {input_path}")

        # 执行人脸增强
        _, _, restored_img = self.enhance(image, paste_back=True)

        # 保存结果
        cv2.imwrite(output_path, restored_img)
        return output_path

    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            "model_name": "GFPGAN",
            "device": self.device,
            "loaded": self.face_enhancer is not None,
        }
