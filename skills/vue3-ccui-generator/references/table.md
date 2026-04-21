# Table 表格

用于展示多条结构类似的数据，可对数据进行排序、筛选、对比或其他操作。

## 基础用法

使用 `data` 属性传入表格数据，`columns` 属性定义列。

```vue
<template>
  <cc-table :data="tableData">
    <cc-table-column prop="date" label="日期" width="180" />
    <cc-table-column prop="name" label="姓名" width="180" />
    <cc-table-column prop="address" label="地址" />
  </cc-table>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const tableData = ref([
  {
    date: '2016-05-02',
    name: '王小虎',
    address: '上海市普陀区金沙江路 1518 弄'
  },
  {
    date: '2016-05-04',
    name: '王小明',
    address: '上海市普陀区金沙江路 1517 弄'
  },
  {
    date: '2016-05-01',
    name: '王小红',
    address: '上海市普陀区金沙江路 1519 弄'
  }
])
</script>
```

## 带斑马纹表格

使用 `stripe` 属性可以创建带斑马纹的表格。

```vue
<template>
  <cc-table :data="tableData" stripe>
    <cc-table-column prop="date" label="日期" width="180" />
    <cc-table-column prop="name" label="姓名" width="180" />
    <cc-table-column prop="address" label="地址" />
  </cc-table>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const tableData = ref([
  {
    date: '2016-05-02',
    name: '王小虎',
    address: '上海市普陀区金沙江路 1518 弄'
  },
  {
    date: '2016-05-04',
    name: '王小明',
    address: '上海市普陀区金沙江路 1517 弄'
  },
  {
    date: '2016-05-01',
    name: '王小红',
    address: '上海市普陀区金沙江路 1519 弄'
  }
])
</script>
```

## 带边框表格

使用 `border` 属性可以添加表格边框。

```vue
<template>
  <cc-table :data="tableData" border>
    <cc-table-column prop="date" label="日期" width="180" />
    <cc-table-column prop="name" label="姓名" width="180" />
    <cc-table-column prop="address" label="地址" />
  </cc-table>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const tableData = ref([
  {
    date: '2016-05-02',
    name: '王小虎',
    address: '上海市普陀区金沙江路 1518 弄'
  },
  {
    date: '2016-05-04',
    name: '王小明',
    address: '上海市普陀区金沙江路 1517 弄'
  },
  {
    date: '2016-05-01',
    name: '王小红',
    address: '上海市普陀区金沙江路 1519 弄'
  }
])
</script>
```

## 固定表头

使用 `height` 属性可以固定表头。

```vue
<template>
  <cc-table :data="tableData" height="200">
    <cc-table-column prop="date" label="日期" width="180" />
    <cc-table-column prop="name" label="姓名" width="180" />
    <cc-table-column prop="address" label="地址" />
  </cc-table>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const tableData = ref([
  {
    date: '2016-05-02',
    name: '王小虎',
    address: '上海市普陀区金沙江路 1518 弄'
  },
  {
    date: '2016-05-04',
    name: '王小明',
    address: '上海市普陀区金沙江路 1517 弄'
  },
  {
    date: '2016-05-01',
    name: '王小红',
    address: '上海市普陀区金沙江路 1519 弄'
  },
  {
    date: '2016-05-03',
    name: '王小华',
    address: '上海市普陀区金沙江路 1520 弄'
  },
  {
    date: '2016-05-05',
    name: '王小丽',
    address: '上海市普陀区金沙江路 1521 弄'
  }
])
</script>
```

## 固定列

使用 `fixed` 属性可以固定列。

```vue
<template>
  <cc-table :data="tableData" border>
    <cc-table-column prop="date" label="日期" width="150" fixed />
    <cc-table-column prop="name" label="姓名" width="120" />
    <cc-table-column prop="province" label="省份" width="120" />
    <cc-table-column prop="city" label="市区" width="120" />
    <cc-table-column prop="address" label="地址" width="300" />
    <cc-table-column prop="zip" label="邮编" width="120" fixed="right" />
  </cc-table>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const tableData = ref([
  {
    date: '2016-05-02',
    name: '王小虎',
    province: '上海',
    city: '普陀区',
    address: '上海市普陀区金沙江路 1518 弄',
    zip: 200333
  },
  {
    date: '2016-05-04',
    name: '王小明',
    province: '上海',
    city: '普陀区',
    address: '上海市普陀区金沙江路 1517 弄',
    zip: 200333
  }
])
</script>
```

## 排序

使用 `sortable` 属性可以开启排序功能。

```vue
<template>
  <cc-table :data="tableData" border>
    <cc-table-column prop="date" label="日期" width="180" sortable />
    <cc-table-column prop="name" label="姓名" width="180" />
    <cc-table-column prop="address" label="地址" sortable />
  </cc-table>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const tableData = ref([
  {
    date: '2016-05-02',
    name: '王小虎',
    address: '上海市普陀区金沙江路 1518 弄'
  },
  {
    date: '2016-05-04',
    name: '王小明',
    address: '上海市普陀区金沙江路 1517 弄'
  },
  {
    date: '2016-05-01',
    name: '王小红',
    address: '上海市普陀区金沙江路 1519 弄'
  }
])
</script>
```

## 多选

使用 `type="selection"` 的 cc-table-column 可以实现多选。

