---
name: vue3-ccui-generator
description: Vue3 + CcUI 组件库前端代码生成器。根据UX需求文档生成Vue3组件代码。触发条件：(1) 用户要求生成Vue3组件 (2) 用户提及CcUI或cc-开头组件 (3) 用户提交UX需求文档要求生成前端代码 (4) 用户要求生成MainPage.vue或其他Vue组件。技术栈：Vue 3 Composition API + TypeScript + CcUI (cc-开头组件) + Tailwind CSS。
---

# Vue3 + CcUI 组件代码生成器

根据UX需求文档生成Vue3组件代码。

## 技术栈

- **Vue 3** - Composition API (`<script setup lang="ts">`)
- **TypeScript** - 类型安全
- **CcUI** - 组件库（cc-开头的组件）
- **Tailwind CSS** - 样式（class属性）

## 生成规则

1. **只生成必要的Vue组件文件** - MainPage.vue 及其他自定义组件
2. **不生成配置文件** - 不要生成 main.ts, App.vue, index.html 等
3. **优先使用CcUI组件** - 在references目录中查找匹配的cc-组件
4. **兜底策略** - 如果CcUI中没有合适的组件，使用ElementUI的组件平替，注意一定不要自己创造CcUI组件

## 输出格式

返回JSON格式：

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
  ],
  "message": "生成说明"
}
```

**重要：path 字段规则**
- 所有 Vue 文件的 `path` 必须是 `/src/xxx.vue` 格式
- **不要**使用子文件夹路径，如 `/src/components/xxx.vue` 或 `/src/views/xxx.vue`
- 所有组件文件都直接放在 `/src/` 目录下

## 组件选择指南

根据UX需求选择合适的CcUI组件：

### 基础组件
| 需求类型 | CcUI组件 |
|---------|---------|
| 按钮 | cc-button |
| 图标 | cc-icon |
| 链接 | cc-link |
| 布局 | cc-container, cc-layout |
| 分割线 | cc-divider |
| 间距 | cc-space |
| 滚动条 | cc-scrollbar |
| 边框 | cc-border |

### 表单组件
| 需求类型 | CcUI组件 |
|---------|---------|
| 输入框 | cc-input |
| 数字输入 | cc-input-number |
| 标签输入 | cc-input-tag |
| 选择器 | cc-select + cc-option |
| 多选框 | cc-checkbox |
| 单选框 | cc-radio |
| 开关 | cc-switch |
| 日期选择 | cc-date-picker |
| 日期时间选择 | cc-date-time-picker |
| 时间选择 | cc-time-picker |
| 时间选择器 | cc-time-select |
| 上传 | cc-upload |
| 滑块 | cc-slider |
| 评分 | cc-rate |
| 颜色选择 | cc-color-picker |
| 级联选择 | cc-cascader |
| 树选择 | cc-tree-select |
| 自动补全 | cc-autocomplete |
| 提及 | cc-mention |
| 穿梭框 | cc-transfer |
| 表单 | cc-form + cc-form-item |
| 虚拟化选择器 | cc-virtualized-select |

### 数据展示
| 需求类型 | CcUI组件 |
|---------|---------|
| 表格 | cc-table |
| 树形控件 | cc-tree |
| 标签 | cc-tag |
| 标签页 | cc-tabs |
| 分页 | cc-pagination |
| 头像 | cc-avatar |
| 图片 | cc-image |
| 卡片 | cc-card |
| 描述列表 | cc-descriptions |
| 统计数值 | cc-statistic |
| 面包屑 | cc-breadcrumb |
| 页头 | cc-page-header |
| 步骤条 | cc-steps |
| 折叠面板 | cc-collapse |
| 分段控制器 | cc-segmented |
| 省略文本 | cc-ellipsis |
| 结果页 | cc-result |

### 反馈组件
| 需求类型 | CcUI组件 |
|---------|---------|
| 消息提示 | cc-message |
| 消息弹框 | cc-message-box |
| 对话框 | cc-dialog |
| 抽屉 | cc-drawer |
| 气泡确认 | cc-popconfirm |
| 气泡卡片 | cc-popover |
| 文字提示 | cc-tooltip |

### 导航组件
| 需求类型 | CcUI组件 |
|---------|---------|
| 菜单 | cc-menu |
| 下拉菜单 | cc-dropdown |
| 锚点 | cc-anchor |
| 回到顶部 | cc-backtop |
| 固钉 | cc-affix |

### 颜色工具
| 需求类型 | CcUI组件 |
|---------|---------|
| 颜色工具 | cc-color |

## 工作流程

1. **分析UX需求** - 理解页面结构、交互逻辑、数据流
2. **选择组件** - 从references/目录查找合适的CcUI组件
3. **生成代码** - 使用Vue 3 Composition API + TypeScript
4. **样式处理** - 优先Tailwind CSS class，必要时使用scoped style

## 查看组件文档

当需要了解具体组件用法时，读取 references/ 目录下的对应组件文档：

- `references/button.md` - 按钮组件
- `references/input.md` - 输入框组件
- `references/form.md` - 表单组件
- `references/select.md` - 选择器组件
- ... 等等

## 代码示例

### 基础页面结构

```vue
<template>
  <div>
    helloworld
  </div>
</template>

<script setup lang="ts">
</script>
```

### 表单页面示例

```vue
<template>
  <div class="max-w-md mx-auto">
    <cc-form :model="form" :rules="rules" label-width="80px">
      <cc-form-item label="姓名" prop="name">
        <cc-input v-model="form.name" placeholder="请输入姓名" />
      </cc-form-item>
      <cc-form-item label="城市" prop="city">
        <cc-select v-model="form.city" placeholder="请选择城市">
          <cc-option label="北京" value="beijing" />
          <cc-option label="上海" value="shanghai" />
        </cc-select>
      </cc-form-item>
      <cc-form-item>
        <cc-button type="primary" @click="handleSubmit">提交</cc-button>
      </cc-form-item>
    </cc-form>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

interface Form {
  name: string
  city: string
}

const form = reactive<Form>({
  name: '',
  city: ''
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  city: [{ required: true, message: '请选择城市', trigger: 'change' }]
}

const handleSubmit = () => {
  console.log('提交:', form)
}
</script>
```

## 注意事项

1. **响应式数据** - 使用 `ref()` 和 `reactive()` 管理状态
2. **类型定义** - 为props、emits、数据定义TypeScript接口
3. **组件命名** - 使用PascalCase命名组件
4. **样式隔离** - 使用 `scoped` 限制样式作用域
5. **可访问性** - 为交互元素添加合适的aria属性
