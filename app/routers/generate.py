import html
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter

from app.database import get_database
from app.schemas.response import Response, ErrorCode
from app.schemas.generate import GenerateRequest, GenerateResponseData, GeneratedFile

router = APIRouter(prefix="/api", tags=["generate"])


def generate_main_page_content(prompt: str) -> str:
    escaped_prompt = html.escape(prompt)
    return f"""<template>
  <div class="max-w-3xl mx-auto p-10">
    <h1 class="text-2xl font-bold text-gray-800 mb-4">{{{{ title }}}}</h1>
    <p class="text-gray-600">基于您的需求生成的内容：</p>
    <blockquote class="bg-gray-100 p-4 border-l-4 border-emerald-500 my-5 text-gray-500">
      {{{{ userPrompt }}}}
    </blockquote>
    <HelloWorld />
  </div>
</template>

<script setup lang="ts">
import {{ ref }} from 'vue'
import HelloWorld from './HelloWorld.vue'

const title = ref('Generated Page')
const userPrompt = ref('{escaped_prompt}')
</script>
"""


HELLO_WORLD_VUE = """<template>
  <div class="p-5 bg-white rounded-lg shadow-md">
    <h2 class="text-xl text-emerald-500 mb-4">Hello World Component</h2>
    <p class="text-gray-700 mb-2">Count: {{ count }}</p>
    <el-button type="primary" @click="count++">Click Me</el-button>
    <el-divider />
    <h3 class="my-4 text-gray-600">Calendar</h3>
    <el-calendar v-model="selectedDate" class="rounded-lg" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const count = ref(0)
const selectedDate = ref(new Date())
</script>
"""


def generate_mock_ai_response(user_message: str, is_update: bool = False) -> str:
    truncated = user_message[:50] if len(user_message) > 50 else user_message
    if is_update:
        responses = [
            f'好的，我已根据您的要求"{truncated}..."更新了代码。',
            f'代码已更新！您的要求"{truncated}..."已应用到项目中。',
            f'修改完成！"{truncated}..."相关的功能已添加。',
        ]
    else:
        responses = [
            f'我理解您的需求："{truncated}..."。我已经为您生成了相应的Vue3项目代码，您可以在右侧的"Code"标签页查看完整的文件结构。',
            f'根据您的要求，我已经生成了项目代码。',
        ]
    import random
    return random.choice(responses)


@router.post("/generate")
async def generate_code(body: GenerateRequest):
    db = get_database()
    
    ai_message = generate_mock_ai_response(
        body.prompt, 
        is_update=bool(body.files and len(body.files) > 0)
    )
    
    if body.files and len(body.files) > 0:
        files = body.files
        main_page = next((f for f in files if f.name == "MainPage.vue"), None)
        if main_page and main_page.content:
            original_content = main_page.content
            if "</blockquote>" in original_content:
                parts = original_content.split("</blockquote>")
                if len(parts) > 1:
                    update_note = f"\n\n    <!-- 更新: {body.prompt} -->\n"
                    parts[0] = parts[0].rstrip() + update_note
                    main_page.content = parts[0] + "\n</blockquote>" + "</blockquote>".join(parts[1:])
    else:
        files = [
            GeneratedFile(
                id="main-page",
                name="MainPage.vue",
                path="/src/MainPage.vue",
                type="file",
                language="vue",
                content=generate_main_page_content(body.prompt)
            ),
            GeneratedFile(
                id="hello-world",
                name="HelloWorld.vue",
                path="/src/HelloWorld.vue",
                type="file",
                language="vue",
                content=HELLO_WORLD_VUE
            ),
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
        
        result = await db.sessions.update_one(
            {"id": body.sessionId},
            update_data
        )
        
        if result.matched_count == 0:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail={"code": ErrorCode.SESSION_NOT_FOUND, "message": "会话不存在", "data": None}
            )
    
    return Response(data=GenerateResponseData(files=files, message=ai_message))
