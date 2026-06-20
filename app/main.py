"""
马赛克去除项目 - FastAPI 主应用
提供图像上传、处理和下载功能
"""
import os
import re
import uuid
import asyncio
import logging
import time
import cv2
import numpy as np
from pathlib import Path
from typing import Optional
try:
    from typing import Literal
except ImportError:
    # Python 3.7 compatibility
    from typing_extensions import Literal
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware

from .config import (
    UPLOAD_DIR, PROCESSED_DIR, ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE, MAX_IMAGE_DIMENSION, HOST, PORT
)
from .processing import ProcessingPipeline
from .processing.pipeline import ProcessingOptions

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# UUID 格式验证
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')


def validate_uuid(file_id: str) -> bool:
    """验证文件ID是否为有效的UUID格式"""
    return bool(UUID_PATTERN.match(file_id))


def validate_path_safety(filepath: Path, base_dir: Path) -> bool:
    """验证文件路径是否在安全目录内"""
    try:
        resolved = filepath.resolve()
        base_resolved = base_dir.resolve()
        return str(resolved).startswith(str(base_resolved))
    except Exception:
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("正在初始化处理流水线...")
    try:
        app.state.pipeline = ProcessingPipeline()
        logger.info("处理流水线初始化完成")
    except Exception as e:
        logger.warning(f"处理流水线初始化失败: {e}")
        logger.info("将使用简化模式运行")
        app.state.pipeline = None
    yield
    # 关闭时清理
    logger.info("应用关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="马赛克去除工具",
    description="基于AI的图片马赛克去除工具，支持全图和局部马赛克处理",
    version="1.0.0",
    lifespan=lifespan
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置静态文件和模板
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


@app.get("/")
async def index(request: Request):
    """主页面"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    上传图片

    Args:
        file: 上传的图片文件

    Returns:
        上传结果，包含文件ID和路径
    """
    # 检查文件扩展名
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {file_ext}，支持的格式: {ALLOWED_EXTENSIONS}"
        )

    # 检查文件大小
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大，最大支持 {MAX_FILE_SIZE // (1024 * 1024)}MB"
        )

    # 生成唯一文件名
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{file_ext}"
    filepath = UPLOAD_DIR / filename

    # 使用线程池执行器进行异步文件写入
    def write_file():
        with open(filepath, "wb") as f:
            f.write(content)

    await asyncio.get_event_loop().run_in_executor(None, write_file)

    logger.info(f"文件上传成功: {filename}, 大小: {len(content)} bytes")

    return {
        "success": True,
        "file_id": file_id,
        "filename": filename,
        "filepath": str(filepath),
        "size": len(content),
    }


