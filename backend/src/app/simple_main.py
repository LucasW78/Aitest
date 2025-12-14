#!/usr/bin/env python3
"""
AI用例生成平台 - 简化版后端服务
支持文件上传、OCR文字识别和AI生成测试用例
"""

import os
import sys
import uuid
import asyncio
import time
import tempfile
import shutil
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import httpx
from loguru import logger

# 配置日志
logger.add("logs/app.log", rotation="1 day", level="INFO")

# 配置
class Settings:
    def __init__(self):
        self.DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-1ec6c3a1c8d3408789f807da84bc6566")
        self.GENERATION_MODEL = os.getenv("GENERATION_MODEL", "qwen-plus-2025-07-28")
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "95"))
        self.ALLOWED_ORIGINS = [
            "http://localhost:9835",
            "http://43.143.37.243:9835",
            "http://127.0.0.1:9835",
            "http://43.143.37.243:9567",
            "http://localhost:9567"
        ]
        self.UPLOAD_DIR = Path("uploads")
        self.UPLOAD_DIR.mkdir(exist_ok=True)
        self.MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

        # 设置通义千问HTTP超时
        os.environ['DASHSCOPE_HTTP_TIMEOUT'] = '300'

settings = Settings()

# 请求和响应模型
class TestCaseGenerationRequest(BaseModel):
    user_input: str = Field("", description="用户需求描述", min_length=0, max_length=5000)
    documentContent: Optional[str] = Field(None, description="文档内容")
    filePath: Optional[str] = Field(None, description="文件路径")
    max_tokens: int = Field(4000, description="生成最大token数", ge=100, le=8000)
    temperature: float = Field(0.7, description="生成温度参数", ge=0.0, le=2.0)

class TestCaseResponse(BaseModel):
    success: bool
    data: Optional[Dict] = None
    message: str = ""
    generation_time: float = 0.0

class FileUploadWithContentResponse(BaseModel):
    success: bool
    filename: str
    filePath: str
    size: int
    content: str
    message: str = ""

# 创建FastAPI应用
app = FastAPI(
    title="AI用例生成平台",
    description="支持文件上传和OCR的测试用例生成平台",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OCR服务
class OCRService:
    def __init__(self):
        self.ocr = None
        self._init_ocr()

    def _init_ocr(self):
        """初始化OCR服务"""
        try:
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(use_angle_cls=True, lang='ch')
            logger.info("PaddleOCR初始化成功")
        except Exception as e:
            logger.error(f"PaddleOCR初始化失败: {e}")
            self.ocr = None

    async def extract_text_from_image(self, image_bytes: bytes) -> str:
        """从图片中提取文字"""
        if not self.ocr:
            return "OCR服务未初始化"

        try:
            import io
            from PIL import Image

            # 转换字节流为PIL Image
            image = Image.open(io.BytesIO(image_bytes))

            # 使用PaddleOCR识别文字
            result = self.ocr.ocr(image_bytes, cls=True)

            # 提取文字内容
            text_lines = []
            if result and result[0]:
                for line in result[0]:
                    if len(line) >= 2:
                        text_lines.append(line[1][0])

            return "\n".join(text_lines) if text_lines else "未识别到文字内容"

        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            return f"OCR识别失败: {str(e)}"

# AI服务
class AIService:
    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        self.model = settings.GENERATION_MODEL
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(300.0),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )

    async def generate_test_case(self, user_input: str, max_tokens: int = 4000, temperature: float = 0.7) -> TestCaseResponse:
        """生成测试用例"""
        start_time = time.time()

        try:
            import dashscope
            from dashscope import Generation

            dashscope.api_key = self.api_key

            # 构建提示词
            system_prompt = """你是一个专业的测试工程师，请根据用户需求生成完整的测试用例。

要求：
1. 生成的测试用例必须包含：正常场景、异常场景、边界条件、性能测试
2. 每个测试用例需要包含具体的测试步骤和预期结果
3. 输出格式必须是JSON格式，符合思维导图结构

JSON格式示例：
{
  "id": "root",
  "label": "测试用例标题",
  "children": [
    {
      "id": "1",
      "label": "正常场景测试",
      "children": [
        {
          "id": "1-1",
          "label": "具体测试用例",
          "data": {
            "testType": "positive",
            "steps": ["步骤1", "步骤2", "步骤3"],
            "expected": "预期结果"
          }
        }
      ]
    }
  ]
}

请严格按照上述格式生成测试用例。"""

            # 调用通义千问API
            response = Generation.call(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                result_format='message'
            )

            if response.status_code == 200:
                content = response.output.choices[0].message.content
                # 尝试解析JSON
                import json
                try:
                    test_case_data = json.loads(content)
                    return TestCaseResponse(
                        success=True,
                        data=test_case_data,
                        message="测试用例生成成功",
                        generation_time=time.time() - start_time
                    )
                except json.JSONDecodeError:
                    # JSON解析失败，返回原始文本
                    return TestCaseResponse(
                        success=False,
                        message=f"AI返回格式错误: {content}",
                        generation_time=time.time() - start_time
                    )
            else:
                return TestCaseResponse(
                    success=False,
                    message=f"AI服务调用失败: {response.message}",
                    generation_time=time.time() - start_time
                )

        except Exception as e:
            logger.error(f"生成测试用例失败: {e}")
            return TestCaseResponse(
                success=False,
                message=f"生成失败: {str(e)}",
                generation_time=time.time() - start_time
            )

