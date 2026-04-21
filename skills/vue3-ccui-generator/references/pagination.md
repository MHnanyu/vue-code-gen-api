# Pagination 分页

当数据量较多时，使用分页可以快速进行数据切换。

## 基础用法

设置 `total`、`page-size` 和 `v-model:current-page` 来进行数据切换。

```vue
<template>
  <cc-pagination v-model:current-page="currentPage" :page-size="20" :total="200" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const currentPage = ref(1)
</script>
```

## 设置最大页码按钮数

默认情况下，当总页数超过 7 页时，Pagination 会折叠多余的页码按钮。通过 `pager-count` 属性可以设置最大页码按钮数。

```vue
<template>
  <cc-pagination :total="500" :pager-count="11" />
</template>
```

## 完整功能

完整的分页组件包含页码、每页显示条数选择、跳转等功能。

```vue
<template>
  <cc-pagination
    v-model:current-page="currentPage"
    v-model:page-size="pageSize"
    :page-sizes="[10, 20, 30, 50]"
    :total="total"
    layout="total, sizes, prev, pager, next, jumper"
    @current-change="handleCurrentChange"
    @page-size-change="handlePageSizeChange"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(100)

const handleCurrentChange = (val: number) => {
  console.log('current change:', val)
}

const handlePageSizeChange = (val: number) => {
  console.log('page size change:', val)
}
</script>
```

## 带有背景色的分页

设置 `background` 属性可以显示带有背景色的分页按钮。

```vue
<template>
  <cc-pagination :total="200" background />
</template>
```

## 简洁分页

当不需要显示过多的功能时，可以设置 `layout` 属性来选择需要显示的功能。

```vue
<template>
  <cc-pagination :total="100" layout="prev, pager, next" />
</template>
```

## 小型分页

在空间有限的情况下，可以使用 `small` 属性来显示小型分页。

```vue
<template>
  <cc-pagination :total="100" small />
</template>
```

## 自定义文本

通过 `prev-text` 和 `next-text` 属性来自定义上一页和下一页的文本。

```vue
<template>
  <cc-pagination :total="100" prev-text="上一页" next-text="下一页" />
</template>
```

## 隐藏当只有一页时

设置 `hide-on-single-page` 属性可以在只有一页时隐藏分页。

```vue
<template>
  <cc-pagination :total="10" hide-on-single-page />
</template>
```

## 禁用分页

设置 `disabled` 属性可以禁用分页。

```vue
<template>
  <cc-pagination :total="100" disabled />
</template>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| current-page | 当前页码 | number | — | 1 |
| page-size | 每页显示条数 | number | — | 10 |
| page-sizes | 每页显示条数选项 | number[] | — | [10, 20, 30, 50, 100] |
| pager-count | 页码按钮数量 | number | — | 7 |
| total | 总条目数 | number | — | 0 |
| layout | 组件布局 | string | total, sizes, prev, pager, next, jumper, -> | total, sizes, prev, pager, next, jumper |
| background | 是否显示背景色 | boolean | — | true |
| disabled | 是否禁用 | boolean | — | false |
| small | 是否使用小型分页 | boolean | — | false |
| hide-on-single-page | 当只有一页时是否隐藏 | boolean | — | false |
| prev-text | 上一页文本 | string | — | — |
| next-text | 下一页文本 | string | — | — |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|---------|
| current-change | 当前页码改变时触发 | (page: number) |
| page-size-change | 每页显示条数改变时触发 | (size: number) |
| prev-click | 点击上一页按钮时触发 | (page: number) |
| next-click | 点击下一页按钮时触发 | (page: number) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| — | 自定义内容（需要配合 Pagination 组件的 slot 扩展） |
