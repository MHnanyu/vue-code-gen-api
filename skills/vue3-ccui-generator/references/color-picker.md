# ColorPicker 颜色选择器

用于颜色选择，支持多种格式。

## 基础用法

使用 v-model 绑定颜色值。

```vue
<template>
  <cc-color-picker v-model="color" />
  <p>当前颜色: {{ color }}</p>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const color = ref('#409EFF')
</script>
```

## 禁用状态

通过 `disabled` 属性设置是否禁用颜色选择器。

```vue
<template>
  <cc-color-picker v-model="color" disabled />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const color = ref('#409EFF')
</script>
```

## 透明度

通过 `show-alpha` 属性设置是否支持透明度选择。

```vue
<template>
  <cc-color-picker v-model="color" show-alpha />
  <p>当前颜色: {{ color }}</p>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const color = ref('rgba(19, 206, 102, 0.8)')
</script>
```

## 预定义颜色

通过 `predefine` 属性设置预定义的颜色列表。

```vue
<template>
  <cc-color-picker v-model="color" :predefine="predefineColors" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const color = ref('#409EFF')
const predefineColors = ref([
  '#ff4500',
  '#ff8c00',
  '#ffd700',
  '#90ee90',
  '#00ced1',
  '#1e90ff',
  '#c71585',
  'rgba(255, 69, 0, 0.68)',
  'rgb(255, 120, 0)',
  'hsv(51, 100, 98)',
  'hsva(120, 40, 94, 0.5)',
  'hsl(181, 100%, 37%)',
  'hsla(209, 100%, 56%, 0.73)',
  '#c7158577'
])
</script>
```

## 不同尺寸

通过 `size` 属性设置颜色选择器的尺寸。

```vue
<template>
  <cc-color-picker v-model="color1" size="large" />
  <cc-color-picker v-model="color2" />
  <cc-color-picker v-model="color3" size="small" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const color1 = ref('#409EFF')
const color2 = ref('#409EFF')
const color3 = ref('#409EFF')
</script>
```

## ColorPicker Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| model-value / v-model | 绑定值 | string | — | — |
| disabled | 是否禁用 | boolean | — | false |
| size | 尺寸 | string | large / default / small | default |
| show-alpha | 是否支持透明度选择 | boolean | — | false |
| color-format | 输出颜色的格式 | string | hsl / hsv / hex / rgb | hex（show-alpha 为 false）/ rgb（show-alpha 为 true）|
| popper-class | ColorPicker 下拉框的类名 | string | — | — |
| predefine | 预定义颜色 | array | — | — |
| validate-event | 输入时是否触发表单验证 | boolean | — | true |
| tabindex | Tabindex 属性 | string / number | — | 0 |
| label | 标签 | string / number | — | — |
| id | 原生 id 属性 | string | — | — |

## ColorPicker Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| change | 当绑定值变化时触发 | 当前颜色值 |
| active-change | 面板中当前显示的颜色发生改变时触发 | 当前显示的颜色值 |

## ColorPicker Slots

| 插槽名 | 说明 |
|-------|------|
| default | 自定义默认内容 |
