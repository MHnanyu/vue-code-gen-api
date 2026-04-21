# DateTimePicker 日期时间选择器

用于选择或输入日期时间。

## 基础用法

以日期时间为基本单位，选择日期和时间。

```vue
<template>
  <cc-date-time-picker
    v-model="value"
    placeholder="选择日期时间"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
</script>
```

## 带快捷选项

使用 `shortcuts` 属性设置快捷选项。

```vue
<template>
  <cc-date-time-picker
    v-model="value"
    placeholder="选择日期时间"
    :shortcuts="shortcuts"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')

const shortcuts = [
  {
    text: '今天',
    value: new Date(),
  },
  {
    text: '昨天',
    value: () => {
      const date = new Date()
      date.setTime(date.getTime() - 3600 * 1000 * 24)
      return date
    },
  },
  {
    text: '一周前',
    value: () => {
      const date = new Date()
      date.setTime(date.getTime() - 3600 * 1000 * 24 * 7)
      return date
    },
  },
]
</script>
```

## 设置默认时间

使用 `default-time` 属性设置默认时间。

```vue
<template>
  <cc-date-time-picker
    v-model="value"
    placeholder="选择日期时间"
    :default-time="defaultTime"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
const defaultTime = new Date(2000, 1, 1, 12, 0, 0)
</script>
```

## 日期时间格式

使用 `format` 指定输入框的格式。使用 `value-format` 指定绑定值的格式。

```vue
<template>
  <div class="demo-date-time-picker">
    <div class="block">
      <span class="demonstration">默认</span>
      <cc-date-time-picker
        v-model="value1"
        placeholder="选择日期时间"
      />
    </div>
    <div class="block">
      <span class="demonstration">带格式</span>
      <cc-date-time-picker
        v-model="value2"
        placeholder="选择日期时间"
        format="YYYY/MM/DD HH:mm:ss"
        value-format="YYYY-MM-DD HH:mm:ss"
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

## 日期时间范围

通过设置 `type` 属性为 `datetimerange`，选择日期时间范围。

```vue
<template>
  <div class="demo-date-time-picker">
    <div class="block">
      <span class="demonstration">默认</span>
      <cc-date-time-picker
        v-model="value1"
        type="datetimerange"
        range-separator="至"
        start-placeholder="开始日期时间"
        end-placeholder="结束日期时间"
      />
    </div>
    <div class="block">
      <span class="demonstration">带快捷选项</span>
      <cc-date-time-picker
        v-model="value2"
        type="datetimerange"
        range-separator="至"
        start-placeholder="开始日期时间"
        end-placeholder="结束日期时间"
        :shortcuts="shortcuts"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value1 = ref([])
const value2 = ref([])

const shortcuts = [
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    },
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    },
  },
  {
    text: '最近三个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
      return [start, end]
    },
  },
]
</script>
```

## 默认值

日期时间选择器会在用户未选择任何日期时间的时候显示默认日期时间。可以使用 `default-value` 来设置默认日期时间。

```vue
<template>
  <cc-date-time-picker
    v-model="value"
    placeholder="选择日期时间"
    :default-value="defaultDate"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
const defaultDate = new Date(2010, 9, 1, 12, 0, 0)
</script>
```

## 日期时间限制

通过 `disabled-date` 属性来限制用户可以选择的日期时间。

```vue
<template>
  <div class="demo-date-time-picker">
    <div class="block">
      <span class="demonstration">禁止选择今天之后的日期</span>
      <cc-date-time-picker
        v-model="value1"
        placeholder="选择日期时间"
        :disabled-date="disabledDate"
      />
    </div>
    <div class="block">
      <span class="demonstration">只能选择今天及以后的日期</span>
      <cc-date-time-picker
        v-model="value2"
        placeholder="选择日期时间"
        :disabled-date="disabledDate2"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value1 = ref('')
const value2 = ref('')

const disabledDate = (time: Date) => {
  return time.getTime() > Date.now()
}

const disabledDate2 = (time: Date) => {
  return time.getTime() < Date.now() - 8.64e7
}
</script>
```

## 禁用状态

使用 `disabled` 属性来禁用日期时间选择器。

```vue
<template>
  <cc-date-time-picker
    v-model="value"
    placeholder="选择日期时间"
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
  <cc-date-time-picker
    v-model="value"
    placeholder="选择日期时间"
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
  <div class="demo-date-time-picker">
    <cc-date-time-picker
      v-model="value1"
      placeholder="默认尺寸"
    />
    <cc-date-time-picker
      v-model="value2"
      placeholder="大尺寸"
      size="large"
    />
    <cc-date-time-picker
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

