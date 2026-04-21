# InputNumber 数字输入框

仅允许输入标准的数字值，可自定义范围。

## 基础用法

```vue
<template>
  <cc-input-number v-model="num" :min="1" :max="10" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const num = ref(1)
</script>
```

## 禁用状态

使用 `disabled` 属性来禁用数字输入框。

```vue
<template>
  <cc-input-number v-model="num" disabled />
</template>
```

## 步进

设置 `step` 属性可以控制步进大小。

```vue
<template>
  <cc-input-number v-model="num" :step="2" />
</template>
```

## 严格步进

设置 `step-strictly` 属性为 true，则只能输入步进的倍数。

```vue
<template>
  <cc-input-number v-model="num" :step="2" step-strictly />
</template>
```

## 精度

设置 `precision` 属性可以控制数值精度。

```vue
<template>
  <cc-input-number v-model="num" :precision="2" :step="0.1" :max="10" />
</template>
```

## 不同尺寸

使用 `size` 属性设置数字输入框尺寸。

```vue
<template>
  <cc-input-number v-model="num1" size="large" />
  <cc-input-number v-model="num2" />
  <cc-input-number v-model="num3" size="small" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const num1 = ref(1)
const num2 = ref(1)
const num3 = ref(1)
</script>
```

## 按钮位置

设置 `controls-position` 属性可以控制按钮位置。

```vue
<template>
  <cc-input-number v-model="num" controls-position="right" />
</template>
```

## 自定义按钮图标

使用 `decrease` 和 `increase` 插槽自定义按钮图标。

```vue
<template>
  <cc-input-number v-model="num" :min="1" :max="10">
    <template #decrease>
      <cc-icon :icon="Minus" />
    </template>
    <template #increase>
      <cc-icon :icon="Plus" />
    </template>
  </cc-input-number>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Minus, Plus } from '@element-plus/icons-vue'

const num = ref(1)
</script>
```

## 前缀和后缀

使用 `prefix` 和 `suffix` 插槽添加前缀和后缀内容。

```vue
<template>
  <cc-input-number v-model="price" :precision="2">
    <template #prefix>¥</template>
    <template #suffix>元</template>
  </cc-input-number>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const price = ref(100)
</script>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| model-value / v-model | 绑定值 | number | — | 0 |
| min | 设置计数器允许的最小值 | number | — | -Infinity |
| max | 设置计数器允许的最大值 | number | — | Infinity |
| step | 计数器步长 | number | — | 1 |
| step-strictly | 是否只能输入 step 的倍数 | boolean | — | false |
| precision | 数值精度 | number | — | — |
| size | 计数器尺寸 | string | large / default / small | — |
| readonly | 原生属性，是否只读 | boolean | — | false |
| disabled | 是否禁用 | boolean | — | false |
| controls | 是否使用控制按钮 | boolean | — | true |
| controls-position | 控制按钮位置 | string | right | — |
| name | 原生属性 | string | — | — |
| label | 输入框关联的 label 文字 | string | — | — |
| placeholder | 输入框默认 placeholder | string | — | — |
| id | 原生属性 | string | — | — |
| value-on-clear | 当值被清空时，返回设置的值 | number / string | number / string | min |
| validate-event | 输入时是否触发表单的校验 | boolean | — | true |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| change | 绑定值被改变时触发 | (currentValue: number, oldValue: number) |
| blur | 在组件 Input 失去焦点时触发 | (event: FocusEvent) |
| focus | 在组件 Input 获得焦点时触发 | (event: FocusEvent) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| prefix | 输入框头部内容 |
| suffix | 输入框尾部内容 |
| decrease | 减少按钮内容 |
| increase | 增加按钮内容 |

## Methods

| 方法名 | 说明 | 参数 |
|------|------|------|
| focus | 使 input 获取焦点 | — |
| blur | 使 input 失去焦点 | — |
