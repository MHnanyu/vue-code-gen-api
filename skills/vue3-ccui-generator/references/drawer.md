# Drawer 抽屉

有些时候, `Dialog` 组件并不满足你的需求, `Drawer` 拥有和 `Dialog` 类似的 API, 但是样式不同。

## 基础用法

使用 `v-model` 属性来控制抽屉的显示与关闭。

```vue
<template>
  <cc-button type="primary" @click="drawerVisible = true">打开抽屉</cc-button>
  <cc-drawer v-model="drawerVisible" title="提示" size="500px">
    <span>这是一段内容</span>
  </cc-drawer>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const drawerVisible = ref(false)
</script>
```

## 方向

通过 `direction` 属性控制抽屉打开的方向。

```vue
<template>
  <cc-button type="primary" @click="drawerVisible = true">从右打开</cc-button>
  <cc-drawer v-model="drawerVisible" title="提示" direction="rtl" size="500px">
    <span>从右侧打开的抽屉</span>
  </cc-drawer>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const drawerVisible = ref(false)
</script>
```

## 不显示标题

通过设置 `show-title` 属性为 `false` 来隐藏标题栏。

```vue
<template>
  <cc-button type="primary" @click="drawerVisible = true">打开抽屉</cc-button>
  <cc-drawer v-model="drawerVisible" :show-title="false" size="500px">
    <span>不显示标题的抽屉</span>
  </cc-drawer>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const drawerVisible = ref(false)
</script>
```

## 尺寸

通过 `size` 属性控制抽屉的尺寸。

```vue
<template>
  <cc-button type="primary" @click="drawerVisible = true">打开抽屉</cc-button>
  <cc-drawer v-model="drawerVisible" title="提示" size="30%">
    <span>使用百分比控制尺寸</span>
  </cc-drawer>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const drawerVisible = ref(false)
</script>
```

## 禁用关闭

可以通过 `close-on-click-modal`、`close-on-press-escape`、`show-close` 属性控制关闭行为。

```vue
<template>
  <cc-button type="primary" @click="drawerVisible = true">禁用关闭</cc-button>
  <cc-drawer v-model="drawerVisible" title="提示" size="500px" :close-on-click-modal="false" :show-close="false">
    <span>禁用点击遮罩关闭和显示关闭按钮</span>
  </cc-drawer>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const drawerVisible = ref(false)
</script>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| model-value / v-model | 绑定值 | boolean | — | false |
| title | 抽屉标题 | string | — | — |
| size | 抽屉尺寸 | string / number | — | 30% |
| direction | 抽屉打开方向 | 'ltr' / 'rtl' / 'ttb' / 'btt' | — | rtl |
| show-close | 是否显示关闭按钮 | boolean | — | true |
| close-on-click-modal | 是否可以通过点击遮罩层关闭抽屉 | boolean | — | true |
| close-on-press-escape | 是否可以通过按下 ESC 关闭抽屉 | boolean | — | true |
| destroy-on-close | 关闭时是否销毁抽屉内的内容 | boolean | — | false |
| show-title | 是否显示标题栏 | boolean | — | true |
| append-to-body | 是否将抽屉插入到 body 元素 | boolean | — | false |
| lock-scroll | 是否锁定 body 的滚动 | boolean | — | true |
| custom-class | 自定义类名 | string | — | — |
| wrapperClosable | 点击遮罩层是否关闭抽屉 | boolean | — | true |
| z-index | z-index 层级 | number | — | — |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|---------|
| open | 抽屉打开的回调 | — |
| opened | 抽屉打开动画结束时的回调 | — |
| close | 抽屉关闭的回调 | — |
| closed | 抽屉关闭动画结束时的回调 | — |
| update:model-value | 更新绑定值的回调 | (val: boolean) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 抽屉内容 |
| title | 自定义标题栏内容 |
