<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import SearchBar from './SearchBar.vue'
import type { SearchResult } from '../types/search'

interface MenuItem {
  id: string
  title: string
  path?: string
  children?: MenuItem[]
}

interface Props {
  menuItems: MenuItem[]
  isOpen: boolean
}

const { menuItems, isOpen } = defineProps<Props>()

const emit = defineEmits(['toggleSidebar', 'menuClick'])
const router = useRouter()

// Track expanded state for each menu item
const expandedItems = ref<Set<string>>(new Set())

const handleMenuClick = (item: MenuItem) => {
  if (item.children?.length) {
    // Toggle expansion for items with children
    if (expandedItems.value.has(item.id)) {
      expandedItems.value.delete(item.id)
    } else {
      expandedItems.value.add(item.id)
    }
  } else if (item.path) {
    // Navigate for items with paths
    router.push(item.path)
    emit('menuClick', item)
  }
}

const handleToggle = () => {
  emit('toggleSidebar')
}

const handleHomeClick = () => {
  router.push('/')
}

const isExpanded = (itemId: string) => {
  return expandedItems.value.has(itemId)
}
</script>

<template>
  <nav :class="['sidebar', isOpen ? 'open' : '']">
    <!-- Home Button -->
    <div class="sidebar-header">
      <button 
        @click="handleHomeClick" 
        class="home-button"
      >
        Home
      </button>
    </div>
    
    <!-- Navigation Menu -->
    <div class="sidebar-content">
      <ul class="sidebar-menu">
        <li v-for="item in menuItems" :key="item.id" class="menu-item">
          <!-- Main menu item -->
          <div 
            class="menu-item-content"
            :class="{ 'has-children': item.children?.length }"
            @click="handleMenuClick(item)"
          >
            <span class="menu-item-title">{{ item.title }}</span>
            <svg 
              v-if="item.children?.length" 
              class="expand-icon"
              :class="{ 'expanded': isExpanded(item.id) }"
              width="12" 
              height="12" 
              viewBox="0 0 12 12" 
              fill="none"
            >
              <path 
                d="M4.5 3L7.5 6L4.5 9" 
                stroke="currentColor" 
                stroke-width="1.5" 
                stroke-linecap="round" 
                stroke-linejoin="round"
              />
            </svg>
          </div>
          
          <!-- Submenu -->
          <ul 
            v-if="item.children?.length && isExpanded(item.id)" 
            class="submenu"
          >
            <li 
              v-for="child in item.children" 
              :key="child.id"
              class="submenu-item"
            >
              <div 
                class="submenu-item-content"
                @click="handleMenuClick(child)"
              >
                {{ child.title }}
              </div>
            </li>
          </ul>
        </li>
      </ul>
    </div>
  </nav>
  
  <!-- Mobile Menu Toggle Button -->
  <button 
    class="menu-toggle" 
    @click="handleToggle"
  >
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
      <path 
        d="M3 6h14M3 10h14M3 14h14" 
        stroke="currentColor" 
        stroke-width="2" 
        stroke-linecap="round"
      />
    </svg>
  </button>
</template>

<style scoped>
.sidebar {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
  width: 280px;
  height: 100vh;
  background-color: #ffffff;
  border-right: 1px solid #e5e7eb;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 20;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease-in-out;
}

.sidebar-header {
  padding: 20px 24px 16px 24px;
  border-bottom: 1px solid #f3f4f6;
  flex-shrink: 0;
}

.home-button {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  text-align: left;
  width: 100%;
  transition: color 0.15s ease;
}

.home-button:hover {
  color: #6b7280;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.sidebar-menu {
  list-style: none;
  padding: 0;
  margin: 0;
}

.menu-item {
  margin: 0;
}

.menu-item-content {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 8px 24px;
  cursor: pointer;
  transition: background-color 0.15s ease;
  color: #374151;
  font-size: 14px;
  font-weight: 500;
  text-align: left;
}

.menu-item-content:hover {
  background-color: #f9fafb;
  color: #111827;
}

.menu-item-content.has-children {
  font-weight: 600;
}

.menu-item-title {
  flex: 1;
  text-align: left;
}

.expand-icon {
  color: #6b7280;
  transition: transform 0.2s ease;
  flex-shrink: 0;
  margin-left: auto;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.submenu {
  list-style: none;
  padding: 0;
  margin: 0;
  background-color: #fafafa;
}

.submenu-item {
  margin: 0;
}

.submenu-item-content {
  padding: 6px 24px 6px 40px;
  cursor: pointer;
  color: #6b7280;
  font-size: 13px;
  font-weight: 400;
  transition: all 0.15s ease;
  border-left: 3px solid transparent;
  text-align: left;
  display: block;
  width: 100%;
}

.submenu-item-content:hover {
  background-color: #f3f4f6;
  color: #374151;
  border-left-color: #e5e7eb;
}

.menu-toggle {
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 30;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 8px;
  cursor: pointer;
  color: #6b7280;
  transition: all 0.15s ease;
  display: none;
}

.menu-toggle:hover {
  background-color: #f9fafb;
  border-color: #d1d5db;
  color: #374151;
}

/* Mobile Styles */
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  }
  
  .sidebar.open {
    transform: translateX(0);
  }
  
  .menu-toggle {
    display: block;
  }
}

@media (min-width: 769px) {
  .menu-toggle {
    display: none;
  }
}

/* Custom scrollbar for webkit browsers */
.sidebar-content::-webkit-scrollbar {
  width: 6px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background-color: #d1d5db;
  border-radius: 3px;
}

.sidebar-content::-webkit-scrollbar-thumb:hover {
  background-color: #9ca3af;
}
</style>