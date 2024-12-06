<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useSearchStore } from '@/stores/searchStore'
import { useAuthStore } from '@/stores/authStore'

const products = ref([])
const searchQuery = ref('')
const allProducts = ref([])
const currentPage = ref(1)
const searchStore = useSearchStore()
const authStore = useAuthStore()
const isLoading = ref(false)
const showResults = ref(false)
const itemsPerPage = 20

// Fetch all products initially
const fetchProducts = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/products')
    const data = await response.json()

    if (Array.isArray(data)) {
      searchStore.setAllProducts(data)
    }
  } catch (error) {
    console.error('Error:', error)
  }
}

// Computed property for filtered products
const filteredProducts = computed(() => {
  if (!searchStore.searchQuery) {
    return searchStore.products
  }

  const query = searchStore.searchQuery.toLowerCase()
  return searchStore.allProducts.filter(product =>
    product.name?.toLowerCase().includes(query) ||
    product.brand?.toLowerCase().includes(query) ||
    product.description?.toLowerCase().includes(query)
  )
})

// Computed property for paginated products
const paginatedProducts = computed(() => {
  const startIndex = (searchStore.currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  return filteredProducts.value.slice(startIndex, endIndex)
})

// Computed total pages
const totalPages = computed(() =>
  Math.ceil(filteredProducts.value.length / itemsPerPage)
)

const recordSearchHistory = async (query) => {
  if (!authStore.isAuthenticated()) return;

  try {
    const response = await fetch('http://localhost:5000/api/search/history', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}` // Make sure token is properly formatted
      },
      body: JSON.stringify({
        search_query: String(query), // Ensure query is a string
        user_id: authStore.user?.id // Add user ID from auth store
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Search history error:', errorData);
      throw new Error(errorData.error || 'Failed to record search history');
    }

    const data = await response.json();
    console.log('Search history recorded:', data);
  } catch (error) {
    console.error('Error recording search history:', error);
  }
}

// Update handleSearch function
const handleSearch = async () => {
  isLoading.value = true;
  showResults.value = true;

  try {
    if (searchStore.searchQuery) {
      // Only record search if user is authenticated
      if (authStore.isAuthenticated()) {
        await recordSearchHistory(searchStore.searchQuery);
      }

      const filtered = searchStore.allProducts.filter(product =>
        product.name?.toLowerCase().includes(searchStore.searchQuery.toLowerCase()) ||
        product.brand?.toLowerCase().includes(searchStore.searchQuery.toLowerCase()) ||
        product.description?.toLowerCase().includes(searchStore.searchQuery.toLowerCase())
      );

      searchStore.setProducts(filtered);
      searchStore.setCurrentPage(1);
    } else {
      const shuffled = [...searchStore.allProducts].sort(() => 0.5 - Math.random());
      searchStore.setProducts(shuffled.slice(0, itemsPerPage));
    }
  } catch (error) {
    console.error('Search error:', error);
  } finally {
    isLoading.value = false;
  }
}

// Handle page change
const changePage = (page) => {
  searchStore.setCurrentPage(page)
}

const getPageNumbers = (current, total) => {
  if (total <= 10) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }

  if (current <= 4) {
    return [1, 2, 3, 4, 5, 6, 7, 8, '...', total]
  }

  if (current >= total - 3) {
    return [1, '...', total - 7, total - 6, total - 5, total - 4, total - 3, total - 2, total - 1, total]
  }

  return [1, '...', current - 2, current - 1, current, current + 1, current + 2, '...', total]
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
          v-model="searchStore.searchQuery"
          type="text"
          placeholder="Search for cosmetics..."
          class="w-full px-6 py-4 bg-gray-800 text-white rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none placeholder-gray-400"
          @keyup.enter="handleSearch"
        />
        <button
          @click="handleSearch"
          class="absolute right-2 top-1/2 transform -translate-y-1/2 bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-md transition-colors"
        >
          Search
        </button>
      </div>
    </div>

    <!-- Results Section -->
    <section v-if="showResults" class="max-w-7xl mx-auto">
      <h2 class="text-2xl font-semibold text-white mb-8">
        {{ searchStore.searchQuery ? 'Search Results:' : 'You might like these:' }}
      </h2>

      <div v-if="isLoading" class="text-center text-gray-400">
        Loading...
      </div>

      <div
        v-else-if="!searchStore.products.length"
        class="text-center text-gray-400"
      >
        No products found matching your search.
      </div>

      <div v-else>
        <!-- Product Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div
            v-for="product in paginatedProducts"
            :key="product.id"
            class="bg-gray-800 rounded-lg overflow-hidden hover:shadow-lg transition-shadow"
          >
            <div class="p-6">
              <h3 class="text-xl font-semibold text-white mb-2 truncate">
                {{ product?.name || 'Untitled Product' }}
              </h3>
              <p class="text-gray-400 mb-4 h-20 overflow-hidden">
                {{ product?.description || 'No description available' }}
              </p>
              <div class="flex justify-between items-center">
                <span class="text-green-500 font-semibold">
                  {{ product?.brand || 'Unknown Brand' }}
                </span>
                <RouterLink
                  :to="{ name: 'product-details', params: { id: product.id }}"
                  class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md transition-colors text-sm"
                >
                  View Details
                </RouterLink>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div class="flex justify-center space-x-2 mt-8" v-if="totalPages > 1">
          <!-- Previous Page Button -->
          <button
            @click="changePage(currentPage - 1)"
            :disabled="currentPage === 1"
            :class="[
              'px-4 py-2 rounded-md transition-colors',
              currentPage === 1
                ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                : 'bg-gray-800 text-gray-300 hover:bg-green-600 hover:text-white'
            ]"
          >
            ←
          </button>

          <!-- Page Numbers -->
          <template v-for="page in getPageNumbers(currentPage, totalPages)" :key="page">
            <span
              v-if="page === '...'"
              class="px-4 py-2 text-gray-500"
            >
              ...
            </span>
            <button
              v-else
              @click="changePage(page)"
              :class="[
                'px-4 py-2 rounded-md transition-colors',
                currentPage === page
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-green-600 hover:text-white'
              ]"
            >
              {{ page }}
            </button>
          </template>

          <!-- Next Page Button -->
          <button
            @click="changePage(currentPage + 1)"
            :disabled="currentPage === totalPages"
            :class="[
              'px-4 py-2 rounded-md transition-colors',
              currentPage === totalPages
                ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                : 'bg-gray-800 text-gray-300 hover:bg-green-600 hover:text-white'
            ]"
          >
            →
          </button>
        </div>
      </div>
    </section>
  </main>
</template>
