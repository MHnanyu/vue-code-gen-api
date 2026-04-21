# Segmented 分段控制器

由多个分段选项组成的控件，用于在多个选项之间切换。

## 基础用法

绑定 `v-model` 到一个值，数组 `options` 指定可选的选项。

```vue
<template>
  <cc-segmented v-model="value" :options="options" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('Apple')
const options = ['Apple', 'Banana', 'Orange']
</script>
```

## 对象数组

使用对象数组形式的 `options`，可以指定每个选项的 `label`、`value` 和 `disabled` 状态。

```vue
<template>
  <cc-segmented v-model="value" :options="options" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('Beijing')
const options = [
  { label: '北京', value: 'Beijing' },
  { label: '上海', value: 'Shanghai' },
  { label: '广州', value: 'Guangzhou' },
  { label: '深圳', value: 'Shenzhen' }
]
</script>
```

## 不同尺寸

使用 `size` 属性设置分段控制器尺寸。

```vue
<template>
  <cc-segmented v-model="value1" :options="options" size="large" />
  <cc-segmented v-model="value2" :options="options" />
  <cc-segmented v-model="value3" :options="options" size="small" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const options = ['iOS', 'Android', 'HarmonyOS']
const value1 = ref('iOS')
const value2 = ref('Android')
const value3 = ref('HarmonyOS')
</script>
```

## 禁用状态

使用 `disabled` 属性禁用整个分段控制器。

```vue
<template>
  <cc-segmented v-model="value1" :options="options" disabled />
  <cc-segmented v-model="value2" :options="options" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const options = ['iOS', 'Android', 'HarmonyOS']
const value1 = ref('iOS')
const value2 = ref('Android')
</script>
```

## 禁用单项

在对象数组中，可以禁用单个选项。

```vue
<template>
  <cc-segmented v-model="value" :options="options" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('Apple')
const options = [
  { label: 'Apple', value: 'Apple' },
  { label: 'Banana', value: 'Banana', disabled: true },
  { label: 'Orange', value: 'Orange' }
]
</script>
```

## 只读模式

使用 `readonly` 属性设置只读模式。

```vue
<template>
  <cc-segmented v-model="value1" :options="options" readonly />
  <cc-segmented v-model="value2" :options="options" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const options = ['iOS', 'Android', 'HarmonyOS']
const value1 = ref('iOS')
const value2 = ref('Android')
</script>
```

## 块级样式

使用 `block` 属性使分段控制器变为块级元素，宽度占满父容器。

```vue
<template>
  <div style="width: 400px">
    <cc-segmented v-model="value" :options="options" block />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('Week')
const options = ['Day', 'Week', 'Month', 'Year']
</script>
```

## 自定义内容

使用默认插槽自定义选项内容。

```vue
<template>
  <cc-segmented v-model="value" :options="options">
    <template #default="{ option, index }">
      <span>{{ option.label }} ({{ index + 1 }})</span>
    </template>
  </cc-segmented>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('Apple')
const options = [
  { label: 'Apple', value: 'Apple' },
  { label: 'Banana', value: 'Banana' },
  { label: 'Orange', value: 'Orange' }
]
</script>
```

## Segmented Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| change | 值改变时触发 | (value: string / number, option: SegmentedOption / string / number) |

## Segmented Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|-------|--------|
| model-value / v-model | 绑定值 | string / number | — | — |
| options | 选项数组 | (SegmentedOption / string / number)[] | — | [] |
| size | 尺寸 | string | large / default / small | default |
| disabled | 是否禁用 | boolean | — | false |
| readonly | 是否只读 | boolean | — | false |
| block | 是否块级显示 | boolean | — | false |

## Segmented Slots

| 名称 | 说明 | 参数 |
|------|------|------|
| default | 自定义选项内容 | { option: SegmentedOption / string / number, index: number } |

## SegmentedOption Type

```typescript
interface SegmentedOption {
  label: string
  value: string | number
  disabled?: boolean
}
```
