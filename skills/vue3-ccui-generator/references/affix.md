# Affix 固钉

将元素固定在页面可视区域。

## 基础用法

固钉默认固定在页面顶部。

```vue
<template>
  <cc-affix>
    <cc-button type="primary">固定在顶部</cc-button>
  </cc-affix>
</template>
```

## 固定位置

设置 `position` 属性来控制固定位置，支持 `top` 和 `bottom`。

```vue
<template>
  <div class="affix-container">
    <cc-affix position="top">
      <cc-button type="primary">固定在顶部</cc-button>
    </cc-affix>
    <div style="height: 1500px;">
      <p>向下滚动查看固钉效果</p>
    </div>
    <cc-affix position="bottom" :offset="20">
      <cc-button type="success">固定在底部</cc-button>
    </cc-affix>
  </div>
</template>
```

## 固定偏移

设置 `offset` 属性来控制固定位置的距离。

```vue
<template>
  <cc-affix :offset="80">
    <cc-button type="primary">距离顶部 80px 固定</cc-button>
  </cc-affix>
</template>
```

## 监听固定状态

使用 `change` 事件来监听固钉的固定状态变化。

```vue
<template>
  <cc-affix @change="handleChange">
    <cc-button type="primary">{{ fixed ? '已固定' : '未固定' }}</cc-button>
  </cc-affix>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const fixed = ref(false)

const handleChange = (isFixed: boolean) => {
  fixed.value = isFixed
  console.log('固钉状态变化:', isFixed)
}
</script>
```

## 固定目标容器

设置 `target` 属性来指定固钉的参照容器。

```vue
<template>
  <div class="affix-target-container" ref="containerRef">
    <cc-affix :target="targetFunc">
      <cc-button type="primary">固定在目标容器内</cc-button>
    </cc-affix>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const containerRef = ref<HTMLElement>()

const targetFunc = () => {
  return containerRef.value
}
</script>

<style scoped>
.affix-target-container {
  height: 300px;
  overflow: auto;
  border: 1px solid #eee;
}
</style>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| offset | 距离顶部的偏移量 | number | — | 0 |
| position | 固定位置 | string | top / bottom | top |
| target | 固定目标的参照元素 | () => HTMLElement | — | — |
| z-index | 固钉的 z-index | number | — | 100 |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|---------|
| change | 固定状态变化时触发 | (isFixed: boolean) |

## Slots
| 插槽名 | 说明 |
|-------|------|
| default | 固钉内容 |
