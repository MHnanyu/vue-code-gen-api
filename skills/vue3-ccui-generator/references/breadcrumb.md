# Breadcrumb 面包屑

显示当前页面的路径，快速返回之前的任意页面。

## 基础用法

适用场景：适用于任何需要导航的场景。

:::demo 使用 `cc-breadcrumb` 和 `cc-breadcrumb-item` 组件来创建面包屑。

```vue
<template>
  <cc-breadcrumb>
    <cc-breadcrumb-item :to="{ path: '/' }">首页</cc-breadcrumb-item>
    <cc-breadcrumb-item>组件</cc-breadcrumb-item>
    <cc-breadcrumb-item>面包屑</cc-breadcrumb-item>
  </cc-breadcrumb>
</template>
```

:::

## 使用图标分隔符

通过设置 `separator-icon` 属性来指定分隔符图标。

:::demo 

```vue
<template>
  <cc-breadcrumb separator-icon="ArrowRight">
    <cc-breadcrumb-item :to="{ path: '/' }">首页</cc-breadcrumb-item>
    <cc-breadcrumb-item>组件</cc-breadcrumb-item>
    <cc-breadcrumb-item>面包屑</cc-breadcrumb-item>
  </cc-breadcrumb>
</template>
```

:::

## 自定义分隔符

通过设置 `separator` 属性来自定义分隔符。

:::demo 

```vue
<template>
  <cc-breadcrumb separator=">">
    <cc-breadcrumb-item :to="{ path: '/' }">首页</cc-breadcrumb-item>
    <cc-breadcrumb-item>组件</cc-breadcrumb-item>
    <cc-breadcrumb-item>面包屑</cc-breadcrumb-item>
  </cc-breadcrumb>
</template>
```

:::

## 路由跳转

使用 `to` 属性设置跳转链接。

:::demo 

```vue
<template>
  <cc-breadcrumb>
    <cc-breadcrumb-item to="/">首页</cc-breadcrumb-item>
    <cc-breadcrumb-item to="/component">组件</cc-breadcrumb-item>
    <cc-breadcrumb-item>面包屑</cc-breadcrumb-item>
  </cc-breadcrumb>
</template>
```

:::

## Breadcrumb Props

| 属性名 | 说明 | 类型 | 默认值 |
|--------|------|------|--------|
| separator | 分隔符 | `string` | `/` |
| separator-icon | 分隔符图标 | `Component` | `-` |

## BreadcrumbItem Props

| 属性名 | 说明 | 类型 | 默认值 |
|--------|------|------|--------|
| to | 路由跳转目标 | `string` / `object` | `-` |
| replace | 是否替换当前历史记录 | `boolean` | `false` |

## BreadcrumbItem Slots

| 插槽名 | 说明 |
|--------|------|
| default | 面包屑项内容 |
