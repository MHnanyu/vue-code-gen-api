# Layout 布局

用于快速搭建页面的整体布局，基于 24 分栏的栅格系统。

## 组件

- `<cc-row>`: 行容器
- `<cc-col>`: 列容器

## 基础布局

使用单一分栏创建基础的栅格布局。

```vue
<template>
  <cc-row>
    <cc-col :span="24"><div class="grid-content ep-bg-purple-dark" /></cc-col>
  </cc-row>
  <cc-row>
    <cc-col :span="12"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="12"><div class="grid-content ep-bg-purple-light" /></cc-col>
  </cc-row>
  <cc-row>
    <cc-col :span="8"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="8"><div class="grid-content ep-bg-purple-light" /></cc-col>
    <cc-col :span="8"><div class="grid-content ep-bg-purple" /></cc-col>
  </cc-row>
  <cc-row>
    <cc-col :span="6"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="6"><div class="grid-content ep-bg-purple-light" /></cc-col>
    <cc-col :span="6"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="6"><div class="grid-content ep-bg-purple-light" /></cc-col>
  </cc-row>
  <cc-row>
    <cc-col :span="4"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="4"><div class="grid-content ep-bg-purple-light" /></cc-col>
    <cc-col :span="4"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="4"><div class="grid-content ep-bg-purple-light" /></cc-col>
    <cc-col :span="4"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="4"><div class="grid-content ep-bg-purple-light" /></cc-col>
  </cc-row>
</template>

<style scoped>
.ep-bg-purple-dark {
  background: #99a9bf;
}
.ep-bg-purple {
  background: #d3dce6;
}
.ep-bg-purple-light {
  background: #e5e9f2;
}
.grid-content {
  border-radius: 4px;
  min-height: 36px;
}
</style>
```

## 分栏间隔

通过 `gutter` 属性设置分栏间隔。

```vue
<template>
  <cc-row :gutter="20">
    <cc-col :span="6"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="6"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="6"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="6"><div class="grid-content ep-bg-purple" /></cc-col>
  </cc-row>
</template>

<style scoped>
.ep-bg-purple {
  background: #d3dce6;
}
.grid-content {
  border-radius: 4px;
  min-height: 36px;
}
</style>
```

## 混合布局

通过任意数量的 `span` 创建复杂的混合布局。

```vue
<template>
  <cc-row :gutter="20">
    <cc-col :span="16"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="8"><div class="grid-content ep-bg-purple" /></cc-col>
  </cc-row>
  <cc-row :gutter="20">
    <cc-col :span="8"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="8"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="4"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="4"><div class="grid-content ep-bg-purple" /></cc-col>
  </cc-row>
  <cc-row :gutter="20">
    <cc-col :span="4"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="16"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="4"><div class="grid-content ep-bg-purple" /></cc-col>
  </cc-row>
</template>

<style scoped>
.ep-bg-purple {
  background: #d3dce6;
}
.grid-content {
  border-radius: 4px;
  min-height: 36px;
  margin-bottom: 20px;
}
</style>
```

## 分栏偏移

通过 `offset` 属性设置分栏偏移。

```vue
<template>
  <cc-row :gutter="20">
    <cc-col :span="6"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="6" :offset="6"><div class="grid-content ep-bg-purple" /></cc-col>
  </cc-row>
  <cc-row :gutter="20">
    <cc-col :span="6" :offset="6"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="6" :offset="6"><div class="grid-content ep-bg-purple" /></cc-col>
  </cc-row>
  <cc-row :gutter="20">
    <cc-col :span="12" :offset="6"><div class="grid-content ep-bg-purple" /></cc-col>
  </cc-row>
</template>

<style scoped>
.ep-bg-purple {
  background: #d3dce6;
}
.grid-content {
  border-radius: 4px;
  min-height: 36px;
  margin-bottom: 20px;
}
</style>
```

## 对齐方式

通过 `justify` 属性设置 flex 布局下的水平排列方式。

