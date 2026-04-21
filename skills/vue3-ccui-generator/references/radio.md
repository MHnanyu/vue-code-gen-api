# Radio 单选框

用于在多个备选项中选中单个状态。

## 基础用法

使用 `v-model` 绑定选中项的值。

```vue
<template>
  <cc-radio v-model="radio" label="1">选项一</cc-radio>
  <cc-radio v-model="radio" label="2">选项二</cc-radio>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const radio = ref('1')
</script>
```

## 禁用状态

使用 `disabled` 属性来禁用单选框。

```vue
<template>
  <cc-radio v-model="radio" label="1" disabled>禁用</cc-radio>
  <cc-radio v-model="radio" label="2">未禁用</cc-radio>
</template>
```

## 单选框组

使用 `cc-radio-group` 包裹一组单选框。

```vue
<template>
  <cc-radio-group v-model="radio">
    <cc-radio label="1">选项一</cc-radio>
    <cc-radio label="2">选项二</cc-radio>
    <cc-radio label="3">选项三</cc-radio>
  </cc-radio-group>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const radio = ref('1')
</script>
```

## 不同尺寸

使用 `size` 属性设置单选框尺寸。

```vue
<template>
  <cc-radio-group v-model="radio" size="large">
    <cc-radio label="1">large</cc-radio>
    <cc-radio label="2">large</cc-radio>
  </cc-radio-group>
  <cc-radio-group v-model="radio">
    <cc-radio label="1">default</cc-radio>
    <cc-radio label="2">default</cc-radio>
  </cc-radio-group>
  <cc-radio-group v-model="radio" size="small">
    <cc-radio label="1">small</cc-radio>
    <cc-radio label="2">small</cc-radio>
  </cc-radio-group>
</template>
```

## 带有边框

使用 `border` 属性设置带有边框的单选框。

```vue
<template>
  <cc-radio v-model="radio" label="1" border>选项一</cc-radio>
  <cc-radio v-model="radio" label="2" border>选项二</cc-radio>
</template>
```

## 单选框按钮样式

使用 `cc-radio-button` 可以实现按钮样式的单选框。

```vue
<template>
  <cc-radio-group v-model="radio">
    <cc-radio-button label="上海" />
    <cc-radio-button label="北京" />
    <cc-radio-button label="广州" />
    <cc-radio-button label="深圳" />
  </cc-radio-group>
</template>
```

## 限制可选数量

使用 `min` 和 `max` 属性限制可选数量。

```vue
<template>
  <cc-radio-group v-model="radio" :min="1" :max="2">
    <cc-radio label="1">选项一</cc-radio>
    <cc-radio label="2">选项二</cc-radio>
    <cc-radio label="3">选项三</cc-radio>
    <cc-radio label="4">选项四</cc-radio>
  </cc-radio-group>
</template>
```

## Radio Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| model-value / v-model | 绑定值 | string / number / boolean | — | — |
| label | 单选框的值 | string / number / boolean | — | — |
| disabled | 是否禁用 | boolean | — | false |
| border | 是否显示边框 | boolean | — | false |
| size | 单选框的尺寸 | string | large / default / small | — |
| name | 原生 name 属性 | string | — | — |
| true-label | 选中时的值 | string / number | — | — |
| false-label | 未选中时的值 | string / number | — | — |

## Radio Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| change | 值改变时触发 | (value: string / number / boolean) |

## RadioGroup Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| model-value / v-model | 绑定值 | string / number / boolean / array | — | — |
| size | 单选框组尺寸 | string | large / default / small | — |
| disabled | 是否禁用 | boolean | — | false |
| min | 最小可选数量 | number | — | — |
| max | 最大可选数量 | number | — | — |

## RadioGroup Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| change | 值改变时触发 | (value: string / number / boolean / array) |

## RadioButton Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| label | 单选框的值 | string / number | — | — |
| disabled | 是否禁用 | boolean | — | false |
| name | 原生 name 属性 | string | — | — |
