"""
API接口测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
import cv2
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app


class TestAPI:
    """API接口测试"""

    def setup_method(self):
        """测试前设置"""
        self.client = TestClient(app)
        # 使用项目目录下的临时文件夹
        self.test_dir = Path(__file__).parent.parent / "temp_test"
        self.test_dir.mkdir(exist_ok=True)

    def teardown_method(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_health_check(self):
        """测试健康检查接口"""
        response = self.client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "timestamp" in data
        assert "pipeline_loaded" in data

    def test_get_info(self):
        """测试获取系统信息接口"""
        response = self.client.get("/api/info")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "马赛克去除工具"
        assert data["version"] == "1.0.0"
        assert "supported_formats" in data
        assert "max_file_size_mb" in data

    def test_main_page(self):
        """测试主页面"""
        response = self.client.get("/")
        assert response.status_code == 200
        assert "马赛克" in response.text

    def test_upload_image(self):
        """测试图片上传"""
        # 创建测试图片
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        test_path = self.test_dir / "test.jpg"
        cv2.imwrite(str(test_path), test_img)

        # 上传图片
        with open(test_path, "rb") as f:
            response = self.client.post(
                "/api/upload",
                files={"file": ("test.jpg", f, "image/jpeg")}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "file_id" in data
        assert data["filename"].endswith(".jpg")

    def test_upload_invalid_format(self):
        """测试上传不支持的格式"""
        # 创建一个文本文件
        test_path = self.test_dir / "test.txt"
        test_path.write_text("not an image")

        with open(test_path, "rb") as f:
            response = self.client.post(
                "/api/upload",
                files={"file": ("test.txt", f, "text/plain")}
            )

        assert response.status_code == 400

    def test_process_nonexistent_file(self):
        """测试处理不存在的文件"""
        # 使用有效的UUID格式但文件不存在
        response = self.client.post(
            "/api/process",
            data={
                "file_id": "00000000-0000-0000-0000-000000000000",
                "mode": "full",
                "face_enhance": "false",
                "scale": "2"
            }
        )
        assert response.status_code == 404

    def test_process_invalid_uuid(self):
        """测试处理无效UUID格式的文件"""
        response = self.client.post(
            "/api/process",
            data={
                "file_id": "invalid-uuid",
                "mode": "full",
                "face_enhance": "false",
                "scale": "2"
            }
        )
        assert response.status_code == 400

    def test_download_nonexistent_file(self):
        """测试下载不存在的文件"""
        response = self.client.get("/api/download/nonexistent.png")
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
