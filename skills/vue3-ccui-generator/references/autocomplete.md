# Autocomplete 自动补全输入框

获得输入建议的自动补全输入框。

## 基础用法

使用 `fetch-suggestions` 属性来获取输入建议。

```vue
<template>
  <cc-autocomplete
    v-model="value"
    :fetch-suggestions="querySearch"
    placeholder="请输入内容"
    @select="handleSelect"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
const restaurants = ref([
  { value: '三全鲜食（北新泾店）', address: '长宁区新渔路144号' },
  { value: 'Hot honey 首尔炸鸡（仙霞路）', address: '上海市长宁区淞虹路661号' },
  { value: '新旺角茶餐厅', address: '上海市普陀区真北路988号创展大厦6层' }
])

const querySearch = (queryString: string, cb: any) => {
  const results = queryString
    ? restaurants.value.filter(item => item.value.toLowerCase().includes(queryString.toLowerCase()))
    : restaurants.value
  cb(results)
}

const handleSelect = (item: any) => {
  console.log(item)
}
</script>
```

## 禁用状态

使用 `disabled` 属性来禁用输入框。

```vue
<template>
  <cc-autocomplete v-model="value" disabled placeholder="禁用状态" />
</template>
```

## 可清空

使用 `clearable` 属性来显示清空按钮。

```vue
<template>
  <cc-autocomplete v-model="value" clearable placeholder="可清空" />
</template>
```

## 自定义模板

使用默认插槽自定义建议项的模板。

```vue
<template>
  <cc-autocomplete v-model="value" :fetch-suggestions="querySearch">
    <template #default="{ item }">
      <div class="custom-item">
        <span class="name">{{ item.value }}</span>
        <span class="addr">{{ item.address }}</span>
      </div>
    </template>
  </cc-autocomplete>
</template>
```

## 远程搜索

从服务端搜索数据。

```vue
<template>
  <cc-autocomplete
    v-model="value"
    :fetch-suggestions="querySearchAsync"
    placeholder="请输入内容"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')

const querySearchAsync = (queryString: string, cb: (results: any[]) => void) => {
  const results = []
  // 模拟异步请求
  setTimeout(() => {
    cb(results)
  }, 500)
}
</script>
```

## 输入长度限制

使用 `maxlength` 属性限制输入长度。

```vue
<template>
  <cc-autocomplete v-model="value" :maxlength="20" show-word-limit placeholder="最多输入20个字符" />
</template>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| model-value / v-model | 绑定值 | string | — | — |
| placeholder | 输入框占位文本 | string | — | — |
| disabled | 是否禁用 | boolean | — | false |
| value-key | 输入建议对象中用于显示的键名 | string | — | value |
| debounce | 获取输入建议的去抖延时 | number | — | 300 |
| placement | 菜单弹出位置 | string | top / top-start / top-end / bottom / bottom-start / bottom-end | bottom-start |
| fetch-suggestions | 返回输入建议的方法 | function(queryString, callback) | — | — |
| popper-class | Autocomplete 下拉列表的类名 | string | — | — |
| trigger-on-focus | 是否在输入框 focus 时显示建议菜单 | boolean | — | true |
| name | 原生 name 属性 | string | — | — |
| select-when-unmatched | 在输入没有匹配建议的情况下，按下回车是否触发 select 事件 | boolean | — | false |
| label | 输入框关联的 label 文字 | string | — | — |
| hide-loading | 是否隐藏远程加载时的加载图标 | boolean | — | false |
| popper-append-to-body | 是否将下拉列表插入至 body | boolean | — | true |
| highlight-first-item | 是否默认突出显示远程搜索建议中的第一项 | boolean | — | false |
| clearable | 是否可清空 | boolean | — | false |
| fit-input-width | 下拉列表的宽度是否与输入框相同 | boolean | — | false |
| maxlength | 原生属性，最大输入长度 | number / string | — | — |
| minlength | 原生属性，最小输入长度 | number / string | — | — |
| show-word-limit | 是否显示输入字数统计 | boolean | — | false |
| teleported | 是否将下拉列表插入至 body | boolean | — | true |
| tabindex | 输入框的 tabindex | number / string | — | — |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| select | 点击选中建议项时触发 | (item: object) |
| change | 在 Input 值改变时触发 | (value: string) |
| input | 在 Input 值改变时触发 | (value: string) |
| clear | 在点击由 clearable 属性生成的清空按钮时触发 | — |
| blur | 在 Input 失去焦点时触发 | (event: FocusEvent) |
| focus | 在 Input 获得焦点时触发 | (event: FocusEvent) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 自定义输入建议项的内容，参数为 { item } |
| prefix | 输入框头部内容 |
| suffix | 输入框尾部内容 |
| prepend | 输入框前置内容 |
| append | 输入框后置内容 |
| loading | 自定义加载组件 |
