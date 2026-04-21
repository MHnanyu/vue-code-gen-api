# Color 色彩

用于展示颜色样本，方便在设计中保持一致的视觉体验。

## 主色

主要品牌色是安全、充满活力的蓝色。

```vue
<template>
  <cc-color color="#409eff" name="Primary" />
</template>
```

## 辅助色

除了主色外的场景色，需要在不同的场景中使用（例如：危险色表示危险的操作）。

```vue
<template>
  <cc-color color="#67c23a" name="Success" />
  <cc-color color="#e6a23c" name="Warning" />
  <cc-color color="#f56c6c" name="Danger" />
  <cc-color color="#909399" name="Info" />
</template>
```

## 中性色

中性色用于文本、背景和边框颜色。通过运用不同的中性色，来表现层次结构。

```vue
<template>
  <cc-color color="#303133" name="主要文字" />
  <cc-color color="#606266" name="常规文字" />
  <cc-color color="#909399" name="次要文字" />
  <cc-color color="#c0c4cc" name="占位文字" />
</template>
```

## 尺寸

Color 组件提供三种尺寸：`small`、`default`、`large`。

```vue
<template>
  <cc-color color="#409eff" name="Small" size="small" />
  <cc-color color="#409eff" name="Default" size="default" />
  <cc-color color="#409eff" name="Large" size="large" />
</template>
```

## 隐藏信息

使用 `show-info` 属性控制是否显示颜色信息。

```vue
<template>
  <cc-color color="#409eff" :show-info="false" />
</template>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| color | 颜色值 | string | — | #409eff |
| name | 颜色名称 | string | — | — |
| title | 标题 | string | — | — |
| size | 尺寸 | string | small / default / large | default |
| show-info | 是否显示颜色信息 | boolean | — | true |
| show-title | 是否显示标题 | boolean | — | false |
| width | 自定义宽度 | string | — | — |
| height | 自定义高度 | string | — | — |
| border-radius | 圆角大小 | string | — | 4px |
