# Rate 评分

用于评分展示和输入评分。

## 基础用法

```vue
<template>
  <cc-rate v-model="rate" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const rate = ref(0)
</script>
```

## 禁用状态

使用 `disabled` 属性来禁用评分组件。

```vue
<template>
  <cc-rate v-model="rate" disabled />
</template>
```

## 不同尺寸

使用 `size` 属性设置评分组件尺寸。

```vue
<template>
  <cc-rate v-model="rate1" size="large" />
  <cc-rate v-model="rate2" />
  <cc-rate v-model="rate3" size="small" />
</template>
```

## 自定义图标

使用 `icon` 属性自定义图标。

```vue
<template>
  <cc-rate v-model="rate" :icon="Star" />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Star } from '@element-plus/icons-vue'

const rate = ref(0)
</script>
```

## 自定义颜色

使用 `colors` 属性自定义选中颜色。

```vue
<template>
  <cc-rate v-model="rate" :colors="['#99A9BF', '#F7BA2A', '#FF9900']" />
</template>
```

## 只读评分

使用 `readonly` 属性设置只读模式，只用于展示评分。

```vue
<template>
  <cc-rate v-model="rate" readonly show-score />
</template>
```

## 显示分数

使用 `show-score` 属性显示当前分数。

```vue
<template>
  <cc-rate v-model="rate" show-score />
</template>
```

## 辅助文字

使用 `show-text` 属性显示辅助文字。

```vue
<template>
  <cc-rate v-model="rate" show-text :texts="['极差', '失望', '一般', '满意', '惊喜']" />
</template>
```

## 允许半选

使用 `allow-half` 属性允许半选。

```vue
<template>
  <cc-rate v-model="rate" allow-half />
</template>
```

## 评分上限

使用 `max` 属性设置评分上限。

```vue
<template>
  <cc-rate v-model="rate" :max="10" show-score />
</template>
```

## 事件测试

使用 `@change` 和 `@hover-change` 事件监听评分变化。

```vue
<template>
  <cc-rate
    v-model="rate"
    @change="handleChange"
    @hover-change="handleHoverChange"
  />
</template>

<script setup lang="ts">
const handleChange = (value: number) => {
  console.log('change:', value)
}

const handleHoverChange = (value: number) => {
  console.log('hover-change:', value)
}
</script>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| model-value / v-model | 绑定值 | number | — | 0 |
| max | 最大分值 | number | — | 5 |
| disabled | 是否禁用 | boolean | — | false |
| allow-half | 是否允许半选 | boolean | — | false |
| low-threshold | 低分和中等分数的临界值 | number | — | 2 |
| high-threshold | 中等分数和高等分数的临界值 | number | — | 4 |
| colors | 选中颜色 | array | — | ['#F7BA2A', '#F7BA2A', '#F7BA2A'] |
| void-color | 未选中颜色 | string | — | #C6D1DE |
| disabled-void-color | 禁用状态下未选中颜色 | string | — | #EFF2F7 |
| icon | 自定义图标 | string / Component | — | Star |
| void-icon | 自定义未选中图标 | string / Component | — | Star |
| disabled-void-icon | 禁用状态下未选中图标 | string / Component | — | StarFilled |
| show-score | 是否显示当前分数 | boolean | — | false |
| show-text | 是否显示辅助文字 | boolean | — | false |
| texts | 辅助文字数组 | array | — | ['极差', '失望', '一般', '满意', '惊喜'] |
| score-template | 分数显示模板 | string | — | {value} |
| size | 尺寸 | string | large / default / small | — |
| clearable | 值是否可以清零 | boolean | — | true |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| change | 值改变时触发 | (value: number) |
| hover-change | 鼠标悬停评分改变时触发 | (value: number) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 自定义图标内容 |
