# Steps 步骤条

引导用户按照流程完成任务的分步导航条。

## 基础用法

适用场景：适用于任务步骤分步展示的场景。

:::demo 使用 `cc-steps` 和 `cc-step` 组件来创建步骤条。

```vue
<template>
  <cc-steps :active="active" @click="handleClick">
    <cc-step title="步骤1" />
    <cc-step title="步骤2" />
    <cc-step title="步骤3" />
  </cc-steps>

  <cc-button style="margin-top: 20px" @click="next">下一步</cc-button>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const active = ref(0)

const next = () => {
  if (active.value++ > 2) active.value = 0
}

const handleClick = (index: number) => {
  active.value = index
}
</script>
```

:::

## 含有描述信息

每个步骤条可以包含描述信息。

:::demo 

```vue
<template>
  <cc-steps :active="1">
    <cc-step title="步骤1" description="这是步骤1的描述信息" />
    <cc-step title="步骤2" description="这是步骤2的描述信息" />
    <cc-step title="步骤3" description="这是步骤3的描述信息" />
  </cc-steps>
</template>
```

:::

## 简洁风格

设置 `simple` 属性可以展示简洁风格的步骤条。

:::demo 

```vue
<template>
  <cc-steps :active="2" simple>
    <cc-step title="步骤1" />
    <cc-step title="步骤2" />
    <cc-step title="步骤3" />
  </cc-steps>
</template>
```

:::

## 自定义图标

可以在步骤条中使用自定义图标。

:::demo 

```vue
<template>
  <cc-steps :active="2">
    <cc-step title="步骤1">
      <template #icon>
        <cc-icon :icon="Edit" />
      </template>
    </cc-step>
    <cc-step title="步骤2">
      <template #icon>
        <cc-icon :icon="Upload" />
      </template>
    </cc-step>
    <cc-step title="步骤3">
      <template #icon>
        <cc-icon :icon="Check" />
      </template>
    </cc-step>
  </cc-steps>
</template>

<script setup lang="ts">
import { Edit, Upload, Check } from '@element-plus/icons-vue'
</script>
```

:::

## 垂直方向

设置 `direction` 属性为 `vertical` 可以展示垂直方向的步骤条。

:::demo 

```vue
<template>
  <cc-steps direction="vertical" :active="1">
    <cc-step title="步骤1" description="这是步骤1的描述信息" />
    <cc-step title="步骤2" description="这是步骤2的描述信息" />
    <cc-step title="步骤3" description="这是步骤3的描述信息" />
  </cc-steps>
</template>
```

:::

## 居中对齐

设置 `align-center` 属性可以让步骤条居中对齐。

:::demo 

```vue
<template>
  <cc-steps :active="1" align-center>
    <cc-step title="步骤1" description="这是一段很长很长很长的描述信息" />
    <cc-step title="步骤2" description="这是步骤2的描述信息" />
    <cc-step title="步骤3" description="这是步骤3的描述信息" />
  </cc-steps>
</template>
```

:::

## 步骤条状态

可以设置步骤条的完成状态。

:::demo 

```vue
<template>
  <cc-steps :active="2" finish-status="success">
    <cc-step title="已完成" />
    <cc-step title="进行中" />
    <cc-step title="待开始" />
  </cc-steps>

  <cc-steps :active="2" finish-status="error" style="margin-top: 20px">
    <cc-step title="已完成" />
    <cc-step title="进行中" />
    <cc-step title="待开始" />
  </cc-steps>
</template>
```

:::

## Steps Props

| 属性名 | 说明 | 类型 | 默认值 |
|--------|------|------|--------|
| active | 当前激活步骤 | `number` | `0` |
| align-center | 是否居中对齐 | `boolean` | `false` |
| active-color | 激活步骤颜色 | `string` | `-` |
| finish-status | 完成状态 | `wait` / `process` / `finish` / `error` / `success` | `finish` |
| hidden | 是否隐藏 | `boolean` | `false` |
| inline | 是否内联 | `boolean` | `false` |
| space | 每个步骤的间距 | `number` / `string` | `-` |
| direction | 步骤条方向 | `horizontal` / `vertical` | `horizontal` |
| percentage | 百分比（仅在简单模式下生效） | `number` | `0` |
| progress-offset | 进度条偏移量 | `number` | `0` |
| simple | 是否简洁风格 | `boolean` | `false` |
| transition-name | 过渡动画名称 | `string` | `-` |

## Step Props

| 属性名 | 说明 | 类型 | 默认值 |
|--------|------|------|--------|
| title | 标题 | `string` | `-` |
| description | 描述信息 | `string` | `-` |
| icon | 图标 | `string` / `Component` | `-` |
| status | 状态 | `wait` / `process` / `finish` / `error` / `success` | `-` |

## Step Slots

| 插槽名 | 说明 |
|--------|------|
| icon | 自定义图标 |
| title | 自定义标题 |
| description | 自定义描述信息 |

## Steps Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| click | 点击步骤时触发 | `(index: number) => void` |
