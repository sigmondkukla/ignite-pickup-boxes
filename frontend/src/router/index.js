import AppLayout from '@/layout/AppLayout.vue';
import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            component: AppLayout,
            children: [
                {
                    path: '/',
                    name: 'crud',
                    alias: '/crud',
                    component: () => import('@/views/Crud.vue')
                },
                {
                    path: '/boxes',
                    name: 'boxes',
                    component: () => import('@/views/Boxes.vue')
                },
            ]
        },
    ]
});

export default router;