# 实例化服务
ocr_service = OCRService()
ai_service = AIService()

# 文件处理工具
async def save_uploaded_file(file_content: bytes, filename: str) -> str:
    """安全地保存上传的文件"""
    try:
        # 使用UUID生成唯一文件名
        file_id = str(uuid.uuid4())
        file_ext = Path(filename).suffix
        safe_filename = f"{file_id}_{file_ext}"
        file_path = settings.UPLOAD_DIR / safe_filename

        with open(file_path, 'wb') as f:
            f.write(file_content)

        logger.info(f"文件保存成功: {file_path}")
        return str(file_path)

    except Exception as e:
        logger.error(f"文件保存失败: {e}")
        raise

async def extract_file_content(filename: str, file_content: bytes) -> str:
    """根据文件类型提取内容"""
    try:
        file_ext = Path(filename).suffix.lower()

        if file_ext in ['.txt', '.md']:
            try:
                return file_content.decode('utf-8')
            except UnicodeDecodeError:
                return file_content.decode('utf-8', errors='ignore')

        elif file_ext == '.pdf':
            try:
                import PyPDF2
                import io

                pdf_stream = io.BytesIO(file_content)
                pdf_reader = PyPDF2.PdfReader(pdf_stream)

                text_content = []
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text = page.extract_text()
                        if text.strip():
                            text_content.append(f"=== 第{page_num + 1}页 ===\n{text}")
                    except Exception as e:
                        text_content.append(f"=== 第{page_num + 1}页 ===\n[提取失败: {str(e)}]")

                return "\n\n".join(text_content) if text_content else "PDF文件内容为空或无法提取"

            except ImportError:
                return "PDF文件解析需要安装PyPDF2库"
            except Exception as e:
                return f"PDF文件解析失败: {str(e)}"

        elif file_ext in ['.docx', '.doc']:
            try:
                if file_ext == '.docx':
                    import docx
                    import io

                    doc_stream = io.BytesIO(file_content)
                    doc = docx.Document(doc_stream)

                    text_content = []
                    for paragraph in doc.paragraphs:
                        if paragraph.text.strip():
                            text_content.append(paragraph.text)

                    return "\n".join(text_content) if text_content else "Word文档内容为空"
                else:
                    return "旧版Word文档(.doc)暂不支持，请转换为.docx格式"

            except ImportError:
                return "Word文档解析需要安装python-docx库"
            except Exception as e:
                return f"Word文档解析失败: {str(e)}"

        elif file_ext in ['.jpg', '.jpeg', '.png']:
            # 使用OCR提取图片文字
            return await ocr_service.extract_text_from_image(file_content)

        else:
            return f"不支持的文件格式: {file_ext}。支持的格式: .txt, .md, .pdf, .docx, .jpg, .jpeg, .png"

    except Exception as e:
        logger.error(f"文件内容提取失败: {e}")
        return f"文件内容提取失败: {str(e)}"

