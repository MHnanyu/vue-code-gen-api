import logging
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.database import get_database
from app.schemas.response import Response, ErrorCode
from app.schemas.generate import GenerateRequest, GenerateResponseData, GeneratedFile
from app.services.ai_factory import AIServiceFactory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["generate"])


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


@router.post("/generate")
async def generate_code(body: GenerateRequest):
    logger.info(f"收到生成请求 - sessionId: {body.sessionId}, prompt长度: {len(body.prompt)}, 文件数: {len(body.files) if body.files else 0}")
    
    db = get_database()
    
    if db is None:
        logger.error("数据库未连接")
        raise HTTPException(
            status_code=500,
            detail={"code": ErrorCode.INTERNAL_ERROR, "message": "数据库未连接", "data": None}
        )
    
    try:
        ai_service = AIServiceFactory.get_service()
        
        existing_files = None
        if body.files and len(body.files) > 0:
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
        
        if body.files and len(body.files) > 0:
            files = body.files
        else:
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
    
    if body.sessionId:
        now = datetime.utcnow()
        
        user_msg = {
            "id": str(uuid4()),
            "role": "user",
            "content": body.prompt,
            "timestamp": now
        }
        
        assistant_msg = {
            "id": str(uuid4()),
            "role": "assistant",
            "content": ai_message,
            "timestamp": now
        }
        
        update_data = {
            "$push": {
                "messages": {"$each": [user_msg, assistant_msg]}
            },
            "$set": {
                "updatedAt": now,
                "files": [f.model_dump() for f in files]
            }
        }
        
        update_result = await db.sessions.update_one(
            {"id": body.sessionId},
            update_data
        )
        
        if update_result.matched_count == 0:
            logger.error(f"会话不存在 - sessionId: {body.sessionId}")
            raise HTTPException(
                status_code=404,
                detail={"code": ErrorCode.SESSION_NOT_FOUND, "message": "会话不存在", "data": None}
            )
        
        logger.info(f"会话更新成功 - sessionId: {body.sessionId}")
    
    return Response(data=GenerateResponseData(files=files, message=ai_message))
