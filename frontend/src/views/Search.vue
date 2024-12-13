<script setup>
import { ref, computed, onMounted, watch } from 'vue'
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
const localQuery = ref('')
const viewState = ref('initial') // 'initial', 'search'
const recommendedProducts = ref([])
const isLoadingRecommendations = ref(false)
const hasSearched = ref(false)

const userPreferences = ref({
  productType: '',
  skinType: ''
})


const showRecommendations = computed(() => !searchStore.searchQuery)

// Add a method to handle initial load
const initializeSearch = async () => {
  console.log('Initializing search...')
  isLoading.value = true
  
  try {
    // Ensure allProducts are loaded in store
    if (!searchStore.allProducts?.length) {
      await fetchProducts()
    }
    
    // Set initial products
    searchStore.setProducts(searchStore.allProducts)
    showResults.value = true
    await fetchRecommendedProducts()
    
  } catch (error) {
    console.error('Error initializing search:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  await fetchProducts()
  viewState.value = 'initial'
  showResults.value = true
  await fetchRecommendedProducts()
})

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

// Update handleSearch function
const handleSearch = async () => {

  if (!searchStore.searchQuery.trim()) {
    searchStore.clearProducts()
    hasSearched.value = false
    return
  }

  isLoading.value = true;
  hasSearched.value = true;

  try {
    console.log('Query type:', typeof searchStore.searchQuery); // Debug type
    console.log('Query value:', searchStore.searchQuery); // Debug value

    searchStore.setSearchQuery(localQuery.value);

    if (localQuery.value) {
      viewState.value = 'search'
      const query = String(localQuery.value).trim(); // Explicitly convert to string
      if (authStore.isAuthenticated()) {
        await recordSearchHistory(query);
      }

      const filtered = searchStore.allProducts.filter(product =>
        product.name?.toLowerCase().includes(searchStore.searchQuery.toLowerCase()) ||
        product.brand?.toLowerCase().includes(searchStore.searchQuery.toLowerCase()) ||
        product.description?.toLowerCase().includes(searchStore.searchQuery.toLowerCase())
      );

      searchStore.setProducts(filtered);
      searchStore.setCurrentPage(1);
    } else {
      // When search query is empty, show all products
      viewState.value = 'initial'
      searchStore.setProducts(searchStore.allProducts);
      searchStore.setCurrentPage(1);
    }
  } catch (error) {
    console.error('Search error:', error);
  } finally {
    isLoading.value = false;
  }
};

const recordSearchHistory = async (query) => {
  if (!authStore.isAuthenticated()) return;

  const userId = localStorage.getItem('user_id');
  if (!userId) {
    console.error('User ID not found in localStorage');
    return;
  }

  const postData = {
    user_id: parseInt(userId, 10), // Ensure user_id is an integer
    search_query: String(query).trim()
  };

  try {
    const response = await fetch('http://localhost:5000/api/search/history', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      credentials: 'include',
      body: JSON.stringify(postData)
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to record search history');
    }

    const data = await response.json();
    console.log('Search history recorded:', data);
  } catch (error) {
    console.error('Error recording search history:', error);
  }
};

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

const getHighestCounts = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/click-counts', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      credentials: 'include'
    })
    const data = await response.json()
    
    const productTypes = {
      Cleanser: data.cleanser_count,
      'Face Mask': data.facemask_count,
      'Eye cream': data.eyecream_count,
      Moisturizer: data.moisturizer_count,
      Treatment: data.treatment_count,
      'Sun protect': data.sunprotect_count
    }
    
    const skinTypes = {
      Normal: data.normal_count,
      Dry: data.dry_count,
      Sensitive: data.sensitive_count, 
      Oily: data.oily_count,
      Combination: data.combination_count
    }

    // Get highest count product type
    const highestProductType = Object.entries(productTypes)
      .reduce((a, b) => (a[1] > b[1] ? a : b))[0]

    // Get highest count skin type  
    const highestSkinType = Object.entries(skinTypes)
      .reduce((a, b) => (a[1] > b[1] ? a : b))[0]

    // Update the reactive variable
    userPreferences.value = {
      productType: highestProductType,
      skinType: highestSkinType
    }

    return { productType: highestProductType, skinType: highestSkinType }
  } catch (error) {
    console.error('Error getting highest counts:', error)
    return { productType: 'cleanser', skinType: 'normal' } // Default fallback
  }
}

const fetchRecommendedProducts = async () => {
  if (!searchStore.searchQuery) {
    isLoadingRecommendations.value = true
    try {
      const { productType, skinType } = await getHighestCounts()
      if (productType && skinType) {
        // Filter products that match both product type and skin type
        recommendedProducts.value = searchStore.allProducts.filter(product => 
          product.Label === productType && 
          product[skinType] === 1
        ).slice(0,9)
      }
    } catch (error) {
      console.error('Error:', error)
      recommendedProducts.value = []
    } finally {
      isLoadingRecommendations.value = false
    }
  }
}



// onMounted(() => {
//   fetchRecommendedProducts()
// })

// Add watcher for search query
watch(() => searchStore.searchQuery, async (newQuery) => {
  if (!newQuery.trim()) {
    searchStore.setProducts([])
    hasSearched.value = false
    viewState.value = 'initial'
    await fetchRecommendedProducts()
    return
  }

  isLoading.value = true
  hasSearched.value = true
  viewState.value = 'search'

  try {
    const filtered = searchStore.allProducts.filter(product =>
      product.name?.toLowerCase().includes(newQuery.toLowerCase()) ||
      product.brand?.toLowerCase().includes(newQuery.toLowerCase()) ||
      product.description?.toLowerCase().includes(newQuery.toLowerCase())
    )
    searchStore.setProducts(filtered)
    await recordSearchHistory(newQuery)
  } catch (error) {
    console.error('Search error:', error)
  } finally {
    isLoading.value = false
  }
}, { immediate: true })


</script>

<template>
  <main class="min-h-screen bg-gray-900 py-12 px-4">
    <!-- Search Section -->
    <!-- Search input without button -->
    <div class="max-w-3xl mx-auto text-center mb-16">
      <h1 class="text-4xl font-bold text-white mb-8">Find Your Perfect Products</h1>
      <input
        v-model="searchStore.searchQuery"
        type="text"
        placeholder="Search products..."
        class="w-full px-6 py-4 bg-gray-800 text-white rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none"
      />
    </div>

    <!-- Recommended Products Section -->
    <section v-if="!hasSearched && recommendedProducts.length">
      <h2 class="text-2xl font-semibold text-white mb-8">
        Recommended {{ userPreferences.productType }} Products for {{ userPreferences.skinType }} Skin
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div
          v-for="product in recommendedProducts"
          :key="product.id"
          class="bg-gray-800 rounded-lg overflow-hidden hover:shadow-lg transition-shadow"
        >
          <div class="p-6">
            <h3 class="text-xl font-semibold text-white mb-2 truncate">
              {{ product.name }}
            </h3>
            <p class="text-green-500 mb-4 h-20 overflow-hidden">
              Price: ${{ product.price }}
            </p>
            <div class="flex justify-between items-center">
              <span class="text-green-500 font-semibold">
                {{ product.brand }}
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
    </section>

    <!-- Results Section -->
    <section v-if="hasSearched" class="max-w-7xl mx-auto">
      <h2 class="text-2xl font-semibold text-white mb-8">
        Search Results
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
