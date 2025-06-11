<script setup lang="ts">
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import axios from 'axios'
import HelloWorld from './components/HelloWorld.vue'
</script>

<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-50">
    <h1 class="text-3xl font-bold mb-6">Neuroscience Website</h1>
    <Button @click="fetchMessage">Click me</Button>
    <p v-if="message" class="mt-4 text-lg">{{ message }}</p>
  </div>
  <HelloWorld msg="Vite + Vue" />
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
