# Anchor 锚点

## 基础用法

锚点组件主要用于跳转到页面指定位置。

```vue
<template>
  <cc-anchor :affix="false">
    <cc-anchor-link href="#basic-usage" title="基础用法" />
    <cc-anchor-link href="#props" title="Props" />
    <cc-anchor-link href="#events" title="Events" />
  </cc-anchor>
</template>
```

## Props

| 属性名 | 说明 | 类型 | 默认值 |
|--------|------|------|--------|
| bounds | 锚点距离窗口顶部安全距离 | `number` | 5 |
| offset | 滚动偏移量 | `number` | 0 |
| target-offset | 锚点滚动偏移量 | `number` | 0 |
| affix | 是否固定钉锚点 | `boolean` | true |
| show-ink | 是否显示连接线 | `boolean` | true |
| type | 锚点类型 | `line` \| `circle` | line |

## Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| click | 点击锚点时触发 | (e: MouseEvent, link: { href: string; title: string }) => void |
| change | 锚点链接切换时触发 | (activeLink: string) => void |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 锚点链接内容 |

## AnchorLink Props

| 属性名 | 说明 | 类型 | 默认值 |
|--------|------|------|--------|
| href | 锚点链接 | `string` | - |
| title | 锚点标题 | `string` | - |
| target | 滚动目标 | `string` \| `HTMLElement` | - |

## AnchorLink Slots

| 插槽名 | 说明 |
|--------|------|
| default | 自定义标题内容 |
