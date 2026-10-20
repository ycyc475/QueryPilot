<template>
  <div ref="chartEl" class="chart"></div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import type { ChartSpec, ColumnInfo } from '@/types/api'

const props = defineProps<{ chart: ChartSpec; columns: ColumnInfo[]; rows: unknown[][] }>()
const chartEl = ref<HTMLElement>()
let instance: echarts.ECharts | null = null

function render() {
  if (!chartEl.value || props.chart.type === 'table') return
  const xIdx = props.columns.findIndex((c) => c.name === props.chart.x_field)
  const yIdx = props.columns.findIndex((c) => c.name === props.chart.y_field)
  if (xIdx < 0 || yIdx < 0) return
  const xData = props.rows.map((r) => r[xIdx])
  const yData = props.rows.map((r) => r[yIdx])
  if (!instance) {
    instance = echarts.init(chartEl.value)
  }
  instance.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 60, right: 24, top: 24, bottom: 48 },
    xAxis: { type: 'category', data: xData, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value' },
    series: [{ type: props.chart.type, data: yData, smooth: props.chart.type === 'line' }],
  })
}

onMounted(render)
watch(() => [props.chart, props.rows], render, { deep: true })
</script>

<style scoped>
.chart {
  width: 100%;
  height: 320px;
}
</style>
