# Container 布局容器

用于布局的容器组件，方便快速搭建页面的基本结构。

## 布局容器组件

- `<cc-container>`: 外层容器。当子元素中包含 `<cc-header>` 或 `<cc-footer>` 时，全部子元素会垂直上下排列，否则会水平左右排列。
- `<cc-header>`: 顶栏容器。
- `<cc-aside>`: 侧边栏容器。
- `<cc-main>`: 主要区域容器。
- `<cc-footer>`: 底栏容器。

## 常见页面布局

### 常见布局

```vue
<template>
  <div class="common-layout">
    <cc-container>
      <cc-header>Header</cc-header>
      <cc-main>Main</cc-main>
    </cc-container>

    <cc-container>
      <cc-header>Header</cc-header>
      <cc-main>Main</cc-main>
      <cc-footer>Footer</cc-footer>
    </cc-container>

    <cc-container>
      <cc-aside width="200px">Aside</cc-aside>
      <cc-main>Main</cc-main>
    </cc-container>

    <cc-container>
      <cc-header>Header</cc-header>
      <cc-container>
        <cc-aside width="200px">Aside</cc-aside>
        <cc-main>Main</cc-main>
      </cc-container>
    </cc-container>

    <cc-container>
      <cc-header>Header</cc-header>
      <cc-container>
        <cc-aside width="200px">Aside</cc-aside>
        <cc-container>
          <cc-main>Main</cc-main>
          <cc-footer>Footer</cc-footer>
        </cc-container>
      </cc-container>
    </cc-container>

    <cc-container>
      <cc-header>Header</cc-header>
      <cc-container>
        <cc-aside width="200px">Aside</cc-aside>
        <cc-container>
          <cc-main>Main</cc-main>
        </cc-container>
        <cc-footer>Footer</cc-footer>
      </cc-container>
    </cc-container>

    <cc-container>
      <cc-aside width="200px">Aside</cc-aside>
      <cc-container>
        <cc-header>Header</cc-header>
        <cc-main>Main</cc-main>
      </cc-container>
    </cc-container>

    <cc-container>
      <cc-aside width="200px">Aside</cc-aside>
      <cc-container>
        <cc-header>Header</cc-header>
        <cc-main>Main</cc-main>
        <cc-footer>Footer</cc-footer>
      </cc-container>
    </cc-container>
  </div>
</template>

<style scoped>
.cc-header,
.cc-footer {
  background-color: #b3c0d1;
  color: #333;
  text-align: center;
  line-height: 60px;
}

.cc-aside {
  background-color: #d3dce6;
  color: #333;
  text-align: center;
  line-height: 200px;
}

.cc-main {
  background-color: #e9eef3;
  color: #333;
  text-align: center;
  line-height: 160px;
}
</style>
```

## 实例

### 顶部导航布局

```vue
<template>
  <cc-container class="layout-container">
    <cc-header>
      <div class="logo">Logo</div>
      <cc-menu mode="horizontal" :ellipsis="false">
        <cc-menu-item index="1">首页</cc-menu-item>
        <cc-menu-item index="2">关于</cc-menu-item>
        <cc-menu-item index="3">联系</cc-menu-item>
      </cc-menu>
    </cc-header>
    <cc-main>
      <h2>主要内容区域</h2>
    </cc-main>
    <cc-footer>
      Copyright © 2024
    </cc-footer>
  </cc-container>
</template>
```

### 侧边导航布局

```vue
<template>
  <cc-container class="layout-container">
    <cc-aside width="200px">
      <cc-menu default-active="1">
        <cc-menu-item index="1">首页</cc-menu-item>
        <cc-menu-item index="2">用户管理</cc-menu-item>
        <cc-menu-item index="3">系统设置</cc-menu-item>
      </cc-menu>
    </cc-aside>
    <cc-container>
      <cc-header>Header</cc-header>
      <cc-main>Main</cc-main>
    </cc-container>
  </cc-container>
</template>
```

## Container Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| direction | 子元素的排列方向 | string | horizontal / vertical | 子元素中有 `cc-header` 或 `cc-footer` 时为 vertical，否则为 horizontal |

## Header Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| height | 顶栏高度 | string | — | 60px |

## Aside Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| width | 侧边栏宽度 | string | — | 300px |

## Main Props

无特定属性

## Footer Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| height | 底栏高度 | string | — | 60px |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 自定义默认内容 |
