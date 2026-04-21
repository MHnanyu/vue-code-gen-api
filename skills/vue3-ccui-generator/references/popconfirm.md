# Popconfirm 气泡确认框

一种目标元素的操作命令，用户点击后，弹出一个气泡确认框来进行二次确认。

## 基础用法

```vue
<template>
  <cc-popconfirm
    title="确定要删除这项内容吗？"
    @confirm="handleConfirm"
    @cancel="handleCancel"
  >
    <template #reference>
      <cc-button>删除</cc-button>
    </template>
  </cc-popconfirm>
</template>

<script setup lang="ts">
const handleConfirm = () => {
  console.log('点击了确认')
}

const handleCancel = () => {
  console.log('点击了取消')
}
</script>
```

## 自定义按钮文字

通过 `confirm-button-text` 和 `cancel-button-text` 自定义按钮文字。

```vue
<template>
  <cc-popconfirm
    confirm-button-text="好的"
    cancel-button-text="算了"
    title="确定要执行此操作吗？"
  >
    <template #reference>
      <cc-button>自定义文字</cc-button>
    </template>
  </cc-popconfirm>
</template>
```

## 按钮类型

通过 `confirm-button-type` 设置确认按钮的类型。

```vue
<template>
  <cc-popconfirm
    title="确定要删除吗？"
    confirm-button-type="primary"
  >
    <template #reference>
      <cc-button>主要按钮</cc-button>
    </template>
  </cc-popconfirm>

  <cc-popconfirm
    title="确定要删除吗？"
    confirm-button-type="success"
  >
    <template #reference>
      <cc-button>成功按钮</cc-button>
    </template>
  </cc-popconfirm>

  <cc-popconfirm
    title="确定要删除吗？"
    confirm-button-type="danger"
  >
    <template #reference>
      <cc-button>危险按钮</cc-button>
    </template>
  </cc-popconfirm>

  <cc-popconfirm
    title="确定要删除吗？"
    confirm-button-type="warning"
  >
    <template #reference>
      <cc-button>警告按钮</cc-button>
    </template>
  </cc-popconfirm>
</template>
```

## 展示位置

通过 `placement` 属性设置弹出位置。

```vue
<template>
  <cc-popconfirm title="上面" placement="top">
    <template #reference>
      <cc-button>top</cc-button>
    </template>
  </cc-popconfirm>

  <cc-popconfirm title="上面开始" placement="top-start">
    <template #reference>
      <cc-button>top-start</cc-button>
    </template>
  </cc-popconfirm>

  <cc-popconfirm title="上面结束" placement="top-end">
    <template #reference>
      <cc-button>top-end</cc-button>
    </template>
  </cc-popconfirm>

  <cc-popconfirm title="下面" placement="bottom">
    <template #reference>
      <cc-button>bottom</cc-button>
    </template>
  </cc-popconfirm>

  <cc-popconfirm title="左边" placement="left">
    <template #reference>
      <cc-button>left</cc-button>
    </template>
  </cc-popconfirm>

  <cc-popconfirm title="右边" placement="right">
    <template #reference>
      <cc-button>right</cc-button>
    </template>
  </cc-popconfirm>
</template>
```

## 隐藏图标

通过 `hide-icon` 隐藏图标。

```vue
<template>
  <cc-popconfirm hide-icon title="确定要执行此操作吗？">
    <template #reference>
      <cc-button>隐藏图标</cc-button>
    </template>
  </cc-popconfirm>
</template>
```

## 禁用

通过 `disabled` 禁用 Popconfirm。

```vue
<template>
  <cc-popconfirm disabled title="禁用状态">
    <template #reference>
      <cc-button>禁用</cc-button>
    </template>
  </cc-popconfirm>
</template>
```

## 手动控制显示

通过 `v-model` 手动控制显示状态。

```vue
<template>
  <cc-popconfirm v-model="visible" title="手动控制">
    <template #reference>
      <cc-button @click="visible = !visible">手动控制</cc-button>
    </template>
  </cc-popconfirm>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const visible = ref(false)
</script>
```

## 图标自定义

通过 `icon` 自定义图标。

```vue
<template>
  <cc-popconfirm title="确定要删除吗？" :icon="InfoFilled">
    <template #reference>
      <cc-button>自定义图标</cc-button>
    </template>
  </cc-popconfirm>
</template>

<script setup lang="ts">
import { InfoFilled } from '@element-plus/icons-vue'
</script>
```

## Attributes

| 参数 | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| title | 标题 | string | — |
| confirm-button-text | 确认按钮文字 | string | — |
| cancel-button-text | 取消按钮文字 | string | — |
| confirm-button-type | 确认按钮类型 | 'primary' / 'success' / 'warning' / 'danger' / 'info' | 'primary' |
| cancel-button-type | 取消按钮类型 | 'primary' / 'success' / 'warning' / 'danger' / 'info' | 'text' |
| icon | 自定义图标 | Component | InfoFilled |
| hide-icon | 是否隐藏图标 | boolean | false |
| disabled | 是否禁用 | boolean | false |
| placement | 弹出位置 | 'top' / 'top-start' / 'top-end' / 'bottom' / 'bottom-start' / 'bottom-end' / 'left' / 'left-start' / 'left-end' / 'right' / 'right-start' / 'right-end' | 'bottom' |
| visible / v-model | 手动控制显示状态 | boolean | false |
| offset | 偏移量 | number | 0 |
| transition | 动画名称 | string | fade-transform |
| show-after | 显示延迟，单位毫秒 | number | 0 |
| hide-after | 隐藏延迟，单位毫秒 | number | 200 |
| auto-close | 点击确认后自动关闭延迟，单位毫秒 | number | 200 |
| show-arrow | 是否显示箭头 | boolean | true |
| popper-options | popper.js 参数 | object | {} |
| teleported | 是否插入到 body | boolean | true |
| persistent | 当 Popconfirm 关闭时，是否强制销毁 | boolean | true |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | Popconfirm 内容 |
| reference | Popconfirm 触发元素 |

## Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| confirm | 点击确认按钮时触发 | — |
| cancel | 点击取消按钮时触发 | — |
| show | 显示时触发 | — |
| hide | 隐藏时触发 | — |
