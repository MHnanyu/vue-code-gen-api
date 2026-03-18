import logging
import os
import json
import time
import uuid
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional

from app.database import get_database
from app.schemas.response import Response, ErrorCode
from app.schemas.generate import (
    GenerateInitialRequest, GenerateIterateRequest, 
    GenerateResponseData, GenerateInitialResponseData,
    GeneratedFile, StageResult, Attachment, UploadResponseData,
    ImageAnalyzeRequest, ImageAnalyzeResponseData
)
from app.services.ai_factory import AIServiceFactory
from app.services.requirement_service import RequirementService
from app.services.openclaw_service import OpenclawService
from app.services.glm4v_service import GLM4VService
from app.config import settings
from app.mock.generate_mock import (
    MOCK_ITERATE_FILES, MOCK_ITERATE_MESSAGE,
    MOCK_INITIAL_FILES, MOCK_INITIAL_MESSAGE, MOCK_STAGES
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["generate"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
MARKDOWN_EXTENSIONS = {".md", ".markdown"}
TEXT_EXTENSIONS = {".txt"}


def get_file_type(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext in IMAGE_EXTENSIONS:
        return "image"
    elif ext in MARKDOWN_EXTENSIONS:
        return "markdown"
    elif ext in TEXT_EXTENSIONS:
        return "text"
    return "text"


@router.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    logger.info(f"收到文件上传请求 - 文件数: {len(files)}")
    
    if len(files) > 5:
        raise HTTPException(
            status_code=400,
            detail={"code": ErrorCode.PARAM_ERROR, "message": "最多支持上传5个文件", "data": None}
        )
    
    uploaded_files = []
    
    for file in files:
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
        saved_filename = f"{file_id}{ext}"
        file_path = os.path.join(UPLOAD_DIR, saved_filename)
        
        content = await file.read()
        file_size = len(content)
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        file_type = get_file_type(file.filename or "")
        
        attachment = Attachment(
            id=file_id,
            url=f"/uploads/{saved_filename}",
            name=file.filename or "unknown",
            type=file_type,
            size=file_size
        )
        uploaded_files.append(attachment)
        logger.info(f"文件上传成功 - id: {file_id}, name: {file.filename}, type: {file_type}, size: {file_size}")
    
    return Response(data=UploadResponseData(files=uploaded_files))


def save_stage_output(
    stage_name: str,
    step_number: int,
    content,
    session_id: str | None = None,
    file_extension: str = "md"
) -> str | None:
    output_dir = "output"
    if session_id:
        output_dir = os.path.join(output_dir, session_id)
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if session_id:
        filename = f"step{step_number}_{stage_name}.{file_extension}"
    else:
        filename = f"step{step_number}_{stage_name}_{timestamp}.{file_extension}"
    
    filepath = os.path.join(output_dir, filename)
    
    try:
        if file_extension == "json":
            with open(filepath, "w", encoding="utf-8") as f:
                if isinstance(content, (dict, list)):
                    json.dump(content, f, ensure_ascii=False, indent=2)
                else:
                    f.write(str(content))
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(str(content))
        
        logger.info(f"已保存阶段{step_number}输出到: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"保存阶段{step_number}输出失败: {str(e)}")
        return None


def save_vue_files_from_json(
    files_data: list[dict],
    session_id: str,
    step_number: int,
    stage_name: str
) -> list[str]:
    if not files_data:
        return []
    
    output_dir = os.path.join("output", session_id, f"step{step_number}_{stage_name}_vue")
    os.makedirs(output_dir, exist_ok=True)
    
    saved_files = []
    used_names = set()
    
    for idx, file_data in enumerate(files_data):
        file_name = file_data.get("name", f"file{idx}.vue")
        
        base_name = file_name
        if base_name in used_names:
            name_without_ext = os.path.splitext(file_name)[0]
            ext = os.path.splitext(file_name)[1]
            counter = 1
            while f"{name_without_ext}_{counter}{ext}" in used_names:
                counter += 1
            file_name = f"{name_without_ext}_{counter}{ext}"
        
        used_names.add(file_name)
        
        file_path = os.path.join(output_dir, file_name)
        
        content = file_data.get("content", "")
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            saved_files.append(file_path)
            logger.info(f"已保存Vue文件: {file_path}")
        except Exception as e:
            logger.error(f"保存Vue文件失败 {file_name}: {str(e)}")
    
    return saved_files


def convert_api_files_to_generated(api_files: list[dict]) -> list[GeneratedFile]:
    """将API返回的文件列表转换为GeneratedFile对象"""
    return [
        GeneratedFile(
            id=file.get("id", f"file-{i}"),
            name=file.get("name", f"file{i}.vue"),
            path=file.get("path", f"/src/{file.get('name', f'file{i}.vue')}"),
            type=file.get("type", "file"),
            language=file.get("language", "vue"),
            content=file.get("content", ""),
            children=file.get("children")
        )
        for i, file in enumerate(api_files)
    ]


async def update_session_files_only(
    db,
    session_id: str | None,
    files: list[GeneratedFile]
):
    if session_id is None or db is None:
        return
    
    now = datetime.utcnow()
    
    update_result = await db.sessions.update_one(
        {"id": session_id},
        {
            "$set": {
                "updatedAt": now,
                "files": [f.model_dump() for f in files]
            }
        }
    )
    
    if update_result.matched_count == 0:
        logger.error(f"会话不存在 - sessionId: {session_id}")
        raise HTTPException(
            status_code=404,
            detail={"code": ErrorCode.SESSION_NOT_FOUND, "message": "会话不存在", "data": None}
        )
    
    logger.info(f"会话文件更新成功 - sessionId: {session_id}")


@router.post("/generate/iterate")
async def generate_iterate(body: GenerateIterateRequest):
    logger.info(f"收到迭代生成请求 - sessionId: {body.sessionId}, prompt长度: {len(body.prompt)}, 文件数: {len(body.files)}")
    
    db = get_database() if body.sessionId else None
    
    # if settings.MOCK_MODE:
    #     logger.info("Mock 模式已开启，返回 mock 数据")
    #     files = MOCK_ITERATE_FILES
    #     ai_message = MOCK_ITERATE_MESSAGE
    #     await update_session_files_only(db, body.sessionId, files)
    #     return Response(data=GenerateResponseData(files=files, message=ai_message))
    
    output_session_id = body.sessionId if body.sessionId else f"no_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if body.sessionId is not None:
        if db is None:
            logger.error("数据库未连接")
            raise HTTPException(
                status_code=500,
                detail={"code": ErrorCode.INTERNAL_ERROR, "message": "数据库未连接", "data": None}
            )
    
    try:
        ai_service = AIServiceFactory.get_service()
        
        existing_files = [f.model_dump() for f in body.files]
        
        logger.info("开始调用AI服务生成代码")
        result = await ai_service.generate_vue_files(
            prompt=body.prompt,
            existing_files=existing_files
        )
        logger.info("AI服务调用完成")
        
        api_files = result.get("files", [])
        ai_message = result.get("message", "代码生成完成")
        
        files = convert_api_files_to_generated(api_files)
        
        if not files:
            ai_message = "未能生成有效的代码文件，请尝试更详细的需求描述"
            logger.warning(f"AI未生成有效文件 - prompt: {body.prompt[:100]}..., result: {result}")
        else:
            logger.info(f"成功生成 {len(files)} 个文件 - message: {ai_message}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        iterate_result_data = {
            "prompt": body.prompt,
            "files": [f.model_dump() for f in files],
            "message": ai_message
        }
        
        save_stage_output(
            stage_name=f"iterate_{timestamp}",
            step_number=0,
            content=iterate_result_data,
            session_id=output_session_id,
            file_extension="json"
        )
        
        if api_files:
            save_vue_files_from_json(
                files_data=api_files,
                session_id=output_session_id,
                step_number=0,
                stage_name=f"iterate_{timestamp}"
            )
        
    except ValueError as e:
        logger.error(f"AI服务配置错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"code": ErrorCode.INTERNAL_ERROR, "message": f"AI服务配置错误: {str(e)}", "data": None}
        )
    except Exception as e:
        import traceback
        logger.error(f"AI生成失败: {str(e)}\n{traceback.format_exc()}")
        ai_message = f"AI生成失败: {str(e)}"
        
        files = body.files
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        iterate_result_data = {
            "prompt": body.prompt,
            "files": [f.model_dump() for f in files],
            "message": ai_message,
            "error": str(e)
        }
        
        save_stage_output(
            stage_name=f"iterate_{timestamp}",
            step_number=0,
            content=iterate_result_data,
            session_id=output_session_id,
            file_extension="json"
        )
        
        if files:
            save_vue_files_from_json(
                files_data=[f.model_dump() for f in files],
                session_id=output_session_id,
                step_number=0,
                stage_name=f"iterate_{timestamp}"
            )
    
    await update_session_files_only(db, body.sessionId, files)
    
    return Response(data=GenerateResponseData(files=files, message=ai_message))


@router.post("/generate/initial")
async def generate_initial(body: GenerateInitialRequest):
    logger.info(f"收到初始生成请求 - sessionId: {body.sessionId}, prompt长度: {len(body.prompt)}, debug: {body.debug}")
    logger.info(f"附件数量: {len(body.attachments) if body.attachments else 0}")
    
    db = get_database() if body.sessionId else None
    
    # if settings.MOCK_MODE:
    #     logger.info("Mock 模式已开启，返回 mock 数据")
    #     files = MOCK_INITIAL_FILES
    #     ai_message = MOCK_INITIAL_MESSAGE
    #     await update_session_files_only(db, body.sessionId, files)
    #     return Response(data=GenerateInitialResponseData(
    #         files=files,
    #         message=ai_message,
    #         stages=MOCK_STAGES if body.debug else None
    #     ))
    
    output_session_id = body.sessionId if body.sessionId else f"no_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if body.sessionId is not None:
        if db is None:
            logger.error("数据库未连接")
            raise HTTPException(
                status_code=500,
                detail={"code": ErrorCode.INTERNAL_ERROR, "message": "数据库未连接", "data": None}
            )
    
    stages = {}
    files = []
    ai_message = "生成完成"
    
    try:
        final_prompt = body.prompt
        
        image_attachments = []
        if body.attachments:
            image_attachments = [a for a in body.attachments if a.type == "image"]
        
        if image_attachments:
            logger.info(f"检测到 {len(image_attachments)} 个图片附件，开始分析图片...")
            
            glm4v_service = GLM4VService()
            image_descriptions = []
            
            for idx, attachment in enumerate(image_attachments):
                logger.info(f"分析图片 {idx + 1}/{len(image_attachments)}: {attachment.name}")
                
                image_url = attachment.url
                is_base64 = False
                
                if image_url.startswith("/uploads/"):
                    local_path = image_url[1:]
                    if os.path.exists(local_path):
                        with open(local_path, "rb") as f:
                            image_url = GLM4VService.bytes_to_base64(f.read())
                            is_base64 = True
                        logger.info(f"图片已转换为Base64: {attachment.name}")
                
                try:
                    image_result = await glm4v_service.describe_for_vue_generation(
                        image_source=image_url,
                        is_base64=is_base64
                    )
                    
                    if image_result.get("success"):
                        desc = image_result["raw_description"]
                        image_descriptions.append(desc)
                        logger.info(f"图片 {attachment.name} 分析完成，描述长度: {len(desc)}")
                    else:
                        logger.warning(f"图片 {attachment.name} 分析失败")
                except Exception as img_err:
                    logger.error(f"图片 {attachment.name} 分析异常: {str(img_err)}")
            
            if image_descriptions:
                combined_image_desc = "\n\n".join([
                    f"=== 图片 {i+1} 分析结果 ===\n{desc}"
                    for i, desc in enumerate(image_descriptions)
                ])
                
                if body.prompt:
                    final_prompt = f"""用户需求：
{body.prompt}

图片分析结果：
{combined_image_desc}"""
                else:
                    final_prompt = f"""图片分析结果：
{combined_image_desc}"""
                
                logger.info(f"已将图片分析结果与用户需求拼接，最终prompt长度: {len(final_prompt)}")
                logger.info(f"最终prompt前500字符:\n{final_prompt[:500]}...")
                
                save_stage_output(
                    stage_name="image_analysis",
                    step_number=0,
                    content=final_prompt,
                    session_id=output_session_id,
                    file_extension="md"
                )
                logger.info("图片分析结果已保存到 output/ 目录")

        requirement_service = RequirementService()
        
        logger.info("阶段1: 需求标准化开始")
        stage1_result = await requirement_service.standardize_requirement(
            user_requirement=final_prompt,
            temperature=0.2
        )

        stages["requirement"] = StageResult(
            status=stage1_result["status"],
            duration=stage1_result.get("duration"),
            output=stage1_result.get("output") if body.debug else None,
            error=stage1_result.get("error")
        )

        if stage1_result.get("output"):
            save_stage_output(
                stage_name="requirement",
                step_number=1,
                content=stage1_result["output"],
                session_id=output_session_id,
                file_extension="md"
            )

        if stage1_result["status"] == "failed":
            logger.error(f"阶段1失败: {stage1_result.get('error')}")
            ai_message = f"需求标准化失败: {stage1_result.get('error')}"

            files = [
                GeneratedFile(
                    id="error-page",
                    name="MainPage.vue",
                    path="/src/MainPage.vue",
                    type="file",
                    language="vue",
                    content=f"""<template>
  <div class="p-6">
    <el-alert
      title="需求标准化失败"
      type="error"
      description="{ai_message}"
      show-icon
    />
    <p class="mt-4 text-gray-600">原始需求：{body.prompt}</p>
  </div>
</template>

<script setup lang="ts">
import {{ ref }} from 'vue'
</script>"""
                )
            ]

            return Response(data=GenerateInitialResponseData(
                files=files,
                message=ai_message,
                stages=stages
            ))
        
        requirement_doc = stage1_result["output"]
        logger.info(f"阶段1完成 - 需求文档长度: {len(requirement_doc)}")
        
        stage2_start = time.time()
        
        if body.componentLib.lower() == "ccui":
            logger.info("阶段2: CcUI组件代码生成（使用 Openclaw API）")
            openclaw_service = OpenclawService()
            
            ccui_prompt = """请调用 vue3-ccui-generator skill，基于以下UX规范文档，生成基于 Vue3 + CcUI 组件库的 MainPage.vue 及其他自定义组件。

输出要求：按照 skill 的要求返回 JSON 格式的结果，且仅输出 JSON 即可。

---
UX规范文档：
""" + requirement_doc
            
            logger.info("调用 Openclaw API")
            logger.info(f"ccui_prompt: {ccui_prompt}")
            result = await openclaw_service.generate_vue_files(
                prompt=ccui_prompt,
                ccui_prompt=""
            )
        else:
            logger.info("阶段2: ElementUI代码生成（使用 GLM5）")
            ai_service = AIServiceFactory.get_service()
            
            logger.info("调用 GLM5 生成 ElementUI 代码")
            result = await ai_service.generate_vue_files(
                prompt=requirement_doc,
                existing_files=None
            )
        
        stage2_duration = time.time() - stage2_start
        
        api_files = result.get("files", [])
        ai_message = result.get("message", f"代码生成完成（{body.componentLib}）")
        
        files = convert_api_files_to_generated(api_files)
        
        stages["generation"] = StageResult(
            status="success",
            duration=round(stage2_duration, 2),
            output=f"生成了 {len(files)} 个文件 ({body.componentLib})" if body.debug else None,
            error=None
        )
        
        save_stage_output(
            stage_name="generation",
            step_number=2,
            content=result,
            session_id=output_session_id,
            file_extension="json"
        )
        
        if api_files:
            save_vue_files_from_json(
                files_data=api_files,
                session_id=output_session_id,
                step_number=2,
                stage_name="generation"
            )
        
        if not files:
            ai_message = "未能生成有效的代码文件，请尝试更详细的需求描述"
            logger.warning(f"生成器未生成有效文件 - prompt: {body.prompt[:100]}...")
        else:
            logger.info(f"成功生成 {len(files)} 个文件 - message: {ai_message}")
        
        if body.componentLib.lower() == "ccui":
            stage3_start = time.time()
            logger.info("阶段3: UX规范优化（使用 Openclaw API）")
            
            openclaw_service = OpenclawService()
            
            optimization_prompt = """请调用 ccui-ux-guardian skill，基于原始的 Vue 组件，生成符合企业 UI/UX 标准的 Vue 组件。

输出要求：按照 skill 的要求返回 JSON 格式的结果，且仅输出 JSON 即可。"""
            
            stage2_files_json = json.dumps([f.model_dump() for f in files], ensure_ascii=False, indent=2)
            
            full_prompt = f"""{optimization_prompt}

待优化的文件：
{stage2_files_json}
"""
            
            logger.info("调用 Openclaw API 进行优化")
            stage3_result = await openclaw_service.generate_vue_files(
                prompt=full_prompt,
                ccui_prompt=""
            )
            
            stage3_api_files = stage3_result.get("files", [])
            stage3_message = stage3_result.get("message", "优化完成")
            
            optimized_files = convert_api_files_to_generated(stage3_api_files)
            
            if optimized_files:
                files = optimized_files
                ai_message = stage3_message
            
            stage3_duration = time.time() - stage3_start
            
            stages["optimization"] = StageResult(
                status="success",
                duration=round(stage3_duration, 2),
                output=f"优化生成了 {len(files)} 个文件" if body.debug else None,
                error=None
            )
            
            save_stage_output(
                stage_name="optimization",
                step_number=3,
                content=stage3_result,
                session_id=output_session_id,
                file_extension="json"
            )
            
            if stage3_api_files:
                save_vue_files_from_json(
                    files_data=stage3_api_files,
                    session_id=output_session_id,
                    step_number=3,
                    stage_name="optimization"
                )
            
    except ValueError as e:
        logger.error(f"AI服务配置错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"code": ErrorCode.INTERNAL_ERROR, "message": f"AI服务配置错误: {str(e)}", "data": None}
        )
    except Exception as e:
        import traceback
        logger.error(f"初始生成失败: {str(e)}\n{traceback.format_exc()}")
        ai_message = f"生成失败: {str(e)}"
        
        escaped_prompt = body.prompt.replace('"', '\\"')
        files = [
            GeneratedFile(
                id="error-page",
                name="MainPage.vue",
                path="/src/MainPage.vue",
                type="file",
                language="vue",
                content=f"""<template>
  <div class="p-6">
    <el-alert
      title="生成失败"
      type="error"
      description="{ai_message}"
      show-icon
    />
    <p class="mt-4 text-gray-600">原始需求：{escaped_prompt}</p>
  </div>
</template>

<script setup lang="ts">
import {{ ref }} from 'vue'
</script>"""
            )
        ]
    
    await update_session_files_only(db, body.sessionId, files)
    
    return Response(data=GenerateInitialResponseData(
        files=files,
        message=ai_message,
        stages=stages if body.debug else None
    ))


@router.post("/image/analyze")
async def analyze_image(body: ImageAnalyzeRequest):
    logger.info("收到图片分析请求")
    
    if not body.imageUrl and not body.imageBase64:
        raise HTTPException(
            status_code=400,
            detail={"code": ErrorCode.PARAM_ERROR, "message": "请提供imageUrl或imageBase64", "data": None}
        )
    
    try:
        glm4v_service = GLM4VService()
        
        image_source = body.imageBase64 if body.imageBase64 else body.imageUrl
        is_base64 = body.imageBase64 is not None
        
        if not image_source:
            raise HTTPException(
                status_code=400,
                detail={"code": ErrorCode.PARAM_ERROR, "message": "图片源无效", "data": None}
            )
        
        if body.prompt:
            result = await glm4v_service.analyze_image(
                image_source=image_source,
                prompt=body.prompt,
                is_base64=is_base64
            )
            return Response(data=ImageAnalyzeResponseData(
                description=result,
                rawDescription=result,
                success=True
            ))
        else:
            result = await glm4v_service.describe_for_vue_generation(
                image_source=image_source,
                is_base64=is_base64
            )
            
            return Response(data=ImageAnalyzeResponseData(
                description=result["raw_description"],
                rawDescription=result["raw_description"],
                success=result["success"]
            ))
    
    except Exception as e:
        import traceback
        logger.error(f"图片分析失败: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={"code": ErrorCode.INTERNAL_ERROR, "message": f"图片分析失败: {str(e)}", "data": None}
        )


@router.post("/image/analyze-file")
async def analyze_image_file(
    file: UploadFile = File(...),
    prompt: Optional[str] = Form(None)
):
    logger.info(f"收到图片文件分析请求 - filename: {file.filename}")
    
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail={"code": ErrorCode.PARAM_ERROR, "message": "请上传图片文件", "data": None}
        )
    
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail={"code": ErrorCode.PARAM_ERROR, "message": f"不支持的文件类型: {ext}", "data": None}
        )
    
    try:
        content = await file.read()
        image_base64 = GLM4VService.bytes_to_base64(content)
        
        glm4v_service = GLM4VService()
        
        if prompt:
            result = await glm4v_service.analyze_image(
                image_source=image_base64,
                prompt=prompt,
                is_base64=True
            )
            return Response(data=ImageAnalyzeResponseData(
                description=result,
                rawDescription=result,
                success=True
            ))
        else:
            result = await glm4v_service.describe_for_vue_generation(
                image_source=image_base64,
                is_base64=True
            )
            
            return Response(data=ImageAnalyzeResponseData(
                description=result["raw_description"],
                rawDescription=result["raw_description"],
                success=result["success"]
            ))
    
    except Exception as e:
        import traceback
        logger.error(f"图片文件分析失败: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={"code": ErrorCode.INTERNAL_ERROR, "message": f"图片文件分析失败: {str(e)}", "data": None}
        )
