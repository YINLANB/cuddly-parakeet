"""
图像处理流水线
协调各个处理模块，提供统一的处理接口
"""
import logging
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass

from .detector import MosaicDetector
from .super_resolution import SuperResolution
from .face_restore import FaceRestore
from .inpainting import Inpainting

logger = logging.getLogger(__name__)


@dataclass
class ProcessingOptions:
    """处理选项"""
    mode: str = "full"  # "full" 或 "partial"
    scale: int = 4  # 放大倍数
    face_enhance: bool = True  # 是否人脸增强
    enhance_result: bool = True  # 是否增强最终结果
    inpaint_method: str = "opencv"  # 修复方法

    def __post_init__(self):
        """验证参数"""
        if self.mode not in ("full", "partial"):
            raise ValueError(f"无效的处理模式: {self.mode}")
        if self.scale < 1 or self.scale > 8:
            raise ValueError(f"无效的放大倍数: {self.scale}")


@dataclass
class ProcessingResult:
    """处理结果"""
    success: bool
    image: Optional[np.ndarray] = None
    mask: Optional[np.ndarray] = None
    detection_info: Optional[dict] = None
    error: Optional[str] = None


class ProcessingPipeline:
    """图像处理流水线"""

    def __init__(self, device: Optional[str] = None):
        """
        初始化处理流水线

        Args:
            device: 计算设备 ('cuda' 或 'cpu')
        """
        self.device = device
        self.detector = MosaicDetector()
        self.super_resolution = SuperResolution(model_name="realesr_anime", device=device)
        self.face_restore = FaceRestore(device=device)
        self.inpainting = Inpainting()

    def process(
        self,
        image: np.ndarray,
        options: Optional[ProcessingOptions] = None
    ) -> ProcessingResult:
        """
        处理图像

        Args:
            image: 输入图像 (BGR格式)
            options: 处理选项

        Returns:
            ProcessingResult 处理结果
        """
        if options is None:
            options = ProcessingOptions()

        try:
            if options.mode == "full":
                return self._process_full(image, options)
            else:
                return self._process_partial(image, options)
        except Exception as e:
            logger.error(f"处理失败: {e}")
            return ProcessingResult(
                success=False,
                error=f"处理失败: {str(e)}"
            )

    def _process_full(
        self,
        image: np.ndarray,
        options: ProcessingOptions
    ) -> ProcessingResult:
        """
        全图马赛克处理

        Args:
            image: 输入图像
            options: 处理选项

        Returns:
            ProcessingResult
        """
        logger.info("开始全图马赛克处理...")

        # 步骤1: 超分辨率增强
        logger.info("步骤1: 超分辨率增强...")
        enhanced, _ = self.super_resolution.enhance(
            image,
            outscale=options.scale
        )

        # 步骤2: 人脸增强 (可选)
        if options.face_enhance:
            logger.info("步骤2: 人脸增强...")
            _, _, enhanced = self.face_restore.enhance(
                enhanced,
                paste_back=True
            )

        return ProcessingResult(
            success=True,
            image=enhanced,
            detection_info={"mode": "full", "scale": options.scale}
        )

    def _process_partial(
        self,
        image: np.ndarray,
        options: ProcessingOptions
    ) -> ProcessingResult:
        """
        局部马赛克处理

        Args:
            image: 输入图像
            options: 处理选项

        Returns:
            ProcessingResult
        """
        logger.info("开始局部马赛克处理...")

        # 步骤1: 检测马赛克区域
        logger.info("步骤1: 检测马赛克区域...")
        mask, detection_info = self.detector.detect_with_info(image)

        if not detection_info["has_mosaic"]:
            logger.info("未检测到明显马赛克区域")
            # 即使没有检测到，也尝试处理

        # 步骤2: 修复马赛克区域
        logger.info("步骤2: 修复马赛克区域...")
        inpainted = self.inpainting.inpaint_with_blend(
            image,
            mask,
            radius=5,
            blend_radius=15
        )

        # 步骤3: 整体增强 (可选)
        if options.enhance_result:
            logger.info("步骤3: 整体增强...")
            enhanced, _ = self.super_resolution.enhance(
                inpainted,
                outscale=options.scale
            )
        else:
            enhanced = inpainted

        # 步骤4: 人脸增强 (可选)
        if options.face_enhance:
            logger.info("步骤4: 人脸增强...")
            _, _, enhanced = self.face_restore.enhance(
                enhanced,
                paste_back=True
            )

        return ProcessingResult(
            success=True,
            image=enhanced,
            mask=mask,
            detection_info=detection_info
        )

    def process_file(
        self,
        input_path: str,
        output_path: str,
        options: Optional[ProcessingOptions] = None
    ) -> dict:
        """
        处理图像文件

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            options: 处理选项

        Returns:
            处理结果字典
        """
        # 读取图像
        image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            return {
                "success": False,
                "error": f"无法读取图像: {input_path}"
            }

        # 处理图像
        result = self.process(image, options)

        if result.success:
            # 保存结果
            cv2.imwrite(output_path, result.image)
            return {
                "success": True,
                "output_path": output_path,
                "detection_info": result.detection_info,
            }
        else:
            return {
                "success": False,
                "error": result.error,
            }

    def get_info(self) -> dict:
        """获取流水线信息"""
        return {
            "super_resolution": self.super_resolution.get_model_info(),
            "face_restore": self.face_restore.get_model_info(),
            "inpainting": self.inpainting.get_method_info(),
        }
