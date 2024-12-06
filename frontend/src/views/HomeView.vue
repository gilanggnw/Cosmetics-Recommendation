<script setup>
const reviews = [
  {
    name: 'Sarah Johnson',
    image: 'https://api.dicebear.com/7.x/avataaars/svg?seed=1',
    text: 'The personalized recommendations completely transformed my skincare routine. My skin has never looked better!',
    rating: 5
  },
  {
    name: 'Emily Chen',
    image: 'https://api.dicebear.com/7.x/avataaars/svg?seed=2',
    text: 'I love how the system considers my specific skin concerns. The product matches were perfect for me.',
    rating: 5
  },
  {
    name: 'Michael Rodriguez',
    image: 'https://api.dicebear.com/7.x/avataaars/svg?seed=3',
    text: 'Finally found products that work together! No more guessing games with my skincare routine.',
    rating: 4
  }
]
</script>

<template>
  <main class="container mx-auto px-4 py-12">
    <div class="max-w-4xl mx-auto text-center">
      <!-- Hero Section -->
      <h1 class="text-5xl font-bold text-white mb-6">
        Discover Your Perfect Beauty Routine
      </h1>
      <p class="text-xl text-gray-300 mb-12">
        Get personalized skincare recommendations tailored to your unique needs and concerns
      </p>

      <RouterLink to="/recommendation">
          <button
          class="bg-green-500 hover:bg-green-600 text-white text-xl font-semibold py-4 px-8 rounded-lg transform transition-all hover:scale-105 shadow-lg hover:shadow-green-500/50"        
        >
          Start Skincare Consultation Now
        </button>
      </RouterLink>
      <!-- Consultation Button -->

      <!-- Features Section -->
      <div class="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div class="p-6 bg-gray-800 rounded-lg">
          <h3 class="text-xl font-semibold text-green-500 mb-3">
            Personalized Analysis
          </h3>
          <p class="text-gray-300">
            Get recommendations based on your skin type and concerns
          </p>
        </div>
        <div class="p-6 bg-gray-800 rounded-lg">
          <h3 class="text-xl font-semibold text-green-500 mb-3">
            Expert Insights
          </h3>
          <p class="text-gray-300">
            Backed by dermatological research and beauty experts
          </p>
        </div>
        <div class="p-6 bg-gray-800 rounded-lg">
          <h3 class="text-xl font-semibold text-green-500 mb-3">
            Smart Matching
          </h3>
          <p class="text-gray-300">
            Find products that work together for optimal results
          </p>
        </div>
      </div>

      <!-- Reviews Section -->
      <section class="mt-24">
        <h2 class="text-3xl font-bold text-white mb-12">What Our Users Say</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div v-for="review in reviews" :key="review.name" class="bg-gray-800 p-6 rounded-lg">
            <img :src="review.image" alt="User Avatar" class="w-16 h-16 rounded-full mx-auto mb-4"/>
            <div class="flex justify-center mb-2">
              <template v-for="star in review.rating" :key="star">
                <svg class="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                </svg>
              </template>
            </div>
            <p class="text-gray-300 mb-4">{{ review.text }}</p>
            <p class="text-green-500 font-semibold">{{ review.name }}</p>
          </div>
        </div>
      </section>

      <!-- Quick Links -->
      <section class="mt-24 border-t border-gray-700 pt-12">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-left">
          <div>
            <h4 class="text-white font-semibold mb-4">Products</h4>
            <ul class="space-y-2">
              <li><a href="#" class="text-gray-400 hover:text-green-500">Skincare</a></li>
              <li><a href="#" class="text-gray-400 hover:text-green-500">Makeup</a></li>
              <li><a href="#" class="text-gray-400 hover:text-green-500">Hair Care</a></li>
            </ul>
          </div>
          <div>
            <h4 class="text-white font-semibold mb-4">Company</h4>
            <ul class="space-y-2">
              <li><a href="#" class="text-gray-400 hover:text-green-500">About Us</a></li>
              <li><a href="#" class="text-gray-400 hover:text-green-500">Contact</a></li>
              <li><a href="#" class="text-gray-400 hover:text-green-500">Careers</a></li>
            </ul>
          </div>
          <div>
            <h4 class="text-white font-semibold mb-4">Support</h4>
            <ul class="space-y-2">
              <li><a href="#" class="text-gray-400 hover:text-green-500">Help Center</a></li>
              <li><a href="#" class="text-gray-400 hover:text-green-500">Privacy Policy</a></li>
              <li><a href="#" class="text-gray-400 hover:text-green-500">Terms of Service</a></li>
            </ul>
          </div>
          <div>
            <h4 class="text-white font-semibold mb-4">Connect</h4>
            <ul class="space-y-2">
              <li><a href="#" class="text-gray-400 hover:text-green-500">Instagram</a></li>
              <li><a href="#" class="text-gray-400 hover:text-green-500">Twitter</a></li>
              <li><a href="#" class="text-gray-400 hover:text-green-500">Facebook</a></li>
            </ul>
          </div>
        </div>
      </section>

      <!-- Footer -->
      <footer class="mt-24 border-t border-gray-700 pt-8">
        <p class="text-gray-400 text-sm">
          © {{ new Date().getFullYear() }} BeautyGuide. All rights reserved.
        </p>
      </footer>
    </div>
  </main>
</template>