# API端点
@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "running",
        "version": "2.1.0",
        "timestamp": time.time(),
        "ocr_service": "已初始化" if ocr_service.ocr else "未初始化"
    }

@app.post("/api/files/upload-with-content", response_model=FileUploadWithContentResponse)
async def upload_file_with_content(file: UploadFile = File(...)):
    """文件上传并提取内容"""
    try:
        start_time = time.time()

        # 检查文件大小
        if file.size and file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"文件过大，最大支持 {settings.MAX_FILE_SIZE // (1024*1024)}MB"
            )

        # 读取文件内容
        file_content = await file.read()

        # 保存文件
        file_path = await save_uploaded_file(file_content, file.filename)

        # 提取文件内容
        extracted_content = await extract_file_content(file.filename, file_content)

        processing_time = time.time() - start_time

        logger.info(f"文件上传成功: {file.filename}, 大小: {len(file_content)} bytes")

        return FileUploadWithContentResponse(
            success=True,
            filename=file.filename,
            filePath=file_path,
            size=len(file_content),
            content=extracted_content,
            message="文件上传并内容提取成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@app.post("/api/testcases/generate", response_model=TestCaseResponse)
async def generate_test_case(request: TestCaseGenerationRequest):
    """生成测试用例"""
    try:
        # 构建输入内容
        if request.documentContent:
            user_input = f"基于以下文档内容生成测试用例：\n\n文档内容：\n{request.documentContent}\n\n用户需求：\n{request.user_input}"
        else:
            user_input = request.user_input

        if not user_input.strip():
            return TestCaseResponse(
                success=False,
                message="请提供输入内容或上传文档"
            )

        # 调用AI服务生成测试用例
        return await ai_service.generate_test_case(
            user_input=user_input,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )

    except Exception as e:
        logger.error(f"生成测试用例失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成测试用例失败: {str(e)}")

@app.post("/api/files/upload-base64", response_model=FileUploadWithContentResponse)
async def upload_file_base64(
    filename: str = Form(...),
    content: str = Form(...),
    size: int = Form(...)
):
    """通过Base64编码上传文件"""
    try:
        import base64

        # Base64解码
        file_content = base64.b64decode(content)

        # 保存文件
        file_path = await save_uploaded_file(file_content, filename)

        # 提取内容
        extracted_content = await extract_file_content(filename, file_content)

        return FileUploadWithContentResponse(
            success=True,
            filename=filename,
            filePath=file_path,
            size=len(file_content),
            content=extracted_content,
            message="Base64文件上传成功"
        )

    except Exception as e:
        logger.error(f"Base64文件上传失败: {e}")
        raise HTTPException(status_code=500, detail=f"Base64文件上传失败: {str(e)}")

@app.get("/api/files/supported-formats")
async def get_supported_formats():
    """获取支持的文件格式"""
    formats = {
        "text": [".txt", ".md"],
        "document": [".pdf", ".docx"],
        "image": [".jpg", ".jpeg", ".png"],
        "all": [".txt", ".md", ".pdf", ".docx", ".jpg", ".jpeg", ".png"]
    }

    return {
        "success": True,
        "formats": formats,
        "max_size_mb": settings.MAX_FILE_SIZE // (1024*1024),
        "ocr_enabled": ocr_service.ocr is not None,
        "message": "支持的文件格式列表"
    }

# 定期清理临时文件的函数
async def cleanup_old_files():
    """清理超过1天的临时文件"""
    try:
        import time
        current_time = time.time()

        for file_path in settings.UPLOAD_DIR.glob("*"):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > 86400:  # 24小时
                    file_path.unlink()
                    logger.info(f"已清理过期文件: {file_path}")

    except Exception as e:
        logger.error(f"文件清理失败: {e}")

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("AI用例生成平台启动完成")
    logger.info(f"PaddleOCR状态: {'已初始化' if ocr_service.ocr else '未初始化'}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    # 清理资源
    if hasattr(ocr_service, 'ocr') and ocr_service.ocr:
        del ocr_service.ocr
    logger.info("AI用例生成平台已关闭")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "simple_main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        access_log=True
    )