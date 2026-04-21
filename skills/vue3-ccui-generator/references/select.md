# Select 选择器

当选项过多时，使用下拉菜单展示并选择内容。

## 基础用法

使用 `v-model` 绑定选中的值。

```vue
<template>
  <cc-select v-model="value" placeholder="请选择">
    <cc-option
      v-for="item in options"
      :key="item.value"
      :label="item.label"
      :value="item.value"
    />
  </cc-select>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
const options = [
  { value: '选项1', label: '黄金糕' },
  { value: '选项2', label: '双皮奶' },
  { value: '选项3', label: '蚵仔煎' },
  { value: '选项4', label: '龙须面' },
  { value: '选项5', label: '北京烤鸭' }
]
</script>
```

## 有禁用选项

使用 `disabled` 属性来禁用某个选项。

```vue
<template>
  <cc-select v-model="value" placeholder="请选择">
    <cc-option
      v-for="item in options"
      :key="item.value"
      :label="item.label"
      :value="item.value"
      :disabled="item.disabled"
    />
  </cc-select>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
const options = [
  { value: '选项1', label: '黄金糕' },
  { value: '选项2', label: '双皮奶', disabled: true },
  { value: '选项3', label: '蚵仔煎' },
  { value: '选项4', label: '龙须面' },
  { value: '选项5', label: '北京烤鸭' }
]
</script>
```

## 禁用选择器

使用 `disabled` 属性禁用整个选择器。

```vue
<template>
  <cc-select v-model="value" placeholder="请选择" disabled>
    <cc-option
      v-for="item in options"
      :key="item.value"
      :label="item.label"
      :value="item.value"
    />
  </cc-select>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
const options = [
  { value: '选项1', label: '黄金糕' },
  { value: '选项2', label: '双皮奶' },
  { value: '选项3', label: '蚵仔煎' },
  { value: '选项4', label: '龙须面' },
  { value: '选项5', label: '北京烤鸭' }
]
</script>
```

## 可清空

使用 `clearable` 属性可以将选择器清空。

```vue
<template>
  <cc-select v-model="value" placeholder="请选择" clearable>
    <cc-option
      v-for="item in options"
      :key="item.value"
      :label="item.label"
      :value="item.value"
    />
  </cc-select>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
const options = [
  { value: '选项1', label: '黄金糕' },
  { value: '选项2', label: '双皮奶' },
  { value: '选项3', label: '蚵仔煎' },
  { value: '选项4', label: '龙须面' },
  { value: '选项5', label: '北京烤鸭' }
]
</script>
```

## 多选

使用 `multiple` 属性可以开启多选模式。

```vue
<template>
  <cc-select v-model="value" multiple placeholder="请选择">
    <cc-option
      v-for="item in options"
      :key="item.value"
      :label="item.label"
      :value="item.value"
    />
  </cc-select>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref([])
const options = [
  { value: '选项1', label: '黄金糕' },
  { value: '选项2', label: '双皮奶' },
  { value: '选项3', label: '蚵仔煎' },
  { value: '选项4', label: '龙须面' },
  { value: '选项5', label: '北京烤鸭' }
]
</script>
```

## 选择器尺寸

使用 `size` 属性来设置选择器尺寸。

```vue
<template>
  <cc-select v-model="value1" placeholder="请选择" size="large">
    <cc-option
      v-for="item in options"
      :key="item.value"
      :label="item.label"
      :value="item.value"
    />
  </cc-select>
  <cc-select v-model="value2" placeholder="请选择">
    <cc-option
      v-for="item in options"
      :key="item.value"
      :label="item.label"
      :value="item.value"
    />
  </cc-select>
  <cc-select v-model="value3" placeholder="请选择" size="small">
    <cc-option
      v-for="item in options"
      :key="item.value"
      :label="item.label"
      :value="item.value"
    />
  </cc-select>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value1 = ref('')
const value2 = ref('')
const value3 = ref('')
const options = [
  { value: '选项1', label: '黄金糕' },
  { value: '选项2', label: '双皮奶' },
  { value: '选项3', label: '蚵仔煎' },
  { value: '选项4', label: '龙须面' },
  { value: '选项5', label: '北京烤鸭' }
]
</script>
```

