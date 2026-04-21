# Transfer 穿梭框

双栏穿梭选择框，常用于将数据从一个容器移动到另一个容器。

## 基础用法

使用 `v-model` 绑定选中的值。

```vue
<template>
  <cc-transfer v-model="value" :data="data" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref(['1', '4'])
const data = ref([
  { key: '1', label: '选项1' },
  { key: '2', label: '选项2' },
  { key: '3', label: '选项3' },
  { key: '4', label: '选项4' },
  { key: '5', label: '选项5' }
])
</script>
```

## 可搜索

设置 `filterable` 属性可以开启搜索功能。

```vue
<template>
  <cc-transfer
    v-model="value"
    :data="data"
    filterable
    filter-placeholder="请输入搜索内容"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref([])
const data = ref([
  { key: '1', label: '选项1' },
  { key: '2', label: '选项2' },
  { key: '3', label: '选项3' },
  { key: '4', label: '选项4' },
  { key: '5', label: '选项5' }
])
</script>
```

## 自定义标题

使用 `titles` 属性自定义左右两侧的标题。

```vue
<template>
  <cc-transfer
    v-model="value"
    :data="data"
    :titles="['源列表', '目标列表']"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref([])
const data = ref([
  { key: '1', label: '选项1' },
  { key: '2', label: '选项2' },
  { key: '3', label: '选项3' },
  { key: '4', label: '选项4' },
  { key: '5', label: '选项5' }
])
</script>
```

## 自定义按钮文案

使用 `button-texts` 属性自定义穿梭按钮的文案。

```vue
<template>
  <cc-transfer
    v-model="value"
    :data="data"
    :button-texts="['到左边', '到右边']"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref([])
const data = ref([
  { key: '1', label: '选项1' },
  { key: '2', label: '选项2' },
  { key: '3', label: '选项3' },
  { key: '4', label: '选项4' },
  { key: '5', label: '选项5' }
])
</script>
```

## 禁用状态

设置 `disabled` 属性禁用整个穿梭框。

```vue
<template>
  <cc-transfer v-model="value" :data="data" disabled />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref(['1', '4'])
const data = ref([
  { key: '1', label: '选项1' },
  { key: '2', label: '选项2' },
  { key: '3', label: '选项3' },
  { key: '4', label: '选项4' },
  { key: '5', label: '选项5' }
])
</script>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| model-value / v-model | 绑定值 | array | — | [] |
| data | 数据源 | array | — | [] |
| filterable | 是否可搜索 | boolean | — | false |
| filter-placeholder | 搜索框占位符 | string | — | 请输入搜索内容 |
| filter-method | 自定义搜索方法 | function | — | — |
| target-order | 右侧列表元素的排序方式 | string | original / push / unshift | original |
| titles | 标题数组 | array | — | ['列表 1', '列表 2'] |
| button-texts | 按钮文字数组 | array | — | [] |
| format | 格式化函数 | object | — | {} |
| props | 配置选项 | object | — | { label: 'label', key: 'key', disabled: 'disabled' } |
| left-default-checked | 初始状态下左侧列表的已勾选项的 key 数组 | array | — | [] |
| right-default-checked | 初始状态下右侧列表的已勾选项的 key 数组 | array | — | [] |
| validate-event | 是否触发表单验证 | boolean | — | true |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|---------|
| change | 选中值发生变化时触发 | (value: array, direction: string, movedKeys: array) |
| left-check-change | 左侧列表勾选状态发生变化时触发 | (value: array, movedKeys: array) |
| right-check-change | 右侧列表勾选状态发生变化时触发 | (value: array, movedKeys: array) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 自定义列表项内容 |
| left-footer | 左侧列表底部区域 |
| right-footer | 右侧列表底部区域 |
