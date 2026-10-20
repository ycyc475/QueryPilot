<template>
  <el-container class="layout">
    <el-header class="header">
      <span class="brand">QueryPilot · 对话式数据分析</span>
      <div class="user-area">
        <span class="username">{{ auth.user?.displayName || auth.user?.email || '' }}</span>
        <el-button link type="primary" @click="onLogout">退出登录</el-button>
      </div>
    </el-header>
    <el-main class="main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

function onLogout() {
  auth.logout()
  router.push({ name: 'login' })
}

onMounted(() => {
  auth.loadMe()
})
</script>

<style scoped>
.layout {
  height: 100vh;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e4e7ed;
}
.brand {
  font-weight: 600;
  font-size: 16px;
}
.user-area {
  display: flex;
  align-items: center;
  gap: 12px;
}
.username {
  color: #606266;
}
.main {
  background: #f0f2f5;
}
</style>
