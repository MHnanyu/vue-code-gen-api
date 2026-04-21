# Switch 开关

表示两种相互对立的状态间的切换，多用于触发「开」或「关」。

## 基础用法

绑定 `v-model` 到一个 `Boolean` 类型的变量。可以使用 `active-color` 属性与 `inactive-color` 属性来设置开关的背景色。

```vue
<template>
  <cc-switch v-model="value" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref(true)
</script>
```

## 禁用状态

使用 `disabled` 属性来禁用开关。

```vue
<template>
  <cc-switch v-model="value1" disabled />
  <cc-switch v-model="value2" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value1 = ref(true)
const value2 = ref(false)
</script>
```

## 不同尺寸

使用 `size` 属性设置开关尺寸。

```vue
<template>
  <cc-switch v-model="value1" size="large" />
  <cc-switch v-model="value2" />
  <cc-switch v-model="value3" size="small" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value1 = ref(true)
const value2 = ref(false)
const value3 = ref(true)
</script>
```

## 文字描述

使用 `active-text` 属性与 `inactive-text` 属性来设置开关的文字描述。

```vue
<template>
  <cc-switch
    v-model="value1"
    active-text="按月付费"
    inactive-text="按年付费"
  />
  <cc-switch
    v-model="value2"
    active-text="开启"
    inactive-text="关闭"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value1 = ref(true)
const value2 = ref(true)
</script>
```

## 扩展的 value 类型

使用 `active-value` 属性与 `inactive-value` 属性来设置开关的值。

```vue
<template>
  <cc-switch
    v-model="value"
    active-value="100"
    inactive-value="0"
  />
  <p>当前值: {{ value }}</p>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('100')
</script>
```

## 加载状态

使用 `loading` 属性来设置开关的加载状态。

```vue
<template>
  <cc-switch v-model="value1" loading />
  <cc-switch v-model="value2" loading disabled />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value1 = ref(true)
const value2 = ref(false)
</script>
```

## 阻止关闭

当 `before-change` 返回 `false` 或者返回 `Promise` 且被 reject 时，则阻止关闭。

```vue
<template>
  <cc-switch v-model="value" :before-change="beforeChange" />
  <p>当前值: {{ value }}</p>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref(true)

const beforeChange = () => {
  return new Promise((resolve) => {
    console.log('阻止关闭')
    resolve(false)
  })
}
</script>
```

## Switch Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| change | 值改变时触发 | (value: boolean / string / number) |
| click | 点击时触发 | (event: MouseEvent) |

## Switch Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|-------|--------|
| model-value / v-model | 绑定值 | boolean / string / number | — | false |
| disabled | 是否禁用 | boolean | — | false |
| loading | 是否显示加载中 | boolean | — | false |
| size | 开关尺寸 | string | large / default / small | — |
| width | 开关宽度 | number / string | — | 40 |
| inline-prompt | 是否显示文字或图标 | boolean | — | false |
| active-text | 打开时的文字描述 | string | — | — |
| inactive-text | 关闭时的文字描述 | string | — | — |
| active-value | 打开时的值 | boolean / string / number | — | true |
| inactive-value | 关闭时的值 | boolean / string / number | — | false |
| active-color | 打开时的背景色 | string | — | — |
| inactive-color | 关闭时的背景色 | string | — | — |
| border-color | 边框颜色 | string | — | — |
| loop | 是否循环切换 | boolean | — | true |
| before-change | 返回 boolean 或者 Promise 的函数，true 时切换 | () => Promise<boolean> / boolean | — | — |

## Switch Slots

| 名称 | 说明 |
|------|------|
| indicator | 自定义图标 |
