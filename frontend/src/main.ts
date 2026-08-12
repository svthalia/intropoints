import "./assets/css/main.css"

import { createApp } from "vue"
import App from "./App.vue"
import { createPinia } from "pinia"
import router from "./router"

import "bootstrap"
import "bootstrap/dist/css/bootstrap.min.css"

import Toast from "vue-toastification"
import "vue-toastification/dist/index.css"

import { library } from "@fortawesome/fontawesome-svg-core"
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome"
import {
  faArrowLeft,
  faCircleUser,
  faSignOut,
  faBars,
  faXmark,
  faHouse,
  faTrophy,
  faFlagCheckered,
  faPaperPlane,
  faMedal,
  faCoins,
  faShoppingCart,
  faBoxOpen,
  faCog,
  faClipboardCheck,
  faChevronUp,
  faChevronDown,
  faStar,
} from "@fortawesome/free-solid-svg-icons"

library.add(
  faArrowLeft,
  faSignOut,
  faCircleUser,
  faBars,
  faXmark,
  faHouse,
  faTrophy,
  faFlagCheckered,
  faPaperPlane,
  faMedal,
  faCoins,
  faShoppingCart,
  faBoxOpen,
  faCog,
  faClipboardCheck,
  faChevronUp,
  faChevronDown,
  faStar,
)

createApp(App)
  .use(createPinia()) //initialize Pinia
  .use(Toast)
  .use(router)
  .component("font-awesome-icon", FontAwesomeIcon)
  .mount("#app")
