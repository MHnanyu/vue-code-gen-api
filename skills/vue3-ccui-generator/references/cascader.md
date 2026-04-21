# Cascader 级联选择器

当一个数据集合有清晰的层级结构时，可通过级联选择器逐级查看并选择。

## 基础用法

有两种触发子菜单的方式。

```vue
<template>
  <div class="block">
    <span class="demonstration">click 激活（默认）</span>
    <cc-cascader v-model="value" :options="options" @change="handleChange" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref([])

const options = [
  {
    value: 'guide',
    label: 'Guide',
    children: [
      {
        value: 'disciplines',
        label: 'Disciplines',
        children: [
          {
            value: 'consistency',
            label: 'Consistency'
          },
          {
            value: 'feedback',
            label: 'Feedback'
          }
        ]
      },
      {
        value: 'navigation',
        label: 'Navigation',
        children: [
          {
            value: 'side nav',
            label: 'Side Navigation'
          },
          {
            value: 'top nav',
            label: 'Top Navigation'
          }
        ]
      }
    ]
  },
  {
    value: 'component',
    label: 'Component',
    children: [
      {
        value: 'basic',
        label: 'Basic',
        children: [
          {
            value: 'layout',
            label: 'Layout'
          },
          {
            value: 'color',
            label: 'Color'
          }
        ]
      },
      {
        value: 'form',
        label: 'Form',
        children: [
          {
            value: 'input',
            label: 'Input'
          },
          {
            value: 'select',
            label: 'Select'
          }
        ]
      }
    ]
  }
]

const handleChange = (value: any) => {
  console.log(value)
}
</script>
```

## 禁用状态

通过在数据中设置 `disabled` 字段来声明该选项是禁用的。

```vue
<template>
  <cc-cascader v-model="value" :options="options" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref([])

const options = [
  {
    value: 'guide',
    label: 'Guide',
    disabled: true,
    children: [
      {
        value: 'disciplines',
        label: 'Disciplines',
        children: [
          {
            value: 'consistency',
            label: 'Consistency'
          }
        ]
      }
    ]
  },
  {
    value: 'component',
    label: 'Component',
    children: [
      {
        value: 'basic',
        label: 'Basic'
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
  <cc-cascader v-model="value" :options="options" clearable />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref(['guide', 'disciplines', 'consistency'])

const options = [
  {
    value: 'guide',
    label: 'Guide',
    children: [
      {
        value: 'disciplines',
        label: 'Disciplines',
        children: [
          {
            value: 'consistency',
            label: 'Consistency'
          }
        ]
      }
    ]
  }
]
</script>
```

## 仅显示最后一级

可以仅在输入框中显示选中最后一级的标签，而不是选中路径的标签。

```vue
<template>
  <cc-cascader v-model="value" :options="options" :show-all-levels="false" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref([])

const options = [
  {
    value: 'guide',
    label: 'Guide',
    children: [
      {
        value: 'disciplines',
        label: 'Disciplines',
        children: [
          {
            value: 'consistency',
            label: 'Consistency'
          }
        ]
      }
    ]
  }
]
</script>
```

## 多选

设置 `props.multiple = true` 即可启用多选模式。

```vue
<template>
  <cc-cascader v-model="value" :options="options" :props="props" clearable />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref([])

const props = {
  multiple: true
}

const options = [
  {
    value: 'guide',
    label: 'Guide',
    children: [
      {
        value: 'disciplines',
        label: 'Disciplines',
        children: [
          {
            value: 'consistency',
            label: 'Consistency'
          },
          {
            value: 'feedback',
            label: 'Feedback'
          }
        ]
      }
    ]
  },
  {
    value: 'component',
    label: 'Component',
    children: [
      {
        value: 'basic',
        label: 'Basic'
      }
    ]
  }
]
</script>
```

## 选择任意一级

可以通过 `props.checkStrictly = true` 设置选择任意一级选项。

```vue
<template>
  <cc-cascader v-model="value" :options="options" :props="props" clearable />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref([])

const props = {
  checkStrictly: true
}

const options = [
  {
    value: 'guide',
    label: 'Guide',
    children: [
      {
        value: 'disciplines',
        label: 'Disciplines',
        children: [
          {
            value: 'consistency',
            label: 'Consistency'
          }
        ]
      }
    ]
  }
]
</script>
```

## 动态加载

当选中某一级时，动态加载该级下的选项。

