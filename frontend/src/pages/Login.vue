<script setup lang="ts">
  import { onMounted, ref } from "vue"
  import { useRouter } from "vue-router"

  import Header from "@/components/Header.vue"

  import { EnvironmentUtilities } from "@/api/utilities"
  import { BackendAPI } from "@/api/backend"

  const error = ref()

  const router = useRouter()

  /*
   *  Redirects the user to the navigation page
   *  if they are already logged in.
   */
  onMounted(() => {
    const api = new BackendAPI()

    if (api.loginSession !== null) {
      router.push({ name: "Navigation" })
    }
  })

  /*
   *  #### YOU SHOULD COMMENT YOUR FUNCTIONS ####
   */
  function startLogin() {
    window.location.href = EnvironmentUtilities.getLoginURL()
  }
</script>

<template>
  <Header :show-menu-button="false" :show-profile-button="false" />

  <div class="login-page">
    <div class="alert-container">
      <div class="alert alert-warning text-center">
        In order to see the homepage, you need to login. You can do so with the button below.
      </div>
    </div>

    <div class="center-content text-center">
      <div v-if="error">
        <ul class="list-unstyled">
          <li>
            <router-link :to="{ name: 'Navigation' }" class="btn btn-login mb-3"> Navigation </router-link>
          </li>
        </ul>
      </div>

      <div v-else>
        <button v-on:click="startLogin()" class="btn btn-login mb-3">Login</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
  .login-page {
    position: fixed;
    top: 56px;
    left: 0;
    right: 0;
    bottom: 0;
  }

  .alert-container {
    display: flex;
    justify-content: center;
    padding-top: 20px;
  }

  .center-content {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }
</style>
