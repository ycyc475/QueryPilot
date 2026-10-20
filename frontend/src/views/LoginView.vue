<template>
  <div class="login-wrap">
    <el-card class="login-card">
      <h2 class="title">QueryPilot 登录</h2>
      <el-form :model="form" @submit.prevent="onSubmit">
        <el-form-item>
          <el-input v-model="form.email" placeholder="邮箱" />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            show-password
            @keyup.enter="onSubmit"
          />
        </el-form-item>
        <el-button type="primary" class="submit" :loading="loading" @click="onSubmit">登录</el-button>
      </el-form>
      <p class="hint">演示账号：admin@querypilot.dev / Admin123!</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const form = ref({ email: '', password: '' })
const loading = ref(false)

async function onSubmit() {
  if (!form.value.email || !form.value.password) {
    ElMessage.warning('请输入邮箱和密码')
    return
  }
  loading.value = true
  try {
    await auth.login(form.value.email, form.value.password)
    ElMessage.success('登录成功')
    router.push({ name: 'workbench' })
  } catch {
    // 错误已由 http 拦截器统一提示
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrap {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
}
.login-card {
  width: 360px;
}
.title {
  text-align: center;
  margin-bottom: 20px;
}
.submit {
  width: 100%;
}
.hint {
  color: #909399;
  font-size: 12px;
  text-align: center;
  margin-top: 12px;
}
</style>
