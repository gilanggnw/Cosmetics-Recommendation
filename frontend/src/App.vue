<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
</script>

<template>
  <div class="min-h-screen bg-gray-900">
    <header class="sticky top-0 w-full py-6 px-4 bg-gray-800 z-50">
      <div class="container mx-auto px-4">
        <nav class="flex justify-between items-center">
          <div class="flex items-center">
            <RouterLink
              to="/"
              class="hover:opacity-80 transition-opacity"
            >
              <img
                src="@/assets/beautyguide-logo.png"
                alt="BeautyGuide Logo"
                class="h-12 w-auto"
              />
            </RouterLink>
          </div>
          <div class="space-x-6">
            <RouterLink
              to="/search"
              class="text-gray-300 hover:text-green-500 transition-colors"
            >
              Search
            </RouterLink>
            <RouterLink
              to="/about"
              class="text-gray-300 hover:text-green-500 transition-colors"
            >
              About
            </RouterLink>

            <template v-if="!authStore.isAuthenticated()">
              <RouterLink
                to="/login"
                class="text-gray-300 hover:text-green-500 transition-colors"
              >
                Login
              </RouterLink>
              <RouterLink
                to="/register"
                class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md transition-colors"
              >
                Register
              </RouterLink>
            </template>
            <template v-else>
              <span class="text-gray-300">Welcome, {{ authStore.user?.username }}</span>
              <button
                @click="authStore.logout"
                class="text-gray-300 hover:text-green-500 transition-colors"
              >
                Logout
              </button>
            </template>
          </div>
        </nav>
      </div>
    </header>

    <RouterView />
  </div>
</template>

<style scoped>
</style>
