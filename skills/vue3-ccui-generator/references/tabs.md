# Tabs 标签页

分隔内容上有关联但不属于同一层级的内容。

## 基础用法

适用场景：适用于需要切换不同内容模块的场景。

:::demo 基础的标签页使用方法。

```vue
<template>
  <cc-tabs v-model="active">
    <cc-tab-pane label="用户管理" name="first">用户管理内容</cc-tab-pane>
    <cc-tab-pane label="配置管理" name="second">配置管理内容</cc-tab-pane>
    <cc-tab-pane label="角色管理" name="third">角色管理内容</cc-tab-pane>
  </cc-tabs>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const active = ref('first')
</script>
```

:::

## 卡片风格

设置 type 为 card 可以显示为卡片风格。

:::demo 

```vue
<template>
  <cc-tabs v-model="active" type="card">
    <cc-tab-pane label="用户管理" name="first">用户管理内容</cc-tab-pane>
    <cc-tab-pane label="配置管理" name="second">配置管理内容</cc-tab-pane>
    <cc-tab-pane label="角色管理" name="third">角色管理内容</cc-tab-pane>
  </cc-tabs>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const active = ref('first')
</script>
```

:::

## 边框卡片风格

设置 type 为 border-card 可以显示为边框卡片风格。

:::demo 

```vue
<template>
  <cc-tabs v-model="active" type="border-card">
    <cc-tab-pane label="用户管理" name="first">用户管理内容</cc-tab-pane>
    <cc-tab-pane label="配置管理" name="second">配置管理内容</cc-tab-pane>
    <cc-tab-pane label="角色管理" name="third">角色管理内容</cc-tab-pane>
  </cc-tabs>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const active = ref('first')
</script>
```

:::

## 自定义标签

可以通过设置 label 添加自定义标签内容。

:::demo 

```vue
<template>
  <cc-tabs v-model="active">
    <cc-tab-pane name="first">
      <template #label>
        <span><el-icon><User /></el-icon> 用户管理</span>
      </template>
      用户管理内容
    </cc-tab-pane>
    <cc-tab-pane name="second">
      <template #label>
        <span><el-icon><Setting /></el-icon> 配置管理</span>
      </template>
      配置管理内容
    </cc-tab-pane>
    <cc-tab-pane name="third">
      <template #label>
        <span><el-icon><UserFilled /></el-icon> 角色管理</span>
      </template>
      角色管理内容
    </cc-tab-pane>
  </cc-tabs>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { User, Setting, UserFilled } from '@element-plus/icons-vue'

const active = ref('first')
</script>
```

:::

## 禁用状态

设置 disabled 属性来禁用标签页。

:::demo 

```vue
<template>
  <cc-tabs v-model="active">
    <cc-tab-pane label="用户管理" name="first">用户管理内容</cc-tab-pane>
    <cc-tab-pane label="配置管理" name="second" disabled>配置管理内容</cc-tab-pane>
    <cc-tab-pane label="角色管理" name="third">角色管理内容</cc-tab-pane>
  </cc-tabs>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const active = ref('first')
</script>
```

:::

## 可关闭

设置 closable 属性可以关闭标签页。

:::demo 

```vue
<template>
  <cc-tabs v-model="active" type="card" editable @tab-remove="handleTabRemove">
    <cc-tab-pane v-for="item in tabList" :key="item.name" :label="item.title" :name="item.name">
      {{ item.content }}
    </cc-tab-pane>
  </cc-tabs>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const active = ref('first')

const tabList = ref([
  { title: '用户管理', name: 'first', content: '用户管理内容' },
  { title: '配置管理', name: 'second', content: '配置管理内容' },
  { title: '角色管理', name: 'third', content: '角色管理内容' }
])

const handleTabRemove = (tabName: string | number) => {
  tabList.value = tabList.value.filter(item => item.name !== tabName)
}
</script>
```

:::

## 动态添加标签页

可以动态添加和关闭标签页。

:::demo 

