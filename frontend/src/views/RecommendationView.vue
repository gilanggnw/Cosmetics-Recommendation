<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'

const skinTypes = ref(['Normal', 'Oily', 'Dry', 'Combination', 'Sensitive'])
const selectedSkinTypes = ref([])
const productTypes = ref(['Cleanser', 'Moisturizer', 'Face Mask', 'Treatment', 'Eye cream', 'Sun protect'])
const selectedProductTypes = ref([])
const minPrice = ref('')
const maxPrice = ref('')
const products = ref([])
const isLoading = ref(true)
const sortOption = ref('none')
const currentPage = ref(1)
const itemsPerPage = 30

const fetchProducts = async () => {
  try {
    const response = await fetch('https://loveyourskin.vercel.app/api/products')
    const data = await response.json()
    products.value = data
  } catch (error) {
    console.error('Error fetching products:', error)
  } finally {
    isLoading.value = false
  }
}

const filteredProducts = computed(() => {
  if (!products.value.length) return []
  
  let filtered = products.value.filter(product => {
    const matchesType = selectedProductTypes.value.length === 0 || 
                       selectedProductTypes.value.includes(product.Label)
    
    const matchesSkinType = selectedSkinTypes.value.length === 0 || 
                           selectedSkinTypes.value.some(type => product[type] == 1)
    
    const productPrice = parseFloat(product.price)
    const matchesMinPrice = !minPrice.value || productPrice >= parseFloat(minPrice.value)
    const matchesMaxPrice = !maxPrice.value || productPrice <= parseFloat(maxPrice.value)
    
    return matchesType && matchesSkinType && matchesMinPrice && matchesMaxPrice
  })

  if (sortOption.value !== 'none') {
    filtered.sort((a, b) => {
      const priceA = parseFloat(a.price)
      const priceB = parseFloat(b.price)
      return sortOption.value === 'asc' ? priceA - priceB : priceB - priceA
    })
  }

  return filtered
})

