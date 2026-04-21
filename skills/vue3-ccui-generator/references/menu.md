# Menu 菜单

## 基础用法

菜单组件用于展示导航菜单。

```vue
<template>
  <cc-menu default-active="1">
    <cc-menu-item index="1">处理中心</cc-menu-item>
    <cc-menu-item index="2">订单管理</cc-menu-item>
    <cc-sub-menu index="3">
      <template #title>分组三</template>
      <cc-menu-item index="3-1">列表</cc-menu-item>
      <cc-menu-item index="3-2">配置</cc-menu-item>
    </cc-sub-menu>
  </cc-menu>
</template>
```

## 垂直菜单

设置 `mode` 为 `vertical` 可以显示垂直菜单。

```vue
<template>
  <cc-menu default-active="1" mode="vertical">
    <cc-menu-item index="1">处理中心</cc-menu-item>
    <cc-menu-item index="2">订单管理</cc-menu-item>
    <cc-menu-item index="3">分组三</cc-menu-item>
  </cc-menu>
</template>
```

## 带折叠功能

可以配合折叠按钮使用。

```vue
<template>
  <cc-button @click="collapse = !collapse">折叠</cc-button>
  <cc-menu :collapse="collapse">
    <cc-menu-item index="1">处理中心</cc-menu-item>
    <cc-menu-item index="2">订单管理</cc-menu-item>
  </cc-menu>
</template>

<script setup>
import { ref } from 'vue'
const collapse = ref(false)
</script>
```

## Menu Props

| 属性名 | 说明 | 类型 | 默认值 |
|--------|------|------|--------|
| mode | 菜单模式 | `horizontal` \| `vertical` | horizontal |
| collapse | 是否折叠 | `boolean` | false |
| background-color | 背景色 | `string` | - |
| text-color | 文字颜色 | `string` | - |
| active-text-color |激活文字颜色 | `string` | - |
| default-active | 默认激活菜单项 | `string` | - |
| default-openeds | 默认展开的子菜单 | `string[]` | - |
| unique-opened | 是否只展开一个子菜单 | `boolean` | false |
| menu-trigger | 子菜单触发方式 | `hover` \| `click` | hover |
| router | 是否使用 vue-router 的模式 | `boolean` | false |

## Menu Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| select | 菜单激活回调 | (index: string, indexPath: string[]) => void |
| open | 子菜单打开回调 | (index: string, indexPath: string[]) => void |
| close | 子菜单关闭回调 | (index: string, indexPath: string[]) => void |

## Menu Slots

| 插槽名 | 说明 |
|--------|------|
| default | 菜单内容 |

## MenuItem Props

| 属性名 | 说明 | 类型 | 默认值 |
|--------|------|------|--------|
| index | 唯一标识 | `string` \| `null` | null |
| disabled | 是否禁用 | `boolean` | false |

## MenuItem Slots

| 插槽名 | 说明 |
|--------|------|
| default | 菜单项内容 |

## SubMenu Props

| 属性名 | 说明 | 类型 | 默认值 |
|--------|------|------|--------|
| index | 唯一标识 | `string` \| `null` | null |
| disabled | 是否禁用 | `boolean` | false |
| popper-class | 弹出菜单的类名 | `string` | - |
| show-timeout | 显示的动画延迟 | `number` | 300 |
| hide-timeout | 隐藏的动画延迟 | `number` | 300 |
| popper-append-to-body | 是否添加到body | `boolean` | - |

## SubMenu Slots

| 插槽名 | 说明 |
|--------|------|
| default | 子菜单内容 |
| title | 子菜单标题 |

## MenuItemGroup Props

| 属性名 | 说明 | 类型 | 默认值 |
|--------|------|------|--------|
| title | 分组标题 | `string` | - |

## MenuItemGroup Slots

| 插槽名 | 说明 |
|--------|------|
| default | 分组内容 |
| title | 分组标题 |
