import logging
import os
import json
import time
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.database import get_database
from app.schemas.response import Response, ErrorCode
from app.schemas.generate import (
    GenerateInitialRequest, GenerateIterateRequest, 
    GenerateResponseData, GenerateInitialResponseData,
    GeneratedFile, StageResult
)
from app.services.ai_factory import AIServiceFactory
from app.services.requirement_service import RequirementService
from app.services.openclaw_service import OpenclawService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["generate"])


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


@router.post("/generate/iterate")
async def generate_iterate(body: GenerateIterateRequest):
    logger.info(f"收到迭代生成请求 - sessionId: {body.sessionId}, prompt长度: {len(body.prompt)}, 文件数: {len(body.files)}")
    
    output_session_id = body.sessionId if body.sessionId else f"no_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    db = None
    if body.sessionId is not None:
        db = get_database()
        
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
    
    if body.sessionId is not None and db is not None:
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


@router.post("/generate/initial")
async def generate_initial(body: GenerateInitialRequest):
    logger.info(f"收到初始生成请求 - sessionId: {body.sessionId}, prompt长度: {len(body.prompt)}, debug: {body.debug}")
    
    output_session_id = body.sessionId if body.sessionId else f"no_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    db = None
    if body.sessionId is not None:
        db = get_database()
        
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
        requirement_service = RequirementService()
        
        logger.info("阶段1: 需求标准化开始")
        stage1_result = await requirement_service.standardize_requirement(
            user_requirement=body.prompt,
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
    
    if body.sessionId is not None and db is not None:
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
    
    return Response(data=GenerateInitialResponseData(
        files=files,
        message=ai_message,
        stages=stages if body.debug else None
    ))
