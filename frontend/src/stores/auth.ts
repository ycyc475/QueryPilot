import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { fetchMe, login as apiLogin } from '@/api/auth'
import { TOKEN_KEY } from '@/utils/constants'
import type { UserInfo } from '@/types/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem(TOKEN_KEY) || '')
  const user = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  async function login(email: string, password: string) {
    const res = await apiLogin(email, password)
    token.value = res.data.token
    user.value = res.data.user
    localStorage.setItem(TOKEN_KEY, token.value)
  }

  async function loadMe() {
    if (!token.value) return
    const res = await fetchMe()
    user.value = res.data
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  return { token, user, isLoggedIn, login, loadMe, logout }
})
