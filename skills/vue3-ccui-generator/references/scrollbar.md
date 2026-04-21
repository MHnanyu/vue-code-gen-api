# Scrollbar 滚动条

用于替换浏览器原生滚动条。

## 基础用法

通过 `height` 属性设置滚动条高度，若希望不出现纵向滚动条，则不设置该属性。

```vue
<template>
  <cc-scrollbar height="400px">
    <p v-for="item in 20" :key="item" class="scrollbar-demo-item">
      {{ item }}
    </p>
  </cc-scrollbar>
</template>

<style scoped>
.scrollbar-demo-item {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 50px;
  margin: 10px;
  text-align: center;
  border-radius: 4px;
  background: #ecf5ff;
  color: #409eff;
}
</style>
```

## 横向滚动

当元素宽度大于父元素宽度时，会显示横向滚动条。

```vue
<template>
  <cc-scrollbar>
    <div class="scrollbar-flex-content">
      <p v-for="item in 50" :key="item" class="scrollbar-demo-item">
        {{ item }}
      </p>
    </div>
  </cc-scrollbar>
</template>

<style scoped>
.scrollbar-flex-content {
  display: flex;
}

.scrollbar-demo-item {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100px;
  height: 50px;
  margin: 10px;
  text-align: center;
  border-radius: 4px;
  background: #ecf5ff;
  color: #409eff;
}
</style>
```

## 最大高度

通过 `max-height` 属性设置滚动条最大高度，当内容高度不超过最大高度时，不会显示纵向滚动条。

```vue
<template>
  <cc-scrollbar max-height="400px">
    <p v-for="item in 20" :key="item" class="scrollbar-demo-item">
      {{ item }}
    </p>
  </cc-scrollbar>
</template>
```

## 手动控制滚动

使用组件的 `ref` 调用 `setScrollTop`、`setScrollLeft` 或 `scrollTo` 方法手动控制滚动条。

```vue
<template>
  <div>
    <cc-button @click="handleScrollTop">滚动到顶部</cc-button>
    <cc-button @click="handleScrollBottom">滚动到底部</cc-button>
  </div>
  <cc-scrollbar ref="scrollbarRef" height="400px">
    <p v-for="item in 100" :key="item" class="scrollbar-demo-item">
      {{ item }}
    </p>
  </cc-scrollbar>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const scrollbarRef = ref()

const handleScrollTop = () => {
  scrollbarRef.value.setScrollTop(0)
}

const handleScrollBottom = () => {
  scrollbarRef.value.setScrollTop(10000)
}
</script>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| height | 滚动条高度 | string / number | — | — |
| max-height | 滚动条最大高度 | string / number | — | — |
| native | 是否使用原生滚动条样式 | boolean | — | false |
| wrap-style | 包裹容器的自定义样式 | string / Array\<object\> | — | — |
| wrap-class | 包裹容器的自定义类名 | string / Array\<string\> | — | — |
| view-style | 视图的自定义样式 | string / Array\<object\> | — | — |
| view-class | 视图的自定义类名 | string / Array\<string\> | — | — |
| noresize | 不响应容器尺寸变化，如果容器尺寸不会发生变化，最好设置它可以优化性能 | boolean | — | false |
| tag | 视图的元素标签 | string | — | div |
| always | 滚动条总是显示 | boolean | — | false |
| min-size | 滚动条最小尺寸 | number | — | 20 |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| scroll | 滚动时触发的事件 | (scrollLeft: number, scrollTop: number) |

## Methods

| 方法名 | 说明 | 参数 |
|------|------|------|
| setScrollTop | 设置滚动条到顶部的距离 | (scrollTop: number) |
| setScrollLeft | 设置滚动条到左侧的距离 | (scrollLeft: number) |
| scrollTo | 滚动到一组特定坐标 | (options: ScrollToOptions \| number, yCoord?: number) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 自定义默认内容 |
