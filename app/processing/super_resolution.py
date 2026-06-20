"""
Real-ESRGAN 超分辨率模块
用于全图马赛克去除，通过AI超分辨率增强图像质量
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


class SuperResolution:
    """Real-ESRGAN 超分辨率处理"""

    def __init__(self, model_name: str = "realesr_anime", device: Optional[str] = None):
        """
        初始化超分辨率处理器

        Args:
            model_name: 模型名称 ('realesrgan' 或 'realesr_anime')
            device: 计算设备 ('cuda' 或 'cpu')
        """
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.upsampler = None

    def load_model(self) -> None:
        """加载模型"""
        if self.model is not None:
            return

        try:
            from basicsr.archs.rrdbnet_arch import RRDBNet
            from realesrgan import RealESRGANer

            # 选择模型配置
            if self.model_name == "realesr_anime":
                model = RRDBNet(
                    num_in_ch=3,
                    num_out_ch=3,
                    num_feat=64,
                    num_block=6,  # anime模型block数较少
                    num_grow_ch=32,
                    scale=4
                )
            else:
                model = RRDBNet(
                    num_in_ch=3,
                    num_out_ch=3,
                    num_feat=64,
                    num_block=23,
                    num_grow_ch=32,
                    scale=4
                )

            # 模型权重路径
            model_path = WEIGHTS_DIR / WEIGHTS[self.model_name]

            # 如果模型不存在，提示下载
            if not model_path.exists():
                self._download_model(model_path)

            # 初始化upsampler
            self.upsampler = RealESRGANer(
                scale=4,
                model_path=str(model_path),
                model=model,
                half=True if self.device == "cuda" else False,
                device=self.device
            )
            self.model = model
            logger.info(f"Real-ESRGAN 模型加载成功: {self.model_name}")

        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise

    def _download_model(self, model_path: Path) -> None:
        """下载模型权重"""
        import urllib.request

        url = MODEL_URLS.get(self.model_name)
        if not url:
            raise ValueError(f"未知模型: {self.model_name}")

        logger.info(f"正在下载模型: {self.model_name}...")
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
        outscale: int = 4,
        alpha_upsampler: str = "realesrgan"
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        增强图像分辨率

        Args:
            image: 输入图像 (BGR格式)
            outscale: 输出放大倍数
            alpha_upsampler: alpha通道上采样方法

        Returns:
            enhanced: 增强后的图像
            output_alpha: alpha通道(如果有)
        """
        if self.upsampler is None:
            self.load_model()

        # 确保图像是uint8格式
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)

        # 执行超分辨率
        try:
            output, output_alpha = self.upsampler.enhance(
                image,
                outscale=outscale,
                alpha_upsampler=alpha_upsampler
            )
            return output, output_alpha
        except Exception as e:
            logger.warning(f"图像增强失败: {e}")
            # 回退到简单上采样
            h, w = image.shape[:2]
            enhanced = cv2.resize(
                image,
                (w * outscale, h * outscale),
                interpolation=cv2.INTER_CUBIC
            )
            return enhanced, None

    def enhance_file(
        self,
        input_path: str,
        output_path: str,
        outscale: int = 4
    ) -> str:
        """
        增强图像文件

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            outscale: 放大倍数

        Returns:
            输出文件路径
        """
        # 读取图像
        image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            raise ValueError(f"无法读取图像: {input_path}")

        # 执行增强
        enhanced, _ = self.enhance(image, outscale=outscale)

        # 保存结果
        cv2.imwrite(output_path, enhanced)
        return output_path

    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "loaded": self.model is not None,
            "scale": 4,
        }
