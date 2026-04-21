# PageHeader 页头

页头组件，用于展示当前页面位置、标题和返回按钮等信息。

## 基础用法

```vue
<template>
  <cc-page-header title="返回" content="详情页面" />
</template>
```

## 自定义标题

```vue
<template>
  <cc-page-header title="自定义标题" content="页面内容">
    <template #content>
      <span style="color: red;">自定义内容区域</span>
    </template>
  </cc-page-header>
</template>
```

## 隐藏返回按钮

```vue
<template>
  <cc-page-header :title="false" content="无返回按钮" />
</template>
```

## 使用 Slots

```vue
<template>
  <cc-page-header title="完整示例">
    <template #extra>
      <cc-button type="primary">操作按钮</cc-button>
    </template>
  </cc-page-header>
</template>
```

## Props

| 属性名 | 说明 | 类型 | 默认值 |
|--------|------|------|--------|
| title | 标题内容，设置为 false 可隐藏返回按钮 | `string \| boolean` | '返回' |
| icon | 标题图标 | `VNode \| string` | - |
| content | 内容区域文字 | `string` | - |
| redirect | 跳转地址 | `string` | - |

## Slots

| 插槽名 | 说明 |
|--------|------|
| header | 自定义头部区域 |
| extra | 额外操作区域 |
| content | 自定义内容区域 |
| default | 默认插槽，内容区域 |
| breadcrumb | 自定义面包屑区域 |

## Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| back | 点击返回按钮时触发 | - |
