# 🖼️ 马赛克去除工具

<div align="center">

基于 AI 的智能图片马赛克去除工具，支持全图和局部马赛克处理。

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103-green.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-1.13+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

</div>

---

## ✨ 功能特点

| 功能 | 说明 |
|------|------|
| 🎯 **智能检测** | 自动识别图片中的马赛克区域 |
| 🚀 **AI增强** | 使用 Real-ESRGAN 进行超分辨率处理 |
| 👤 **人脸优化** | 集成 GFPGAN 专门优化人脸恢复 |
| 🔧 **多种模式** | 支持全图马赛克和局部马赛克处理 |
| 🌐 **Web界面** | 简洁美观的在线使用界面 |
| ⚡ **高性能** | 支持GPU加速，处理速度快 |
| 📋 **格式选择** | 支持 PNG/JPEG/WebP 输出，可调节质量 |
| 📐 **放大查看** | 点击图片可放大查看细节 |
| 📋 **粘贴上传** | 支持 Ctrl+V 直接粘贴截图 |
| 🔒 **安全防护** | 包含路径遍历防护、输入验证等安全措施 |

## 📋 支持的马赛克类型

| 类型 | 说明 | 处理方法 | 效果 |
|------|------|----------|------|
| 全图马赛克 | 整张图片被像素化 | Real-ESRGAN 超分辨率 | ⭐⭐⭐⭐ |
| 局部马赛克 | 图片部分区域马赛克 | 智能检测 + 图像修复 | ⭐⭐⭐ |
| 人脸马赛克 | 人脸区域被模糊 | GFPGAN 人脸恢复 | ⭐⭐⭐⭐ |

## 🛠️ 安装要求

### 最低要求
- Python 3.7+
- 4GB 内存
- 2GB 磁盘空间（含模型）

### 推荐配置
- Python 3.8+
- NVIDIA GPU (CUDA 11.0+)
- 8GB+ 内存
- SSD 硬盘

## 📦 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/mosaic-removal-tool.git
cd mosaic-removal-tool
```

### 2. 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 下载模型权重

```bash
python download_weights.py
```

模型文件会自动下载到 `weights/` 目录：

| 模型 | 大小 | 用途 |
|------|------|------|
| GFPGANv1.4.pth | ~332MB | 人脸恢复 |
| RealESRGAN_x4plus_anime_6B.pth | ~18MB | 动漫/插画增强 |

### 5. 启动应用

```bash
# 方式一：使用启动脚本（推荐）
python run.py

# 方式二：双击启动
双击 "启动工具.bat"

# 方式三：直接运行
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 6. 访问应用

打开浏览器访问: **http://localhost:8000**

---

## 📖 使用说明

### 上传图片

1. **点击上传**：点击上传区域选择文件
2. **拖拽上传**：直接拖拽图片到上传区域
3. **粘贴上传**：截图后按 `Ctrl+V` 粘贴

**支持格式**：JPG, PNG, BMP, WebP  
**文件限制**：最大 50MB，最大尺寸 8192x8192

### 选择处理模式

| 模式 | 适用场景 | 说明 |
|------|----------|------|
| **全图马赛克** | 整张图片被像素化 | 使用AI超分辨率增强 |
| **局部马赛克** | 部分区域有马赛克 | 自动检测并修复 |

### 可选设置

| 选项 | 说明 | 默认值 |
|------|------|--------|
| 人脸增强 | 专门优化人脸区域恢复 | ✅ 开启 |
| 放大倍数 | 图片放大比例 | 4x |
| 输出格式 | PNG(无损)/JPEG/WebP | PNG |
| 图片质量 | JPEG/WebP的质量 (1-100%) | 95% |

### 处理与下载

1. 点击 **"开始处理"** 按钮
2. 等待处理完成（显示处理耗时）
3. **点击查看**：点击结果图片可放大查看细节
4. **下载结果**：点击下载按钮保存处理后的图片

---

## 📊 修复效果说明

