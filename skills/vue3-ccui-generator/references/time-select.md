# TimeSelect 时间选择

用于选择固定时间点。

## 基础用法

```vue
<template>
  <cc-time-select
    v-model="value"
    placeholder="选择时间"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
</script>
```

## 时间间隔

使用 `step` 属性设置时间间隔。

```vue
<template>
  <cc-time-select
    v-model="value"
    placeholder="选择时间"
    :step="'00:30'"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
</script>
```

## 起始和结束时间

使用 `start` 和 `end` 属性设置起始和结束时间。

```vue
<template>
  <cc-time-select
    v-model="value"
    placeholder="选择时间"
    start="08:30"
    end="18:30"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
</script>
```

## 禁用状态

使用 `disabled` 属性来禁用时间选择。

```vue
<template>
  <cc-time-select
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
  <cc-time-select
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
  <div class="demo-time-select">
    <cc-time-select
      v-model="value1"
      placeholder="默认尺寸"
    />
    <cc-time-select
      v-model="value2"
      placeholder="大尺寸"
      size="large"
    />
    <cc-time-select
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

## 时间格式

使用 `format` 指定输入框的格式。使用 `value-format` 指定绑定值的格式。

```vue
<template>
  <div class="demo-time-select">
    <div class="block">
      <span class="demonstration">默认</span>
      <cc-time-select
        v-model="value1"
        placeholder="选择时间"
      />
    </div>
    <div class="block">
      <span class="demonstration">带格式</span>
      <cc-time-select
        v-model="value2"
        placeholder="选择时间"
        format="HH:mm"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value1 = ref('')
const value2 = ref('')
</script>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| model-value / v-model | 绑定值 | string | — | — |
| readonly | 完全只读 | boolean | — | false |
| disabled | 禁用 | boolean | — | false |
| editable | 文本框可输入 | boolean | — | true |
| clearable | 是否显示清除按钮 | boolean | — | true |
| size | 输入框尺寸 | string | large / default / small | default |
| placeholder | 占位内容 | string | — | — |
| format | 显示在输入框中的格式 | string | 见时间格式 | HH:mm:ss |
| value-format | 绑定值的格式 | string | 见时间格式 | — |
| start | 起始时间 | string | — | 09:00 |
| end | 结束时间 | string | — | 18:00 |
| step | 时间间隔 | string | — | 00:30 |
| min-time | 早于该时间的时间将被禁用 | string | — | — |
| max-time | 晚于该时间的时间将被禁用 | string | — | — |
| name | 原生 name 属性 | string | — | — |
| prefix-icon | 自定义前缀图标 | string / Component | — | Clock |
| clear-icon | 自定义清除图标 | string / Component | — | CircleClose |
| teleported | 是否将 time-select 的下拉列表插入至 body | boolean | — | true |
| validate-event | 输入时是否触发表单验证 | boolean | — | true |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| change | 用户确认选定的值时触发 | value: string |
| blur | 在组件 Input 失去焦点时触发 | (event: FocusEvent) |
| focus | 在组件 Input 获得焦点时触发 | (event: FocusEvent) |
| visible-change | 当 TimeSelect 的下拉列表出现/消失时触发 | (visibility: boolean) |

## Methods

| 方法名 | 说明 | 参数 |
|-------|------|------|
| focus | 使 input 获取焦点 | — |
