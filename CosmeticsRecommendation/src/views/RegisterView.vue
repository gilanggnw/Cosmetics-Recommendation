<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')

const handleRegister = async () => {
  // Password validation
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  try {
    const response = await fetch('http://localhost:5000/api/user/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value,
        email: email.value,
        password_hash: password.value, // In production, hash this client-side or let server handle it
      }),
    })

    const data = await response.json()

    if (response.ok) {
      // Auto login after registration
      authStore.setToken(data.token)
      authStore.setUser({
        username: username.value,
        email: email.value
      })
      router.push('/')
    } else {
      error.value = data.error || 'Registration failed'
    }
  } catch (err) {
    error.value = 'An error occurred during registration'
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-900 py-12 px-4">
    <div class="max-w-md mx-auto bg-gray-800 rounded-lg p-8">
      <h2 class="text-3xl font-bold text-white mb-6">Register</h2>

      <form @submit.prevent="handleRegister" class="space-y-6">
        <!-- Username Field -->
        <div>
          <label class="block text-gray-300 mb-2" for="username">Username</label>
          <input
            id="username"
            v-model="username"
            type="text"
            required
            class="w-full px-4 py-2 bg-gray-700 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>

        <!-- Email Field -->
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

        <!-- Password Field -->
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

        <!-- Confirm Password Field -->
        <div>
          <label class="block text-gray-300 mb-2" for="confirm-password">Confirm Password</label>
          <input
            id="confirm-password"
            v-model="confirmPassword"
            type="password"
            required
            class="w-full px-4 py-2 bg-gray-700 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>

        <!-- Error Message -->
        <div v-if="error" class="text-red-500">{{ error }}</div>

        <!-- Submit Button -->
        <button
          type="submit"
          class="w-full bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded-md transition-colors"
        >
          Register
        </button>
      </form>

      <!-- Login Link -->
      <p class="mt-4 text-gray-400 text-center">
        Already have an account?
        <RouterLink to="/login" class="text-green-500 hover:text-green-400">
          Login here
        </RouterLink>
      </p>
    </div>
  </div>
</template>
