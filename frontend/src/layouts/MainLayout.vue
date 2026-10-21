<template>
  <el-container class="layout">
    <el-header class="header">
      <div class="left">
        <span class="brand">QueryPilot</span>
        <el-button link @click="router.push({ name: 'workbench' })">工作台</el-button>
        <el-button v-if="isAdmin" link @click="router.push({ name: 'admin-query-runs' })">查询审计</el-button>
      </div>
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
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const isAdmin = computed(() => auth.user?.role === 'ADMIN')

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
.left {
  display: flex;
  align-items: center;
  gap: 16px;
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
