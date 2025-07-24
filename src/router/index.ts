import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import HowToUsePage from '../pages/HowToUsePage.vue'
import GlossaryPage from '../pages/GlossaryPage.vue'
import Topic1Page1 from '../pages/Topic1Page1.vue'
import Topic2Page1 from '../pages/Topic2Page1.vue'
import Topic3Page from '../pages/Topic3Page.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage
    },
    {
      path: '/platform-guide',
      name: 'platform-guide',
      component: HowToUsePage
    },
    {
      path: '/platform-guide/:section',
      name: 'platform-guide-section',
      component: HowToUsePage
    },
    {
      path: '/glossary',
      name: 'glossary',
      component: GlossaryPage
    },
    {
      path: '/topic1',
      name: 'topic1',
      component: Topic1Page1
    },
    {
      path: '/topic2',
      name: 'topic2',
      component: Topic2Page1
    },
    {
      path: '/topic3',
      name: 'topic3',
      component: Topic3Page
    }
  ]
})

export default router 