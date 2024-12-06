<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen bg-gray-900">
    <header class="w-full py-6 px-4 bg-gray-800">
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
          </div>
        </nav>
      </div>
    </header>

    <RouterView />
  </div>
</template>

<style scoped>
</style>
