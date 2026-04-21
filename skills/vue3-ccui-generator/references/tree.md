# Tree 树形控件

用清晰的层级结构展示信息。

## 基础用法

基础的树形结构展示。

```vue
<template>
  <cc-tree
    :data="data"
    :props="defaultProps"
    @node-click="handleNodeClick"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface TreeNode {
  label: string
  children?: TreeNode[]
}

const defaultProps = {
  children: 'children',
  label: 'label'
}

const data: TreeNode[] = [
  {
    label: '一级 1',
    children: [
      {
        label: '二级 1-1',
        children: [
          {
            label: '三级 1-1-1'
          }
        ]
      }
    ]
  },
  {
    label: '一级 2',
    children: [
      {
        label: '二级 2-1',
        children: [
          {
            label: '三级 2-1-1'
          }
        ]
      },
      {
        label: '二级 2-2',
        children: [
          {
            label: '三级 2-2-1'
          }
        ]
      }
    ]
  },
  {
    label: '一级 3',
    children: [
      {
        label: '二级 3-1',
        children: [
          {
            label: '三级 3-1-1'
          }
        ]
      },
      {
        label: '二级 3-2',
        children: [
          {
            label: '三级 3-2-1'
          }
        ]
      }
    ]
  }
]

const handleNodeClick = (data: TreeNode) => {
  console.log(data)
}
</script>
```

## 可选择

适用于需要选择节点时使用。

```vue
<template>
  <cc-tree
    :data="data"
    :props="defaultProps"
    show-checkbox
    @check="handleCheck"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const defaultProps = {
  children: 'children',
  label: 'label'
}

const data = [
  {
    id: 1,
    label: '一级 1',
    children: [
      {
        id: 4,
        label: '二级 1-1',
        children: [
          {
            id: 9,
            label: '三级 1-1-1'
          },
          {
            id: 10,
            label: '三级 1-1-2'
          }
        ]
      }
    ]
  },
  {
    id: 2,
    label: '一级 2',
    children: [
      {
        id: 5,
        label: '二级 2-1'
      },
      {
        id: 6,
        label: '二级 2-2'
      }
    ]
  }
]

const handleCheck = (checkedNodes: any, checkedKeys: any) => {
  console.log('checkedNodes:', checkedNodes)
  console.log('checkedKeys:', checkedKeys)
}
</script>
```

## 禁用状态

```vue
<template>
  <cc-tree
    :data="data"
    :props="defaultProps"
    :default-expand-all="true"
    :default-checked-keys="[5]"
    :default-expanded-keys="[2, 3]"
    show-checkbox
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const defaultProps = {
  children: 'children',
  label: 'label'
}

const data = [
  {
    id: 1,
    label: '一级 1',
    children: [
      {
        id: 4,
        label: '二级 1-1',
        children: [
          {
            id: 9,
            label: '三级 1-1-1'
          },
          {
            id: 10,
            label: '三级 1-1-2'
          }
        ]
      }
    ]
  },
  {
    id: 2,
    label: '一级 2',
    children: [
      {
        id: 5,
        label: '二级 2-1'
      },
      {
        id: 6,
        label: '二级 2-2'
      }
    ]
  }
]
</script>
```

## 禁用状态

节点的禁用状态。

```vue
<template>
  <cc-tree
    :data="data"
    :props="defaultProps"
    show-checkbox
    node-key="id"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const defaultProps = {
  children: 'children',
  label: 'label'
}

const data = [
  {
    id: 1,
    label: '一级 1',
    children: [
      {
        id: 4,
        label: '二级 1-1',
        disabled: true,
        children: [
          {
            id: 9,
            label: '三级 1-1-1'
          },
          {
            id: 10,
            label: '三级 1-1-2'
          }
        ]
      }
    ]
  },
  {
    id: 2,
    label: '一级 2',
    children: [
      {
        id: 5,
        label: '二级 2-1'
      },
      {
        id: 6,
        label: '二级 2-2'
      }
    ]
  }
]
</script>
```

## 树节点的选择

支持单选、多选、父子联动选择。

```vue
<template>
  <div>
    <div class="mb-4">
      <cc-radio-group v-model="checkStrictly" size="small">
        <cc-radio-button :label="true">父子不互选</cc-radio-button>
        <cc-radio-button :label="false">父子互选</cc-radio-button>
      </cc-radio-group>
    </div>
    <cc-tree
      :data="data"
      :props="defaultProps"
      :check-strictly="checkStrictly"
      show-checkbox
      default-expand-all
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const checkStrictly = ref(false)

const defaultProps = {
  children: 'children',
  label: 'label'
}

const data = [
  {
    id: 1,
    label: '一级 1',
    children: [
      {
        id: 4,
        label: '二级 1-1',
        children: [
          {
            id: 9,
            label: '三级 1-1-1'
          },
          {
            id: 10,
            label: '三级 1-1-2'
          }
        ]
      }
    ]
  },
  {
    id: 2,
    label: '一级 2',
    children: [
      {
        id: 5,
        label: '二级 2-1'
      },
      {
        id: 6,
        label: '二级 2-2'
      }
    ]
  }
]
</script>
```

## 自定义节点内容

