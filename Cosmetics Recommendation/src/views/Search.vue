<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink, RouterView } from 'vue-router'

const products = ref([])
const searchQuery = ref('')
const isLoading = ref(true)

const fetchProducts = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/products')
    const data = await response.json()
    console.log('Fetched data:', data) // Add debugging

    if (Array.isArray(data)) {
      // Get 9 random products for recommendations
      const shuffled = [...data].sort(() => 0.5 - Math.random())
      products.value = shuffled.slice(0, 9)
      console.log('Processed products:', products.value) // Add debugging
    } else {
      console.error('Data is not an array:', data)
      products.value = []
    }
    isLoading.value = false
  } catch (error) {
    console.error('Error fetching products:', error)
    products.value = []
    isLoading.value = false
  }
}

onMounted(() => {
  fetchProducts()
})
</script>

<template>
  <main class="min-h-screen bg-gray-900 py-12 px-4">
    <!-- Search Section -->
    <div class="max-w-3xl mx-auto text-center mb-16">
      <h1 class="text-4xl font-bold text-white mb-8">
        Find Your Perfect Products
      </h1>
      <div class="relative">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search for cosmetics..."
          class="w-full px-6 py-4 bg-gray-800 text-white rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none placeholder-gray-400"
        />
        <button
          class="absolute right-2 top-1/2 transform -translate-y-1/2 bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-md transition-colors"
        >
          Search
        </button>
      </div>
    </div>

    <!-- Recommendations Section -->
    <section class="max-w-7xl mx-auto">
      <h2 class="text-2xl font-semibold text-white mb-8">You might like these:</h2>

      <div v-if="isLoading" class="text-center text-gray-400">
        Loading recommendations...
      </div>

      <div
        v-else
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        <!-- Product Cards -->
        <div
          v-for="product in products"
          :key="product.id"
          class="bg-gray-800 rounded-lg overflow-hidden hover:shadow-lg transition-shadow"
        >
          <div class="p-6">
            <h3 class="text-xl font-semibold text-white mb-2 truncate">
              {{ product.name }}
            </h3>
            <p class="text-gray-400 mb-4 h-20 overflow-hidden">
              {{ product.description }}
            </p>
            <div class="flex justify-between items-center">
              <span class="text-green-500 font-semibold">
                {{ product.brand }}
              </span>
              <RouterLink
                v-if="product?.id !== undefined"
                :to="{ name: 'product-details', params: { id: product.id }}"
                class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md transition-colors text-sm"
              >
                View Details
              </RouterLink>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>