const paginatedProducts = computed(() => {
  const startIndex = (currentPage.value - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  return filteredProducts.value.slice(startIndex, endIndex)
})

const totalPages = computed(() => {
  return Math.ceil(filteredProducts.value.length / itemsPerPage)
})

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const goToPage = (page) => {
  currentPage.value = page
}

onMounted(() => {
  fetchProducts()
})

const visiblePages = computed(() => {
  const delta = 2 // Number of pages to show before and after current page
  const range = []
  
  for (let i = 1; i <= totalPages.value; i++) {
    if (
      i === 1 || // First page
      i === totalPages.value || // Last page
      (i >= currentPage.value - delta && i <= currentPage.value + delta) // Pages around current
    ) {
      range.push(i)
    } else if (range[range.length - 1] !== '...') {
      range.push('...')
    }
  }
  
  return range
})


</script>

<template>
  <div class="flex">
    <!-- Sidebar -->
    <div class="fixed left-0 top-24 w-64 h-[calc(100vh-6rem)] bg-gray-800 text-white flex flex-col border-r border-gray-700 overflow-y-auto">
      <div class="p-4 text-2xl font-bold">Filters</div>
      
      <!-- Product Type Checkboxes -->
      <div class="px-4 py-2">
        <label class="block text-sm font-medium text-gray-300 mb-2">Product Type</label>
        <div class="grid grid-cols-2 gap-2">
          <div v-for="type in productTypes" :key="type" class="flex items-center">
            <input 
              type="checkbox"
              :id="type"
              v-model="selectedProductTypes"
              :value="type"
              class="h-4 w-4 rounded border-gray-600 text-green-500 focus:ring-green-500 bg-gray-700"
            >
            <label :for="type" class="ml-2 text-sm text-gray-300 truncate">{{ type }}</label>
          </div>
        </div>
      </div>

      <!-- Skin Type Checkboxes -->
      <div class="px-4 py-2">
        <label class="block text-sm font-medium text-gray-300 mb-2">Skin Type</label>
        <div class="grid grid-cols-2 gap-2">
          <div v-for="type in skinTypes" :key="type" class="flex items-center">
            <input 
              type="checkbox"
              :id="type"
              v-model="selectedSkinTypes"
              :value="type"
              class="h-4 w-4 rounded border-gray-600 text-green-500 focus:ring-green-500 bg-gray-700"
            >
            <label :for="type" class="ml-2 text-sm text-gray-300 truncate">{{ type }}</label>
          </div>
        </div>
      </div>

      <!-- Sort Dropdown -->
      <div class="px-4 py-2">
        <label for="sort-option" class="block text-sm font-medium text-gray-300 mb-2">Sort by Price</label>
        <select
          id="sort-option"
          v-model="sortOption"
          class="mt-1 block w-full bg-gray-700 border border-gray-600 text-white py-2 px-3 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
        >
          <option value="none">No sorting</option>
          <option value="asc">Price: Low to High</option>
          <option value="desc">Price: High to Low</option>
        </select>
      </div>

      <!-- Price Range Inputs -->
      <div class="px-4 py-2">
        <label for="min-price" class="block text-sm font-medium text-gray-300">Minimum Price</label>
        <input 
          type="number" 
          id="min-price" 
          v-model="minPrice"
          class="mt-1 block w-full bg-gray-700 border border-gray-600 text-white py-2 px-3 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
          placeholder="0"
        >
      </div>

      <div class="px-4 py-2">
        <label for="max-price" class="block text-sm font-medium text-gray-300">Maximum Price</label>
        <input 
          type="number" 
          id="max-price" 
          v-model="maxPrice"
          class="mt-1 block w-full bg-gray-700 border border-gray-600 text-white py-2 px-3 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
          placeholder="1000"
        >
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 ml-64 p-8 overflow-x-hidden">
      <div v-if="isLoading" class="text-center text-gray-400">
        Loading products...
      </div>
      
      <div v-else class="max-w-7xl mx-auto px-4">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div 
            v-for="product in paginatedProducts" 
            :key="product.id" 
            class="bg-gray-800 rounded-lg overflow-hidden shadow-lg"
          >
            <div class="p-6">
              <h3 class="text-xl font-semibold text-white mb-2">
                {{ product.name }}
              </h3>
              <p class="text-gray-400 mb-2">Brand: {{ product.brand }}</p>
              <p class="text-green-500 font-bold mb-4">Price: ${{ product.price }}</p>
              <p class="text-gray-400 mb-2">Type: {{ product.Label }}</p>
              
              <div class="text-sm text-gray-400" v-if="Object.entries(product).some(([key, value]) => 
                ['Normal', 'Oily', 'Dry', 'Combination', 'Sensitive'].includes(key) && value == 1)">
                <p class="mb-2">Suitable for: 
                  {{
                    [
                      product.Normal == 1 ? 'Normal' : null,
                      product.Oily == 1 ? 'Oily' : null,
                      product.Dry == 1 ? 'Dry' : null,
                      product.Combination == 1 ? 'Combination' : null,
                      product.Sensitive == 1 ? 'Sensitive' : null
                    ].filter(Boolean).join(', ')
                  }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination Controls -->
        <div class="mt-8 flex justify-center items-center space-x-4">
          <button 
            @click="prevPage"
            :disabled="currentPage === 1"
            class="px-4 py-2 bg-gray-700 text-white rounded-md disabled:opacity-50 hover:bg-gray-600"
          >
            Previous
          </button>
          
          <div class="flex space-x-2">
            <template v-for="(page, index) in visiblePages" :key="index">
              <span 
                v-if="page === '...'"
                class="px-4 py-2 text-gray-400"
              >
                ...
              </span>
              <button 
                v-else
                @click="goToPage(page)"
                :class="[
                  'px-4 py-2 rounded-md',
                  currentPage === page 
                    ? 'bg-green-500 text-white' 
                    : 'bg-gray-700 text-white hover:bg-gray-600'
                ]"
              >
                {{ page }}
              </button>
            </template>
          </div>

          <button 
            @click="nextPage"
            :disabled="currentPage === totalPages"
            class="px-4 py-2 bg-gray-700 text-white rounded-md disabled:opacity-50 hover:bg-gray-600"
          >
            Next
          </button>
        </div>

        <div class="mt-4 text-center text-gray-400">
          Showing {{ (currentPage - 1) * itemsPerPage + 1 }} - 
          {{ Math.min(currentPage * itemsPerPage, filteredProducts.length) }} 
          of {{ filteredProducts.length }} products
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}
</style>