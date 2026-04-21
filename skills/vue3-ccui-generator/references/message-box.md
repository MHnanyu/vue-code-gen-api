# MessageBox 消息弹框

模拟系统的消息提示弹框，用于消息提示、确认操作和输入内容。

## 消息提示

使用 `alert` 方法弹出消息提示。

```vue
<template>
  <cc-button type="primary" @click="handleAlert">消息提示</cc-button>
</template>

<script setup lang="ts">
import { CcMessageBox } from 'cc-ui'

const handleAlert = async () => {
  await CcMessageBox.alert('这是一条提示信息', '提示')
}
</script>
```

## 确认消息

使用 `confirm` 方法弹出确认弹框。

```vue
<template>
  <cc-button type="primary" @click="handleConfirm">确认消息</cc-button>
</template>

<script setup lang="ts">
import { CcMessageBox } from 'cc-ui'

const handleConfirm = async () => {
  try {
    await CcMessageBox.confirm('此操作将永久删除该文件，是否继续？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    console.log('确认')
  } catch {
    console.log('取消')
  }
}
</script>
```

## 输入框

使用 `prompt` 方法弹出输入弹框。

```vue
<template>
  <cc-button type="primary" @click="handlePrompt">输入框</cc-button>
</template>

<script setup lang="ts">
import { CcMessageBox } from 'cc-ui'

const handlePrompt = async () => {
  try {
    const { value } = await CcMessageBox.prompt('请输入您的姓名', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /.+/,
      inputErrorMessage: '姓名不能为空'
    })
    console.log('输入的值:', value)
  } catch {
    console.log('取消')
  }
}
</script>
```

## 自定义配置

可以通过配置对象自定义弹框样式。

```vue
<template>
  <cc-button type="primary" @click="handleCustom">自定义配置</cc-button>
</template>

<script setup lang="ts">
import { CcMessageBox } from 'cc-ui'

const handleCustom = async () => {
  await CcMessageBox.alertWithOptions({
    title: '自定义标题',
    message: '这是一条自定义配置的消息',
    confirmButtonText: '知道了',
    type: 'success',
    callback: (action) => {
      console.log('action:', action)
    }
  })
}
</script>
```

## 使用 HTML 片段

设置 `dangerouslyUseHTMLString` 为 true 来使用 HTML 片段。

```vue
<template>
  <cc-button type="primary" @click="handleHtml">HTML 内容</cc-button>
</template>

<script setup lang="ts">
import { CcMessageBox } from 'cc-ui'

const handleHtml = async () => {
  await CcMessageBox.alert('<strong style="color: red">这是 HTML 内容</strong>', '提示', {
    dangerouslyUseHTMLString: true
  })
}
</script>
```

## 区分取消和关闭

在有些场景下，用户点击取消和点击关闭按钮，需要区分为两种处理逻辑。

```vue
<template>
  <cc-button type="primary" @click="handleDistinguish">区分取消和关闭</cc-button>
</template>

<script setup lang="ts">
import { CcMessageBox } from 'cc-ui'

const handleDistinguish = async () => {
  try {
    await CcMessageBox.confirm('此操作将永久删除该文件，是否继续？', '提示', {
      distinguishCancelAndClose: true
    })
    console.log('确认')
  } catch (action) {
    console.log('action:', action) // cancel 或 close
  }
}
</script>
```

## 居中布局

设置 `center` 属性让内容居中布局。

```vue
<template>
  <cc-button type="primary" @click="handleCenter">居中布局</cc-button>
</template>

<script setup lang="ts">
import { CcMessageBox } from 'cc-ui'

const handleCenter = async () => {
  await CcMessageBox.alert('这是一条提示信息', '提示', {
    center: true
  })
}
</script>
```

## Methods

| 方法名 | 说明 | 参数 |
|-------|------|------|
| alert | 打开消息提示弹框 | (message: string, title?: string, options?: Options) => Promise |
| confirm | 打开确认弹框 | (message: string, title?: string, options?: Options) => Promise |
| prompt | 打开输入弹框 | (message: string, title?: string, options?: Options) => Promise |
| alertWithOptions | 通过配置对象打开消息提示弹框 | (options: Options) => Promise |
| confirmWithOptions | 通过配置对象打开确认弹框 | (options: Options) => Promise |
| promptWithOptions | 通过配置对象打开输入弹框 | (options: Options) => Promise |
| close | 关闭弹框 | () => void |

## Options

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| title | 标题 | string | — | 提示 |
| message | 消息内容 | string | — | — |
| type | 消息类型 | string | success / warning / info / error | info |
| icon | 自定义图标 | Component | — | — |
| custom-class | 自定义类名 | string | — | — |
| callback | 关闭后的回调 | (action: string) => void | — | — |
| confirmButtonText | 确认按钮文本 | string | — | 确定 |
| cancelButtonText | 取消按钮文本 | string | — | 取消 |
| showClose | 是否显示关闭按钮 | boolean | — | true |
| closeOnClickModal | 是否可以通过点击遮罩关闭 | boolean | — | true |
| closeOnPressEscape | 是否可以通过按下 ESC 关闭 | boolean | — | true |
| distinguishCancelAndClose | 是否区分取消和关闭 | boolean | — | false |
| center | 是否居中布局 | boolean | — | false |
| roundButton | 是否使用圆角按钮 | boolean | — | false |
| dangerouslyUseHTMLString | 是否将 message 作为 HTML 片段处理 | boolean | — | false |
| inputPattern | 输入框的正则表达式 | RegExp | — | — |
| inputValidator | 输入框的验证函数 | (value: string) => boolean / string | — | — |
| inputErrorMessage | 输入框验证失败时的提示文字 | string | — | 输入数据不合法 |
| autofocus | 输入框是否自动聚焦 | boolean | — | false |
