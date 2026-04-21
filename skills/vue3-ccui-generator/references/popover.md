# Popover 气泡卡片

弹出式卡片，用于展示更复杂的内容。

## 基础用法

```vue
<template>
  <cc-popover
    title="标题"
    content="这是一段内容"
  >
    <template #reference>
      <cc-button>点击弹出</cc-button>
    </template>
  </cc-popover>
</template>
```

## 触发方式

可以通过 `trigger` 属性设置触发方式。

```vue
<template>
  <cc-popover
    trigger="click"
    content="点击触发"
  >
    <template #reference>
      <cc-button>click 触发</cc-button>
    </template>
  </cc-popover>
  
  <cc-popover
    trigger="hover"
    content="hover 触发"
  >
    <template #reference>
      <cc-button>hover 触发</cc-button>
    </template>
  </cc-popover>
  
  <cc-popover
    trigger="focus"
    content="focus 触发"
  >
    <template #reference>
      <cc-button>focus 触发</cc-button>
    </template>
  </cc-popover>
  
  <cc-popover
    trigger="manual"
    v-model="visible"
    content="手动触发"
  >
    <template #reference>
      <cc-button @click="visible = !visible">manual 触发</cc-button>
    </template>
  </cc-popover>
</template>
```

## 展示位置

通过 `placement` 属性设置弹出位置。

```vue
<template>
  <cc-popover
    placement="top"
    content="top"
  >
    <template #reference>
      <cc-button>top</cc-button>
    </template>
  </cc-popover>
  
  <cc-popover
    placement="top-start"
    content="top-start"
  >
    <template #reference>
      <cc-button>top-start</cc-button>
    </template>
  </cc-popover>
  
  <cc-popover
    placement="top-end"
    content="top-end"
  >
    <template #reference>
      <cc-button>top-end</cc-button>
    </template>
  </cc-popover>
  
  <cc-popover
    placement="bottom"
    content="bottom"
  >
    <template #reference>
      <cc-button>bottom</cc-button>
    </template>
  </cc-popover>
  
  <cc-popover
    placement="left"
    content="left"
  >
    <template #reference>
      <cc-button>left</cc-button>
    </template>
  </cc-popover>
  
  <cc-popover
    placement="right"
    content="right"
  >
    <template #reference>
      <cc-button>right</cc-button>
    </template>
  </cc-popover>
</template>
```

## 嵌套复杂内容

可以通过默认插槽嵌套任意内容。

```vue
<template>
  <cc-popover width="200">
    <template #reference>
      <cc-button>嵌套复杂内容</cc-button>
    </template>
    <div class="custom-content">
      <p>用户名: admin</p>
      <p>角色: 管理员</p>
      <p>状态: 正常</p>
    </div>
  </cc-popover>
</template>

<style scoped>
.custom-content p {
  margin: 5px 0;
  font-size: 14px;
}
</style>
```

## 嵌套操作

可以在 Popover 中嵌套操作按钮。

```vue
<template>
  <cc-popover width="200">
    <template #reference>
      <cc-button>操作 Popover</cc-button>
    </template>
    <div class="action-content">
      <p>确定要执行此操作吗？</p>
      <div class="action-buttons">
        <cc-button size="small" @click="handleCancel">取消</cc-button>
        <cc-button size="small" type="primary" @click="handleConfirm">确定</cc-button>
      </div>
    </div>
  </cc-popover>
</template>

<style scoped>
.action-content p {
  margin-bottom: 10px;
}
.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
```

## 禁用

通过 `disabled` 属性禁用 Popover。

```vue
<template>
  <cc-popover
    disabled
    content="禁用状态"
  >
    <template #reference>
      <cc-button>禁用</cc-button>
    </template>
  </cc-popover>
</template>
```

## Attributes

| 参数 | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| trigger | 触发方式 | 'click' / 'hover' / 'focus' / 'manual' | 'click' |
| title | 标题 | string | — |
| content | 内容 | string | — |
| placement | 弹出位置 | 'top' / 'top-start' / 'top-end' / 'bottom' / 'bottom-start' / 'bottom-end' / 'left' / 'left-start' / 'left-end' / 'right' / 'right-start' / 'right-end' | 'bottom' |
| width | 宽度 | string / number | 最小 150px |
| disabled | 是否禁用 | boolean | false |
| visible / v-model | 手动控制显示状态 | boolean | false |
| offset | 偏移量 | number | 0 |
| transition | 动画名称 | string | fade-transform |
| show-after | 显示延迟，单位毫秒 | number | 0 |
| hide-after | 隐藏延迟，单位毫秒 | number | 200 |
| auto-close | 鼠标离开后隐藏延迟，单位毫秒 | number | 0 |
| show-arrow | 是否显示箭头 | boolean | true |
| arrow-offset | 箭头偏移量 | number | 0 |
| popper-options | popper.js 参数 | object | {} |
| tabindex | Popover 虚拟节点 tabindex | number / string | 0 |
| teleported | 是否插入到 body | boolean | true |
| persistent | 当 Popover 关闭时，是否强制销毁 | boolean | true |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | Popover 内容 |
| reference | Popover 触发元素 |

## Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| show | 显示时触发 | — |
| hide | 隐藏时触发 | — |
