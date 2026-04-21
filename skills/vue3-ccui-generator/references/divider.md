# Divider 分割线

用于分隔内容的分割线。

## 基础用法

对不同章节的文本段落进行分割。

```vue
<template>
  <div>
    <p>我奔跑，我攀爬，我会飞翔。</p>
    <p>永不言败。</p>
    <cc-divider />
    <p>我奔跑，我攀爬，我会飞翔。</p>
    <p>永不言败。</p>
  </div>
</template>
```

## 设置文案

可以在分割线上自定义文案内容。

```vue
<template>
  <div>
    <p>我奔跑，我攀爬，我会飞翔。</p>
    <p>永不言败。</p>
    <cc-divider content-position="left">分割线</cc-divider>
    <p>我奔跑，我攀爬，我会飞翔。</p>
    <p>永不言败。</p>
    <cc-divider content-position="center">分割线</cc-divider>
    <p>我奔跑，我攀爬，我会飞翔。</p>
    <p>永不言败。</p>
    <cc-divider content-position="right">分割线</cc-divider>
  </div>
</template>
```

## 垂直分割

```vue
<template>
  <div>
    <span>雨纷纷</span>
    <cc-divider direction="vertical" />
    <span>旧故里</span>
    <cc-divider direction="vertical" />
    <span>草木深</span>
  </div>
</template>
```

## 设置分割线样式

可设置分割线的样式。

```vue
<template>
  <div>
    <p>我奔跑，我攀爬，我会飞翔。</p>
    <p>永不言败。</p>
    <cc-divider border-style="dashed" />
    <p>我奔跑，我攀爬，我会飞翔。</p>
    <p>永不言败。</p>
    <cc-divider border-style="dotted" />
    <p>我奔跑，我攀爬，我会飞翔。</p>
    <p>永不言败。</p>
  </div>
</template>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| direction | 设置分割线方向 | string | horizontal / vertical | horizontal |
| border-style | 设置分割线样式 | string | — | solid |
| content-position | 设置分割线文案的位置 | string | left / right / center | center |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 自定义默认内容 |
