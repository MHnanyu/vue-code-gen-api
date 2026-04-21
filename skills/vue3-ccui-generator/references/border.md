# Border 边框

用于展示边框样式，包含边框、圆角、阴影等功能。

## 基础用法

默认显示边框。

```vue
<template>
  <cc-border>
    这是一个带边框的内容区域
  </cc-border>
</template>
```

## 边框样式

通过 `border-style` 属性设置边框样式，支持 `solid`、`dashed`、`dotted`、`none`。

```vue
<template>
  <cc-border border-style="solid">实线边框</cc-border>
  <cc-border border-style="dashed">虚线边框</cc-border>
  <cc-border border-style="dotted">点线边框</cc-border>
</template>
```

## 边框颜色

通过 `border-color` 属性设置边框颜色。

```vue
<template>
  <cc-border border-color="#409eff">蓝色边框</cc-border>
  <cc-border border-color="#67c23a">绿色边框</cc-border>
  <cc-border border-color="#e6a23c">橙色边框</cc-border>
  <cc-border border-color="#f56c6c">红色边框</cc-border>
</template>
```

## 边框宽度

通过 `border-width` 属性设置边框宽度。

```vue
<template>
  <cc-border border-width="1px">1px 边框</cc-border>
  <cc-border border-width="2px">2px 边框</cc-border>
  <cc-border border-width="3px">3px 边框</cc-border>
</template>
```

## 圆角

通过 `border-radius` 属性设置圆角大小。

```vue
<template>
  <cc-border border-radius="0px">无圆角</cc-border>
  <cc-border border-radius="4px">小圆角</cc-border>
  <cc-border border-radius="8px">中圆角</cc-border>
  <cc-border border-radius="16px">大圆角</cc-border>
  <cc-border round>圆形边框</cc-border>
</template>
```

## 阴影

通过 `shadow` 属性设置阴影显示时机，支持 `always`、`hover`、`never`。

```vue
<template>
  <cc-border shadow="always">总是显示阴影</cc-border>
  <cc-border shadow="hover">悬浮时显示阴影</cc-border>
  <cc-border shadow="never">不显示阴影</cc-border>
</template>
```

## 内边距

通过 `padding` 属性设置内边距。

```vue
<template>
  <cc-border padding="10px">小内边距</cc-border>
  <cc-border padding="20px">中等内边距</cc-border>
  <cc-border padding="40px">大内边距</cc-border>
</template>
```

## 尺寸

通过 `width` 和 `height` 属性设置宽度和高度。

```vue
<template>
  <cc-border width="200px" height="100px">
    固定尺寸
  </cc-border>
</template>
```

## 自定义边框

通过 `border` 属性直接设置完整的边框样式。

```vue
<template>
  <cc-border border="2px dashed #409eff">
    自定义边框样式
  </cc-border>
</template>
```

## 无边框

设置 `border` 为 `false` 可以移除边框。

```vue
<template>
  <cc-border :border="false" shadow="always">
    无边框但有阴影
  </cc-border>
</template>
```

## 组合使用

可以组合使用多个属性。

```vue
<template>
  <cc-border 
    border-color="#409eff" 
    border-width="2px" 
    border-radius="8px" 
    shadow="hover"
    padding="30px"
  >
    <h3>组合样式</h3>
    <p>这是一个组合了多种边框属性的内容区域</p>
  </cc-border>
</template>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| border | 是否显示边框，或完整的边框样式 | boolean / string | — | true |
| border-color | 边框颜色 | string | — | #dcdfe6 |
| border-width | 边框宽度 | string | — | 1px |
| border-style | 边框样式 | string | solid / dashed / dotted / none | solid |
| border-radius | 圆角大小 | string / boolean | — | 4px |
| shadow | 阴影显示时机 | string | always / hover / never | never |
| padding | 内边距 | string | — | 20px |
| margin | 外边距 | string | — | — |
| width | 宽度 | string | — | — |
| height | 高度 | string | — | — |
| round | 是否为圆角 | boolean | — | false |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 边框内的内容 |