### ⚠️ 重要前提

> **AI无法真正"还原"被马赛克破坏的像素信息**，而是基于学习到的自然图像规律**生成视觉上合理的内容**。

### 不同马赛克程度的修复效果

| 马赛克程度 | 修复效果 | 说明 |
|------------|----------|------|
| **轻微马赛克** | ⭐⭐⭐⭐⭐ 优秀 | 像素块较大，AI能很好重建 |
| **中等马赛克** | ⭐⭐⭐⭐ 良好 | 效果明显，细节可能有偏差 |
| **严重马赛克** | ⭐⭐⭐ 一般 | 能改善，但细节会丢失 |
| **极度马赛克** | ⭐⭐ 较差 | 只能生成模糊的近似内容 |

### 影响效果的因素

| 因素 | 影响 |
|------|------|
| **马赛克块大小** | 块越大越难修复 |
| **原图复杂度** | 简单图案比复杂场景好修复 |
| **图片类型** | 动漫/插画效果 > 真实照片 |
| **放大倍数** | 4x 放大通常效果最佳 |
| **人脸区域** | GFPGAN 对人脸有专门优化 |

### 能力边界

**✅ 能做好的：**
- 减少马赛克的视觉干扰
- 生成视觉上合理的替代内容
- 改善整体图像质量
- 人脸区域专门恢复（GFPGAN）

**❌ 不能做到的：**
- 还原真实的原始像素
- 100% 准确恢复细节
- 修复信息完全丢失的区域

### 建议

1. **找一张轻微马赛克的图片测试** - 效果最好
2. **尝试 4x 放大** - 平衡效果和速度
3. **开启人脸增强** - 如果图片包含人脸
4. **对比原图和结果** - 点击图片放大查看细节

---

## 🔧 API 接口

### 上传图片

```http
POST /api/upload
Content-Type: multipart/form-data

参数:
- file: 图片文件

响应:
{
  "success": true,
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "550e8400-e29b-41d4-a716-446655440000.jpg",
  "size": 1234567
}
```

### 处理图片

```http
POST /api/process
Content-Type: multipart/form-data

参数:
- file_id: 文件ID (UUID格式)
- mode: 处理模式 ("full" 或 "partial")
- face_enhance: 人脸增强 (true/false)
- scale: 放大倍数 (1-8)
- output_format: 输出格式 ("png"/"jpeg"/"webp")
- jpeg_quality: 图片质量 (1-100)

响应:
{
  "success": true,
  "output_filename": "550e8400-..._processed.png",
  "original_size": "1920x1080",
  "processed_size": "7680x4320",
  "processing_time_ms": 3500
}
```

### 下载结果

```http
GET /api/download/{filename}

响应: 图片文件
```

### 健康检查

```http
GET /api/health

响应:
{
  "status": "healthy",
  "pipeline_loaded": true,
  "timestamp": "2024-01-01T00:00:00"
}
```

---

## 📁 项目结构

```
mosaic-removal-tool/
├── app/                          # 应用主目录
│   ├── __init__.py
│   ├── __main__.py               # 命令行入口
│   ├── config.py                 # 配置文件
│   ├── main.py                   # FastAPI 主应用
│   ├── processing/               # 图像处理模块
│   │   ├── __init__.py
│   │   ├── detector.py           # 马赛克检测
│   │   ├── super_resolution.py   # Real-ESRGAN 超分辨率
│   │   ├── face_restore.py       # GFPGAN 人脸恢复
│   │   ├── inpainting.py         # 图像修复
│   │   └── pipeline.py           # 处理流水线
│   ├── static/                   # 前端静态文件
│   │   ├── css/style.css
│   │   └── js/app.js
│   └── templates/
│       └── index.html            # 主页面
├── tests/                        # 单元测试
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api.py              # API 测试
│   ├── test_detector.py         # 检测模块测试
│   ├── test_pipeline.py         # 流水线测试
│   └── test_super_resolution.py # 超分辨率测试
├── weights/                      # 模型权重 (需运行下载脚本)
├── uploads/                      # 上传文件 (运行时生成)
├── processed/                    # 处理结果 (运行时生成)
├── .gitignore                    # Git 忽略配置
├── LICENSE                       # MIT 许可证
├── README.md                     # 项目文档
├── requirements.txt              # Python 依赖
├── pyproject.toml                # Python 包配置
├── download_weights.py           # 模型下载脚本
├── run.py                        # 启动脚本
└── 启动工具.bat                   # Windows 启动脚本
```

