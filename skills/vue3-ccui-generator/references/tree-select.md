# TreeSelect 树选择

TreeSelect 树选择是一种具有树形层级结构的选择器，用户可以从多层级的数据中进行选择。

## 基础用法

树选择器的基础用法。

```vue
<template>
  <cc-tree-select v-model="value" :data="data" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')

const data = [
  {
    value: '1',
    label: 'Level 1-1',
    children: [
      {
        value: '1-1',
        label: 'Level 1-1-1'
      },
      {
        value: '1-2',
        label: 'Level 1-1-2'
      }
    ]
  },
  {
    value: '2',
    label: 'Level 1-2',
    children: [
      {
        value: '2-1',
        label: 'Level 1-2-1'
      }
    ]
  }
]
</script>
```

## 可清空

通过 `clearable` 设置输入框可清空。

```vue
<template>
  <cc-tree-select v-model="value" :data="data" clearable />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('1')

const data = [
  {
    value: '1',
    label: 'Level 1-1',
    children: [
      {
        value: '1-1',
        label: 'Level 1-1-1'
      }
    ]
  }
]
</script>
```

## 禁用状态

通过在数据中设置 `disabled` 字段来声明该选项是禁用的。

```vue
<template>
  <cc-tree-select v-model="value" :data="data" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')

const data = [
  {
    value: '1',
    label: 'Level 1-1',
    disabled: true,
    children: [
      {
        value: '1-1',
        label: 'Level 1-1-1'
      }
    ]
  },
  {
    value: '2',
    label: 'Level 1-2',
    children: [
      {
        value: '2-1',
        label: 'Level 1-2-1'
      }
    ]
  }
]
</script>
```

## 多选

设置 `multiple` 即可启用多选模式。

```vue
<template>
  <cc-tree-select v-model="value" :data="data" multiple clearable />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref([])

const data = [
  {
    value: '1',
    label: 'Level 1-1',
    children: [
      {
        value: '1-1',
        label: 'Level 1-1-1'
      },
      {
        value: '1-2',
        label: 'Level 1-1-2'
      }
    ]
  },
  {
    value: '2',
    label: 'Level 1-2',
    children: [
      {
        value: '2-1',
        label: 'Level 1-2-1'
      }
    ]
  }
]
</script>
```

## 可搜索

设置 `filterable` 开启搜索功能。

```vue
<template>
  <cc-tree-select v-model="value" :data="data" filterable placeholder="请输入关键词搜索" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')

const data = [
  {
    value: '1',
    label: '指南',
    children: [
      {
        value: '1-1',
        label: '设计原则'
      },
      {
        value: '1-2',
        label: '响应式设计'
      }
    ]
  },
  {
    value: '2',
    label: '组件',
    children: [
      {
        value: '2-1',
        label: '基础组件'
      },
      {
        value: '2-2',
        label: '表单组件'
      }
    ]
  }
]
</script>
```

## 展开任意层级

设置 `checkStrictly` 可以选择任意层级的节点。

```vue
<template>
  <cc-tree-select v-model="value" :data="data" checkStrictly clearable />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')

const data = [
  {
    value: '1',
    label: 'Level 1-1',
    children: [
      {
        value: '1-1',
        label: 'Level 1-1-1'
      }
    ]
  }
]
</script>
```

## 自定义节点内容

可以自定义备选项的节点内容。

```vue
<template>
  <cc-tree-select v-model="value" :data="data">
    <template #default="{ data }">
      <span>{{ data.label }}</span>
      <span v-if="data.children" style="color: #999; font-size: 12px;"> ({{ data.children.length }}) </span>
    </template>
  </cc-tree-select>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')

const data = [
  {
    value: '1',
    label: 'Level 1-1',
    children: [
      {
        value: '1-1',
        label: 'Level 1-1-1'
      }
    ]
  }
]
</script>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| model-value / v-model | 选中项绑定值 | - | — | — |
| data | 可选项数据源 | array | — | — |
| props | 配置选项 | object | — | — |
| multiple | 是否多选 | boolean | — | false |
| checkStrictly | 是否遵守父子不关联 | boolean | — | false |
| show-checkbox | 节点是否显示复选框 | boolean | — | false |
| filterable | 是否可搜索 | boolean | — | false |
| filter-method | 自定义搜索方法 | function(node, keyword) | - | - |
| clearable | 是否可清空 | boolean | — | false |
| placeholder | 占位符 | string | — | Please select |
| size | 尺寸 | string | large / default / small | — |
| disabled | 是否禁用 | boolean | — | false |
| expand-on-click-node | 是否在点击节点时展开 | boolean | — | true |
| auto-expand-parent | 是否自动展开父节点 | boolean | — | true |
| default-expand-all | 是否默认展开所有节点 | boolean | — | false |
| expand-on-click-node | 是否在点击节点时展开节点 | boolean | — | true |
| accordion | 是否手风琴模式 | boolean | — | false |
| indent | 相邻级节点间的水平缩进 | number | — | 16 |
| lazy | 是否懒加载子节点 | boolean | — | false |
| load | 加载子节点数据的方法 | function(node, resolve) | - | - |
| popper-class | 自定义浮层类名 | string | — | — |
| teleported | 是否将下拉菜单插入至 body | boolean | - | true |

## Props Configuration

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| value | 指定选项的值为选项对象的某个属性值 | string | — | 'value' |
| label | 指定选项标签为选项对象的某个属性值 | string | — | 'label' |
| children | 指定选项的子选项为选项对象的某个属性值 | string | — | 'children' |
| disabled | 指定选项的禁用为选项对象的某个属性值 | string | — | 'disabled' |
| leaf | 指定选项的叶子节点的标志位为选项对象的某个属性值 | string | — | 'leaf' |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| change | 当绑定值变化时触发 | (value) |
| focus | 当获得焦点时触发 | (event: FocusEvent) |
| blur | 当失去焦点时触发 | (event: FocusEvent) |
| visible-change | 下拉框出现/隐藏时触发 | (value) |
| remove-tag | 在多选模式下，移除Tag时触发 | (value) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 自定义备选项的节点内容，参数为 { data } |
| empty | 无匹配选项时的内容 |
| prefix | 输入框前缀内容 |
| suffix | 输入框后缀内容 |
