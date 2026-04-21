---
name: enterprise-vue-refiner
description: 将 Vue 3 + Element Plus + Tailwind CSS 代码按照企业 UI/UX 规范进行审查和修正。输入原始 Vue 代码 JSON，输出符合规范的 Vue 代码 JSON，一一对应。适用于代码生成管道、批量合规审查、设计评审前清洗。
---

# Enterprise Vue Refiner

将 Vue 3 + Element Plus + Tailwind CSS 代码按照企业 UI/UX 规范进行审查和修正。

## 输入输出契约

### 输入

合法 JSON，结构如下：

```json
{
  "files": [
    {
      "id": "main-page",
      "name": "MainPage.vue",
      "path": "/src/MainPage.vue",
      "type": "file",
      "language": "vue",
      "content": "<template>...</template><script setup lang=\"ts\">...</script><style scoped>...</style>"
    }
  ]
}
```

### 输出

**必须**返回与输入一一对应的 JSON。不允许增减文件、不允许改变 id/name/path/type/language。

```json
{
  "files": [
    {
      "id": "main-page",
      "name": "MainPage.vue",
      "path": "/src/MainPage.vue",
      "type": "file",
      "language": "vue",
      "content": "<template>...修正后...</template><script setup lang=\"ts\">...</script><style scoped>...修正后...</style>"
    }
  ],
  "message": "## 修正说明\n\n### MainPage.vue\n\n| 位置 | 规则 | 修改内容 |\n|------|------|----------|\n| template L12 | FDN-001 | 硬编码颜色 `#333` → `text-gray-900` |\n| template L35 | CMP-003 | 工具栏按钮间距 → `gap-3` |\n\n共修正 **5** 处违规，涉及 3 条规则。"
}
```

- 无需修改的文件：`content` 原样返回
- `message`：Markdown 字符串，列出每个文件的修改点

## 规则数据

规则存储在 `data/` 目录的 CSV 文件中，**CSV 是唯一事实来源**：

| 文件 | 覆盖范围 | 前缀 |
|------|---------|------|
| `foundation-rules.csv` | 颜色、字体、间距、阴影、圆角 | FDN |
| `component-rules.csv` | 表格、工具栏、表单、按钮、下拉等 | CMP |
| `global-layout-rules.csv` | 页面布局、安全边距、详情页、列表页、审批页、新建页 | LAY/DET/LST/CRE/APV |

CSV 每行一条规则，关键字段：
- `rule_id`：规则标识（FDN-001、CMP-035 等）
- `default_value`：规范要求的具体值（如 12px、#F5F6F8、medium）
- `preferred_pattern`：推荐实现方式
- `anti_pattern`：应避免的做法

**按需加载**：根据代码中发现的模式，只加载相关的规则族，不全量读取。直接用 read 工具读取对应 CSV 文件。

## 转换流程

### 1. Parse

解析每个 file 的 content，识别 `<template>`、`<script>`、`<style>` 三个区域。仅处理 template 和 style，**不修改 script 中的业务逻辑**。

### 2. Scan

扫描所有文件，收集以下模式：
- 硬编码颜色（hex/rgb）
- 非标准间距/字体/圆角值
- Element Plus 组件缺失 size/配置
- 表格/工具栏/表单布局违规
- 页面结构违规

先全局扫描，识别跨文件共性模式，再统一修复。

### 3. Load

根据发现的模式，加载相关 CSV 规则。例如：
- 发现硬编码颜色 → 加载 foundation-rules.csv 的 color 相关规则
- 发现表格组件 → 加载 component-rules.csv 的 table 相关规则
- 发现页面布局 → 加载 global-layout-rules.csv 的 layout 相关规则

从 CSV 的 `default_value` 字段获取规范要求的实际值，直接用对应的 Tailwind 类替换。

### 4. Fix

按以下优先级修复：

1. **样式标准化**：将硬编码值替换为标准 Tailwind 类（参照 CSV `default_value`）
2. **组件规范**：补充 Element Plus 组件缺失的 prop（size、clearable 等）
3. **布局规范**：修正间距、对齐、结构
4. **Element Plus 品牌色覆盖**：通过 `:deep()` 选择器覆盖第三方组件默认样式
5. **按钮规范**：间距、排序、样式

### 5. Verify

修复后自检：
- 替换后的值是否与 CSV `default_value` 一致
- 是否引入新的违规
- 业务逻辑、事件绑定、数据流是否完整保留

### 6. Output

组装 JSON 输出。files 与输入一一对应，message 用 Markdown 列出修改点。

## 硬约束

### 不可变

- **不修改** `<script>` 中的业务逻辑、数据流、事件处理、路由、状态管理
- **不修改** 组件的 props 和 emit 接口
- **不引入** 新的 npm 依赖
- **不增减** 文件，不改变 file 的 id/name/path/type/language
- **不改变** 元素的 v-model、@click、:prop 等绑定

### Element Plus 组件使用约束

- **图标**：必须通过 `<el-icon>` slot 使用，严禁通过 `:icon` prop 传入组件引用（会导致 `getBoundingClientRect is not a function`）
  - ✅ `<el-button><el-icon><Refresh /></el-icon></el-button>`
  - ❌ `<el-button :icon="Refresh" />`
- **Prop 合法性**：不得给 Element Plus 组件添加不存在的 prop（如 `el-table` 无 `row-height`），行高/样式应通过 `:deep()` CSS 实现
- **插槽列禁用 tooltip**：使用了自定义 `#default` 插槽的 `el-table-column`，不得加 `show-overflow-tooltip`（会导致冲突的悬浮气泡）
- **禁止嵌套 tooltip**：不在 `el-button` 外层包 `el-tooltip`（tooltip 容器会破坏 flex 布局间距），按钮文字本身已能表达操作含义
- **操作列按钮**：使用 `link` 属性而非 `type="text"`（text 已 deprecated 且 padding 过大），纯 icon 按钮不需要 `gap` 间距

### Element Plus 组件覆盖

需要覆盖 Element Plus 默认样式时，**必须在组件的 `<style scoped>` 中**使用 `:deep()` 选择器：

```css
<style scoped>
:deep(.el-button) {
  margin: 0;
}
:deep(.el-button--primary) {
  --el-button-bg-color: #0067D1;
  --el-button-hover-bg-color: #2E86DE;
}
</style>
```

### 样式设置方式

- ✅ 使用标准 Tailwind 类：`class="gap-3 text-sm bg-gray-50"`
- ❌ 不使用 CSS 变量：`style="gap: var(--ui-space-m);"`
- ❌ 不使用任意值（有标准类时）：`class="gap-[12px]"`（应用 `gap-3`）

## 页面类型规则速查

`global-layout-rules.csv` 包含多种页面类型的规则：

| 页面类型 | 前缀 | 核心规则 |
|---------|------|---------|
| 通用布局 | LAY | 安全边距 32px、页面背景 gray-50、卡片样式、搜索区间距 24px×20px |
| 详情页 | DET | 概览区（标题+基本信息）、Tab/折叠容器、三层嵌套结构、底部操作栏 |
| 列表页 | LST | 筛选区 + 列表区、>30 条用表格、<10 条用卡片 |
| 新建页 | CRE | 弹窗三段式（头/内容/底）、面包屑、步骤/单页模式 |
| 审批页 | APV | 三栏布局、审批时间线、操作按钮语义色 |

根据输入代码的页面特征，自动匹配相关规则族。