```vue
<template>
  <cc-row class="row-bg" justify="center">
    <cc-col :span="6"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="6"><div class="grid-content ep-bg-purple-light" /></cc-col>
    <cc-col :span="6"><div class="grid-content ep-bg-purple" /></cc-col>
  </cc-row>
  <cc-row class="row-bg" justify="space-between">
    <cc-col :span="6"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="6"><div class="grid-content ep-bg-purple-light" /></cc-col>
    <cc-col :span="6"><div class="grid-content ep-bg-purple" /></cc-col>
  </cc-row>
  <cc-row class="row-bg" justify="space-around">
    <cc-col :span="6"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="6"><div class="grid-content ep-bg-purple-light" /></cc-col>
    <cc-col :span="6"><div class="grid-content ep-bg-purple" /></cc-col>
  </cc-row>
  <cc-row class="row-bg" justify="space-evenly">
    <cc-col :span="6"><div class="grid-content ep-bg-purple" /></cc-col>
    <cc-col :span="6"><div class="grid-content ep-bg-purple-light" /></cc-col>
    <cc-col :span="6"><div class="grid-content ep-bg-purple" /></cc-col>
  </cc-row>
</template>

<style scoped>
.row-bg {
  background-color: #f9fafc;
  padding: 10px 0;
  margin-bottom: 20px;
}
.ep-bg-purple {
  background: #d3dce6;
}
.ep-bg-purple-light {
  background: #e5e9f2;
}
.grid-content {
  border-radius: 4px;
  min-height: 36px;
}
</style>
```

## 响应式布局

参照了 Bootstrap 的响应式设计，预设了五个响应尺寸：`xs`、`sm`、`md`、`lg` 和 `xl`。

```vue
<template>
  <cc-row :gutter="10">
    <cc-col :xs="24" :sm="12" :md="8" :lg="6" :xl="4">
      <div class="grid-content ep-bg-purple" />
    </cc-col>
    <cc-col :xs="24" :sm="12" :md="8" :lg="6" :xl="4">
      <div class="grid-content ep-bg-purple-light" />
    </cc-col>
    <cc-col :xs="24" :sm="12" :md="8" :lg="6" :xl="4">
      <div class="grid-content ep-bg-purple" />
    </cc-col>
    <cc-col :xs="24" :sm="12" :md="8" :lg="6" :xl="4">
      <div class="grid-content ep-bg-purple-light" />
    </cc-col>
    <cc-col :xs="24" :sm="12" :md="8" :lg="6" :xl="4">
      <div class="grid-content ep-bg-purple" />
    </cc-col>
    <cc-col :xs="24" :sm="12" :md="8" :lg="6" :xl="4">
      <div class="grid-content ep-bg-purple-light" />
    </cc-col>
  </cc-row>
</template>

<style scoped>
.ep-bg-purple {
  background: #d3dce6;
}
.ep-bg-purple-light {
  background: #e5e9f2;
}
.grid-content {
  border-radius: 4px;
  min-height: 36px;
  margin-bottom: 10px;
}
</style>
```

## Row Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| gutter | 栅格间隔 | number / string | — | 0 |
| justify | flex 布局下的水平排列方式 | string | start / end / center / space-around / space-between / space-evenly | start |
| align | flex 布局下的垂直排列方式 | string | top / middle / bottom | top |
| tag | 自定义元素标签 | string | — | div |

## Col Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| span | 栅格占据的列数 | number | — | 24 |
| offset | 栅格左侧的间隔格数 | number | — | 0 |
| push | 栅格向右移动格数 | number | — | 0 |
| pull | 栅格向左移动格数 | number | — | 0 |
| xs | `<768px` 响应式栅格 | number / object | — | — |
| sm | `≥768px` 响应式栅格 | number / object | — | — |
| md | `≥992px` 响应式栅格 | number / object | — | — |
| lg | `≥1200px` 响应式栅格 | number / object | — | — |
| xl | `≥1920px` 响应式栅格 | number / object | — | — |
| tag | 自定义元素标签 | string | — | div |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 自定义默认内容 |
