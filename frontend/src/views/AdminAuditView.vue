<template>
  <el-card>
    <template #header>查询审计</template>
    <el-table v-loading="loading" :data="runs" size="small">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="question" label="问题" min-width="220" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="row.status === 'SUCCEEDED' ? 'success' : 'danger'" size="small">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="durationMs" label="耗时(ms)" width="90" />
      <el-table-column prop="rowCount" label="行数" width="70" />
      <el-table-column prop="errorCode" label="错误码" width="150" show-overflow-tooltip />
      <el-table-column prop="createdAt" label="时间" width="180" />
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { listQueryRuns } from '@/api/conversation'
import type { QueryRun } from '@/types/api'

const runs = ref<QueryRun[]>([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const res = await listQueryRuns()
    runs.value = res.data
  } finally {
    loading.value = false
  }
})
</script>
