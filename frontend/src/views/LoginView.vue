<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')

const handleLogin = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: email.value,
        password: password.value,
      }),
    })

    const data = await response.json()

    if (response.ok) {
      authStore.setToken(data.token)
      authStore.setUser(data.user)
      localStorage.setItem('user_id', parseInt(data.user.id, 10)) // Store user ID as an integer in localStorage
      router.push('/')
    } else {
      error.value = data.error || 'Login failed'
    }
  } catch (err) {
    error.value = 'An error occurred during login'
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-900 py-12 px-4">
    <div class="max-w-md mx-auto bg-gray-800 rounded-lg p-8">
      <h2 class="text-3xl font-bold text-white mb-6">Login</h2>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label class="block text-gray-300 mb-2" for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            required
            class="w-full px-4 py-2 bg-gray-700 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>

        <div>
          <label class="block text-gray-300 mb-2" for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            class="w-full px-4 py-2 bg-gray-700 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>

        <div v-if="error" class="text-red-500">{{ error }}</div>

        <button
          type="submit"
          class="w-full bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded-md transition-colors"
        >
          Login
        </button>
      </form>

      <p class="mt-4 text-gray-400 text-center">
        Don't have an account?
        <RouterLink to="/register" class="text-green-500 hover:text-green-400">
          Register here
        </RouterLink>
      </p>
    </div>
  </div>
</template>
