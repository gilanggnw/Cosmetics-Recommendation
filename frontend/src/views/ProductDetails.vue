<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const product = ref(null)
const isLoading = ref(true)
const isBookmarked = ref(false)

const fetchProductDetails = async () => {
  try {
    const response = await fetch(`http://localhost:5000/api/products/${route.params.id}`)
    const data = await response.json()
    if (data.error) {
      router.push('/search')
      return
    }
    product.value = data
    isLoading.value = false
  } catch (error) {
    console.error('Error:', error)
    isLoading.value = false
  }
}

const addBookmark = async () => {
  if (!authStore.isAuthenticated()) {
    router.push('/login')
    return
  }

  try {
    const userId = localStorage.getItem('user_id')
    const response = await fetch('http://localhost:5000/api/bookmark', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        user_id: parseInt(userId, 10),
        product_id: route.params.id
      })
    })

    if (response.ok) {
      isBookmarked.value = true
    }
  } catch (error) {
    console.error('Error adding bookmark:', error)
  }
}

onMounted(() => {
  fetchProductDetails()
})
</script>

<template>
  <main class="min-h-screen bg-gray-900 py-12 px-4">
    <div class="max-w-6xl mx-auto">
      <div v-if="isLoading" class="text-center text-gray-400">
        <div class="animate-pulse">Loading product details...</div>
      </div>

      <div v-else-if="product" class="bg-gray-800 rounded-lg p-8">
        <!-- Navigation and Action Bar -->
        <div class="flex justify-between items-center mb-8">
          <RouterLink
            to="/search"
            class="text-green-500 hover:text-green-400 flex items-center gap-2"
          >
            <span>←</span> Back to Search
          </RouterLink>

          <button
            @click="addBookmark"
            :disabled="isBookmarked"
            class="bg-green-500 hover:bg-green-600 disabled:bg-gray-500 disabled:cursor-not-allowed text-white px-6 py-2 rounded-md transition-colors"
          >
            {{ isBookmarked ? '★ Bookmarked' : '☆ Add to Bookmarks' }}
          </button>
        </div>

        <!-- Product Header -->
        <div class="border-b border-gray-700 pb-6 mb-6">
          <h1 class="text-3xl font-bold text-white mb-2">{{ product.name }}</h1>
          <div class="flex items-center gap-4">
            <span class="text-green-500 font-semibold text-xl">{{ product.brand }}</span>
            <span class="text-gray-400">|</span>
            <span class="text-gray-300">${{ product.price }}</span>
            <span class="text-gray-400">|</span>
            <div class="flex items-center">
              <span class="text-yellow-400">★</span>
              <span class="text-gray-300 ml-1">{{ product.rating }}</span>
            </div>
          </div>
        </div>

        <!-- Product Content -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
          <!-- Left Column - Details -->
          <div>
            <div class="bg-gray-750 rounded-lg p-6">
              <h2 class="text-xl font-semibold text-white mb-4">Product Details</h2>
              <dl class="space-y-4">
                <div>
                  <dt class="text-green-500 text-sm">Category</dt>
                  <dd class="text-gray-300 mt-1">{{ product.category }}</dd>
                </div>
                <div>
                  <dt class="text-green-500 text-sm">Skin Type</dt>
                  <dd class="text-gray-300 mt-1">{{ product.skinType || 'All Skin Types' }}</dd>
                </div>
                <div>
                  <dt class="text-green-500 text-sm">Price</dt>
                  <dd class="text-gray-300 mt-1">${{ product.price }}</dd>
                </div>
              </dl>
            </div>
          </div>

          <!-- Right Column - Ingredients & Description -->
          <div>
            <div class="bg-gray-750 rounded-lg p-6">
              <h2 class="text-xl font-semibold text-white mb-4">Ingredients</h2>
              <p class="text-gray-300 leading-relaxed">
                {{ product.ingredients }}
              </p>
            </div>

            <div class="bg-gray-750 rounded-lg p-6 mt-6">
              <h2 class="text-xl font-semibold text-white mb-4">Description</h2>
              <p class="text-gray-300 leading-relaxed">
                {{ product.description }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Not Found State -->
      <div v-else class="text-center">
        <p class="text-white text-xl mb-4">Product not found</p>
        <RouterLink
          to="/search"
          class="inline-block bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-md transition-colors"
        >
          Return to Search
        </RouterLink>
      </div>
    </div>
  </main>
</template>
