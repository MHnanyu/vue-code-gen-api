# Backtop 回到顶部

返回页面顶部的操作按钮。

## 基础用法

默认情况下，回到顶部按钮会出现在页面右下角。

```vue
<template>
  <div class="backtop-container">
    <div style="height: 1500px;">
      <p>向下滚动查看回到顶部按钮</p>
    </div>
    <cc-backtop />
  </div>
</template>
```

## 自定义内容

可以通过插槽自定义回到顶部按钮的内容。

```vue
<template>
  <div class="backtop-container">
    <div style="height: 1500px;">
      <p>向下滚动查看自定义按钮</p>
    </div>
    <cc-backtop>
      <div class="custom-backtop">
        UP
      </div>
    </cc-backtop>
  </div>
</template>

<style scoped>
.custom-backtop {
  width: 40px;
  height: 40px;
  line-height: 40px;
  text-align: center;
  background: #409eff;
  color: #fff;
  border-radius: 50%;
  font-weight: bold;
}
</style>
```

## 滚动目标

设置 `target` 属性来指定滚动容器。

```vue
<template>
  <div class="backtop-target-container" ref="containerRef">
    <div class="content">
      <p v-for="i in 20" :key="i">内容区域 {{ i }}</p>
    </div>
    <cc-backtop :target="containerRef" :visibility-height="200" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const containerRef = ref<HTMLElement>()
</script>

<style scoped>
.backtop-target-container {
  height: 300px;
  overflow-y: auto;
  border: 1px solid #eee;
  position: relative;
}
.content {
  padding: 20px;
}
</style>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| target | 滚动目标容器 | string / () => HTMLElement | — | — |
| visibility-height | 滚动高度达到此值时显示按钮 | number | — | 200 |
| right | 距离右边距 | number | — | 40 |
| bottom | 距离底部边距 | number | — | 40 |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|---------|
| click | 点击按钮时触发 | (event: MouseEvent) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 按钮内容 |
