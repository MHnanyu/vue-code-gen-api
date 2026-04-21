# Image 图片

图片组件，支持预览、懒加载等功能。

## 基础用法

```vue
<template>
  <cc-image src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" :width="300" :height="300" />
</template>
```

## 适应容器

通过 `fit` 属性指定图片适应方式。

```vue
<template>
  <div class="image-fit">
    <cc-image
      v-for="fit in fits"
      :key="fit"
      :fit="fit"
      :src="url"
      :width="100"
      :height="100"
    />
  </div>
</template>

<script setup lang="ts">
const fits = ['fill', 'contain', 'cover', 'none', 'scale-down']
const url = 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
</script>
```

## 懒加载

使用 `lazy` 属性启用懒加载。

```vue
<template>
  <cc-image
    src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
    :width="300"
    :height="300"
    lazy
  />
</template>
```

## 图片预览

使用 `preview-src-list` 属性开启预览功能。

```vue
<template>
  <cc-image
    :src="url"
    :preview-src-list="[url, url2]"
    :width="300"
    :height="300"
  />
</template>

<script setup lang="ts">
const url = 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
const url2 = 'https://cube.elemecdn.com/3/7c/3ea6beec44369c3ddb99c0ee4d6aejpeg.jpeg'
</script>
```

## Props

| 属性名 | 说明 | 类型 | 默认值 |
|--------|------|------|--------|
| src | 图片源 | `string` | - |
| fit | 图片适应方式 | `'fill' \| 'contain' \| 'cover' \| 'none' \| 'scale-down'` | - |
| width | 图片宽度 | `number \| string` | - |
| height | 图片高度 | `number \| string` | - |
| alt | 替代文本 | `string` | - |
| loading | 加载状态 | `'lazy' \| 'eager'` | - |
| lazy | 是否懒加载 | `boolean` | `false` |
| preview-src-list | 预览图片列表 | `string[]` | - |
| initial-index | 初始预览索引 | `number` | `0` |
| hide-on-click-modal | 点击遮罩是否关闭预览 | `boolean` | `false` |
| preview-teleported | 预览是否 teleport | `boolean` | `false` |
| z-index | 预览 z-index | `number` | `2000` |

## Slots

| 插槽名 | 说明 |
|--------|------|
| error | 加载失败时显示的内容 |
| preview | 预览区域自定义内容 |

## Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| load | 图片加载成功时触发 | `(e: Event)` |
| error | 图片加载失败时触发 | `(e: Event)` |
| switch | 切换预览图片时触发 | `(index: number)` |
| close | 关闭预览时触发 | - |
