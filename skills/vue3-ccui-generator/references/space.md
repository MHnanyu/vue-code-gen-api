# Space 间距

设置组件之间的间距。

## 基础用法

使用 `cc-space` 组件来设置组件之间的间距。

```vue
<template>
  <cc-space>
    <cc-button>按钮1</cc-button>
    <cc-button>按钮2</cc-button>
    <cc-button>按钮3</cc-button>
  </cc-space>
</template>
```

## 垂直布局

使用 `direction` 属性来控制布局方向。

```vue
<template>
  <cc-space direction="vertical">
    <cc-button>按钮1</cc-button>
    <cc-button>按钮2</cc-button>
    <cc-button>按钮3</cc-button>
  </cc-space>
</template>
```

## 控制间距的大小

使用 `size` 属性来控制间距大小，支持 `large`、`default`、`small` 三种预设值，也可以自定义数值。

```vue
<template>
  <cc-space size="large">
    <cc-button>Large</cc-button>
    <cc-button>Large</cc-button>
  </cc-space>
  <cc-space size="default">
    <cc-button>Default</cc-button>
    <cc-button>Default</cc-button>
  </cc-space>
  <cc-space size="small">
    <cc-button>Small</cc-button>
    <cc-button>Small</cc-button>
  </cc-space>
  <cc-space :size="30">
    <cc-button>30px</cc-button>
    <cc-button>30px</cc-button>
  </cc-space>
</template>
```

## 自动换行

使用 `wrap` 属性来控制是否自动换行。

```vue
<template>
  <cc-space wrap>
    <cc-button v-for="i in 20" :key="i">按钮 {{ i }}</cc-button>
  </cc-space>
</template>
```

## 间隔符

使用 `spacer` 属性来设置间隔符。

```vue
<template>
  <cc-space spacer="|">
    <span>文字1</span>
    <span>文字2</span>
    <span>文字3</span>
  </cc-space>
</template>
```

## 填充容器

使用 `fill` 属性来填充容器。

```vue
<template>
  <cc-space fill>
    <cc-button>按钮1</cc-button>
    <cc-button>按钮2</cc-button>
    <cc-button>按钮3</cc-button>
  </cc-space>
</template>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| alignment | 对齐方式 | string | — | center |
| direction | 排列方向 | string | horizontal / vertical | horizontal |
| size | 间隔大小 | string / number / [number, number] | large / default / small | small |
| spacer | 间隔符 | string / number / VNode | — | — |
| wrap | 是否自动换行 | boolean | — | false |
| fill | 是否填充容器 | boolean | — | false |
| fill-ratio | 填充比例 | number | — | 100 |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | Space 内容 |
