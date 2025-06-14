import { createRouter, createWebHistory } from 'vue-router'
import Topic1Page1 from '../pages/Topic1Page1.vue'
import Topic1Page2 from '../pages/Topic1Page2.vue'
import Topic2Page1 from '../pages/Topic2Page1.vue'
import Topic3Page from '../pages/Topic3Page.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/topic1/page1'
    },
    {
      path: '/topic1/page1',
      name: 'topic1-page1',
      component: Topic1Page1
    },
    {
      path: '/topic1/page2',
      name: 'topic1-page2',
      component: Topic1Page2
    },
    {
      path: '/topic2/page1',
      name: 'topic2-page1',
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