# Mention 提及

用于输入@提及的输入框组件。

## 基础用法

```vue
<template>
  <cc-mention v-model="value" :options="options" placeholder="请输入@提及" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
const options = [
  { value: 'alice', label: 'Alice' },
  { value: 'bob', label: 'Bob' },
  { value: 'charlie', label: 'Charlie' }
]
</script>
```

## 自定义触发字符

使用 `prefix` 属性自定义触发提及的字符。

```vue
<template>
  <cc-mention v-model="value" :options="options" prefix="#" placeholder="输入#触发提及" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
const options = [
  { value: 'tag1', label: '标签1' },
  { value: 'tag2', label: '标签2' },
  { value: 'tag3', label: '标签3' }
]
</script>
```

## 多触发字符

使用 `prefix` 属性设置多个触发字符。

```vue
<template>
  <cc-mention v-model="value" :options="options" :prefix="['@', '#']" placeholder="输入@或#触发提及" />
</template>
```

## 自定义选项渲染

使用默认插槽自定义选项的渲染。

```vue
<template>
  <cc-mention v-model="value" :options="options" placeholder="请输入@提及">
    <template #default="{ option }">
      <div class="custom-option">
        <span class="name">{{ option.label }}</span>
        <span class="value">@{{ option.value }}</span>
      </div>
    </template>
  </cc-mention>
</template>
```

## 分组选项

使用 `label` 属性对选项进行分组。

```vue
<template>
  <cc-mention v-model="value" :options="options" placeholder="请输入@提及" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
const options = [
  { value: 'alice', label: 'Alice', group: 'Team A' },
  { value: 'bob', label: 'Bob', group: 'Team A' },
  { value: 'charlie', label: 'Charlie', group: 'Team B' },
  { value: 'david', label: 'David', group: 'Team B' }
]
</script>
```

## 禁用状态

使用 `disabled` 属性来禁用提及输入框。

```vue
<template>
  <cc-mention v-model="value" :options="options" disabled placeholder="禁用状态" />
</template>
```

## 可清空

使用 `clearable` 属性来显示清空按钮。

```vue
<template>
  <cc-mention v-model="value" :options="options" clearable placeholder="可清空" />
</template>
```

## 不同尺寸

使用 `size` 属性设置输入框尺寸。

```vue
<template>
  <cc-mention v-model="value1" :options="options" size="large" placeholder="large 尺寸" />
  <cc-mention v-model="value2" :options="options" placeholder="默认尺寸" />
  <cc-mention v-model="value3" :options="options" size="small" placeholder="small 尺寸" />
</template>
```

## 前缀和后缀

使用 `prefix` 和 `suffix` 插槽添加前缀和后缀内容。

```vue
<template>
  <cc-mention v-model="value" :options="options" placeholder="请输入@提及">
    <template #prefix>提及:</template>
    <template #suffix>人</template>
  </cc-mention>
</template>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| model-value / v-model | 绑定值 | string | — | — |
| options | 选项数据源 | array | — | [] |
| prefix | 触发字符 | string / array | — | @ |
| split | 设置分割字符 | string | — | ' ' |
| filter | 自定义筛选方法 | function | — | — |
| placement | 下拉框位置 | string | top / top-start / bottom / bottom-start | bottom-start |
| popper-class | 下拉框自定义类名 | string | — | — |
| popper-options | 下拉框Popper.js参数 | object | — | — |
| disabled | 是否禁用 | boolean | — | false |
| clearable | 是否可清空 | boolean | — | false |
| size | 输入框尺寸 | string | large / default / small | — |
| placeholder | 输入框占位文本 | string | — | — |
| maxlength | 输入框最大长度 | number / string | — | — |
| minlength | 输入框最小长度 | number / string | — | — |
| readonly | 原生属性，是否只读 | boolean | — | false |
| autocomplete | 原生属性 | string | — | off |
| name | 原生属性 | string | — | — |
| label | 输入框关联的 label 文字 | string | — | — |
| tabindex | 输入框的 tabindex | number / string | — | — |
| validate-event | 输入时是否触发表单的校验 | boolean | — | true |

## Options Attributes

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| value | 选项的值 | string / number | — | — |
| label | 选项的标签 | string | — | — |
| disabled | 是否禁用该选项 | boolean | — | false |
| group | 选项分组 | string | — | — |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| change | 在值改变时触发 | (value: string) |
| input | 在输入时触发 | (value: string) |
| blur | 在组件失去焦点时触发 | (event: FocusEvent) |
| focus | 在组件获得焦点时触发 | (event: FocusEvent) |
| clear | 在点击清空按钮时触发 | — |
| select | 在选择选项时触发 | (option: object) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 自定义选项内容，参数为 { option, index } |
| prefix | 输入框头部内容 |
| suffix | 输入框尾部内容 |
| header | 下拉框头部内容 |
| footer | 下拉框尾部内容 |

## Methods

| 方法名 | 说明 | 参数 |
|------|------|------|
| focus | 使 input 获取焦点 | — |
| blur | 使 input 失去焦点 | — |
| select | 选中 input 中的文字 | — |
