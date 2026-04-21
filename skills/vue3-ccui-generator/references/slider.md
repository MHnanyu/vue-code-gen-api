# Slider 滑块

通过拖动滑块在一个固定区间内进行选择。

## 基础用法

从 0 到 100 的滑块，默认值为 0。

```vue
<template>
  <cc-slider v-model="value" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref(0)
</script>
```

## 禁用状态

使用 `disabled` 属性来禁用滑块。

```vue
<template>
  <cc-slider v-model="value" disabled />
</template>
```

## 带有输入框

使用 `show-input` 属性显示输入框。

```vue
<template>
  <cc-slider v-model="value" show-input />
</template>
```

## 范围选择

使用 `range` 属性开启范围选择，此时绑定的值为数组。

```vue
<template>
  <cc-slider v-model="value" range />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref([10, 80])
</script>
```

## 设置步长

使用 `step` 属性设置步长。

```vue
<template>
  <cc-slider v-model="value" :step="10" show-stops />
</template>
```

## 显示间断点

使用 `show-stops` 属性显示间断点。

```vue
<template>
  <cc-slider v-model="value" :step="10" show-stops />
</template>
```

## 自定义范围

使用 `min` 和 `max` 属性设置范围。

```vue
<template>
  <cc-slider v-model="value" :min="10" :max="90" />
</template>
```

## 格式化 Tooltip

使用 `format-tooltip` 属性格式化 Tooltip 内容。

```vue
<template>
  <cc-slider v-model="value" :format-tooltip="formatTooltip" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref(0)

const formatTooltip = (val: number) => {
  return val / 100
}
</script>
```

## 竖向模式

使用 `vertical` 属性开启竖向模式，同时需要设置高度。

```vue
<template>
  <cc-slider v-model="value" vertical height="200px" />
</template>
```

## 展示标记

使用 `marks` 属性展示标记。

```vue
<template>
  <cc-slider v-model="value" :marks="marks" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref(30)

const marks = {
  0: '0°C',
  8: '8°C',
  37: '37°C',
  50: {
    style: {
      color: '#1989FA'
    },
    label: '50%'
  },
  100: '100°C'
}
</script>
```

## Props

| 属性名 | 说明 | 类型 | 可选值 | 默认值 |
|--------|------|------|--------|--------|
| model-value / v-model | 绑定值 | number / array | — | 0 |
| min | 最小值 | number | — | 0 |
| max | 最大值 | number | — | 100 |
| disabled | 是否禁用 | boolean | — | false |
| step | 步长 | number | — | 1 |
| show-input | 是否显示输入框，仅在非范围选择时有效 | boolean | — | false |
| show-input-controls | 在显示输入框的情况下，是否显示输入框的控制按钮 | boolean | — | true |
| show-stops | 是否显示间断点 | boolean | — | false |
| show-tooltip | 是否显示 tooltip | boolean | — | true |
| format-tooltip | 格式化 tooltip message | function(value) | — | — |
| range | 是否为范围选择 | boolean | — | false |
| vertical | 是否竖向模式 | boolean | — | false |
| height | Slider 高度，竖向模式时必填 | string | — | — |
| label | 屏幕阅读器标签 | string | — | — |
| range-start-label | 当 range 为 true 时，屏幕阅读器标签的开始标签 | string | — | — |
| range-end-label | 当 range 为 true 时，屏幕阅读器标签的结束标签 | string | — | — |
| debounce | 输入时的去抖延迟，毫秒，仅在 show-input 等于 true 的时候有效 | number | — | 300 |
| tooltip-class | tooltip 的自定义类名 | string | — | — |
| marks | 标记，key 的类型必须为 number 且取值在闭区间 [min, max] 内，每个标记可以单独设置样式 | object | — | — |

## Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| change | 值改变时触发（使用鼠标拖曳时，只在松开鼠标后触发） | val，新状态的值 |
| input | 数据改变时触发（使用鼠标拖曳时，活动过程实时触发） | val，新状态的值 |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 自定义默认内容 |
