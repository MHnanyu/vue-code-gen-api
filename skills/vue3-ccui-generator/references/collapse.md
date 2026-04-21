# Collapse 折叠面板

通过折叠面板收纳大量区域内容。

## 基础用法

可同时展开多个面板，面板之间不影响。

```vue
<template>
  <cc-collapse>
    <cc-collapse-item title="一致性 Consistency" name="1">
      <div>与现实生活一致：与现实生活的流程、逻辑保持一致，遵循用户习惯的语言和概念；</div>
      <div>在界面中一致：所有的元素和结构需保持一致，或者有直接的关联。</div>
    </cc-collapse-item>
    <cc-collapse-item title="反馈 Feedback" name="2">
      <div>控制反馈：通过界面样式和交互动效让用户可以清晰的感知自己的操作；</div>
      <div>页面反馈：操作后，通过页面元素的变化与用户进行持续对话。</div>
    </cc-collapse-item>
    <cc-collapse-item title="效率 Efficiency" name="3">
      <div>简化流程：设计简洁直观的操作流程；</div>
      <div>清晰明确：语言表达清晰且表意明确；</div>
      <div>帮助用户识别：界面简单直观的表达重要信息。</div>
    </cc-collapse-item>
    <cc-collapse-item title="可控 Controllability" name="4">
      <div>用户决策：根据场景可给予用户操作建议或安全提示，但不能代替用户进行决策；</div>
      <div>结果可控：用户可以自由的进行操作，包括撤销、回退和终止当前操作等。</div>
    </cc-collapse-item>
  </cc-collapse>
</template>
```

## 手风琴效果

每次只能展开一个面板，通过 `accordion` 属性来控制开启。

```vue
<template>
  <cc-collapse accordion>
    <cc-collapse-item title="一致性 Consistency" name="1">
      <div>与现实生活一致：与现实生活的流程、逻辑保持一致，遵循用户习惯的语言和概念；</div>
    </cc-collapse-item>
    <cc-collapse-item title="反馈 Feedback" name="2">
      <div>控制反馈：通过界面样式和交互动效让用户可以清晰的感知自己的操作；</div>
    </cc-collapse-item>
    <cc-collapse-item title="效率 Efficiency" name="3">
      <div>简化流程：设计简洁直观的操作流程；</div>
    </cc-collapse-item>
  </cc-collapse>
</template>
```

## 面板标题

除了可以通过 `title` 属性设置标题，还可以通过 `title` 插槽自定义标题。

```vue
<template>
  <cc-collapse>
    <cc-collapse-item name="1">
      <template #title>
        <span>一致性 Consistency</span>
        <cc-icon class="header-icon"><InfoFilled /></cc-icon>
      </template>
      <div>与现实生活一致：与现实生活的流程、逻辑保持一致，遵循用户习惯的语言和概念；</div>
    </cc-collapse-item>
    <cc-collapse-item title="反馈 Feedback" name="2">
      <div>控制反馈：通过界面样式和交互动效让用户可以清晰的感知自己的操作；</div>
    </cc-collapse-item>
    <cc-collapse-item title="效率 Efficiency" name="3">
      <div>简化流程：设计简洁直观的操作流程；</div>
    </cc-collapse-item>
  </cc-collapse>
</template>
```

## 折叠面板嵌套

折叠面板可以嵌套使用。

```vue
<template>
  <cc-collapse accordion>
    <cc-collapse-item title="一级 1" name="1">
      <cc-collapse>
        <cc-collapse-item title="二级 1-1" name="1-1">
          <div>这是二级 1-1 的内容</div>
        </cc-collapse-item>
        <cc-collapse-item title="二级 1-2" name="1-2">
          <div>这是二级 1-2 的内容</div>
        </cc-collapse-item>
      </cc-collapse>
    </cc-collapse-item>
    <cc-collapse-item title="一级 2" name="2">
      <div>这是一级 2 的内容</div>
    </cc-collapse-item>
    <cc-collapse-item title="一级 3" name="3">
      <div>这是一级 3 的内容</div>
    </cc-collapse-item>
  </cc-collapse>
</template>
```

## 自定义面板标题内容

可以在标题区域添加图标或自定义操作。

```vue
<template>
  <cc-collapse>
    <cc-collapse-item name="1">
      <template #title>
        <span>一致性 Consistency</span>
        <cc-tag size="small" type="primary">推荐</cc-tag>
      </template>
      <div>与现实生活一致：与现实生活的流程、逻辑保持一致，遵循用户习惯的语言和概念；</div>
    </cc-collapse-item>
    <cc-collapse-item title="反馈 Feedback" name="2">
      <div>控制反馈：通过界面样式和交互动效让用户可以清晰的感知自己的操作；</div>
    </cc-collapse-item>
    <cc-collapse-item title="效率 Efficiency" name="3">
      <div>简化流程：设计简洁直观的操作流程；</div>
    </cc-collapse-item>
  </cc-collapse>
</template>
```

## 禁用状态

通过 `disabled` 属性禁用指定面板。

```vue
<template>
  <cc-collapse>
    <cc-collapse-item title="一致性 Consistency" name="1">
      <div>与现实生活一致：与现实生活的流程、逻辑保持一致，遵循用户习惯的语言和概念；</div>
    </cc-collapse-item>
    <cc-collapse-item title="反馈 Feedback" name="2" disabled>
      <div>控制反馈：通过界面样式和交互动效让用户可以清晰的感知自己的操作；</div>
    </cc-collapse-item>
    <cc-collapse-item title="效率 Efficiency" name="3">
      <div>简化流程：设计简洁直观的操作流程；</div>
    </cc-collapse-item>
  </cc-collapse>
</template>
```

## 折叠面板 Attributes

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| accordion | 是否手风琴模式 | boolean | — | false |
| modelValue / v-model | 当前激活的面板(如果是手风琴模式，绑定值为字符串类型，否则为数组) | string[] | — | — |
| border | 是否显示边框 | boolean | — | true |

## 折叠面板 Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------- |
| change | 切换面板时触发 | (activeNames: string[]) |

## 折叠面板 Slots

| 插槽名 | 说明 |
|-------|------|
| default | 默认插槽 |

## 折叠面板 Item Attributes

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| title | 面板标题 | string | — | — |
| name | 唯一标志符，默认为面板的顺序索引 | string | — | — |
| disabled | 是否禁用 | boolean | — | false |

## 折叠面板 Item Slots

| 插槽名 | 说明 |
|-------|------|
| default | 面板内容 |
| title | 面板标题 |
| extra | 面板标题右侧额外内容 |
