CCUI_GENERATION_PROMPT = """请调用 vue3-ccui-generator skill，基于以下UX规范文档，生成基于 Vue3 + CcUI 组件库的原型页面。

【原型极简原则】
- 这是一次性原型图，不是生产代码
- 尽量只生成 MainPage.vue 一个文件
- script 部分使用硬编码 mock 数据，不需要 API 调用、表单验证等逻辑
- 不要定义 interface/type，不需要复杂 TypeScript
- 每个文件不超过 300 行
- 重点在于组件位置、布局结构、基础样式

输出要求：按照 skill 的要求返回 JSON 格式的结果，且仅输出 JSON 即可。

---
UX规范文档：
"""

CCUI_OPTIMIZATION_PROMPT = """请调用 ccui-ux-guardian skill，基于原始的 Vue 组件，生成符合企业 UI/UX 标准的 Vue 组件。

【注意】
- 保持原型极简原则，优化仅限样式和布局层面
- 不要增加复杂逻辑、API 调用、表单验证等

输出要求：按照 skill 的要求返回 JSON 格式的结果，且仅输出 JSON 即可。"""

ELEMENTUI_OPTIMIZATION_PROMPT = """请调用 enterprise-vue-refiner skill，基于原始的 Vue 组件，生成符合企业 UI/UX 标准的 Vue 组件。

【注意】
- 保持原型极简原则，优化仅限样式和布局层面
- 不要增加复杂逻辑、API 调用、表单验证等

输出要求：按照 skill 的要求返回 JSON 格式的结果，且仅输出 JSON 即可。"""


def get_generation_prompt(component_lib: str, requirement_doc: str) -> str:
    if component_lib.lower() == "ccui":
        return CCUI_GENERATION_PROMPT + requirement_doc
    return requirement_doc


def get_optimization_prompt(component_lib: str) -> str:
    if component_lib.lower() == "ccui":
        return CCUI_OPTIMIZATION_PROMPT
    return ELEMENTUI_OPTIMIZATION_PROMPT
