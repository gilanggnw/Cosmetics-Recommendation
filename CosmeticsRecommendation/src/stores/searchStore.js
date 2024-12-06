import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSearchStore = defineStore('search', () => {
  const searchQuery = ref('')
  const currentPage = ref(1)
  const products = ref([])
  const allProducts = ref([])

  function setSearchQuery(query) {
    searchQuery.value = query
  }

  function setCurrentPage(page) {
    currentPage.value = page
  }

  function setProducts(newProducts) {
    products.value = newProducts
  }

  function setAllProducts(newAllProducts) {
    allProducts.value = newAllProducts
  }

  return {
    searchQuery,
    currentPage,
    products,
    allProducts,
    setSearchQuery,
    setCurrentPage,
    setProducts,
    setAllProducts
  }
})
