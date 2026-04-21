# Form 表单

由输入框、选择器、单选框、多选框等控件组成，用以收集、校验、提交数据。

## 基础用法

表单组件需要配合表单项组件一起使用。

```vue
<template>
  <cc-form :model="form" label-width="80px">
    <cc-form-item label="姓名">
      <cc-input v-model="form.name" placeholder="请输入姓名" />
    </cc-form-item>
    <cc-form-item label="邮箱">
      <cc-input v-model="form.email" placeholder="请输入邮箱" />
    </cc-form-item>
  </cc-form>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

const form = reactive({
  name: '',
  email: ''
})
</script>
```

## 表单验证

使用 rules 属性定义验证规则。

```vue
<template>
  <cc-form ref="formRef" :model="form" :rules="rules" label-width="80px">
    <cc-form-item label="姓名" prop="name">
      <cc-input v-model="form.name" placeholder="请输入姓名" />
    </cc-form-item>
    <cc-form-item label="邮箱" prop="email">
      <cc-input v-model="form.email" placeholder="请输入邮箱" />
    </cc-form-item>
    <cc-form-item>
      <cc-button type="primary" @click="submitForm">提交</cc-button>
      <cc-button @click="resetForm">重置</cc-button>
    </cc-form-item>
  </cc-form>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'

interface FormInstance {
  validate: () => Promise<void>
  resetFields: () => void
}

interface FormRules {
  [key: string]: Array<{ required?: boolean; message?: string; trigger?: string; type?: string }>
}

const formRef = ref<FormInstance>()
const form = reactive({
  name: '',
  email: ''
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  console.log('提交成功')
}

const resetForm = () => {
  formRef.value?.resetFields()
}
</script>
```

## 行内表单

设置 `inline` 属性使表单变为行内表单。

```vue
<template>
  <cc-form :model="form" inline>
    <cc-form-item label="姓名">
      <cc-input v-model="form.name" placeholder="请输入姓名" />
    </cc-form-item>
    <cc-form-item>
      <cc-button type="primary" @click="onSubmit">查询</cc-button>
    </cc-form-item>
  </cc-form>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

const form = reactive({
  name: ''
})

const onSubmit = () => {
  console.log('查询')
}
</script>
```

## 对齐方式

通过 `label-position` 属性设置标签的位置。

```vue
<template>
  <cc-form :model="form" label-position="left" label-width="100px">
    <cc-form-item label="姓名">
      <cc-input v-model="form.name" />
    </cc-form-item>
    <cc-form-item label="邮箱">
      <cc-input v-model="form.email" />
    </cc-form-item>
  </cc-form>
</template>
```

## 表单尺寸

通过 `size` 属性设置表单组件的尺寸。

```vue
<template>
  <cc-form :model="form" size="large" label-width="80px">
    <cc-form-item label="姓名">
      <cc-input v-model="form.name" />
    </cc-form-item>
  </cc-form>

  <cc-form :model="form" size="default" label-width="80px">
    <cc-form-item label="姓名">
      <cc-input v-model="form.name" />
    </cc-form-item>
  </cc-form>

  <cc-form :model="form" size="small" label-width="80px">
    <cc-form-item label="姓名">
      <cc-input v-model="form.name" />
    </cc-form-item>
  </cc-form>
</template>
```

## Props

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|-----|------|------|-------|-------|
| model | 表单数据对象 | object | — | — |
| rules | 表单验证规则 | object | — | — |
| inline | 是否为行内表单 | boolean | — | false |
| label-position | 标签的位置 | string | left / right / top | right |
| label-width | 标签的宽度 | string / number | — | — |
| label-suffix | 标签后缀 | string | — | — |
| hide-required-asterisk | 是否隐藏必填字段的星号 | boolean | — | false |
| show-message | 是否显示校验错误信息 | boolean | — | true |
| inline-message | 是否以行内形式展示校验信息 | boolean | — | false |
| status-icon | 是否在输入框中显示校验结果图标 | boolean | — | false |
| validate-on-rule-change | 是否在 rules 属性改变后立即触发验证 | boolean | — | true |
| size | 表单组件的尺寸 | string | large / default / small | — |
| disabled | 是否禁用表单内的所有组件 | boolean | — | false |
| scroll-to-error | 验证失败时是否滚动到错误字段 | boolean | — | false |

## Events

| 事件名 | 说明 | 回调参数 |
|------|------|---------|
| validate | 任一表单项被校验后触发 | (prop: string, isValid: boolean, message: string) |

## Methods

| 方法名 | 说明 | 参数 |
|------|------|------|
| validate | 验证整个表单 | (callback?: (isValid: boolean) => void) |
| validateField | 验证指定字段 | (props: string \| string[], callback?: (errorMessage: string) => void) |
| clearValidate | 清除验证结果 | (props?: string \| string[]) |
| resetFields | 重置表单 | — |
