"""
图像修复模块
使用 OpenCV 内置修复算法 + 可选的 LaMa 模型进行图像修复
"""
import logging
import cv2
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)


class Inpainting:
    """图像修复处理器"""

    def __init__(self, method: str = "opencv"):
        """
        初始化修复处理器

        Args:
            method: 修复方法 ('opencv' 或 'lama')
        """
        self.method = method
        self.lama_model = None

    def load_lama_model(self) -> None:
        """加载 LaMa 模型 (可选)"""
        if self.lama_model is not None:
            return

        try:
            # LaMa 需要额外的依赖，这里提供接口但不强制要求
            # 如果需要更好的修复效果，可以安装 lama-cleaner
            logger.info("LaMa 模型需要额外安装: pip install IOPaint")
            logger.info("当前使用 OpenCV 修复算法作为替代")
        except Exception as e:
            logger.warning(f"LaMa 模型加载失败，使用 OpenCV: {e}")

    def inpaint(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        radius: int = 5,
        method: Optional[str] = None
    ) -> np.ndarray:
        """
        修复图像中的指定区域

        Args:
            image: 输入图像 (BGR格式)
            mask: 修复区域mask (255=修复区域, 0=保留区域)
            radius: 修复半径
            method: 修复方法 (覆盖默认设置)

        Returns:
            修复后的图像
        """
        method = method or self.method

        if method == "lama":
            return self._inpaint_lama(image, mask)
        else:
            return self._inpaint_opencv(image, mask, radius)

    def _inpaint_opencv(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        radius: int = 5
    ) -> np.ndarray:
        """
        使用 OpenCV Telea 算法修复图像

        Args:
            image: 输入图像
            mask: 修复mask
            radius: 修复半径

        Returns:
            修复后的图像
        """
        # 确保mask是uint8类型
        if mask.dtype != np.uint8:
            mask = mask.astype(np.uint8)

        # 使用 Telea 方法（通常效果更好且更稳定）
        result = cv2.inpaint(image, mask, radius, cv2.INPAINT_TELEA)

        return result

    def _inpaint_lama(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        使用 LaMa 模型修复图像

        注意：需要安装 IOPaint: pip install IOPaint
        """
        try:
            # 尝试使用 IOPaint/LaMa
            from iopaint.api import LocalClient

            client = LocalClient()
            result = client.inpaint(
                image=image,
                mask=mask,
                model="lama"
            )
            return result
        except ImportError:
            logger.warning("IOPaint 未安装，回退到 OpenCV")
            return self._inpaint_opencv(image, mask)
        except Exception as e:
            logger.warning(f"LaMa 修复失败，回退到 OpenCV: {e}")
            return self._inpaint_opencv(image, mask)

    def inpaint_with_blend(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        radius: int = 5,
        blend_radius: int = 10
    ) -> np.ndarray:
        """
        修复图像并进行边缘融合

        Args:
            image: 输入图像
            mask: 修复mask
            radius: 修复半径
            blend_radius: 融合半径

        Returns:
            融合后的图像
        """
        # 执行修复
        inpainted = self.inpaint(image, mask, radius)

        # 先调整mask尺寸（在添加维度之前）
        if mask.shape[:2] != image.shape[:2]:
            mask = cv2.resize(mask, (image.shape[1], image.shape[0]))

        # 创建融合mask（边缘渐变）
        blend_mask = cv2.GaussianBlur(
            mask.astype(np.float32) / 255.0,
            (blend_radius * 2 + 1, blend_radius * 2 + 1),
            0
        )

        # 融合原图和修复结果
        if len(blend_mask.shape) == 2:
            blend_mask = blend_mask[:, :, np.newaxis]

        # 混合
        result = image.astype(np.float32) * (1 - blend_mask) + \
                 inpainted.astype(np.float32) * blend_mask
        result = np.clip(result, 0, 255).astype(np.uint8)

        return result

    def get_method_info(self) -> dict:
        """获取方法信息"""
        return {
            "method": self.method,
            "available_methods": ["opencv", "lama"],
            "lama_installed": self._check_lama_installed(),
        }

    def _check_lama_installed(self) -> bool:
        """检查 LaMa 是否已安装"""
        try:
            import iopaint
            return True
        except ImportError:
            return False
