# Statistic 统计数值

用于展示统计数值信息。

## 基础用法

```vue
<template>
  <cc-statistic title="用户总数" :value="1000" />
</template>
```

## 带前后缀

使用 `prefix` 和 `suffix` 属性设置数值的前后缀。

```vue
<template>
  <cc-statistic title="销售额" :value="10000" prefix="$" />
  <cc-statistic title="转化率" :value="0.75" suffix="%" />
</template>
```

## 格式化数值

使用 `formatter` 属性自定义数值显示格式。

```vue
<template>
  <cc-statistic title="用户总数" :value="10000" :formatter="(value) => value.toLocaleString()" />
</template>
```

## 数值动画

使用 `animation` 属性开启数值动画效果。

```vue
<template>
  <cc-statistic title="活跃用户" :value="5000" :animation="true" />
</template>
```

## 自定义动画时长

使用 `animation-duration` 属性设置动画时长。

```vue
<template>
  <cc-statistic 
    title="累计访问量" 
    :value="100000" 
    :animation="true" 
    :animation-duration="2000" 
  />
</template>
```

## 精细控制动画

使用 `animation-duration` 和 `value-from` 属性控制动画。

```vue
<template>
  <cc-statistic 
    title="从零开始计数" 
    :value="2024" 
    :animation="true" 
    :value-from="0"
  />
</template>
```

## 使用插槽

使用插槽自定义内容。

```vue
<template>
  <cc-statistic title="自定义内容">
    <template #prefix>$</template>
    1,234.56
    <template #suffix>USD</template>
  </cc-statistic>
</template>
```

## 不同样式

使用 `value-style` 属性设置数值样式。

```vue
<template>
  <cc-statistic 
    title="收入" 
    :value="50000" 
    prefix="$" 
    :value-style="{ color: '#67c23a' }" 
  />
  <cc-statistic 
    title="支出" 
    :value="30000" 
    prefix="$" 
    :value-style="{ color: '#f56c6c' }" 
  />
</template>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| title | 标题 | string | — | — |
| value | 数值 | number / string | — | 0 |
| prefix | 前缀 | string | — | — |
| suffix | 后缀 | string | — | — |
| value-style | 数值样式 | object | — | {} |
| animation | 是否动画 | boolean | — | false |
| animation-duration | 动画时长(ms) | number | — | 2000 |
| value-from | 动画起始值 | number | — | 0 |
| decimal-separator | 小数分隔符 | string | — | . |
| group-separator | 千分位分隔符 | string | — | , |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 自定义数值内容 |
| title | 自定义标题 |
| prefix | 自定义前缀 |
| suffix | 自定义后缀 |
