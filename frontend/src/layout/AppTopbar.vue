<script setup>
import { useLayout } from '@/layout/composables/layout';

const { toggleDarkMode, isDarkTheme } = useLayout();
</script>

<template>
    <div class="layout-topbar">
        <div class="layout-topbar-logo-container" style="padding-left: 0;">
            <router-link to="/" class="layout-topbar-logo">
                <span style="white-space: nowrap;">Makerspace Pickup Boxes</span>
            </router-link>
        </div>

        <div class="layout-topbar-actions">
            <div class="layout-topbar-menu hidden lg:block">
                <!-- New navigation links for switching views -->
                <router-link to="/crud" class="layout-topbar-action">
                    <i class="pi pi-list"></i>
                    <span>CRUD View</span>
                </router-link>
                <router-link to="/boxes" class="layout-topbar-action">
                    <i class="pi pi-th-large"></i>
                    <span>Boxes View</span>
                </router-link>

                <button type="button" class="layout-topbar-action" @click="toggleDarkMode">
                    <i :class="['pi', { 'pi-moon': isDarkTheme, 'pi-sun': !isDarkTheme }]"></i>
                    <span>Dark Mode</span>
                </button>
            </div>
        </div>
    </div>
</template>