```vue
<template>
  <cc-cascader v-model="value" :props="props" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref([])

let id = 0
const props = {
  lazy: true,
  lazyLoad(node: any, resolve: any) {
    const { level } = node
    setTimeout(() => {
      const nodes = Array.from({ length: level + 1 }).map(() => ({
        value: ++id,
        label: `Option${id}`,
        leaf: level >= 2
      }))
      resolve(nodes)
    }, 1000)
  }
}
</script>
```

## 可搜索

可以快捷地搜索选项并选择。

```vue
<template>
  <cc-cascader v-model="value" :options="options" filterable placeholder="试试搜索：指南" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref([])

const options = [
  {
    value: 'guide',
    label: '指南',
    children: [
      {
        value: 'disciplines',
        label: '纪律',
        children: [
          {
            value: 'consistency',
            label: '一致性'
          }
        ]
      }
    ]
  },
  {
    value: 'component',
    label: '组件',
    children: [
      {
        value: 'basic',
        label: '基础'
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
  <cc-cascader v-model="value" :options="options">
    <template #default="{ node, data }">
      <span>{{ data.label }}</span>
      <span v-if="!node.isLeaf"> ({{ data.children.length }}) </span>
    </template>
  </cc-cascader>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref([])

const options = [
  {
    value: 'guide',
    label: 'Guide',
    children: [
      {
        value: 'disciplines',
        label: 'Disciplines',
        children: [
          {
            value: 'consistency',
            label: 'Consistency'
          },
          {
            value: 'feedback',
            label: 'Feedback'
          }
        ]
      }
    ]
  }
]
</script>
```

## 级联面板

级联面板是级联选择器的核心组件。

```vue
<template>
  <cc-cascader-panel v-model="value" :options="options" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref([])

const options = [
  {
    value: 'guide',
    label: 'Guide',
    children: [
      {
        value: 'disciplines',
        label: 'Disciplines',
        children: [
          {
            value: 'consistency',
            label: 'Consistency'
          }
        ]
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
| options | 可选项数据源 | array | — | — |
| props | 配置选项 | object | — | — |
| size | 尺寸 | string | large / default / small | — |
| placeholder | 输入框占位文本 | string | — | Select |
| disabled | 是否禁用 | boolean | — | false |
| clearable | 是否可清空 | boolean | — | false |
| show-all-levels | 输入框中是否显示选中值的完整路径 | boolean | — | true |
| collapse-tags | 多选模式下是否折叠Tag | boolean | — | false |
| collapse-tags-tooltip | 折叠Tag时展示所有选中的Tag | boolean | — | false |
| separator | 选项分隔符 | string | — | ' / ' |
| filterable | 是否可搜索选项 | boolean | — | false |
| filter-method | 自定义搜索逻辑 | function(node, keyword) | - | - |
| debounce | 搜索关键词输入的去抖延迟 | number | — | 300 |
| before-filter | 筛选之前的钩子 | function(value) | - | - |
| popper-class | 自定义浮层类名 | string | — | — |
| teleported | 是否将下拉列表插入至 body | boolean | - | true |
| tag-type | 标签类型 | string | success/info/warning/danger | info |

## Props Configuration

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| expandTrigger | 次级菜单的展开方式 | string | click / hover | 'click' |
| multiple | 是否多选 | boolean | - | false |
| checkStrictly | 是否严格的遵守父子节点不互相关联 | boolean | - | false |
| emitPath | 在选中节点改变时，是否返回由该节点所在的各级菜单的值所组成的数组 | boolean | - | true |
| lazy | 是否动态加载子节点 | boolean | - | false |
| lazyLoad | 加载动态数据的方法 | function(node, resolve) | - | - |
| value | 指定选项的值为选项对象的某个属性值 | string | — | 'value' |
| label | 指定选项标签为选项对象的某个属性值 | string | — | 'label' |
| children | 指定选项的子选项为选项对象的某个属性值 | string | — | 'children' |
| disabled | 指定选项的禁用为选项对象的某个属性值 | string | — | 'disabled' |
| leaf | 指定选项的叶子节点的标志位为选项对象的某个属性值 | string | — | 'leaf' |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| change | 当绑定值变化时触发的事件 | (value) |
| expand-change | 当展开节点发生变化时触发 | (value) |
| blur | 当失去焦点时触发 | (event: FocusEvent) |
| focus | 当获得焦点时触发 | (event: FocusEvent) |
| visible-change | 下拉框出现/隐藏时触发 | (value) |
| remove-tag | 在多选模式下，移除Tag时触发 | (value) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 自定义备选项的节点内容，参数为 { node, data } |
| empty | 无匹配选项时的内容 |