```vue
<template>
  <cc-table :data="tableData" @selection-change="handleSelectionChange">
    <cc-table-column type="selection" width="55" />
    <cc-table-column prop="date" label="日期" width="180" />
    <cc-table-column prop="name" label="姓名" width="180" />
    <cc-table-column prop="address" label="地址" />
  </cc-table>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const tableData = ref([
  {
    date: '2016-05-02',
    name: '王小虎',
    address: '上海市普陀区金沙江路 1518 弄'
  },
  {
    date: '2016-05-04',
    name: '王小明',
    address: '上海市普陀区金沙江路 1517 弄'
  },
  {
    date: '2016-05-01',
    name: '王小红',
    address: '上海市普陀区金沙江路 1519 弄'
  }
])

const handleSelectionChange = (val: any[]) => {
  console.log(val)
}
</script>
```

## 展开行

使用 `type="expand"` 的 cc-table-column 可以实现展开行功能。

```vue
<template>
  <cc-table :data="tableData">
    <cc-table-column type="expand">
      <template #default="scope">
        <div m="4">
          <p m="t-0 b-2">姓名: {{ scope.row.name }}</p>
          <p>地址: {{ scope.row.address }}</p>
        </div>
      </template>
    </cc-table-column>
    <cc-table-column prop="date" label="日期" width="180" />
    <cc-table-column prop="name" label="姓名" width="180" />
  </cc-table>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const tableData = ref([
  {
    date: '2016-05-02',
    name: '王小虎',
    address: '上海市普陀区金沙江路 1518 弄'
  },
  {
    date: '2016-05-04',
    name: '王小明',
    address: '上海市普陀区金沙江路 1517 弄'
  }
])
</script>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| data | 显示的数据 | array | — | — |
| height | Table 的高度，默认为自动高度 | string / number | — | — |
| max-height | Table 的最大高度 | string / number | — | — |
| stripe | 是否为斑马纹表格 | boolean | — | false |
| border | 是否带有纵向边框 | boolean | — | false |
| size | Table 的尺寸 | string | large / default / small | — |
| fit | 列的宽度是否自撑开 | boolean | — | true |
| show-header | 是否显示表头 | boolean | — | true |
| highlight-current-row | 是否高亮当前行 | boolean | — | false |
| row-class-name | 行的 className | Function(row, rowIndex) / string | — | — |
| row-style | 行的 style | Function(row, rowIndex) / object | — | — |
| cell-class-name | 单元格的 className | Function(row, column, rowIndex, columnIndex) / string | — | — |
| cell-style | 单元格的 style | Function(row, column, rowIndex, columnIndex) / object | — | — |
| header-row-class-name | 表头行的 className | Function(row, rowIndex) / string | — | — |
| header-row-style | 表头行的 style | Function(row, rowIndex) / object | — | — |
| row-key | 行数据的 Key | Function(row) / string | — | — |
| empty-text | 空数据时显示的文本 | string | — | — |
| default-expand-all | 是否默认展开所有行 | boolean | — | false |
| expand-row-keys | 展开行的 keys | array | — | — |
| default-sort | 默认排序列和排序方式 | object | — | — |
| tooltip-effect | tooltip 的 effect | string | dark / light | — |
| show-summary | 是否在表尾显示合计行 | boolean | — | false |
| sum-text | 合计行第一列的文本 | string | — | Sum |
| summary-method | 自定义合计行计算方法 | Function({ columns, data }) | — | — |
| span-method | 合并行或列的计算方法 | Function({ row, column, rowIndex, columnIndex }) | — | — |
| select-on-indeterminate | 在多选表格中，当仅有部分行被选中时，点击表头多选框的行为 | boolean | — | true |
| indent | 树形表格的缩进 | number | — | 16 |
| lazy | 是否懒加载子节点数据 | boolean | — | — |
| load | 加载子节点数据的回调 | Function(row, treeNode, resolve) | — | — |
| tree-props | 渲染子数据的配置 | object | — | — |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|---------|
| select | 当用户手动勾选数据行的 Checkbox 时触发 | (selection, row) |
| select-all | 当用户手动勾选全选 Checkbox 时触发 | (selection) |
| selection-change | 当选择项发生变化时会触发 | (selection) |
| cell-click | 当某个单元格被点击时触发 | (row, column, cell, event) |
| cell-dblclick | 当某个单元格被双击时触发 | (row, column, cell, event) |
| row-click | 当某一行被点击时触发 | (row, column, event) |
| row-dblclick | 当某一行被双击时触发 | (row, column, event) |
| header-click | 当某一列的表头被点击时触发 | (column, event) |
| header-dragend | 当拖动表尾使得列宽发生变化时触发 | (newWidth, oldWidth, column, columns) |
| sort-change | 当表格的排序条件发生变化时触发 | ({ prop, order }) |
| filter-change | 当表格的筛选条件发生变化时触发 | (filters) |
| current-change | 当表格当前行发生变化时触发 | (currentRow, oldCurrentRow) |
| header-contextmenu | 当表头被右键点击时触发 | (column, event) |
| row-contextmenu | 当某一行被右键点击时触发 | (row, column, event) |
| expand-change | 当用户对某一行展开或者关闭时会触发 | (row, expanded) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 表格内容 |
| append | 插入至表格最后一行之后的内容 |
| empty | 自定义空数据的内容 |
| header | 表头插槽 |
