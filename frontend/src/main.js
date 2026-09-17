import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

import Aura from '@primevue/themes/aura';
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import ToastService from 'primevue/toastservice';

import InputNumber from 'primevue/inputnumber';

import '@/assets/styles.scss';
import '@/assets/tailwind.css';
import axios from 'axios';

// Production-safe: nginx proxies /api → backend
axios.defaults.baseURL = '/api';
// optional (only if you use cookies/sessions)
// axios.defaults.withCredentials = true;

const app = createApp(App);

app.use(router);

app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: '.app-dark'
    }
  }
});

app.use(ToastService);
app.use(ConfirmationService);

app.component('InputNumber', InputNumber);

app.mount('#app');
