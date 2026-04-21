# Result 结果

用于展示操作结果信息。

## 基础用法

```vue
<template>
  <cc-result
    icon="success"
    title="操作成功"
    sub-title="请根据提示进行操作"
  />
</template>
```

## 不同图标

使用 `icon` 属性设置不同的图标。

```vue
<template>
  <cc-result
    icon="info"
    title="提示"
    sub-title="这是一条提示信息"
  />
  <cc-result
    icon="warning"
    title="警告"
    sub-title="请注意以下警告信息"
  />
  <cc-result
    icon="error"
    title="错误"
    sub-title="操作失败，请重试"
  />
</template>
```

## 自定义图标

使用 `icon` 插槽自定义图标。

```vue
<template>
  <cc-result title="自定义图标">
    <template #icon>
      <cc-icon :icon="Star" :size="60" />
    </template>
  </cc-result>
</template>

<script setup lang="ts">
import { Star } from '@element-plus/icons-vue'
</script>
```

## 自定义标题和副标题

使用 `title` 和 `subTitle` 插槽自定义标题和副标题。

```vue
<template>
  <cc-result>
    <template #title>自定义标题</template>
    <template #subTitle>自定义副标题内容</template>
  </cc-result>
</template>
```

## 添加操作按钮

使用默认插槽添加操作按钮。

```vue
<template>
  <cc-result
    icon="success"
    title="操作成功"
    sub-title="请根据提示进行操作"
  >
    <template #default>
      <cc-button type="primary">返回首页</cc-button>
      <cc-button>查看详情</cc-button>
    </template>
  </cc-result>
</template>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| title | 标题 | string | — | — |
| sub-title | 副标题 | string | — | — |
| icon | 图标类型 | string | success / info / warning / error | info |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 自定义操作区内容 |
| icon | 自定义图标 |
| title | 自定义标题 |
| subTitle | 自定义副标题 |
