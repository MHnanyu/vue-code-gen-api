# Tag 标签

用于标记和选择。

## 基础用法

由 `type` 属性来选择标签的类型。

```vue
<template>
  <cc-tag>标签</cc-tag>
  <cc-tag type="primary">主要标签</cc-tag>
  <cc-tag type="success">成功标签</cc-tag>
  <cc-tag type="warning">警告标签</cc-tag>
  <cc-tag type="danger">危险标签</cc-tag>
  <cc-tag type="info">信息标签</cc-tag>
</template>
```

## 可移除标签

设置 `closable` 属性可以定义一个可关闭的标签。

```vue
<template>
  <cc-tag closable>标签一</cc-tag>
  <cc-tag type="primary" closable>标签二</cc-tag>
  <cc-tag type="success" closable>标签三</cc-tag>
  <cc-tag type="warning" closable>标签四</cc-tag>
  <cc-tag type="danger" closable>标签五</cc-tag>
</template>
```

## 动态编辑标签

动态编辑标签可以通过点击关闭按钮和 Input 组件来实现。

```vue
<template>
  <cc-tag
    v-for="tag in dynamicTags"
    :key="tag"
    closable
    :type="tagTypes[tag % tagTypes.length]"
    @close="handleCloseTag(tag)"
  >
    {{ tag }}
  </cc-tag>
  <cc-input
    v-if="inputVisible"
    ref="InputRef"
    v-model="inputValue"
    class="input-new-tag"
    size="small"
    @keyup.enter="handleInputConfirm"
    @blur="handleInputConfirm"
  />
  <cc-button v-else class="button-new-tag" size="small" @click="showInput">+ New Tag</cc-button>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'

const dynamicTags = ref(['标签一', '标签二', '标签三'])
const tagTypes = ref(['primary', 'success', 'warning', 'danger', 'info'])
const inputVisible = ref(false)
const inputValue = ref('')
const InputRef = ref<HTMLInputElement>(null)

const handleCloseTag = (tag: string) => {
  dynamicTagsTags.value.splice(dynamicTags.value.indexOf(tag), 1)
}

const showInput = () => {
  inputVisible.value = true
  nextTick(() => {
    InputRef.value?.focus()
  })
}

const handleInputConfirm = () => {
  if (inputValue.value) {
    dynamicTags.value.push(inputValue.value)
  }
  inputVisible.value = false
  inputValue.value = ''
}
</script>

<style scoped>
.button-new-tag {
  margin-left: 10px;
  height: 32px;
  line-height: 30px;
  padding-top: 0;
  padding-bottom: 0;
}

.input-new-tag {
  width: 90px;
  margin-left: 10px;
  vertical-align: bottom;
}
</style>
```

## 标签尺寸

设置 `size` 属性来选择标签的尺寸。

```vue
<template>
  <cc-tag>默认标签</cc-tag>
  <cc-tag size="large">大型标签</cc-tag>
  <cc-tag size="small">小型标签</cc-tag>
</template>
```

## 标签主题

设置 `effect` 属性来选择标签的主题。

```vue
<template>
  <div class="tag-group">
    <span class="tag-group-title">Light</span>
    <cc-tag effect="light">标签</cc-tag>
    <cc-tag effect="light" type="primary">主要标签</cc-tag>
    <cc-tag effect="light" type="success">成功标签</cc-tag>
    <cc-tag effect="light" type="warning">警告标签</cc-tag>
    <cc-tag effect="light" type="danger">危险标签</cc-tag>
    <cc-tag effect="light" type="info">信息标签</cc-tag>
  </div>
  <div class="tag-group">
    <span class="tag-group-title">Dark</span>
    <cc-tag effect="dark">标签</cc-tag>
    <cc-tag effect="dark" type="primary">主要标签</cc-tag>
    <cc-tag effect="dark" type="success">成功标签</cc-tag>
    <cc-tag effect="dark" type="warning">警告标签</cc-tag>
    <cc-tag effect="dark" type="danger">危险标签</cc-tag>
    <cc-tag effect="dark" type="info">信息标签</cc-tag>
  </div>
  <div class="tag-group">
    <span class="tag-group-title">Plain</span>
    <cc-tag effect="plain">标签</cc-tag>
    <cc-tag effect="plain" type="primary">主要标签</cc-tag>
    <cc-tag effect="plain" type="success">成功标签</cc-tag>
    <cc-tag effect="plain" type="warning">警告标签</cc-tag>
    <cc-tag effect="plain" type="danger">危险标签</cc-tag>
    <cc-tag effect="plain" type="info">信息标签</cc-tag>
  </div>
</template>

<style scoped>
.tag-group {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.tag-group-title {
  font-weight: bold;
  margin-right: 10px;
}
</style>
```

## 圆角标签

设置 `round` 属性来选择圆角标签。

```vue
<template>
  <cc-tag round>标签</cc-tag>
  <cc-tag type="primary" round>主要标签</cc-tag>
  <cc-tag type="success" round>成功标签</cc-tag>
  <cc-tag type="warning" round>警告标签</cc-tag>
  <cc-tag type="danger" round>危险标签</cc-tag>
  <cc-tag type="info" round>信息标签</cc-tag>
</template>
```

## 边框标签

设置 `hit` 属性来选择有边框的标签。

```vue
<template>
  <cc-tag hit>标签</cc-tag>
  <cc-tag type="primary" hit>主要标签</cc-tag>
  <cc-tag type="success" hit>成功标签</cc-tag>
  <cc-tag type="warning" hit>警告标签</cc-tag>
  <cc-tag type="danger" hit>危险标签</cc-tag>
  <cc-tag type="info" hit>信息标签</cc-tag>
</template>
```

## 自定义颜色

使用 `color` 属性来自定义标签的背景色。

```vue
<template>
  <cc-tag color="#626aef">标签</cc-tag>
  <cc-tag color="#67c23a">成功标签</cc-tag>
  <cc-tag color="#e6a23c">警告标签</cc-tag>
  <cc-tag color="#f56c6c">危险标签</cc-tag>
  <cc-tag color="#909399">信息标签</cc-tag>
</template>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| type | 类型 | string | primary / success / warning / danger / info | — |
| closable | 是否可关闭 | boolean | — | false |
| disable-transitions | 是否禁用渐变动画 | boolean | — | false |
| hit | 是否有边框描边 | boolean | — | false |
| color | 背景色 | string | — | — |
| size | 尺寸 | string | large / default / small | default |
| effect | 主题 | string | light / dark / plain | light |
| round | 是否圆角 | boolean | — | false |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|---------|
| close | 关闭标签时触发 | (event: Event) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 标签内容 |