---

## 🔒 安全特性

| 特性 | 说明 |
|------|------|
| 路径遍历防护 | 验证所有文件路径，防止目录遍历攻击 |
| UUID格式验证 | 文件ID必须是有效的UUID格式 |
| 输入参数验证 | 限制放大倍数(1-8)、图像尺寸、文件大小 |
| 文件名安全检查 | 防止恶意文件名注入 |
| CORS配置 | 支持跨域请求配置 |

---

## 🧪 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_api.py -v
python -m pytest tests/test_detector.py -v

# 生成测试报告
python -m pytest tests/ -v --tb=short
```

---

## ⚠️ 注意事项

### 关于处理效果

> ⚠️ **重要说明**：当前技术无法真正还原被马赛克破坏的像素信息。AI模型是基于学习到的自然图像规律生成视觉上合理的内容，属于"智能修复"而非"真实还原"。

- **人脸恢复**：GFPGAN 对人脸恢复效果较好，但对严重马赛克的恢复有限
- **处理时间**：GPU模式下通常 2-10 秒，CPU模式可能需要 30 秒以上
- **最佳效果**：动漫/插画类图片效果最佳，真实照片也有不错效果

### 法律声明

- 📚 本工具仅供学习研究使用
- ⚖️ 用户需自行承担使用责任
- 🚫 请勿用于任何违法违规用途

---

## 🐛 常见问题

### 安装问题

| 问题 | 解决方案 |
|------|----------|
| `No module named 'torch'` | 安装 PyTorch：`pip install torch torchvision` |
| `No module named 'cv2'` | 安装 OpenCV：`pip install opencv-python` |
| 模型下载失败 | 检查网络连接，或手动下载模型到 `weights/` 目录 |

### 运行问题

| 问题 | 解决方案 |
|------|----------|
| 处理速度很慢 | 使用 GPU 版本 PyTorch，或减小图片尺寸 |
| 内存不足 | 处理较小图片，或关闭人脸增强选项 |
| 健康检查显示 "degraded" | 检查模型文件是否存在于 `weights/` 目录 |
| 端口被占用 | 修改 `run.py` 中的 PORT 配置 |

---

## 📚 技术栈

| 类别 | 技术 |
|------|------|
| **后端框架** | FastAPI + Python |
| **前端技术** | HTML + CSS + JavaScript |
| **AI模型** | Real-ESRGAN + GFPGAN |
| **深度学习** | PyTorch |
| **图像处理** | OpenCV + NumPy |
| **单元测试** | pytest |

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

---

## 🔗 相关资源

| 资源 | 链接 | 说明 |
|------|------|------|
| Real-ESRGAN | [GitHub](https://github.com/xinntao/Real-ESRGAN) | 超分辨率模型 |
| GFPGAN | [GitHub](https://github.com/TencentARC/GFPGAN) | 人脸恢复模型 |
| FastAPI | [官方文档](https://fastapi.tiangolo.com/) | Web框架文档 |
| OpenCV | [官方文档](https://opencv.org/) | 图像处理库 |
| PyTorch | [官网](https://pytorch.org/) | 深度学习框架 |

---

## 🙏 致谢

感谢以下开源项目：

- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) - 实用的图像超分辨率工具
- [GFPGAN](https://github.com/TencentARC/GFPGAN) - 人脸恢复算法
- [FastAPI](https://github.com/tiangolo/fastapi) - 高性能 Web 框架

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！**

</div>
