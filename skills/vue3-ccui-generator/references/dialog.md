# Dialog 对话框

在保留当前页面状态的情况下，告知用户并承载相关操作。

## 基础用法

使用 `v-model` 属性来控制对话框的显示与关闭。

```vue
<template>
  <cc-button type="primary" @click="dialogVisible = true">打开对话框</cc-button>
  <cc-dialog v-model="dialogVisible" title="提示" width="500px">
    <span>这是一段内容</span>
    <template #footer>
      <span class="dialog-footer">
        <cc-button @click="dialogVisible = false">取消</cc-button>
        <cc-button type="primary" @click="dialogVisible = false">确定</cc-button>
      </span>
    </template>
  </cc-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const dialogVisible = ref(false)
</script>
```

## 不显示标题

通过设置 `show-title` 属性为 `false` 来隐藏标题栏。

```vue
<template>
  <cc-button type="primary" @click="dialogVisible = true">打开对话框</cc-button>
  <cc-dialog v-model="dialogVisible" :show-title="false">
    <span>不显示标题的对话框</span>
  </cc-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const dialogVisible = ref(false)
</script>
```

## 居中对话框

设置 `center` 属性可以让标题和底部居中。

```vue
<template>
  <cc-button type="primary" @click="dialogVisible = true">居中对话框</cc-button>
  <cc-dialog v-model="dialogVisible" title="提示" width="500px" center>
    <span>内容居中的对话框</span>
  </cc-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const dialogVisible = ref(false)
</script>
```

## 禁用关闭

可以通过 `close-on-click-modal`、`close-on-press-escape`、`show-close` 属性控制关闭行为。

```vue
<template>
  <cc-button type="primary" @click="dialogVisible = true">禁用关闭</cc-button>
  <cc-dialog v-model="dialogVisible" title="提示" width="500px" :close-on-click-modal="false" :show-close="false">
    <span>禁用点击遮罩关闭和显示关闭按钮</span>
  </cc-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const dialogVisible = ref(false)
</script>
```

## 打开动画

通过 `append-to-body` 属性将对话框插入到 body 元素。

```vue
<template>
  <cc-button type="primary" @click="dialogVisible = true">打开对话框</cc-button>
  <cc-dialog v-model="dialogVisible" title="提示" width="500px" append-to-body>
    <span>对话框已插入到 body</span>
  </cc-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const dialogVisible = ref(false)
</script>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| model-value / v-model | 绑定值 | boolean | — | false |
| title | 对话框标题 | string | — | — |
| width | 对话框宽度 | string / number | — | 50% |
| fullscreen | 是否全屏显示 | boolean | — | false |
| modal | 是否显示遮罩层 | boolean | — | true |
| close-on-click-modal | 是否可以通过点击遮罩层关闭对话框 | boolean | — | true |
| close-on-press-escape | 是否可以通过按下 ESC 关闭对话框 | boolean | — | true |
| show-close | 是否显示关闭按钮 | boolean | — | true |
| center | 是否居中显示 | boolean | — | false |
| destroy-on-close | 关闭时是否销毁对话框内的内容 | boolean | — | false |
| show-title | 是否显示标题栏 | boolean | — | true |
| append-to-body | 是否将对话框插入到 body 元素 | boolean | — | false |
| lock-scroll | 是否锁定 body 的滚动 | boolean | — | true |
| custom-class | 自定义类名 | string | — | — |
| top | 距离顶部的距离（仅在非全屏模式下有效） | string | — | 15vh |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|---------|
| open | 对话框打开的回调 | — |
| opened | 对话框打开动画结束时的回调 | — |
| close | 对话框关闭的回调 | — |
| closed | 对话框关闭动画结束时的回调 | — |
| update:model-value | 更新绑定值的回调 | (val: boolean) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 对话框内容 |
| title | 自定义标题栏内容 |
| footer | 自定义底部内容 |
