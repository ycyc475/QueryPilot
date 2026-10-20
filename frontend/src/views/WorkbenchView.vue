<template>
  <div class="workbench">
    <el-card>
      <template #header>选择数据集</template>
      <div v-loading="loading" class="dataset-grid">
        <el-card
          v-for="d in datasets"
          :key="d.id"
          class="dataset-card"
          :class="{ selected: selectedId === d.id }"
          shadow="hover"
          @click="select(d)"
        >
          <div class="ds-name">{{ d.name }}</div>
          <div class="ds-desc">{{ d.description }}</div>
          <div class="ds-source">数据源：{{ d.source.name }}（{{ d.source.dbType }}）</div>
        </el-card>
      </div>
    </el-card>

    <el-card class="placeholder">
      <el-empty description="对话式分析将在后续阶段（Agent 模块）实现，当前阶段完成登录与数据集查询" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { listDatasets } from '@/api/dataset'
import type { Dataset } from '@/types/api'

const datasets = ref<Dataset[]>([])
const selectedId = ref<number | null>(null)
const loading = ref(false)

function select(d: Dataset) {
  selectedId.value = d.id
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await listDatasets()
    datasets.value = res.data
    if (datasets.value.length) {
      selectedId.value = datasets.value[0].id
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dataset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.dataset-card {
  cursor: pointer;
}
.dataset-card.selected {
  border-color: var(--el-color-primary);
}
.ds-name {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 8px;
}
.ds-desc {
  color: #606266;
  font-size: 13px;
  margin-bottom: 8px;
}
.ds-source {
  color: #909399;
  font-size: 12px;
}
.placeholder {
  margin-top: 16px;
}
</style>
