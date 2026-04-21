# Card 卡片

常用的数据展示容器。

## 基础用法

使用 `body-style` 属性来定义卡片内容的样式。

```vue
<template>
  <cc-card>
    <div>卡片内容</div>
  </cc-card>
</template>
```

## 简单卡片

卡片可以只有内容区域。

```vue
<template>
  <cc-card>
    <p>卡片内容 1</p>
    <p>卡片内容 2</p>
    <p>卡片内容 3</p>
  </cc-card>
</template>
```

## 带标题和操作

使用 `header` 插槽来定义卡片标题和操作区域。

```vue
<template>
  <cc-card>
    <template #header>
      <div class="card-header">
        <span>卡片标题</span>
        <cc-button type="primary">操作</cc-button>
      </div>
    </template>
    <p>卡片内容</p>
  </cc-card>
</template>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
```

## 卡片阴影

使用 `shadow` 属性来控制卡片阴影。

```vue
<template>
  <cc-card shadow="hover">
    <p>hover 时显示阴影</p>
  </cc-card>
  <cc-card shadow="always">
    <p>始终显示阴影</p>
  </cc-card>
  <cc-card shadow="never">
    <p>不显示阴影</p>
  </cc-card>
</template>
```

## 卡片尺寸

使用 `body-style` 属性来定义内容区域的内边距。

```vue
<template>
  <cc-card :body-style="{ padding: '20px' }">
    <p>默认内边距 20px</p>
  </cc-card>
  <cc-card :body-style="{ padding: '0px' }">
    <p>无内边距</p>
  </cc-card>
</template>
```

##  Images 图片卡片

结合图片和内容区域。

```vue
<template>
  <cc-card :body-style="{ padding: '0px' }">
    <img src="https://element-plus.org/images/element-plus-logo.svg" class="image" />
    <div style="padding: 14px">
      <span>图片卡片</span>
      <div class="bottom">
        <time class="time">2024-01-01</time>
        <cc-button type="text">操作</cc-button>
      </div>
    </div>
  </cc-card>
</template>

<style scoped>
.image {
  width: 100%;
  display: block;
}
.bottom {
  margin-top: 13px;
  line-height: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.time {
  font-size: 13px;
  color: #999;
}
</style>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| body-style | 卡片内容区的自定义样式 | object | — | { padding: '20px' } |
| body-class | 卡片内容区的自定义类名 | string | — | — |
| shadow | 卡片阴影类型 | string | always / hover / never | always |
| header | 卡片标题区域自定义渲染函数 | string / object | — | — |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| click | 点击卡片时触发 | (event: MouseEvent) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 卡片内容区域 |
| header | 卡片标题区域 |