可以通过插槽自定义树节点的内容。

```vue
<template>
  <cc-tree
    :data="data"
    :props="defaultProps"
    show-checkbox
    default-expand-all
  >
    <template #default="{ node, data }">
      <span class="custom-tree-node">
        <span>{{ node.label }}</span>
        <span>
          <a @click="append(data)">添加</a>
          <a @click="remove(node, data)" style="margin-left: 8px">删除</a>
        </span>
      </span>
    </template>
  </cc-tree>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { CcMessage } from 'cc-ui'

interface TreeNode {
  id: number
  label: string
  children?: TreeNode[]
}

let id = 100

const defaultProps = {
  children: 'children',
  label: 'label'
}

const data: TreeNode[] = [
  {
    id: 1,
    label: '一级 1',
    children: [
      {
        id: 4,
        label: '二级 1-1',
        children: [
          {
            id: 9,
            label: '三级 1-1-1'
          },
          {
            id: 10,
            label: '三级 1-1-2'
          }
        ]
      }
    ]
  }
]

const append = (data: TreeNode) => {
  if (!data.children) {
    data.children = []
  }
  data.children.push({
    id: id++,
    label: '新增节点'
  })
  CcMessage.success('添加成功')
}

const remove = (node: any, data: TreeNode) => {
  const parent = node.parent
  const children = parent.data.children || parent.data
  const index = children.findIndex((d: any) => d.id === data.id)
  children.splice(index, 1)
  CcMessage.success('删除成功')
}
</script>

<style scoped>
.custom-tree-node {
  display: flex;
  justify-content: space-between;
  width: 100%;
  padding-right: 8px;
}
</style>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| data | 展示数据 | array | — | — |
| empty-text | 空数据文本 | string | — | — |
| render-after-expand | 是否在第一次展开时才渲染子节点 | boolean | — | true |
| node-key | 每个树节点用来作为唯一标识的属性 | string | — | — |
| props | 配置选项 | object | — | 见下表 |
| highlight-current | 是否高亮当前选中节点 | boolean | — | true |
| default-expand-all | 是否默认展开所有节点 | boolean | — | false |
| expand-on-click-node | 是否在点击节点时展开 | boolean | — | true |
| auto-expand-parent | 展开节点时是否自动展开父节点 | boolean | — | true |
| default-expanded-keys | 默认展开的节点的 key 的数组 | array | — | — |
| show-checkbox | 节点是否可被选择 | boolean | — | false |
| check-strictly | 在显示复选框的情况下，是否严格的遵循父子不互相关联的做法 | boolean | — | false |
| default-checked-keys | 默认勾选的节点的 key 的数组 | array | — | — |
| current-node-key | 当前节点 | string / number | — | — |
| render-content | 渲染函数 | function | — | — |
| lazy | 是否懒加载子节点 | boolean | — | false |
| load | 加载子节点数据的函数 | function | — | — |
| filter-node-method | 对树节点进行筛选时执行的方法 | function | — | — |
| accordion | 是否每次只打开一个同级树节点展开 | boolean | — | false |
| indent | 相邻级节点间的水平缩进 | number | — | 24 |
| icon | 自定义树节点图标 | component | — | — |
| draggable | 是否可拖拽 | boolean | — | false |
| allow-drop | 拖拽时判定放置目标是否能被放置 | function | — | — |
| allow-drag | 判断节点能否被拖拽 | function | — | — |

### props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| label | 指定节点标签为节点对象的某个属性值 | string / function | — | — |
| children | 指定子树为节点对象的某个属性值 | string | — | — |
| disabled | 指定节点选择框是否禁用为节点对象的某个属性值 | string / function | — | — |
| isLeaf | 指定节点是否为叶子节点 | string / function | — | — |
| class | 节点class | string / function | — | — |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|---------|
| node-click | 节点被点击时触发 | (data: TreeNode, node: TreeNode, event: Event) |
| node-contextmenu | 节点被右键点击时触发 | (event: Event, data: TreeNode, node: TreeNode) |
| check-change | 节点选中状态改变时触发 | (data: TreeNode, checked: boolean) |
| check | 复选框被点击时触发 | (data: TreeNode, checkedInfo: { checkedKeys: TreeNode[], checkedNodes: TreeNode[], halfCheckedKeys: TreeNode[], halfCheckedNodes: TreeNode[] }) |
| current-change | 当前节点变化时触发 | (data: TreeNode, node: TreeNode) |
| node-expand | 节点展开时触发 | (data: TreeNode, node: TreeNode) |
| node-collapse | 节点收起时触发 | (data: TreeNode, node: TreeNode) |
| node-drag-start | 节点开始拖拽时触发 | (event: DragEvent, node: TreeNode) |
| node-drag-end | 节点拖拽结束时触发 | (event: DragEvent, dropNode: TreeNode, dropType: 'inner' / 'prev' / 'next', event: DragEvent) |
| node-drop | 节点放下时触发 | (event: DragEvent, dropNode: TreeNode, dropType: 'inner' / 'prev' / 'next', event: DragEvent) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 树节点的内容，参数为 { node, data } |
| node | 节点区内容，参数为 { node, data } |
| empty | 配置空数据状态，参数为 — |
