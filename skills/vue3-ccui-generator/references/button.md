# Button 按钮

常用的操作按钮。

## 基础用法

使用 `type` 属性来定义按钮的样式。

```vue
<template>
  <cc-button>默认按钮</cc-button>
  <cc-button type="primary">主要按钮</cc-button>
  <cc-button type="success">成功按钮</cc-button>
  <cc-button type="warning">警告按钮</cc-button>
  <cc-button type="danger">危险按钮</cc-button>
  <cc-button type="info">信息按钮</cc-button>
</template>
```

## 禁用状态

使用 `disabled` 属性来控制按钮是否禁用。

```vue
<template>
  <cc-button disabled>默认按钮</cc-button>
  <cc-button type="primary" disabled>主要按钮</cc-button>
</template>
```

## 简洁按钮

使用 `plain` 属性来获得简洁的按钮。

```vue
<template>
  <cc-button plain>朴素按钮</cc-button>
  <cc-button type="primary" plain>主要按钮</cc-button>
</template>
```

## 圆角按钮

使用 `round` 属性来获得圆角按钮。

```vue
<template>
  <cc-button round>圆角按钮</cc-button>
  <cc-button type="primary" round>主要按钮</cc-button>
</template>
```

## 图标按钮

使用 `icon` 属性来添加图标。

```vue
<template>
  <cc-button type="primary" icon="Search">搜索</cc-button>
  <cc-button type="primary" icon="Edit">编辑</cc-button>
</template>
```

## 按钮尺寸

使用 `size` 属性来设置按钮尺寸，支持 `large`、`default`、`small` 三种尺寸。

```vue
<template>
  <cc-button size="large">大型按钮</cc-button>
  <cc-button size="default">默认按钮</cc-button>
  <cc-button size="small">小型按钮</cc-button>
</template>
```

## 加载状态

使用 `loading` 属性来显示加载状态。

```vue
<template>
  <cc-button type="primary" :loading="loading" @click="handleClick">
    {{ loading ? '加载中...' : '点击加载' }}
  </cc-button>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const loading = ref(false)

const handleClick = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
  }, 2000)
}
</script>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| size | 尺寸 | string | large / default / small | default |
| type | 类型 | string | primary / success / warning / danger / info / default | default |
| plain | 是否朴素按钮 | boolean | — | false |
| text | 是否文字按钮 | boolean | — | false |
| bg | 是否显示文字按钮背景色 | boolean | — | false |
| link | 是否为链接按钮 | boolean | — | false |
| round | 是否圆角按钮 | boolean | — | false |
| circle | 是否圆形按钮 | boolean | — | false |
| loading | 是否加载中状态 | boolean | — | false |
| loading-icon | 自定义加载中图标 | string / Component | — | Loading |
| disabled | 是否禁用状态 | boolean | — | false |
| icon | 图标组件 | string / Component | — | — |
| autofocus | 是否默认聚焦 | boolean | — | false |
| native-type | 原生 type 属性 | string | button / submit / reset | button |
| auto-insert-space | 自动在两个中文字符之间插入空格 | boolean | — | — |
| tag | 自定义元素标签 | string / Component | — | button |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| click | 点击按钮时触发 | (event: MouseEvent) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 按钮内容 |
| icon | 自定义图标组件 |
| loading | 自定义加载组件 |
