<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

const sidebarOpen = ref(false)
const sections = ref<HTMLElement[]>([])

const handleSidebarToggle = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const handleSidebarLinkClick = () => {
  sidebarOpen.value = false
}

function handleScroll() {
  sections.value.forEach(section => {
    const imagePlaceholder = section.querySelector('.image-placeholder') as HTMLElement | null
    if (!imagePlaceholder) return
    const stickyTopOffset = 32 // 2rem in px
    const sectionTop = section.offsetTop
    const sectionHeight = section.offsetHeight
    const imagePlaceholderHeight = imagePlaceholder.offsetHeight
    const stickPoint = sectionTop - stickyTopOffset
    const unstickPoint = sectionTop + sectionHeight - imagePlaceholderHeight - stickyTopOffset
    const scrollPosition = window.scrollY
    if (scrollPosition >= stickPoint && scrollPosition < unstickPoint) {
      imagePlaceholder.classList.add('sticky')
    } else {
      imagePlaceholder.classList.remove('sticky')
    }
  })
}

onMounted(() => {
  nextTick(() => {
    sections.value = Array.from(document.querySelectorAll('.content-section')) as HTMLElement[]
    window.addEventListener('scroll', handleScroll, { passive: true })
    handleScroll()
  })
})
onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div class="bg-white text-gray-800 min-h-screen">
    <!-- Sidebar Navigation -->
    <nav :class="['sidebar p-6 fixed top-0 left-0 h-full z-20 bg-gray-50 border-r border-gray-200 overflow-y-auto transition-transform', sidebarOpen ? 'open' : '']">
      <div class="flex items-center justify-between mb-8">
        <a href="#" class="text-xl font-bold text-gray-900">Home</a>
      </div>
      <ul class="sidebar-menu space-y-2">
        <li>
          <a href="#" class="flex items-center justify-between p-2 rounded-lg hover:bg-gray-200 toc-item">
            <span>Topic 1</span>
            <svg class="w-4 h-4 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
          </a>
          <ul class="ml-4 mt-2 space-y-2">
            <li><a href="#section-1-1" class="block p-2 rounded-lg hover:bg-gray-200" @click="handleSidebarLinkClick">Sub-topic 1.1</a></li>
            <li><a href="#section-1-2" class="block p-2 rounded-lg hover:bg-gray-200" @click="handleSidebarLinkClick">Sub-topic 1.2</a></li>
          </ul>
        </li>
        <li>
          <a href="#" class="flex items-center justify-between p-2 rounded-lg hover:bg-gray-200 toc-item">
            <span>Topic 2</span>
            <svg class="w-4 h-4 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
          </a>
          <ul class="ml-4 mt-2 space-y-2">
            <li><a href="#section-2-1" class="block p-2 rounded-lg hover:bg-gray-200" @click="handleSidebarLinkClick">Sub-topic 2.1</a></li>
          </ul>
        </li>
        <li>
          <a href="#section-3" class="flex items-center justify-between p-2 rounded-lg hover:bg-gray-200" @click="handleSidebarLinkClick">
            <span>Topic 3</span>
          </a>
        </li>
      </ul>
    </nav>
    <!-- Mobile Menu Toggle Button -->
    <button class="menu-toggle fixed top-4 left-4 z-30 bg-white p-2 rounded-md shadow-md md:hidden" @click="handleSidebarToggle">
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path></svg>
    </button>
    <!-- Main Content -->
    <main class="main-content" :style="{ marginLeft: '20%' }">
      <!-- Section 1.1 -->
      <section id="section-1-1" class="content-section min-h-screen">
        <div class="image-placeholder bg-gray-300 rounded-lg h-64 w-full mb-4 shadow-lg flex items-center justify-center">
          <span class="text-gray-500">Image Placeholder 1</span>
        </div>
        <div class="text-content">
          <h2 class="text-3xl font-bold mb-4">Sub-topic 1.1</h2>
          <p class="text-lg leading-relaxed mb-4">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
          <p class="text-lg leading-relaxed">Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
        </div>
      </section>
      <!-- Section 1.2 -->
      <section id="section-1-2" class="content-section min-h-screen">
        <div class="image-placeholder bg-gray-300 rounded-lg h-64 w-full mb-4 shadow-lg flex items-center justify-center">
          <span class="text-gray-500">Image Placeholder 2</span>
        </div>
        <div class="text-content">
          <h2 class="text-3xl font-bold mb-4">Sub-topic 1.2</h2>
          <p class="text-lg leading-relaxed">Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.</p>
        </div>
      </section>
      <!-- Section 2.1 -->
      <section id="section-2-1" class="content-section min-h-screen">
        <div class="image-placeholder bg-gray-300 rounded-lg h-64 w-full mb-4 shadow-lg flex items-center justify-center">
          <span class="text-gray-500">Image Placeholder 3</span>
        </div>
        <div class="text-content">
          <h2 class="text-3xl font-bold mb-4">Sub-topic 2.1</h2>
          <p class="text-lg leading-relaxed">At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus.</p>
        </div>
      </section>
      <!-- Section 3 (No sticky image) -->
      <section id="section-3" class="content-section min-h-screen">
        <div class="text-content" style="padding-top: 2rem;">
          <h2 class="text-3xl font-bold mb-4">Topic 3</h2>
          <p class="text-lg leading-relaxed">This is a section without a sticky image. The content starts at the top of the section. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat.</p>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.sidebar {
  width: 20%;
  min-width: 220px;
  max-width: 300px;
  transition: transform 0.3s ease-in-out;
}
.main-content {
  margin-left: 20%;
  width: 80%;
  transition: margin-left 0.3s;
}
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    width: 250px;
    position: fixed;
    z-index: 20;
  }
  .sidebar.open {
    transform: translateX(0);
  }
  .main-content {
    margin-left: 0;
    width: 100%;
  }
}
.image-placeholder.sticky {
  position: fixed;
  top: 2rem;
  width: calc(80% - 4rem);
  max-width: 600px;
  z-index: 10;
}
.content-section {
  display: flex;
  flex-direction: column;
  padding: 2rem;
}
.text-content {
  padding-top: calc(16rem + 2rem);
}
@media (max-width: 768px) {
  .image-placeholder.sticky {
    width: calc(100% - 4rem);
  }
}
.sidebar-menu ul {
  display: none;
}
.sidebar-menu li.active > ul {
  display: block;
}
</style>
