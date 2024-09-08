<script setup>
import { useLayout } from '@/layout/composables/layout';
import AppConfigurator from './AppConfigurator.vue';

const { onMenuToggle, toggleDarkMode, isDarkTheme } = useLayout();
</script>

<template>
    <div class="layout-topbar">
        <div class="layout-topbar-logo-container">
            <!-- <button class="layout-menu-button layout-topbar-action" @click="onMenuToggle">
                <i class="pi pi-bars"></i>
            </button> -->
            <router-link to="/" class="layout-topbar-logo">
                <svg version="1.1" viewBox="0 0 512.25 182.11" xml:space="preserve" xmlns="http://www.w3.org/2000/svg">
                    <g transform="translate(.12269 -164.88)" fill="none" stroke="var(--primary-color)"
                        stroke-linecap="round" stroke-width="3.5">
                        <path d="m1.6273 215.23 63.096-5.7534" />
                        <path d="m1.7234 224.27 64.143-5.899" />
                        <path d="m1.7912 336.42 92.553-8.8146" />
                        <path d="m1.7912 345.24 94.52-8.8146" />
                        <path d="m58.137 316.15 16.544-79.467" />
                        <path d="m66.959 315.28 16.544-79.467" />
                        <path d="m83.496 313.44 16.544-79.467" />
                        <path d="m92.318 312.57 16.544-79.467" />
                        <path d="m77.868 206.91s0.20342-14.171 15.324-15.053" />
                        <path d="m92.921 213.56s5.899-0.0678 6.6448-6.4414" />
                        <path d="m93.124 222.17s14.239 0.13561 15.053-15.459" />
                        <path d="m265.86 293.4 15.765-76.517" />
                        <path d="m274.71 292.5 15.866-76.755" />
                        <path d="m187.68 301.82 15.956-77.812" />
                        <path d="m196.58 300.88 16.01-78.001" />
                        <path d="m291.35 290.52 15.765-75.941" />
                        <path d="m300.24 289.65 15.832-76.348" />
                        <path d="m284.81 187.52s0.20341-14.171 15.324-15.053" />
                        <path d="m299.86 194.17s5.899-0.0678 6.6448-6.4414" />
                        <path d="m300.06 202.78s14.239 0.13561 15.053-15.459" />
                        <path d="m121.48 204.07 147.04-14.095" />
                        <path d="m122.44 212.89 147.04-14.095" />
                        <path
                            d="m153.42 230.03s-13.548-0.15431-20.616 5.9452c-7.0686 6.0995-10.866 11.706-13.329 19.274-2.4624 7.5684-6.4246 24.548-6.6164 28.575-0.19178 4.0274-0.57534 10.836 1.0548 13.521" />
                        <path
                            d="m151.41 238.95s-17.068-1.6301-22.726 16.301c-5.6575 17.931-7.1918 30.781-7.1918 30.781s-2.2055 15.055 11.507 14.479" />
                        <path d="m133.38 308.47s-1.8219 5.7534 4.5068 5.9452 8.6301-8.726 8.6301-8.726" />
                        <path
                            d="m156.3 252.47c0.26808 3.927-0.56562 14.739-5.274 29.342-1.1817 3.6654-4.7945 6.7123-8.2466 6.9041-6.3371 0.35206-5.2324-7.161-4.4589-11.842 0.77353-4.6815 4.5319-19.289 6.1849-22.774 3.7352-7.8746 11.433-6.925 11.794-1.6301z" />
                        <path
                            d="m179.17 226.63-14.671 71.534s-2.637 21.767-24.931 25.555c-22.294 3.7877-22.582-7.4794-22.678-13.233" />
                        <path
                            d="m188.11 225.46-14.976 74.215s-3.3224 24.613-27.868 31.529c-24.545 6.9161-39.801-2.78-36.75-21.494" />
                        <path d="m183.72 318.83 326.65-31.164" />
                        <path d="m510.23 296.68-325.45 31.08" />
                        <path
                            d="m213.07 299.12s7.3197-37.515 11.261-53.018c0.71049-1.9678 3.3577-6.7786 9.5604-5.6956 1.3508 0.23585 3.1868 2.0341 2.3732 6.7127-0.81366 4.6785-10.578 50.921-10.578 50.921" />
                        <path
                            d="m242.31 295.92 11.651-56.253s1.4519-8.317-5.7534-10.404c-6.952-2.0137-12.993 1.2466-12.993 1.2466" />
                        <path
                            d="m251.33 295.05 11.555-55.52s2.7867-15.469-13.808-19.274c-7.5274-1.726-13.856 1.3904-13.856 1.3904" />
                        <path d="m329.42 184 180.95-17.369" />
                        <path d="m510.28 175.76-120.88 11.693" />
                        <path d="m359.32 190.34-28.919 2.6783" />
                        <path d="m337.53 206.73-1.0548 5.274-4.6986 0.0719" stroke-linejoin="round" />
                        <path d="m345.01 211.34-1.4623 7.3356-4.5788 0.5274" stroke-linejoin="round" />
                        <path
                            d="m325.3 240.29 5.4897-0.52741-5.5752 26.543s-4.9294 16.668 13.222 21.019c4.8775 1.1693 16.07-1.2883 16.07-1.2883"
                            stroke-linejoin="round" />
                        <path
                            d="m336.68 229.7 4.5429-0.33901-7.6619 36.818s-2.0942 10.085 5.7634 11.934c6.9161 1.6273 14.171-0.61024 14.171-0.61024"
                            stroke-linejoin="round" />
                        <path d="m363.26 201.61-3.0343 15.375 6.594-0.74585" stroke-linejoin="round" />
                        <path d="m375.01 188.44-3.9435 19.466 6.113-0.79109" stroke-linejoin="round" />
                        <path d="m364.78 226.66-6.9161 0.9323-7.0949 33.961s-2.1062 6.6939 4.7978 5.4452"
                            stroke-linejoin="round" />
                        <path d="m371.32 235.46-6.3527 0.50343-4.4388 23.529" stroke-linejoin="round" />
                        <path
                            d="m447.79 240.83s4.492-15.341 0.83059-28.156c-3.6614-12.815-21.223-12.747-21.223-12.747s-19.883-0.80793-32.004 12.408c-12.001 13.086-14.756 40.855-14.442 44.954 0.26668 3.4858-1.1436 23.497 23.732 24.138 18.342 0.47284 38.852-13.629 41.225-32.817"
                            stroke-linejoin="round" />
                        <path
                            d="m420.21 250.78 16.816-1.5595c-0.0504-0.0252-3.3246 19.352-25.834 23.325-21.696 3.8292-22.006-9.7501-21.969-16.07 0.0387-6.5825 2.8478-24.206 7.8653-32.207 5.0175-8.0009 10.713-15.731 25.766-16.341s18.578 5.56 19.121 11.188c0.54245 5.6278-2.5088 21.494-2.5088 21.494l-32.004 3.797s-4.9879 13.772 2.0341 16.883c6.6963 2.9668 10.564-7.3948 10.713-10.51z"
                            stroke-linejoin="round" />
                        <path
                            d="m409.58 234.28 15.241-1.5181s4.7202-13.942-4.4746-13.876c-8.6914 0.0625-10.766 15.394-10.766 15.394z"
                            stroke-linejoin="round" />
                    </g>
                </svg>
                <span>Ignite Pickup Boxes</span>
            </router-link>
        </div>

        <div class="layout-topbar-actions">
            <div class="layout-config-menu">
                <button type="button" class="layout-topbar-action" @click="toggleDarkMode">
                    <i :class="['pi', { 'pi-moon': isDarkTheme, 'pi-sun': !isDarkTheme }]"></i>
                </button>
                <!-- <div class="relative">
                    <button
                        v-styleclass="{ selector: '@next', enterFromClass: 'hidden', enterActiveClass: 'animate-scalein', leaveToClass: 'hidden', leaveActiveClass: 'animate-fadeout', hideOnOutsideClick: true }"
                        type="button" class="layout-topbar-action layout-topbar-action-highlight">
                        <i class="pi pi-palette"></i>
                    </button>
                    <AppConfigurator />
                </div> -->
            </div>

            <button class="layout-topbar-menu-button layout-topbar-action"
                v-styleclass="{ selector: '@next', enterFromClass: 'hidden', enterActiveClass: 'animate-scalein', leaveToClass: 'hidden', leaveActiveClass: 'animate-fadeout', hideOnOutsideClick: true }">
                <i class="pi pi-ellipsis-v"></i>
            </button>

            <div class="layout-topbar-menu hidden lg:block">
                <div class="layout-topbar-menu-content">
                    <button type="button" class="layout-topbar-action">
                        <i class="pi pi-cog"></i>
                        <span>Settings</span>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
