# Checkbox 多选框

多选框组件，用于在一组选项中进行多项选择。

## 基础用法

单独使用可以表示两种状态之间的切换，写在标签中的内容为 checkbox 按钮后的介绍。

```vue
<template>
  <cc-checkbox v-model="checked">选项</cc-checkbox>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const checked = ref(true)
</script>
```

## 禁用状态

通过 `disabled` 属性设置是否禁用多选框。

```vue
<template>
  <cc-checkbox v-model="checked1" disabled>禁用状态（选中）</cc-checkbox>
  <cc-checkbox v-model="checked2" disabled>禁用状态（未选中）</cc-checkbox>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const checked1 = ref(true)
const checked2 = ref(false)
</script>
```

## 多选框组

适用于多个勾选框绑定到同一个数组的情景，通过是否勾选来表示这一组选项中选中的项。

```vue
<template>
  <cc-checkbox-group v-model="checkList">
    <cc-checkbox label="Option A" />
    <cc-checkbox label="Option B" />
    <cc-checkbox label="Option C" />
    <cc-checkbox label="Option D" disabled />
  </cc-checkbox-group>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const checkList = ref(['Option A', 'Option B'])
</script>
```

## 中间状态

`indeterminate` 属性用以表示 checkbox 的不确定状态，一般用于实现全选的效果。

```vue
<template>
  <cc-checkbox
    v-model="checkAll"
    :indeterminate="isIndeterminate"
    @change="handleCheckAllChange"
  >
    全选
  </cc-checkbox>
  <cc-divider />
  <cc-checkbox-group v-model="checkedCities" @change="handleCheckedCitiesChange">
    <cc-checkbox v-for="city in cities" :key="city" :label="city">
      {{ city }}
    </cc-checkbox>
  </cc-checkbox-group>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const checkAll = ref(false)
const isIndeterminate = ref(true)
const cities = ['北京', '上海', '广州', '深圳']
const checkedCities = ref(['上海', '深圳'])

const handleCheckAllChange = (val: boolean) => {
  checkedCities.value = val ? cities : []
  isIndeterminate.value = false
}

const handleCheckedCitiesChange = (value: string[]) => {
  const checkedCount = value.length
  checkAll.value = checkedCount === cities.length
  isIndeterminate.value = checkedCount > 0 && checkedCount < cities.length
}
</script>
```

## 可选项目数量限制

使用 `min` 和 `max` 属性能够限制可以被勾选的项目的数量。

```vue
<template>
  <cc-checkbox-group v-model="checkedCities1" :min="1" :max="3">
    <cc-checkbox v-for="city in cities" :key="city" :label="city">
      {{ city }}
    </cc-checkbox>
  </cc-checkbox-group>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const cities = ['北京', '上海', '广州', '深圳']
const checkedCities1 = ref(['上海', '深圳'])
</script>
```

## 按钮样式

按钮样式的多选框。

```vue
<template>
  <cc-checkbox-group v-model="checkboxGroup1">
    <cc-checkbox-button v-for="city in cities" :key="city" :label="city">
      {{ city }}
    </cc-checkbox-button>
  </cc-checkbox-group>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const cities = ['北京', '上海', '广州', '深圳']
const checkboxGroup1 = ref(['上海'])
</script>
```

## 带有边框

设置 `border` 属性可以渲染为带有边框的多选框。

```vue
<template>
  <cc-checkbox-group v-model="checkboxGroup2">
    <cc-checkbox v-for="city in cities" :key="city" :label="city" border>
      {{ city }}
    </cc-checkbox>
  </cc-checkbox-group>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const cities = ['北京', '上海', '广州', '深圳']
const checkboxGroup2 = ref(['上海'])
</script>
```

## Checkbox Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| model-value / v-model | 绑定值 | string / number / boolean | — | — |
| label | 选中状态的值（只有在 `checkbox-group` 或者绑定对象类型为 `array` 时有效） | string / number / boolean | — | — |
| true-label | 选中时的值 | string / number | — | — |
| false-label | 没有选中时的值 | string / number | — | — |
| disabled | 是否禁用 | boolean | — | false |
| border | 是否显示边框 | boolean | — | false |
| size | Checkbox 的尺寸 | string | large / default / small | — |
| name | 原生 name 属性 | string | — | — |
| checked | 当前是否勾选（只有在 `v-model` 或 `model-value` 未绑定时有效） | boolean | — | false |
| indeterminate | 设置不确定状态，仅负责样式控制 | boolean | — | false |
| validate-event | 输入时是否触发表单验证 | boolean | — | true |
| tabindex | 输入框的 tabindex | string / number | — | — |
| id | 原生 id 属性 | string | — | — |
| controls | 原生属性，当与另一个控件组合使用时有效 | string | — | — |

## Checkbox Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| change | 当绑定值变化时触发 | (value: string \| number \| boolean) |

## Checkbox Slots

| 插槽名 | 说明 |
|-------|------|
| default | 默认插槽，内容显示在多选框后面 |

## CheckboxGroup Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| model-value / v-model | 绑定值 | array | — | [] |
| size | 多选框组尺寸 | string | large / default / small | — |
| disabled | 是否禁用 | boolean | — | false |
| min | 可被勾选的 checkbox 的最小数量 | number | — | — |
| max | 可被勾选的 checkbox 的最大数量 | number | — | — |
| label | Tabindex 属性 | string | — | — |
| validate-event | 输入时是否触发表单验证 | boolean | — | true |
| tag | 分组标签 | string | — | — |

## CheckboxGroup Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| change | 当绑定值变化时触发 | (value: array) |

## CheckboxGroup Slots

| 插槽名 | 说明 |
|-------|------|
| default | 自定义默认内容 |

## CheckboxButton Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| label | 选中状态的值（只有在 `checkbox-group` 或者绑定对象类型为 `array` 时有效） | string / number / boolean | — | — |
| true-label | 选中时的值 | string / number | — | — |
| false-label | 没有选中时的值 | string / number | — | — |
| disabled | 是否禁用 | boolean | — | false |
| name | 原生 name 属性 | string | — | — |
| checked | 当前是否勾选 | boolean | — | false |

## CheckboxButton Slots

| 插槽名 | 说明 |
|-------|------|
| default | 默认插槽，内容显示在多选框后面 |
