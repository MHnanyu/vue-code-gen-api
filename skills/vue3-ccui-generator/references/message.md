# Message 消息提示

## 基本用法

```vue
<template>
  <cc-button @click="handleSuccess">成功消息</cc-button>
</template>

<script setup>
import { CcMessage } from '@/components/Message/index.vue'

const handleSuccess = () => {
  CcMessage.success('这是一条成功消息')
}
</script>
```

## 消息类型

通过不同的方法展示不同类型的消息：

- `CcMessage.success(message, options)` - 成功消息
- `CcMessage.warning(message, options)` - 警告消息
- `CcMessage.error(message, options)` - 错误消息
- `CcMessage.info(message, options)` - 信息消息

## Props

| 参数 | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| message | 消息内容 | string / VNode | - |
| type | 消息类型 | 'success' / 'warning' / 'info' / 'error' | info |
| duration | 显示时间，单位毫秒 | number | 3000 |
| showClose | 是否显示关闭按钮 | boolean | false |
| center | 文字是否居中 | boolean | false |
| offset | 消息距离顶部的偏移量 | number | 20 |
| zIndex | 消息的 z-index | number | - |

## Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| close | 关闭时的回调 | (instance: any) => void |
| click | 点击消息时的回调 | (instance: any) => void |

##  Methods

| 方法名 | 说明 |
|--------|------|
| close | 关闭当前消息 |
| closeAll | 关闭所有消息 |

## 关闭所有消息

```javascript
CcMessage.closeAll()
```
