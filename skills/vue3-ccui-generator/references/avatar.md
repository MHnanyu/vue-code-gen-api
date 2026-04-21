# Avatar 头像

头像组件，用于展示用户头像或占位符。

## 基础用法

通过 `src` 属性指定头像图片地址。

```vue
<cc-avatar src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"></cc-avatar>
```

## 不同尺寸

通过 `size` 属性设置头像尺寸，支持数字和字符串类型。

```vue
<cc-avatar :size="50" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"></cc-avatar>
<cc-avatar size="small" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"></cc-avatar>
<cc-avatar size="medium" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"></cc-avatar>
<cc-avatar size="large" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"></cc-avatar>
```

## 圆形头像

通过 `shape` 属性设置头像形状。

```vue
<cc-avatar shape="circle" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"></cc-avatar>
<cc-avatar shape="square" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"></cc-avatar>
```

## 头像占位符

当图片加载失败或未提供 `src` 时，显示占位符内容。

```vue
<cc-avatar>User</cc-avatar>
<cc-avatar src="">User</cc-avatar>
```

## Props

| 属性名 | 说明 | 类型 | 默认值 |
|--------|------|------|--------|
| size | 头像大小 | number / 'small' / 'medium' / 'large' | 'large' |
| shape | 头像形状 | 'circle' / 'square' | 'circle' |
| src | 图片地址 | string | - |
| srcSet | 图片 srcSet | string | - |
| alt | 图片 alt | string | - |
| fit | 图片适配方式 | 'fill' / 'contain' / 'cover' / 'none' / 'scale-down' | 'cover' |

## Slots

| 插槽名 | 说明 |
|--------|------|
| default | 头像内容，当 src 加载失败时显示 |

## Events

| 事件名 | 说明 | 回调参数 |
|--------|------|----------|
| error | 图片加载失败时触发 | (e: Event) |
