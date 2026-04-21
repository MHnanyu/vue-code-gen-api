# TableColumn 表格列

用于展示表格的列数据，配合 cc-table 使用。

## 基础用法

使用 `prop` 属性指定列字段，`label` 属性指定列标题。

```vue
<template>
  <cc-table :data="tableData">
    <cc-table-column prop="date" label="日期" width="180"></cc-table-column>
    <cc-table-column prop="name" label="姓名" width="180"></cc-table-column>
    <cc-table-column prop="address" label="地址"></cc-table-column>
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

## 自定义列内容

通过默认插槽可以自定义列的内容。

```vue
<template>
  <cc-table :data="tableData">
    <cc-table-column prop="date" label="日期" width="180"></cc-table-column>
    <cc-table-column prop="name" label="姓名" width="180"></cc-table-column>
    <cc-table-column label="操作">
      <template #default="scope">
        <el-button link type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
        <el-button link type="primary" size="small" @click="handleDelete(scope.row)">删除</el-button>
      </template>
    </cc-table-column>
  </cc-table>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const tableData = ref([
  {
    date: '2016-05-02',
    name: '王小虎',
    address: '上海市普陀区金沙江路 1518 弄'
  }
])

const handleEdit = (row: any) => {
  console.log('编辑', row)
}

const handleDelete = (row: any) => {
  console.log('删除', row)
}
</script>
```

## 带排序的列

使用 `sortable` 属性可以开启排序功能。

```vue
<template>
  <cc-table :data="tableData" border>
    <cc-table-column prop="date" label="日期" width="180" sortable></cc-table-column>
    <cc-table-column prop="name" label="姓名" width="180"></cc-table-column>
    <cc-table-column prop="address" label="地址" sortable></cc-table-column>
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

## 固定列

使用 `fixed` 属性可以固定列。

```vue
<template>
  <cc-table :data="tableData" border>
    <cc-table-column prop="date" label="日期" width="150" fixed></cc-table-column>
    <cc-table-column prop="name" label="姓名" width="120"></cc-table-column>
    <cc-table-column prop="province" label="省份" width="120"></cc-table-column>
    <cc-table-column prop="city" label="市区" width="120"></cc-table-column>
    <cc-table-column prop="address" label="地址" width="300"></cc-table-column>
    <cc-table-column prop="zip" label="邮编" width="120" fixed="right"></cc-table-column>
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

## 多选列

使用 `type="selection"` 可以实现多选。

```vue
<template>
  <cc-table :data="tableData" @selection-change="handleSelectionChange">
    <cc-table-column type="selection" width="55"></cc-table-column>
    <cc-table-column prop="date" label="日期" width="180"></cc-table-column>
    <cc-table-column prop="name" label="姓名" width="180"></cc-table-column>
    <cc-table-column prop="address" label="地址"></cc-table-column>
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

使用 `type="expand"` 可以实现展开行功能。

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
    <cc-table-column prop="date" label="日期" width="180"></cc-table-column>
    <cc-table-column prop="name" label="姓名" width="180"></cc-table-column>
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

## 自定义表头

通过 `header` 插槽可以自定义表头内容。

```vue
<template>
  <cc-table :data="tableData" border>
    <cc-table-column prop="date" label="日期" width="180">
      <template #header>
        <span>日期</span>
        <el-icon><Calendar /></el-icon>
      </template>
    </cc-table-column>
    <cc-table-column prop="name" label="姓名" width="180"></cc-table-column>
    <cc-table-column prop="address" label="地址"></cc-table-column>
  </cc-table>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const tableData = ref([
  {
    date: '2016-05-02',
    name: '王小虎',
    address: '上海市普陀区金沙江路 1518 弄'
  }
])
</script>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| type | 列的类型 | string | selection / index / expand | — |
| index | 自定义列的索引 | number / Function | — | — |
| column-key | column 的 key | string | — | — |
| prop | 字段名称 | string | — | — |
| label | 列标题 | string | — | — |
| width | 列宽度 | string / number | — | — |
| min-width | 列最小宽度 | string / number | — | — |
| fixed | 固定列 | string / boolean | true / left / right | — |
| render-header | 列标题自定义渲染 | Function | — | — |
| sortable | 是否可以排序 | boolean / string | true / false / 'custom' | false |
| sort-method | 自定义排序方法 | Function | — | — |
| sort-by | 指定数据排序的字段 | string / Function / array | — | — |
| sort-orders | 排序的顺序 | array | — | ['ascending', 'descending', null] |
| resizable | 是否可以调整列宽 | boolean | — | true |
| formatter | 格式化单元格内容 | Function | — | — |
| show-overflow-tooltip | 是否溢出省略 | boolean | — | — |
| align | 对齐方式 | string | left / center / right | left |
| header-align | 表头对齐方式 | string | left / center / right | — |
| class-name | 列的 className | string | — | — |
| label-class-name | 列标题的 className | string | — | — |
| selectable | 判断是否可以选择 | Function | — | — |
| reserve-selection | 数据更新时保留选中状态 | boolean | — | false |
| filter-method | 筛选方法 | Function | — | — |
| filtered-value | 筛选的值 | array | — | — |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 列的默认内容 |
| header | 列标题的内容 |
