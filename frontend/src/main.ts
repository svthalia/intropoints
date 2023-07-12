import './assets/css/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import "bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";

import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faUser, faImages, faTrophy, faChartLine, faRightToBracket, faArrowLeft, faAngleRight } from '@fortawesome/free-solid-svg-icons'

library.add(faUser, faImages, faTrophy, faChartLine, faRightToBracket, faArrowLeft, faAngleRight);

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.component('font-awesome-icon', FontAwesomeIcon);

app.mount('#app')
