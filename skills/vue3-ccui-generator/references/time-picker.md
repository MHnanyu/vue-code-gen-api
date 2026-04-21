# TimePicker 时间选择器

用于选择时间。

## 基础用法

```vue
<template>
  <cc-time-picker
    v-model="value"
    placeholder="选择时间"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
</script>
```

## 固定时间点

提供几个固定的时间点供用户选择。

```vue
<template>
  <cc-time-picker
    v-model="value"
    placeholder="选择时间"
    :disabled-hours="disabledHours"
    :disabled-minutes="disabledMinutes"
    :disabled-seconds="disabledSeconds"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref(new Date(2016, 9, 10, 18, 40))

const makeDisabled = (hourArr: number[]) => {
  return () => {
    return hourArr
  }
}

const disabledHours = makeDisabled([2, 5, 8])
const disabledMinutes = makeDisabled([10, 20, 30])
const disabledSeconds = makeDisabled([15, 45, 55])
</script>
```

## 任意时间点

可以选择任意时间。

```vue
<template>
  <cc-time-picker
    v-model="value"
    is-range
    range-separator="至"
    start-placeholder="开始时间"
    end-placeholder="结束时间"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref([new Date(2016, 9, 10, 8, 40), new Date(2016, 9, 10, 18, 40)])
</script>
```

## 时间范围

选择时间范围。

```vue
<template>
  <cc-time-picker
    v-model="value"
    is-range
    range-separator="至"
    start-placeholder="开始时间"
    end-placeholder="结束时间"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref([new Date(2016, 9, 10, 8, 40), new Date(2016, 9, 10, 18, 40)])
</script>
```

## 带有箭头显示

在弹出窗口中有箭头显示时间。

```vue
<template>
  <cc-time-picker
    v-model="value"
    arrow-control
    placeholder="选择时间"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
</script>
```

## 时间格式

使用 `format` 指定输入框的格式。使用 `value-format` 指定绑定值的格式。

```vue
<template>
  <div class="demo-time-picker">
    <div class="block">
      <span class="demonstration">默认</span>
      <cc-time-picker
        v-model="value1"
        placeholder="选择时间"
      />
    </div>
    <div class="block">
      <span class="demonstration">带格式</span>
      <cc-time-picker
        v-model="value2"
        placeholder="选择时间"
        format="HH:mm:ss"
      />
    </div>
    <div class="block">
      <span class="demonstration">时间戳</span>
      <cc-time-picker
        v-model="value3"
        placeholder="选择时间"
        value-format="x"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value1 = ref('')
const value2 = ref('')
const value3 = ref('')
</script>
```

## 禁用状态

使用 `disabled` 属性来禁用时间选择器。

```vue
<template>
  <cc-time-picker
    v-model="value"
    placeholder="选择时间"
    disabled
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
</script>
```

## 可清空

使用 `clearable` 属性来显示清空按钮。

```vue
<template>
  <cc-time-picker
    v-model="value"
    placeholder="选择时间"
    clearable
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
</script>
```

## 尺寸

使用 `size` 属性设置尺寸。

```vue
<template>
  <div class="demo-time-picker">
    <cc-time-picker
      v-model="value1"
      placeholder="默认尺寸"
    />
    <cc-time-picker
      v-model="value2"
      placeholder="大尺寸"
      size="large"
    />
    <cc-time-picker
      v-model="value3"
      placeholder="小尺寸"
      size="small"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value1 = ref('')
const value2 = ref('')
const value3 = ref('')
</script>
```

## 自定义前缀图标和清除图标

使用 `prefix-icon` 和 `clear-icon` 属性自定义前缀图标和清除图标。

```vue
<template>
  <cc-time-picker
    v-model="value"
    placeholder="选择时间"
    prefix-icon="Clock"
    clear-icon="CircleClose"
    clearable
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
</script>
```

## 选择日期的固定时间点

通过 `disabled-hours`, `disabled-minutes`, `disabled-seconds` 属性来限制固定时间点。

```vue
<template>
  <cc-time-picker
    v-model="value"
    placeholder="选择时间"
    :disabled-hours="[1, 5, 10]"
    :disabled-minutes="[10, 30, 50]"
    :disabled-seconds="[15, 45]"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref(new Date(2016, 9, 10, 18, 40))
</script>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| model-value / v-model | 绑定值 | Date / string / number / Array | — | — |
| readonly | 完全只读 | boolean | — | false |
| disabled | 禁用 | boolean | — | false |
| editable | 文本框可输入 | boolean | — | true |
| clearable | 是否显示清除按钮 | boolean | — | true |
| size | 输入框尺寸 | string | large / default / small | default |
| placeholder | 非范围选择时的占位内容 | string | — | — |
| start-placeholder | 范围选择时开始时间的占位内容 | string | — | — |
| end-placeholder | 范围选择时结束时间的占位内容 | string | — | — |
| is-range | 是否为时间范围选择 | boolean | — | false |
| arrow-control | 是否使用箭头进行时间选择 | boolean | — | false |
| format | 显示在输入框中的格式 | string | 见时间格式 | HH:mm:ss |
| popper-class | TimePicker 下拉框的类名 | string | — | — |
| popper-options | 自定义 popper 选项 | object | — | — |
| range-separator | 选择范围时的分隔符 | string | — | '-' |
| default-value | 选择器打开时默认显示的时间 | Date / [Date, Date] | — | — |
| value-format | 绑定值的格式 | string | 见时间格式 | — |
| id | 等价于原生 input id 属性 | string / [string, string] | — | — |
| name | 原生 name 属性 | string | — | — |
| prefix-icon | 自定义前缀图标 | string / Component | — | Clock |
| clear-icon | 自定义清除图标 | string / Component | — | CircleClose |
| validate-event | 输入时是否触发表单验证 | boolean | — | true |
| disabled-hours | 禁止选择的小时 | function / array | — | — |
| disabled-minutes | 禁止选择的分钟 | function / array | — | — |
| disabled-seconds | 禁止选择的秒数 | function / array | — | — |
| teleported | 是否将 time-picker 的下拉列表插入至 body | boolean | — | true |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| change | 用户确认选定的值时触发 | value: Date / string / number / Array |
| blur | 在组件 Input 失去焦点时触发 | (event: FocusEvent) |
| focus | 在组件 Input 获得焦点时触发 | (event: FocusEvent) |
| visible-change | 当 TimePicker 的下拉列表出现/消失时触发 | (visibility: boolean) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 自定义单元格内容 |

## Methods

| 方法名 | 说明 | 参数 |
|-------|------|------|
| focus | 使 input 获取焦点 | — |
| handleOpen | 打开时间选择器弹窗 | — |
| handleClose | 关闭时间选择器弹窗 | — |
