from typing import Optional
from uuid import uuid4

from fastapi import APIRouter

from app.database import get_database
from app.schemas.response import Response
from app.schemas.generate import GenerateRequest, GenerateResponseData, GeneratedFile

router = APIRouter(prefix="/api", tags=["generate"])


@router.post("/generate", response_model=Response[GenerateResponseData])
async def generate_code(body: GenerateRequest):
    db = get_database()
    
    demo_files = [
        GeneratedFile(
            id="app-vue",
            name="App.vue",
            path="/src/App.vue",
            type="file",
            language="vue",
            content="""<template>
  <div class="app">
    <h1>{{ title }}</h1>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const title = ref('Generated Page')
</script>

<style scoped>
.app {
  padding: 20px;
}
</style>"""
        ),
        GeneratedFile(
            id="main-ts",
            name="main.ts",
            path="/src/main.ts",
            type="file",
            language="typescript",
            content="""import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')"""
        )
    ]
    
    response_data = GenerateResponseData(
        files=demo_files,
        message=f"已根据您的需求「{body.prompt}」生成了代码（组件库: {body.componentLib}）"
    )
    
    return Response(data=response_data)
