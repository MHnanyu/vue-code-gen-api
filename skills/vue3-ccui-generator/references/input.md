# Input 输入框

通过鼠标或键盘输入内容。

## 基础用法

```vue
<template>
  <cc-input v-model="input" placeholder="请输入内容" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const input = ref('')
</script>
```

## 禁用状态

使用 `disabled` 属性来禁用输入框。

```vue
<template>
  <cc-input v-model="input" disabled placeholder="禁用状态" />
</template>
```

## 可清空

使用 `clearable` 属性来显示清空按钮。

```vue
<template>
  <cc-input v-model="input" clearable placeholder="可清空" />
</template>
```

## 密码输入框

使用 `show-password` 属性来显示切换密码可见性的按钮。

```vue
<template>
  <cc-input v-model="password" show-password placeholder="请输入密码" />
</template>
```

## 带图标的输入框

使用 `prefix-icon` 和 `suffix-icon` 属性来添加图标，也可以使用插槽自定义前后置内容。

```vue
<template>
  <cc-input v-model="input1" placeholder="请输入内容" :prefix-icon="Search" />
  <cc-input v-model="input2" placeholder="请输入内容" :suffix-icon="Search" />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'

const input1 = ref('')
const input2 = ref('')
</script>
```

使用插槽自定义内容：

```vue
<template>
  <cc-input v-model="input" placeholder="请输入内容">
    <template #prefix>
      <span>🔍</span>
    </template>
    <template #suffix>
      <span>🔍</span>
    </template>
  </cc-input>
</template>
```

## 复合型输入框

使用 `prepend` 和 `append` 插槽来添加前置或后置内容。

```vue
<template>
  <cc-input v-model="input1" placeholder="请输入内容">
    <template #prepend>Http://</template>
  </cc-input>
  <cc-input v-model="input2" placeholder="请输入内容">
    <template #append>.com</template>
  </cc-input>
  <cc-input v-model="input3" placeholder="请输入内容">
    <template #prepend>
      <cc-select v-model="select" style="width: 100px">
        <cc-option label="餐厅名" value="1" />
        <cc-option label="订单号" value="2" />
        <cc-option label="用户电话" value="3" />
      </cc-select>
    </template>
    <template #append>
      <cc-button icon="Search" />
    </template>
  </cc-input>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const input1 = ref('')
const input2 = ref('')
const input3 = ref('')
const select = ref('1')
</script>
```

## 文本域

设置 `type="textarea"` 来使用文本域。

```vue
<template>
  <cc-input v-model="textarea" type="textarea" placeholder="请输入内容" />
</template>
```

## 自适应文本域

设置 `autosize` 属性来使文本域自适应高度。

```vue
<template>
  <cc-input v-model="textarea1" type="textarea" :autosize="true" placeholder="自适应高度" />
  <cc-input v-model="textarea2" type="textarea" :autosize="{ minRows: 2, maxRows: 6 }" placeholder="限制最小和最大行数" />
</template>
```

## 输入长度限制

使用 `maxlength` 属性限制输入长度，配合 `show-word-limit` 显示字数统计。

```vue
<template>
  <cc-input v-model="input" :maxlength="10" show-word-limit placeholder="最多输入10个字符" />
  <cc-input v-model="textarea" type="textarea" :maxlength="30" show-word-limit placeholder="最多输入30个字符" />
</template>
```

## 尺寸

使用 `size` 属性设置输入框尺寸。

```vue
<template>
  <cc-input v-model="input1" size="large" placeholder="large 尺寸" />
  <cc-input v-model="input2" placeholder="默认尺寸" />
  <cc-input v-model="input3" size="small" placeholder="small 尺寸" />
</template>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| type | 类型 | string | text / textarea / password / number / ... | text |
| model-value / v-model | 绑定值 | string / number | — | — |
| maxlength | 原生属性，最大输入长度 | number / string | — | — |
| minlength | 原生属性，最小输入长度 | number / string | — | — |
| show-word-limit | 是否显示输入字数统计 | boolean | — | false |
| placeholder | 输入框占位文本 | string | — | — |
| clearable | 是否可清空 | boolean | — | false |
| show-password | 是否显示切换密码图标 | boolean | — | false |
| disabled | 是否禁用 | boolean | — | false |
| size | 输入框尺寸 | string | large / default / small | — |
| prefix-icon | 自定义前缀图标 | string / Component | — | — |
| suffix-icon | 自定义后缀图标 | string / Component | — | — |
| rows | 文本域内部可视高度 | number | — | 2 |
| autosize | 自适应内容高度，只对 textarea 类型有效 | boolean / object | — | false |
| autocomplete | 原生属性 | string | — | off |
| name | 原生属性 | string | — | — |
| readonly | 原生属性，是否只读 | boolean | — | false |
| max | 原生属性，设置最大值 | — | — | — |
| min | 原生属性，设置最小值 | — | — | — |
| step | 原生属性，设置输入字段的合法数字间隔 | — | — | — |
| resize | 控制是否能被用户缩放 | string | none / both / horizontal / vertical | — |
| autofocus | 原生属性，自动获取焦点 | boolean | — | false |
| form | 原生属性 | string | — | — |
| label | 输入框关联的 label 文字 | string | — | — |
| tabindex | 输入框的 tabindex | number / string | — | — |
| validate-event | 输入时是否触发表单的校验 | boolean | — | true |
| input-style | input 元素或 textarea 元素的 style | string / object | — | — |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| blur | 在 Input 失去焦点时触发 | (event: FocusEvent) |
| focus | 在 Input 获得焦点时触发 | (event: FocusEvent) |
| change | 在 Input 值改变时触发 | (value: string / number) |
| input | 在 Input 值改变时触发 | (value: string / number) |
| clear | 在点击由 clearable 属性生成的清空按钮时触发 | — |
| mouseleave | 鼠标离开 Input 时触发 | (event: MouseEvent) |
| mouseenter | 鼠标进入 Input 时触发 | (event: MouseEvent) |
| keydown | 原生 keydown 事件 | (event: KeyboardEvent) |
| keyup | 原生 keyup 事件 | (event: KeyboardEvent) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| prefix | 输入框头部内容 |
| suffix | 输入框尾部内容 |
| prepend | 输入框前置内容 |
| append | 输入框后置内容 |

## Methods

| 方法名 | 说明 | 参数 |
|------|------|------|
| focus | 使 input 获取焦点 | — |
| blur | 使 input 失去焦点 | — |
| select | 选中 input 中的文字 | — |
