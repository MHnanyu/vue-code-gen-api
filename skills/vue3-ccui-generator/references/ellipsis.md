# Ellipsis 文本省略

当文本过长时，使用省略号展示，并支持展开/收起功能。

## 基础用法

使用 `content` 属性设置文本内容，`line` 属性设置最大显示行数。

```vue
<template>
  <cc-ellipsis :content="text" :line="1" />
</template>

<script setup lang="ts">
const text = '这是一段很长的文本内容，用于展示文本省略组件的基本用法。当文本超过指定宽度时，会自动显示省略号。'
</script>
```

## 多行省略

通过设置 `line` 属性来控制显示的行数。

```vue
<template>
  <cc-ellipsis :content="text" :line="2" />
</template>

<script setup lang="ts">
const text = '这是一段很长的文本内容，用于展示多行文本省略。通过设置 line 属性，可以控制显示的行数。当文本内容超过指定行数时，会自动截断并显示省略号。这种效果在展示摘要或简介时非常有用。'
</script>
```

## 带 Tooltip

当鼠标悬停在省略文本上时，显示完整内容的提示。使用 `showTooltip` 属性控制是否显示提示。

```vue
<template>
  <cc-ellipsis 
    :content="text" 
    :line="1" 
    show-tooltip 
    tooltip-placement="top" 
  />
</template>

<script setup lang="ts">
const text = '这是一段很长的文本内容，鼠标悬停时会显示完整的文本内容。'
</script>
```

## 可展开/收起

使用 `expandable` 属性使文本支持展开/收起操作。

```vue
<template>
  <cc-ellipsis 
    :content="text" 
    :line="2" 
    expandable 
    expand-text="展开" 
    collapse-text="收起" 
  />
</template>

<script setup lang="ts">
const text = '这是一段很长的文本内容，支持展开和收起功能。点击展开可以看到完整的内容，再次点击收起可以折叠文本。这种交互方式在需要展示详细信息但又要保持页面简洁的场景中非常有用。'
</script>
```

## 自定义最大宽度

使用 `max-width` 属性设置文本容器的最大宽度。

```vue
<template>
  <cc-ellipsis :content="text" :line="1" max-width="300px" />
</template>

<script setup lang="ts">
const text = '这是一段设置了最大宽度的文本，超过300px时会显示省略号。'
</script>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| content | 文本内容 | string | — | — |
| line | 最大显示行数 | number | — | 1 |
| show-tooltip | 是否显示 tooltip | boolean | — | true |
| tooltip-placement | tooltip 的位置 | string | top / bottom / left / right | top |
| tooltip-effect | tooltip 的主题 | string | dark / light | dark |
| expandable | 是否可展开/收起 | boolean | — | false |
| expand-text | 展开按钮文本 | string | — | '展开' |
| collapse-text | 收起按钮文本 | string | — | '收起' |
| max-width | 最大宽度 | string / number | — | '100%' |

## Slots

该组件暂无插槽。