## 可搜索

使用 `filterable` 属性可以开启搜索功能。

```vue
<template>
  <cc-select v-model="value" placeholder="请选择" filterable>
    <cc-option
      v-for="item in options"
      :key="item.value"
      :label="item.label"
      :value="item.value"
    />
  </cc-select>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
const options = [
  { value: '选项1', label: '黄金糕' },
  { value: '选项2', label: '双皮奶' },
  { value: '选项3', label: '蚵仔煎' },
  { value: '选项4', label: '龙须面' },
  { value: '选项5', label: '北京烤鸭' }
]
</script>
```

## 分组

使用 `cc-option-group` 组件对选项进行分组。

```vue
<template>
  <cc-select v-model="value" placeholder="请选择">
    <cc-option-group
      v-for="group in options"
      :key="group.label"
      :label="group.label"
    >
      <cc-option
        v-for="item in group.options"
        :key="item.value"
        :label="item.label"
        :value="item.value"
      />
    </cc-option-group>
  </cc-select>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const value = ref('')
const options = [
  {
    label: '热门城市',
    options: [
      { value: 'Shanghai', label: '上海' },
      { value: 'Beijing', label: '北京' }
    ]
  },
  {
    label: '城市名',
    options: [
      { value: 'Chengdu', label: '成都' },
      { value: 'Shenzhen', label: '深圳' },
      { value: 'Guangzhou', label: '广州' },
      { value: 'Dalian', label: '大连' }
    ]
  }
]
</script>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| model-value / v-model | 绑定值 | string / number / boolean / object / array | — | — |
| multiple | 是否多选 | boolean | — | false |
| disabled | 是否禁用 | boolean | — | false |
| value-key | 作为 value 唯一标识的键名 | string | — | value |
| size | 尺寸 | string | large / default / small | default |
| clearable | 是否可以清空选项 | boolean | — | false |
| clear-icon | 自定义清空图标 | string / Component | — | — |
| filterable | 是否可搜索 | boolean | — | false |
| filter-method | 自定义搜索方法 | function | — | — |
| remote | 是否为远程搜索 | boolean | — | false |
| remote-method | 远程搜索方法 | function | — | — |
| loading | 是否正在从远程获取数据 | boolean | — | false |
| loading-text | 远程加载时显示的文本 | string | — | 加载中 |
| no-match-text | 搜索条件无匹配时显示的文本 | string | — | 无匹配数据 |
| no-data-text | 无选项时显示的文本 | string | — | 无数据 |
| placeholder | 占位符 | string | — | 请选择 |
| collapse-tags | 多选时是否将选中值按文字的形式展示 | boolean | — | false |
| collapse-tags-tooltip | 当鼠标悬停于折叠标签的泡沫时，是否显示所有选中的标签 | boolean | — | false |
| default-first-option | 按回车时，选择第一个匹配项 | boolean | — | false |
| reserve-keyword | 多选且可搜索时，是否在选择选项后保留当前的搜索关键词 | boolean | — | false |
| appearance | 选择器外观 | string | smooth /outlined / filled | outlined |
| label | 选择器左侧标签 | string | — | — |
| tag-type | 标签类型 | string | success / info / warning / danger | info |
| validate-event | 是否触发表单验证 | boolean | — | true |
| prefix | 自定义前缀图标 | string / Component | — | — |
| suffix | 自定义后缀图标 | string / Component | — | — |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|---------|
| change | 选中值发生变化时触发 | (value: any) |
| clear | 可清空模式下点击清空按钮时触发 | — |
| visible-change | 下拉框出现/隐藏时触发 | (visible: boolean) |
| remove-tag | 多选模式下移除tag时触发 | (tag: any) |
| focus | 当选择器的输入框获得焦点时触发 | (event: Event) |
| blur | 当选择器的输入框失去焦点时触发 | (event: Event) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 自定义 Options 列表 |
| prefix | 自定义前缀图标组件 |
| suffix | 自定义后缀图标组件 |
| empty | 自定义无选项时的列表 |
| label | 自定义选项标签 |
