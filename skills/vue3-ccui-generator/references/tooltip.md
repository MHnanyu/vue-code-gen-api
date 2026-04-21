# Tooltip 文字提示

常用于展示鼠标 hover 时的提示信息。

## 基础用法

```vue
<template>
  <cc-tooltip content="这是一段提示信息">
    <cc-button>鼠标悬停</cc-button>
  </cc-tooltip>
</template>
```

## 展示位置

通过 `placement` 属性设置弹出位置。

```vue
<template>
  <div class="placement-demo">
    <cc-tooltip content="上面" placement="top">
      <cc-button>top</cc-button>
    </cc-tooltip>
    <cc-tooltip content="上面开始" placement="top-start">
      <cc-button>top-start</cc-button>
    </cc-tooltip>
    <cc-tooltip content="上面结束" placement="top-end">
      <cc-button>top-end</cc-button>
    </cc-tooltip>
    <cc-tooltip content="下面" placement="bottom">
      <cc-button>bottom</cc-button>
    </cc-tooltip>
    <cc-tooltip content="左边" placement="left">
      <cc-button>left</cc-button>
    </cc-tooltip>
    <cc-tooltip content="右边" placement="right">
      <cc-button>right</cc-button>
    </cc-tooltip>
  </div>
</template>
```

## 主题

通过 `effect` 设置主题。

```vue
<template>
  <cc-tooltip content="深色主题" effect="dark">
    <cc-button>深色主题</cc-button>
  </cc-tooltip>
  <cc-tooltip content="浅色主题" effect="light">
    <cc-button>浅色主题</cc-button>
  </cc-tooltip>
</template>
```

## 触发方式

通过 `trigger` 设置触发方式。

```vue
<template>
  <cc-tooltip content="hover 触发">
    <cc-button>hover</cc-button>
  </cc-tooltip>
  <cc-tooltip content="click 触发" trigger="click">
    <cc-button>click</cc-button>
  </cc-tooltip>
  <cc-tooltip content="focus 触发" trigger="focus">
    <cc-button>focus</cc-button>
  </cc-tooltip>
</template>
```

## 手动控制显示

通过 `v-model` 手动控制显示状态。

```vue
<template>
  <cc-tooltip v-model="visible" content="手动控制">
    <cc-button @click="visible = !visible">手动控制</cc-button>
  </cc-tooltip>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const visible = ref(false)
</script>
```

## 禁用

通过 `disabled` 禁用 Tooltip。

```vue
<template>
  <cc-tooltip content="禁用状态" disabled>
    <cc-button>禁用</cc-button>
  </cc-tooltip>
</template>
```

## 动画

通过 `transition` 自定义动画。

```vue
<template>
  <cc-tooltip content="自定义动画" transition="fade-scale">
    <cc-button>自定义动画</cc-button>
  </cc-tooltip>
</template>
```

## 显示/隐藏延迟

通过 `show-after` 和 `hide-after` 设置延迟。

```vue
<template>
  <cc-tooltip content="显示延迟 500ms" :show-after="500">
    <cc-button>显示延迟</cc-button>
  </cc-tooltip>
  <cc-tooltip content="隐藏延迟 500ms" :hide-after="500">
    <cc-button>隐藏延迟</cc-button>
  </cc-tooltip>
</template>
```

## 插槽

```vue
<template>
  <cc-tooltip>
    <template #content>
      <div>自定义内容</div>
    </template>
    <cc-button>使用插槽</cc-button>
  </cc-tooltip>
</template>
```

## Attributes

| 参数 | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| content | 显示的内容 | string | — |
| placement | 弹出位置 | 'top' / 'top-start' / 'top-end' / 'bottom' / 'bottom-start' / 'bottom-end' / 'left' / 'left-start' / 'left-end' / 'right' / 'right-start' / 'right-end' | 'top' |
| effect | 主题 | 'dark' / 'light' | 'dark' |
| trigger | 触发方式 | 'hover' / 'click' / 'focus' | 'hover' |
| visible / v-model | 手动控制显示状态 | boolean | false |
| disabled | 是否禁用 | boolean | false |
| offset | 偏移量 | number | 0 |
| transition | 动画名称 | string | fade-scale |
| show-after | 显示延迟，单位毫秒 | number | 0 |
| hide-after | 隐藏延迟，单位毫秒 | number | 200 |
| show-arrow | 是否显示箭头 | boolean | true |
| teleported | 是否插入到 body | boolean | true |
| popper-options | popper.js 参数 | object | {} |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | Tooltip 触发元素 |
| content | Tooltip 内容 |

## Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| show | 显示时触发 | — |
| hide | 隐藏时触发 | — |
