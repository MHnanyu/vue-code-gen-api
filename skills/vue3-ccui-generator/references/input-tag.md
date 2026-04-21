# InputTag 输入框标签

用于输入多个标签的输入框组件。

## 基础用法

```vue
<template>
  <cc-input-tag v-model="tags" placeholder="请输入标签" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const tags = ref(['Tag 1', 'Tag 2'])
</script>
```

## 禁用状态

使用 `disabled` 属性来禁用输入框标签。

```vue
<template>
  <cc-input-tag v-model="tags" disabled placeholder="禁用状态" />
</template>
```

## 只读状态

使用 `readonly` 属性来设置只读状态。

```vue
<template>
  <cc-input-tag v-model="tags" readonly placeholder="只读状态" />
</template>
```

## 可清空

使用 `clearable` 属性来显示清空按钮。

```vue
<template>
  <cc-input-tag v-model="tags" clearable placeholder="可清空" />
</template>
```

## 最大标签数

使用 `max` 属性限制最大标签数量。

```vue
<template>
  <cc-input-tag v-model="tags" :max="3" placeholder="最多3个标签" />
</template>
```

## 标签类型

使用 `tag-type` 属性设置标签类型。

```vue
<template>
  <cc-input-tag v-model="tags" tag-type="success" placeholder="success类型标签" />
</template>
```

## 标签效果

使用 `tag-effect` 属性设置标签效果。

```vue
<template>
  <cc-input-tag v-model="tags" tag-effect="dark" placeholder="dark效果标签" />
</template>
```

## 触发方式

使用 `trigger` 属性设置触发添加标签的方式。

```vue
<template>
  <cc-input-tag v-model="tags1" trigger="Enter" placeholder="按Enter添加" />
  <cc-input-tag v-model="tags2" trigger="Space" placeholder="按空格添加" />
</template>
```

## 不同尺寸

使用 `size` 属性设置输入框尺寸。

```vue
<template>
  <cc-input-tag v-model="tags1" size="large" placeholder="large 尺寸" />
  <cc-input-tag v-model="tags2" placeholder="默认尺寸" />
  <cc-input-tag v-model="tags3" size="small" placeholder="small 尺寸" />
</template>
```

## 前缀和后缀

使用 `prefix` 和 `suffix` 插槽添加前缀和后缀内容。

```vue
<template>
  <cc-input-tag v-model="tags">
    <template #prefix>标签:</template>
    <template #suffix>个</template>
  </cc-input-tag>
</template>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| model-value / v-model | 绑定值 | array | — | — |
| max | 最大标签数量 | number | — | — |
| maxlength | 输入框最大长度 | number / string | — | — |
| minlength | 输入框最小长度 | number / string | — | — |
| clearable | 是否可清空 | boolean | — | false |
| disabled | 是否禁用 | boolean | — | false |
| readonly | 原生属性，是否只读 | boolean | — | false |
| size | 输入框尺寸 | string | large / default / small | — |
| placeholder | 输入框占位文本 | string | — | — |
| trigger | 触发添加标签的方式 | string | Enter / Space | Enter |
| tag-type | 标签类型 | string | success / info / warning / danger | — |
| tag-effect | 标签效果 | string | dark / light / plain | light |
| validate-event | 输入时是否触发表单的校验 | boolean | — | true |
| persistent | 是否持久化显示输入框 | boolean | — | true |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| update:modelValue | 在标签值改变时触发 | (value: array) |
| change | 在标签值改变时触发 | (value: array) |
| blur | 在组件失去焦点时触发 | (event: FocusEvent) |
| focus | 在组件获得焦点时触发 | (event: FocusEvent) |
| clear | 在点击清空按钮时触发 | — |

## Slots

| 插槽名 | 说明 |
|-------|------|
| prefix | 输入框头部内容 |
| suffix | 输入框尾部内容 |

## Methods

| 方法名 | 说明 | 参数 |
|------|------|------|
| focus | 使 input 获取焦点 | — |
| blur | 使 input 失去焦点 | — |
