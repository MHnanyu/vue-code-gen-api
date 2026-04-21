# VirtualizedSelect 虚拟化选择器

虚拟化选择器组件，适用于大数据量场景，通过虚拟滚动技术优化性能。

## 基础用法

使用 `v-model` 绑定选中项的值，通过 `options` 属性设置选项数据。

```vue
<template>
  <cc-virtualized-select v-model="value" :options="options" placeholder="请选择" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
const options = Array.from({ length: 1000 }).map((_, idx) => ({
  value: `option-${idx + 1}`,
  label: `选项 ${idx + 1}`
}))
</script>
```

## 禁用状态

使用 `disabled` 属性禁用选择器。

```vue
<template>
  <cc-virtualized-select v-model="value" disabled placeholder="禁用状态" :options="options" />
</template>
```

## 可清空

使用 `clearable` 属性可清空选中项。

```vue
<template>
  <cc-virtualized-select v-model="value" clearable placeholder="可清空" :options="options" />
</template>
```

## 多选

使用 `multiple` 属性开启多选模式。

```vue
<template>
  <cc-virtualized-select v-model="value" multiple placeholder="请选择" :options="options" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref([])
const options = Array.from({ length: 1000 }).map((_, idx) => ({
  value: `option-${idx + 1}`,
  label: `选项 ${idx + 1}`
}))
</script>
```

## 多选折叠标签

使用 `collapse-tags` 属性折叠多选标签，`collapse-tags-tooltip` 属性在hover时显示所有标签。

```vue
<template>
  <cc-virtualized-select 
    v-model="value" 
    multiple 
    collapse-tags 
    collapse-tags-tooltip 
    placeholder="请选择" 
    :options="options" 
  />
</template>
```

## 可搜索

使用 `filterable` 属性开启搜索功能。

```vue
<template>
  <cc-virtualized-select v-model="value" filterable placeholder="可搜索" :options="options" />
</template>
```

## 自定义高度

使用 `height` 属性设置下拉框高度。

```vue
<template>
  <cc-virtualized-select v-model="value" :height="200" placeholder="请选择" :options="options" />
</template>
```

## 分组

使用选项的 `options` 属性实现分组。

```vue
<template>
  <cc-virtualized-select v-model="value" placeholder="请选择城市" :options="groupedOptions" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
const groupedOptions = [
  {
    label: '热门城市',
    options: [
      { value: 'beijing', label: '北京' },
      { value: 'shanghai', label: '上海' }
    ]
  },
  {
    label: '其他城市',
    options: [
      { value: 'guangzhou', label: '广州' },
      { value: 'shenzhen', label: '深圳' }
    ]
  }
]
</script>
```

## 不同尺寸

使用 `size` 属性设置尺寸，可选值为 `large`、`default`、`small`。

```vue
<template>
  <cc-virtualized-select v-model="value1" size="large" placeholder="large" :options="options" />
  <cc-virtualized-select v-model="value2" placeholder="default" :options="options" />
  <cc-virtualized-select v-model="value3" size="small" placeholder="small" :options="options" />
</template>
```

## 远程搜索

使用 `remote` 和 `remote-method` 属性实现远程搜索。

```vue
<template>
  <cc-virtualized-select 
    v-model="value" 
    filterable 
    remote 
    :remote-method="remoteMethod" 
    :loading="loading" 
    placeholder="请输入关键词" 
    :options="options" 
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
const loading = ref(false)
const options = ref([])

const remoteMethod = (query: string) => {
  if (query) {
    loading.value = true
    setTimeout(() => {
      loading.value = false
      options.value = Array.from({ length: 100 }).map((_, idx) => ({
        value: `${query}-${idx}`,
        label: `${query} 结果 ${idx + 1}`
      }))
    }, 200)
  } else {
    options.value = []
  }
}
</script>
```

## 自定义渲染

使用 `props` 属性自定义选项的标签和值字段。

```vue
<template>
  <cc-virtualized-select v-model="value" placeholder="请选择" :options="options" :props="props" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
const props = {
  label: 'name',
  value: 'id'
}
const options = [
  { id: 1, name: '选项一' },
  { id: 2, name: '选项二' },
  { id: 3, name: '选项三' }
]
</script>
```

## Props

| 属性名 | 说明 | 类型 | 可选值 | 默认值 |
|--------|------|------|--------|--------|
| v-model | 绑定值 | string / number / boolean / object / array | — | — |
| options | 选项数据 | array | — | — |
| multiple | 是否多选 | boolean | — | false |
| disabled | 是否禁用 | boolean | — | false |
| clearable | 是否可清空 | boolean | — | false |
| filterable | 是否可搜索 | boolean | — | false |
| collapse-tags | 多选时是否折叠标签 | boolean | — | false |
| collapse-tags-tooltip | 折叠标签时是否显示tooltip | boolean | — | false |
| max-collapse-tags | 显示的标签最大数量 | number | — | 1 |
| size | 尺寸 | string | large / default / small | default |
| placeholder | 占位符 | string | — | 请选择 |
| loading | 是否加载中 | boolean | — | false |
| loading-text | 加载中文字 | string | — | 加载中 |
| no-match-text | 搜索无匹配文字 | string | — | 无匹配数据 |
| no-data-text | 无数据文字 | string | — | 无数据 |
| popper-class | 下拉框的类名 | string | — | — |
| height | 下拉框高度 | number | — | 274 |
| scrollbar-always-on | 是否总是显示滚动条 | boolean | — | false |
| reserve-keyword | 多选时是否保留搜索关键词 | boolean | — | true |
| value-key | 作为value唯一标识的键名 | string | — | value |
| props | 配置选项 | object | — | — |
| remote | 是否远程搜索 | boolean | — | false |
| remote-method | 远程搜索方法 | function(query) | — | — |
| filter-method | 自定义搜索方法 | function(query) | — | — |
| teleported | 是否将下拉框插入到body | boolean | — | true |
| persistent | 是否在下拉框关闭时销毁元素 | boolean | — | true |
| tag-type | 标签类型 | string | success / info / warning / danger | info |
| tag-effect | 标签效果 | string | dark / light / plain | light |
| validate-event | 是否触发表单验证 | boolean | — | true |
| placement | 下拉框出现的位置 | string | top / top-start / top-end / bottom / bottom-start / bottom-end / left / left-start / left-end / right / right-start / right-end | bottom-start |
| name | 原生name属性 | string | — | — |
| autocomplete | 原生autocomplete属性 | string | — | off |
| id | 原生id属性 | string | — | — |

## Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| change | 选中值发生变化时触发 | (value: any) |
| visible-change | 下拉框出现/隐藏时触发 | (visible: boolean) |
| remove-tag | 多选模式下移除标签时触发 | (value: any) |
| clear | 可清空模式下点击清空时触发 | — |
| blur | 失去焦点时触发 | (event: FocusEvent) |
| focus | 获得焦点时触发 | (event: FocusEvent) |
| filter-query-change | 搜索关键词改变时触发 | (query: string) |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 自定义默认内容 |
| header | 下拉框头部内容 |
| footer | 下拉框底部内容 |
| empty | 无数据时的内容 |
| tag | 多选时的标签内容 |
| loading | 加载中的内容 |

## Methods

| 方法名 | 说明 | 参数 |
|--------|------|------|
| focus | 使选择器获取焦点 | — |
| blur | 使选择器失去焦点 | — |
