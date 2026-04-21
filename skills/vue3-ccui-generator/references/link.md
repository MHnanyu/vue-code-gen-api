# Link 链接

文字超链接。

## 基础用法

使用 `type` 属性来定义链接的样式。

```vue
<template>
  <cc-link>默认链接</cc-link>
  <cc-link type="primary">主要链接</cc-link>
  <cc-link type="success">成功链接</cc-link>
  <cc-link type="warning">警告链接</cc-link>
  <cc-link type="danger">危险链接</cc-link>
  <cc-link type="info">信息链接</cc-link>
</template>
```

## 禁用状态

使用 `disabled` 属性来控制链接是否禁用。

```vue
<template>
  <cc-link disabled>默认链接</cc-link>
  <cc-link type="primary" disabled>主要链接</cc-link>
</template>
```

## 下划线

使用 `underline` 属性来控制链接是否显示下划线。

```vue
<template>
  <cc-link :underline="false">无下划线</cc-link>
  <cc-link type="primary" :underline="false">无下划线</cc-link>
</template>
```

## 图标链接

使用 `icon` 属性来添加图标。

```vue
<template>
  <cc-link type="primary" :icon="Search">搜索</cc-link>
  <cc-link type="primary" :icon="Edit">编辑</cc-link>
</template>
```

## 跳转链接

使用 `href` 和 `target` 属性来设置跳转链接。

```vue
<template>
  <cc-link href="https://example.com" target="_blank">示例链接</cc-link>
  <cc-link type="primary" href="https://example.com" target="_blank">示例链接</cc-link>
</template>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| type | 类型 | string | primary / success / warning / danger / info / default | default |
| underline | 是否显示下划线 | boolean | — | true |
| disabled | 是否禁用状态 | boolean | — | false |
| href | 原生 href 属性 | string | — | — |
| icon | 图标组件 | string / Component | — | — |
| target | 原生 target 属性 | string | — | — |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| click | 点击链接时触发 | (event: MouseEvent) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 链接内容 |
| icon | 自定义图标组件 |
