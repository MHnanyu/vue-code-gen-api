from app.schemas.generate import GeneratedFile, StageResult


MOCK_ITERATE_FILES = [
    GeneratedFile(
        id="mock-main-page",
        name="MainPage.vue",
        path="/src/MainPage.vue",
        type="file",
        language="vue",
        content="""<template>
  <div class="main-page">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>用户列表</span>
          <el-button type="primary" @click="handleAdd">新增用户</el-button>
        </div>
      </template>
      <el-table :data="tableData" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">
              {{ scope.row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        class="pagination"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, sizes, prev, pager, next"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const tableData = ref([
  { id: 1, name: '张三', email: 'zhangsan@example.com', status: 'active' },
  { id: 2, name: '李四', email: 'lisi@example.com', status: 'inactive' },
  { id: 3, name: '王五', email: 'wangwu@example.com', status: 'active' },
])

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(100)

function handleAdd() {
  console.log('新增用户')
}

function handleEdit(row: any) {
  console.log('编辑用户:', row)
}

function handleDelete(row: any) {
  console.log('删除用户:', row)
}
</script>

<style scoped>
.main-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>"""
    )
]

MOCK_ITERATE_MESSAGE = "迭代生成完成（Mock 数据）"

MOCK_INITIAL_FILES = [
    GeneratedFile(
        id="mock-initial-main",
        name="MainPage.vue",
        path="/src/MainPage.vue",
        type="file",
        language="vue",
        content="""<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6" v-for="item in stats" :key="item.title">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" :style="{ backgroundColor: item.color }">
              <el-icon><component :is="item.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ item.value }}</div>
              <div class="stat-title">{{ item.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>销售趋势</span>
          </template>
          <div class="chart-placeholder">图表区域</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>最新动态</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in activities"
              :key="index"
              :timestamp="activity.time"
            >
              {{ activity.content }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { User, ShoppingCart, Money, TrendCharts } from '@element-plus/icons-vue'

const stats = ref([
  { title: '用户总数', value: '1,234', color: '#409EFF', icon: User },
  { title: '订单数量', value: '5,678', color: '#67C23A', icon: ShoppingCart },
  { title: '销售额', value: '¥89,012', color: '#E6A23C', icon: Money },
  { title: '转化率', value: '23.5%', color: '#F56C6C', icon: TrendCharts },
])

const activities = ref([
  { content: '完成首页设计', time: '2024-01-15 10:30' },
  { content: '新增用户模块', time: '2024-01-15 09:20' },
  { content: '修复登录问题', time: '2024-01-14 18:00' },
])
</script>

<style scoped>
.dashboard {
  padding: 20px;
}
.stat-card {
  display: flex;
  align-items: center;
}
.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}
.stat-info {
  margin-left: 15px;
}
.stat-value {
  font-size: 24px;
  font-weight: bold;
}
.stat-title {
  color: #909399;
  font-size: 14px;
}
.chart-placeholder {
  height: 300px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}
</style>"""
    )
]

MOCK_INITIAL_MESSAGE = "初始生成完成（Mock 数据）"

MOCK_STAGES = {
    "requirement": StageResult(
        status="success",
        duration=1.5,
        output=None,
        error=None
    ),
    "generation": StageResult(
        status="success",
        duration=3.2,
        output=None,
        error=None
    ),
    "optimization": StageResult(
        status="success",
        duration=2.1,
        output=None,
        error=None
    )
}
