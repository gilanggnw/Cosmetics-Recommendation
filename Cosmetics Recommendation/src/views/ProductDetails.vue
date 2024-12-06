<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const product = ref(null)
const isLoading = ref(true)

const fetchProductDetails = async () => {
  try {
    const response = await fetch(`http://localhost:5000/api/products/${route.params.id}`)
    const data = await response.json()
    if (data.error) {
      router.push('/search') // Redirect if product not found
      return
    }
    product.value = data
    isLoading.value = false
  } catch (error) {
    console.error('Error:', error)
    isLoading.value = false
  }
}

onMounted(() => {
  fetchProductDetails()
})
</script>

<template>
  <main class="min-h-screen bg-gray-900 py-12 px-4">
    <div class="max-w-4xl mx-auto">
      <div v-if="isLoading" class="text-center text-gray-400">
        Loading product details...
      </div>

      <div v-else-if="product" class="bg-gray-800 rounded-lg p-8">
        <div class="mb-8">
          <RouterLink
            to="/search"
            class="text-green-500 hover:text-green-400 flex items-center gap-2"
          >
            ← Back to Search
          </RouterLink>
        </div>

        <h1 class="text-3xl font-bold text-white mb-4">{{ product.name }}</h1>
        <div class="mb-6  ">
          <span class="text-green-500 font-semibold text-xl">{{ product.brand }}</span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h2 class="text-xl font-semibold text-white mb-3">Details</h2>
            <div class="space-y-2">
              <p class="text-gray-300">
                <span class="text-green-500">Category:</span>
                {{ product.category }}
              </p>
              <p class="text-gray-300">
                <span class="text-green-500">Rating:</span>
                {{ product.rating }}
              </p>
              <p class="text-gray-300">
                <span class="text-green-500">Price:</span>
                ${{ product.price }}
              </p>
              <p class="text-gray-300">
                <span class="text-green-500">Ingredients:</span>
                {{ product.ingredients }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-center text-white">
        <p>Product not found</p>
        <RouterLink
          to="/search"
          class="text-green-500 hover:text-green-400 mt-4 inline-block"
        >
          Return to Search
        </RouterLink>
      </div>
    </div>
  </main>
</template>
