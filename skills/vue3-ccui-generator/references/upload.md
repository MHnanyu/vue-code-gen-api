# Upload 上传

文件选择上传和拖拽上传。

## 基础用法

使用 `action` 属性设置上传地址。

```vue
<template>
  <cc-upload
    action="https://run.mocky.io/v3/435e224c-44fb-4773-9faf-380c5e6a2188"
    :limit="3"
    accept=".jpg,.png,.pdf"
  >
    <cc-button type="primary">点击上传</cc-button>
  </cc-upload>
</template>
```

## 拖拽上传

使用 `drag` 属性启用拖拽上传功能。

```vue
<template>
  <cc-upload
    drag
    action="https://run.mocky.io/v3/435e224c-44fb-4773-9faf-380c5e6a2188"
    multiple
  >
    <cc-icon :icon="UploadFilled" :size="40" />
    <div class="upload-text">
      将文件拖到此处，或<em>点击上传</em>
    </div>
    <template #tip>
      <div class="upload-tip">
        jpg/png 文件且不超过 500kb
      </div>
    </template>
  </cc-upload>
</template>

<script setup lang="ts">
import { UploadFilled } from '@element-plus/icons-vue'
</script>

<style scoped>
.upload-text {
  text-align: center;
  margin-top: 10px;
}
.upload-tip {
  text-align: center;
  color: #999;
  font-size: 12px;
  margin-top: 10px;
}
</style>
```

## 照片墙

使用 `list-type` 属性设置为 `picture-card` 来实现照片墙模式。

```vue
<template>
  <cc-upload
    action="https://run.mocky.io/v3/435e224c-44fb-4773-9faf-380c5e6a2188"
    list-type="picture-card"
    :limit="5"
    v-model:file-list="fileList"
  >
    <cc-icon :icon="Plus" />
  </cc-upload>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Plus } from '@element-plus/icons-vue'

interface UploadFile {
  name: string
  url: string
}

const fileList = ref<UploadFile[]>([
  {
    name: 'food.jpeg',
    url: 'https://fuss10.elemecdn.com/3/63/4e696f65c9854189c9e6f2c06dae7jpeg.jpeg?imageMogr2/thumbnail/360x360'
  },
  {
    name: 'food2.jpeg',
    url: 'https://fuss10.elemecdn.com/3/63/4e696f65c9854189c9e6f2c06dae7jpeg.jpeg?imageMogr2/thumbnail/360x360'
  }
])
</script>
```

## 手动上传

使用 `auto-upload` 属性设置为 `false` 来禁用自动上传，手动控制上传时机。

```vue
<template>
  <cc-upload
    ref="uploadRef"
    action="https://run.mocky.io/v3/435e224c-44fb-4773-9faf-380c5e6a2188"
    :auto-upload="false"
    :limit="3"
  >
    <cc-button type="primary">选择文件</cc-button>
    <template #tip>
      <div class="upload-tip" style="margin-top: 10px;">
        支持 jpg/png 格式，不超过 500kb
      </div>
    </template>
  </cc-upload>
  <div style="margin-top: 10px;">
    <cc-button type="primary" @click="submitUpload">开始上传</cc-button>
    <cc-button @click="clearFiles">清空文件</cc-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const uploadRef = ref()

const submitUpload = () => {
  uploadRef.value?.submit()
}

const clearFiles = () => {
  uploadRef.value?.clearFiles()
}
</script>

<style scoped>
.upload-tip {
  color: #999;
  font-size: 12px;
}
</style>
```

## 禁用状态

使用 `disabled` 属性禁用上传组件。

```vue
<template>
  <cc-upload
    action="https://run.mocky.io/v3/435e224c-44fb-4773-9faf-380c5e6a2188"
    disabled
  >
    <cc-button disabled>点击上传</cc-button>
  </cc-upload>
</template>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| action | 上传请求 URL | string | — | — |
| method | 上传请求的 HTTP 方法 | string | post / put | post |
| headers | 设置上传的请求头部 | object | — | {} |
| data | 上传时附带的额外参数 | object | — | {} |
| multiple | 是否支持多选文件 | boolean | — | false |
| drag | 是否启用拖拽上传 | boolean | — | false |
| accept | 接受上传的文件类型 | string | — | — |
| limit | 限制上传文件数量 | number | — | — |
| auto-upload | 是否在选取文件后立即上传 | boolean | — | true |
| file-list | 上传文件列表 | UploadUserFile[] | — | [] |
| disabled | 是否禁用 | boolean | — | false |
| list-type | 文件列表的类型 | string | text / picture / picture-card | text |
| show-file-list | 是否显示文件列表 | boolean | — | true |
| drag | 是否启用拖拽上传 | boolean | — | false |
| with-credentials | 是否支持发送 cookie 凭证信息 | boolean | — | false |
| name | 上传的文件字段名 | string | — | file |
| timeout | 上传超时时间（毫秒） | number | — | — |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|--------|
| change | 文件状态改变时的钩子 | (file: UploadFile, fileList: UploadFile[]) |
| remove | 文件列表中移除文件时的钩子 | (file: UploadFile) |
| success | 文件上传成功时的钩子 | (response: any, file: UploadFile) |
| error | 文件上传失败时的钩子 | (error: Error, file: UploadFile) |
| progress | 文件上传时的钩子 | (event: ProgressEvent, file: UploadFile) |
| exceed | 文件超出个数限制时的钩子 | (files: File[], fileList: UploadFile[]) |

## Slots

| 插槽名 | 说明 |
|-------|------|
| default | 触发上传组件的控件 |
| trigger | 自定义触发文件上传的内容 |
| tip | 提示说明文字 |
| file | 自定义文件列表中显示的内容 |