@app.post("/api/process")
async def process_image(
    file_id: str = Form(...),
    mode: Literal["full", "partial"] = Form("full"),
    face_enhance: bool = Form(True),
    scale: int = Form(default=4, ge=1, le=8),
    output_format: Literal["png", "jpeg", "webp"] = Form("png"),
    jpeg_quality: int = Form(default=95, ge=1, le=100)
):
    """
    处理图片

    Args:
        file_id: 文件ID (必须是有效的UUID格式)
        mode: 处理模式 ('full' 全图 或 'partial' 局部)
        face_enhance: 是否启用人脸增强
        scale: 放大倍数 (1-8)
        output_format: 输出格式 (png, jpeg, webp)
        jpeg_quality: JPEG/WebP 质量 (1-100)

    Returns:
        处理结果
    """
    # 验证 file_id 格式
    if not validate_uuid(file_id):
        raise HTTPException(status_code=400, detail="无效的文件ID格式")

    # 查找上传的文件
    upload_files = list(UPLOAD_DIR.glob(f"{file_id}.*"))
    if not upload_files:
        raise HTTPException(status_code=404, detail="文件不存在")

    input_path = upload_files[0]

    # 验证文件路径安全性
    if not validate_path_safety(input_path, UPLOAD_DIR):
        raise HTTPException(status_code=400, detail="无效的文件路径")

    # 读取图像
    image = cv2.imread(str(input_path), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise HTTPException(status_code=400, detail="无法读取图像文件")

    # 检查图像尺寸
    h, w = image.shape[:2]
    if h > MAX_IMAGE_DIMENSION or w > MAX_IMAGE_DIMENSION:
        raise HTTPException(
            status_code=400,
            detail=f"图像尺寸过大，最大支持 {MAX_IMAGE_DIMENSION}x{MAX_IMAGE_DIMENSION}"
        )

    # 配置处理选项
    options = ProcessingOptions(
        mode=mode,
        scale=scale,
        face_enhance=face_enhance,
        enhance_result=True,
        inpaint_method="opencv"
    )

    # 获取处理流水线
    pipeline = getattr(app.state, 'pipeline', None)

    # 使用线程池执行器进行异步图像处理
    def process():
        if pipeline is None:
            # 简化模式：只做基本的图像处理
            from .processing.pipeline import ProcessingResult
            enhanced = cv2.resize(
                image,
                (w * options.scale, h * options.scale),
                interpolation=cv2.INTER_CUBIC
            )
            return ProcessingResult(
                success=True,
                image=enhanced,
                detection_info={"mode": options.mode, "scale": options.scale, "simplified": True}
            )
        else:
            return pipeline.process(image, options)

    # 记录处理时间
    start_time = time.time()

    try:
        result = await asyncio.get_event_loop().run_in_executor(None, process)
    except Exception as e:
        logger.error(f"处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

    end_time = time.time()
    processing_time_ms = int((end_time - start_time) * 1000)

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    # 保存处理结果
    output_filename = f"{file_id}_processed.{output_format}"
    output_path = PROCESSED_DIR / output_filename

    def save_result():
        # 根据格式设置保存参数
        if output_format == "jpeg":
            params = [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality]
        elif output_format == "webp":
            params = [cv2.IMWRITE_WEBP_QUALITY, jpeg_quality]
        else:  # png
            params = [cv2.IMWRITE_PNG_COMPRESSION, 3]

        cv2.imwrite(str(output_path), result.image, params)

    await asyncio.get_event_loop().run_in_executor(None, save_result)

    logger.info(f"图像处理完成: {output_filename}, 耗时: {processing_time_ms}ms")

    return {
        "success": True,
        "file_id": file_id,
        "output_filename": output_filename,
        "detection_info": result.detection_info,
        "original_size": f"{w}x{h}",
        "processed_size": f"{result.image.shape[1]}x{result.image.shape[0]}",
        "processing_time_ms": processing_time_ms,
    }


@app.get("/api/download/{filename}")
async def download_image(filename: str):
    """
    下载处理后的图片

    Args:
        filename: 文件名

    Returns:
        图片文件
    """
    # 验证文件名安全性（防止路径遍历）
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="无效的文件名")

    # 验证文件名格式（只允许字母、数字、下划线、横线、点）
    if not re.match(r'^[\w\-\.]+$', filename):
        raise HTTPException(status_code=400, detail="无效的文件名格式")

    filepath = PROCESSED_DIR / filename

    # 验证路径安全性
    if not validate_path_safety(filepath, PROCESSED_DIR):
        raise HTTPException(status_code=400, detail="无效的文件路径")

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(
        path=str(filepath),
        media_type="image/png",
        filename=filename
    )


@app.get("/api/preview/{file_id}")
async def preview_images(file_id: str):
    """
    获取原图和处理后的预览

    Args:
        file_id: 文件ID (必须是有效的UUID格式)

    Returns:
        原图和处理后图片的路径
    """
    # 验证 file_id 格式
    if not validate_uuid(file_id):
        raise HTTPException(status_code=400, detail="无效的文件ID格式")

    # 查找原图
    original_files = list(UPLOAD_DIR.glob(f"{file_id}.*"))
    processed_files = list(PROCESSED_DIR.glob(f"{file_id}_processed.*"))

    if not original_files:
        raise HTTPException(status_code=404, detail="原图不存在")

    return {
        "original": f"/api/file/uploads/{original_files[0].name}",
        "processed": f"/api/file/processed/{processed_files[0].name}" if processed_files else None,
    }


@app.get("/api/file/{folder}/{filename}")
async def serve_file(folder: str, filename: str):
    """提供文件访问"""
    # 验证文件夹名称
    if folder not in ["uploads", "processed"]:
        raise HTTPException(status_code=400, detail="无效的文件夹")

    # 验证文件名安全性
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="无效的文件名")

    if folder == "uploads":
        filepath = UPLOAD_DIR / filename
    else:
        filepath = PROCESSED_DIR / filename

    # 验证路径安全性
    base_dir = UPLOAD_DIR if folder == "uploads" else PROCESSED_DIR
    if not validate_path_safety(filepath, base_dir):
        raise HTTPException(status_code=400, detail="无效的文件路径")

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(path=str(filepath))


@app.get("/api/info")
async def get_info():
    """获取系统信息"""
    pipeline = getattr(app.state, 'pipeline', None)
    return {
        "title": "马赛克去除工具",
        "version": "1.0.0",
        "supported_formats": list(ALLOWED_EXTENSIONS),
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
        "max_image_dimension": MAX_IMAGE_DIMENSION,
        "pipeline_info": pipeline.get_info() if pipeline else None,
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    pipeline = getattr(app.state, 'pipeline', None)
    return {
        "status": "healthy" if pipeline else "degraded",
        "pipeline_loaded": pipeline is not None,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
