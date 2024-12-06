<template>
  <div class="min-h-screen bg-gray-900 py-12 px-4">
    <div class="max-w-4xl mx-auto text-center">
      <h1 class="text-4xl font-bold text-white mb-6">
        404 - Page Not Found
      </h1>
      <p class="text-gray-300 mb-8">
        The page you're looking for doesn't exist.
      </p>
      <RouterLink
        to="/"
        class="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg transition-colors"
      >
        Return Home
      </RouterLink>
    </div>
  </div>
</template>