```vue
<template>
  <cc-tabs v-model="active" type="card" editable addable @tab-add="handleTabAdd" @tab-remove="handleTabRemove">
    <cc-tab-pane v-for="item in tabList" :key="item.name" :label="item.title" :name="item.name">
      {{ item.content }}
    </cc-tab-pane>
  </cc-tabs>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const active = ref('first')

const tabList = ref([
  { title: '用户管理', name: 'first', content: '用户管理内容' },
  { title: '配置管理', name: 'second', content: '配置管理内容' },
  { title: '角色管理', name: 'third', content: '角色管理内容' }
])

const handleTabRemove = (tabName: string | number) => {
  tabList.value = tabList.value.filter(item => item.name !== tabName)
}

const handleTabAdd = () => {
  const newTabName = `${tabList.value.length + 1}`
  tabList.value.push({
    title: `新标签${newTabName}`,
    name: newTabName,
    content: `新标签${newTabName}内容`
  })
}
</script>
```

:::

## 延迟加载

设置 lazy 属性可以延迟加载标签页内容。

:::demo 

```vue
<template>
  <cc-tabs v-model="active" type="border-card">
    <cc-tab-pane label="用户管理" name="first">用户管理内容</cc-tab-pane>
    <cc-tab-pane label="配置管理" name="second" lazy>配置管理内容（延迟加载）</cc-tab-pane>
    <cc-tab-pane label="角色管理" name="third" lazy>角色管理内容（延迟加载）</cc-tab-pane>
  </cc-tabs>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const active = ref('first')
</script>
```

:::

## 动态效果

可以通过 effect 属性设置切换动画效果。

:::demo 

```vue
<template>
  <div style="margin-bottom: 20px">
    <el-radio-group v-model="effect" size="small">
      <el-radio-button value="light">light</el-radio-button>
      <el-radio-button value="dark">dark</el-radio-button>
    </el-radio-group>
  </div>
  <cc-tabs v-model="active" :effect="effect" type="border-card">
    <cc-tab-pane label="用户管理" name="first">用户管理内容</cc-tab-pane>
    <cc-tab-pane label="配置管理" name="second">配置管理内容</cc-tab-pane>
    <cc-tab-pane label="角色管理" name="third">角色管理内容</cc-tab-pane>
  </cc-tabs>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const active = ref('first')
const effect = ref('light')
</script>
```

:::

## Tabs Props

| 属性名 | 说明 | 类型 | 默认值 |
|--------|------|------|--------|
| modelValue | 绑定值，选中选项卡的 name | `string` / `number` | `-` |
| type | 风格类型 | `card` / `border-card` / `''` | `-` |
| addable | 是否可添加 | `boolean` | `false` |
| editable | 是否可编辑 | `boolean` | `false` |
| effect | 动态效果 | `light` / `dark` | `light` |
| card | 卡片风格 | `boolean` | `false` |
| lazy | 延迟加载 | `boolean` | `false` |
| before-leave | 切换标签前的回调函数 | `(newTabName: string \| number, oldTabName: string \| number) => void \| boolean \| Promise<void \| boolean>` | `-` |
| expand-width | 展开宽度 | `number` / `string` | `-` |

## TabPane Props

| 属性名 | 说明 | 类型 | 默认值 |
|--------|------|------|--------|
| label | 标签标题 | `string` | `-` |
| name | 标签标识 | `string` / `number` | `-` |
| closable | 是否可关闭 | `boolean` | `false` |
| disabled | 是否禁用 | `boolean` | `false` |
| lazy | 是否延迟加载 | `boolean` | `false` |

## TabPane Slots

| 插槽名 | 说明 |
|--------|------|
| default | 标签页内容 |
| label | 自定义标签内容 |

## Tabs Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| tab-add | 点击添加标签按钮时触发 | `-` |
| tab-remove | 点击关闭标签按钮时触发 | `(tabName: string \| number)` |
| update:model-value | 绑定值变化时触发 | `(value: string \| number)` |
