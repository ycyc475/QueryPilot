<template>
  <div class="chat-page">
    <div class="chat-scroll">
      <el-empty v-if="messages.length === 0" description="开始提问，例如：过去30天每天的实付销售额趋势" />
      <div v-for="(m, i) in messages" :key="i" class="msg-row" :class="m.role">
        <div class="bubble" :class="m.role">{{ m.content }}</div>
        <div v-if="m.result" class="result">
          <ChartRenderer
            v-if="m.result.chart.type !== 'table'"
            :chart="m.result.chart"
            :columns="m.result.columns"
            :rows="m.result.rows"
          />
          <table v-if="m.result.rows.length" class="data-table">
            <thead>
              <tr><th v-for="c in m.result.columns" :key="c.name">{{ c.name }}</th></tr>
            </thead>
            <tbody>
              <tr v-for="(row, ri) in m.result.rows" :key="ri">
                <td v-for="(cell, ci) in row" :key="ci">{{ cell }}</td>
              </tr>
            </tbody>
          </table>
          <el-collapse class="sql-collapse">
            <el-collapse-item title="查看 SQL">
              <pre class="sql">{{ m.result.sql }}</pre>
            </el-collapse-item>
          </el-collapse>
          <p class="meta">耗时 {{ m.result.durationMs }}ms · {{ m.result.rowCount }} 行</p>
        </div>
      </div>
    </div>
    <div class="input-row">
      <el-input v-model="input" placeholder="输入你的分析问题…" @keyup.enter="send" />
      <el-button type="primary" :loading="loading" @click="send">发送</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ask, getConversation } from '@/api/conversation'
import type { QueryRunResult } from '@/types/api'
import ChartRenderer from '@/components/ChartRenderer.vue'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  result?: QueryRunResult
}

const route = useRoute()
const conversationId = Number(route.params.id)
const messages = ref<ChatMessage[]>([])
const input = ref('')
const loading = ref(false)

onMounted(async () => {
  const res = await getConversation(conversationId)
  messages.value = res.data.messages.map((m) => ({
    role: m.role as 'user' | 'assistant',
    content: m.content,
  }))
})

async function send() {
  const q = input.value.trim()
  if (!q || loading.value) return
  loading.value = true
  messages.value.push({ role: 'user', content: q })
  input.value = ''
  try {
    const res = await ask(conversationId, q)
    messages.value.push({ role: 'assistant', content: res.data.summary, result: res.data })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
}
.chat-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.msg-row {
  margin-bottom: 16px;
}
.bubble {
  display: inline-block;
  max-width: 70%;
  padding: 10px 14px;
  border-radius: 8px;
  white-space: pre-wrap;
}
.bubble.user {
  background: #409eff;
  color: #fff;
}
.bubble.assistant {
  background: #fff;
  border: 1px solid #e4e7ed;
}
.msg-row.user {
  text-align: right;
}
.result {
  margin-top: 10px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 12px;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
  font-size: 13px;
}
.data-table th,
.data-table td {
  border: 1px solid #ebeef5;
  padding: 6px 8px;
  text-align: right;
}
.data-table th {
  background: #f5f7fa;
  text-align: left;
}
.sql-collapse {
  margin-top: 8px;
}
.sql {
  margin: 0;
  font-size: 12px;
  background: #f5f7fa;
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
}
.meta {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}
.input-row {
  display: flex;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid #e4e7ed;
}
</style>
