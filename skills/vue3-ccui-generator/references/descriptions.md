# Descriptions 描述列表

列表形式展示多个字段。

## 基础用法

```vue
<template>
  <cc-descriptions title="用户信息">
    <cc-descriptions-item label="用户名">kooriookami</cc-descriptions-item>
    <cc-descriptions-item label="手机号">18100000000</cc-descriptions-item>
    <cc-descriptions-item label="居住地">苏州</cc-descriptions-item>
    <cc-descriptions-item label="备注">学校</cc-descriptions-item>
    <cc-descriptions-item label="地址">
      江苏省苏州市吴中区吴中大道1188号
    </cc-descriptions-item>
  </cc-descriptions>
</template>
```

## 不同尺寸

通过 `size` 属性设置尺寸，通过 `border` 属性设置是否显示边框。

```vue
<template>
  <cc-descriptions
    class="margin-top"
    title="带边框"
    :column="3"
    :size="size"
    border
  >
    <template #extra>
      <cc-button type="primary">操作</cc-button>
    </template>
    <cc-descriptions-item label="用户名">kooriookami</cc-descriptions-item>
    <cc-descriptions-item label="手机号">18100000000</cc-descriptions-item>
    <cc-descriptions-item label="居住地">苏州</cc-descriptions-item>
    <cc-descriptions-item label="备注">学校</cc-descriptions-item>
    <cc-descriptions-item label="地址">
      江苏省苏州市吴中区吴中大道1188号
    </cc-descriptions-item>
  </cc-descriptions>

  <cc-descriptions
    class="margin-top"
    title="无边框"
    :column="3"
    :size="size"
  >
    <template #extra>
      <cc-button type="primary">操作</cc-button>
    </template>
    <cc-descriptions-item label="用户名">kooriookami</cc-descriptions-item>
    <cc-descriptions-item label="手机号">18100000000</cc-descriptions-item>
    <cc-descriptions-item label="居住地">苏州</cc-descriptions-item>
    <cc-descriptions-item label="备注">学校</cc-descriptions-item>
    <cc-descriptions-item label="地址">
      江苏省苏州市吴中区吴中大道1188号
    </cc-descriptions-item>
  </cc-descriptions>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const size = ref('default')
</script>

<style scoped>
.margin-top {
  margin-top: 20px;
}
</style>
```

## 垂直列表

通过 `direction` 属性设置排列方向。

```vue
<template>
  <cc-descriptions
    title="垂直列表带边框"
    direction="vertical"
    :column="4"
    border
  >
    <cc-descriptions-item label="用户名">kooriookami</cc-descriptions-item>
    <cc-descriptions-item label="手机号">18100000000</cc-descriptions-item>
    <cc-descriptions-item label="居住地" :span="2">苏州</cc-descriptions-item>
    <cc-descriptions-item label="备注">学校</cc-descriptions-item>
    <cc-descriptions-item label="地址">
      江苏省苏州市吴中区吴中大道1188号
    </cc-descriptions-item>
  </cc-descriptions>
</template>
```

## 单元格跨行

通过 `rowspan` 属性设置单元格跨越的行数。

```vue
<template>
  <cc-descriptions title="水平列表" border>
    <cc-descriptions-item
      :rowspan="2"
      :width="140"
      label="头像"
      align="center"
    >
      <img
        style="width: 100px; height: 100px"
        src="https://example.com/avatar.png"
      />
    </cc-descriptions-item>
    <cc-descriptions-item label="用户名">kooriookami</cc-descriptions-item>
    <cc-descriptions-item label="手机号">18100000000</cc-descriptions-item>
    <cc-descriptions-item label="居住地">苏州</cc-descriptions-item>
    <cc-descriptions-item label="备注">学校</cc-descriptions-item>
    <cc-descriptions-item label="地址">
      江苏省苏州市吴中区吴中大道1188号
    </cc-descriptions-item>
  </cc-descriptions>
</template>
```

## 自定义样式

通过 `label-class-name` 和 `class-name` 属性自定义样式。

```vue
<template>
  <cc-descriptions title="自定义样式列表" :column="3" border>
    <cc-descriptions-item
      label="用户名"
      label-align="right"
      align="center"
      label-class-name="my-label"
      class-name="my-content"
      width="150px"
    >
      kooriookami
    </cc-descriptions-item>
    <cc-descriptions-item label="手机号" label-align="right" align="center">
      18100000000
    </cc-descriptions-item>
    <cc-descriptions-item label="居住地" label-align="right" align="center">
      苏州
    </cc-descriptions-item>
    <cc-descriptions-item label="备注" label-align="right" align="center">
      学校
    </cc-descriptions-item>
    <cc-descriptions-item label="地址" label-align="right" align="center">
      江苏省苏州市吴中区吴中大道1188号
    </cc-descriptions-item>
  </cc-descriptions>
</template>

<style scoped>
:deep(.my-label) {
  background: #e1f3d8 !important;
}
:deep(.my-content) {
  background: #fde2e2;
}
</style>
```

## Descriptions Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| border | 是否带有边框 | boolean | — | false |
| column | 一行 Descriptions Item 的数量 | number | — | 3 |
| direction | 排列的方向 | string | horizontal / vertical | horizontal |
| size | 列表的尺寸 | string | large / default / small | — |
| title | 标题文本，显示在左上方 | string | — | '' |
| extra | 操作区文本，显示在右上方 | string | — | '' |
| label-width | 每一列的标签宽度 | string / number | — | — |

## Descriptions Slots

| 插槽名 | 说明 |
|-------|------|
| default | 自定义默认内容 |
| title | 自定义标题，显示在左上方 |
| extra | 自定义操作区，显示在右上方 |

## DescriptionsItem Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| label | 标签文本 | string | — | '' |
| span | 列的数量 | number | — | 1 |
| rowspan | 单元格应该跨越的行数 | number | — | 1 |
| width | 列的宽度 | string / number | — | '' |
| min-width | 列的最小宽度 | string / number | — | '' |
| label-width | 列标签宽 | string / number | — | — |
| align | 列的内容对齐方式 | string | left / center / right | left |
| label-align | 列的标签对齐方式 | string | left / center / right | — |
| class-name | 列的内容自定义类名 | string | — | '' |
| label-class-name | 列的标签自定义类名 | string | — | '' |

## DescriptionsItem Slots

| 插槽名 | 说明 |
|-------|------|
| default | 自定义默认内容 |
| label | 自定义标签 |