## 输入框可编辑

使用 `editable` 属性控制输入框是否可编辑。

- `editable: true` - 可以在输入框中直接输入日期时间文本
- `editable: false` - 只能通过日期时间选择器选择，不能手动输入

```vue
<template>
  <div class="demo-date-time-picker">
    <div class="block">
      <span class="demonstration">可编辑（可手动输入）</span>
      <cc-date-time-picker
        v-model="value1"
        placeholder="选择日期时间"
        editable
      />
    </div>
    <div class="block">
      <span class="demonstration">不可编辑（只能选择）</span>
      <cc-date-time-picker
        v-model="value2"
        placeholder="选择日期时间"
        :editable="false"
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

## 自定义前缀图标和清除图标

使用 `prefix-icon` 和 `clear-icon` 属性自定义前缀图标和清除图标。

```vue
<template>
  <cc-date-time-picker
    v-model="value"
    placeholder="选择日期时间"
    prefix-icon="Calendar"
    clear-icon="CircleClose"
    clearable
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
</script>
```

## 自定义内容

使用默认插槽自定义单元格内容，参数为 { type, day, date }。

```vue
<template>
  <cc-date-time-picker v-model="value" placeholder="选择日期时间">
    <template #default="{ date }">
      <div class="custom-cell">
        {{ date?.getDate() || '' }}
      </div>
    </template>
  </cc-date-time-picker>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
</script>

<style scoped>
.custom-cell {
  height: 30px;
  padding: 0;
  line-height: 30px;
}
</style>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| model-value / v-model | 绑定值 | Date / number / string / Array | — | — |
| readonly | 完全只读 | boolean | — | false |
| disabled | 禁用 | boolean | — | false |
| editable | 文本框可输入 | boolean | — | true |
| clearable | 是否显示清除按钮 | boolean | — | true |
| size | 输入框尺寸 | string | large / default / small | default |
| placeholder | 非范围选择时的占位内容 | string | — | — |
| start-placeholder | 范围选择时开始日期的占位内容 | string | — | — |
| end-placeholder | 范围选择时结束日期的占位内容 | string | — | — |
| type | 显示类型 | string | datetime / datetimerange | datetime |
| format | 显示在输入框中的格式 | string | 见日期格式 | YYYY-MM-DD HH:mm:ss |
| popper-class | DateTimePicker 下拉框的类名 | string | — | — |
| popper-options | 自定义 popper 选项 | object | — | — |
| range-separator | 选择范围时的分隔符 | string | — | '-' |
| default-value | 选择器打开时默认显示的时间 | Date / [Date, Date] | — | — |
| default-time | 范围选择时选中日期所使用的当日内具体时刻 | Date / [Date, Date] | — | — |
| value-format | 绑定值的格式 | string | 见日期格式 | — |
| id | 等价于原生 input id 属性 | string / [string, string] | — | — |
| name | 原生 name 属性 | string | — | — |
| unlink-panels | 在范围选择器里取消两个日期面板之间的联动 | boolean | — | false |
| prefix-icon | 自定义前缀图标 | string / Component | — | Date |
| clear-icon | 自定义清除图标 | string / Component | — | CircleClose |
| validate-event | 输入时是否触发表单验证 | boolean | — | true |
| disabled-date | 禁止选择的日期 | function(Date) => boolean | — | — |
| shortcuts | 设置快捷选项，需要传入数组对象 | object[{ text: string, value: Date / function }] | — | — |
| cell-class-name | 设置自定义 className | function(Date) => string | — | — |
| teleported | 是否将 date-time-picker 的下拉列表插入至 body | boolean | — | true |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| change | 用户确认选定的值时触发 | value: Date / number / string / Array |
| blur | 在组件 Input 失去焦点时触发 | (event: FocusEvent) |
| focus | 在组件 Input 获得焦点时触发 | (event: FocusEvent) |
| calendar-change | 日期选择器面板日期改变时触发 | [Date, Date] |
| panel-change | 日期选择器面板切换时触发 | (view, oldView, index) |
| visible-change | 当 DateTimePicker 的下拉列表出现/消失时触发 | (visibility: boolean) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 自定义单元格内容，参数为 { type, day, date } |
| range-separator | 自定义范围分割符内容 |

## Methods

| 方法名 | 说明 | 参数 |
|-------|------|------|
| focus | 使 input 获取焦点 | — |
| handleOpen | 打开日期时间选择器弹窗 | — |
| handleClose | 关闭日期时间选择器弹窗 | — |
