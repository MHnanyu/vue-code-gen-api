# Icon 图标

语义化的矢量图标组件。

## 基础用法

使用 `icon` 属性或默认插槽来显示图标。

```vue
<template>
  <cc-icon :icon="Search" />
  <cc-icon :icon="Edit" />
  <cc-icon :icon="Check" />
</template>

<script setup lang="ts">
import { Search, Edit, Check } from '@element-plus/icons-vue'
</script>
```

## 图标尺寸

使用 `size` 属性来设置图标尺寸。

```vue
<template>
  <cc-icon :icon="Search" :size="16" />
  <cc-icon :icon="Search" :size="24" />
  <cc-icon :icon="Search" :size="32" />
  <cc-icon :icon="Search" :size="48" />
</template>
```

## 图标颜色

使用 `color` 属性来设置图标颜色。

```vue
<template>
  <cc-icon :icon="Search" color="#409EFC" />
  <cc-icon :icon="Search" color="#67C23A" />
  <cc-icon :icon="Search" color="#E6A23C" />
  <cc-icon :icon="Search" color="#F56C6C" />
</template>
```

## 结合按钮使用

图标可以和按钮组件结合使用。

```vue
<template>
  <cc-button type="primary">
    <cc-icon :icon="Search" />
    <span>搜索</span>
  </cc-button>
</template>
```

## 使用 SVG 图标

通过默认插槽使用自定义 SVG 图标。

```vue
<template>
  <cc-icon :size="24">
    <svg viewBox="0 0 1024 1024">
      <path fill="currentColor" d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372z"/>
    </svg>
  </cc-icon>
</template>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| icon | 图标组件 | Component | — | — |
| size | 图标尺寸 | number / string | — | — |
| color | 图标颜色 | string | — | — |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 自定义图标内容，可以是 SVG 或其他内容 |
