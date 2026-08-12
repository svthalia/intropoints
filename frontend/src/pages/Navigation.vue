<script setup lang="ts">
  import { BackendAPI } from "@/api/backend"
  import { EnvironmentUtilities } from "@/api/utilities"
  import Header from "@/components/Header.vue"
  import type User from "@/models/user.model"
  import { computed, ref, onMounted } from "vue"

  const APIInstance = new BackendAPI()

  const user = ref<User | null>(null)

  async function loadUser() {
    try {
      user.value = await APIInstance.getCurrentUser()
    } catch (err) {
      console.error("Failed to load user:", err) //TODO: Remove this log
      user.value = null
    }
  }

  onMounted(loadUser)

  const userPermissions = computed(() => {
    const permissions = user.value?.permissions ?? []

    if (permissions.includes("users.ic_member")) return "IC member"
    if (permissions.includes("users.mentor")) return "Mentor"
    if (permissions.includes("users.participant")) return "Participant"

    return "User"
  })

  function navigateExternal(url: string) {
    window.location.href = url
  }

  //  Sort of the first thing that I thought could guard website
  //  access down the line - no Access Token -> No mount!
  if (!APIInstance.getAccessToken()) {
    window.location.href = EnvironmentUtilities.getBaseURI()
  }
</script>

<template>
  <div class="page">
    <Header :show-menu-button="true" :show-profile-button="true" />

    <main class="page-main">
      <section class="hero-card">
        <p class="hero-kicker">Welcome</p>
        <h1>Scavenger Hunt</h1>
        <p class="hero-text">
          Choose where you want to go. Track challenges, submit entries, and follow the tournament progress from one
          place.
        </p>
      </section>

      <section class="nav-grid">
        <router-link :to="{ name: 'Marketplaces' }" class="nav-card dark-card dark-card-hover">
          <div class="icon-box">
            <font-awesome-icon :icon="['fas', 'shopping-cart']" />
          </div>
          <div class="nav-card-content">
            <h2>Marketplaces</h2>
            <p>Buy items for your tournament with your earned Coins.</p>
          </div>
        </router-link>

        <router-link :to="{ name: 'Submissions' }" class="nav-card dark-card dark-card-hover">
          <div class="icon-box">
            <font-awesome-icon :icon="['fas', 'paper-plane']" />
          </div>
          <div class="nav-card-content">
            <h2>Submissions</h2>
            <p>See the entries of all the teams.</p>
          </div>
        </router-link>

        <router-link :to="{ name: 'Tournament' }" class="nav-card dark-card dark-card-hover">
          <div class="icon-box">
            <font-awesome-icon :icon="['fas', 'trophy']" />
          </div>
          <div class="nav-card-content">
            <h2>Tournaments</h2>
            <p>Check rankings, progress, and how everyone is performing.</p>
          </div>
        </router-link>

        <router-link :to="{ name: 'Inventory' }" class="nav-card dark-card dark-card-hover">
          <div class="icon-box">
            <font-awesome-icon :icon="['fas', 'box-open']" />
          </div>
          <div class="nav-card-content">
            <h2>Inventory</h2>
            <p>View your items, stats, and team information.</p>
          </div>
        </router-link>

        <div
          v-if="userPermissions === 'IC member' || userPermissions === 'Mentor'"
          class="nav-card dark-card dark-card-hover"
          @click="navigateExternal('https://scavengerhunt.thalia.nu/admin')"
        >
          <div class="icon-box">
            <font-awesome-icon :icon="['fas', 'cog']" />
          </div>
          <div class="nav-card-content">
            <h2>Admin</h2>
            <p>Access the admin panel to manage the tournament.</p>
          </div>
        </div>

        <router-link
          v-if="userPermissions === 'IC member'"
          :to="{ name: 'GradingOverview' }"
          class="nav-card dark-card dark-card-hover"
        >
          <div class="icon-box">
            <font-awesome-icon :icon="['fas', 'clipboard-check']" />
          </div>

          <div class="nav-card-content">
            <h2>Grading</h2>
            <p>Access the grading panel to evaluate submissions.</p>
          </div>
        </router-link>
      </section>
    </main>
  </div>
</template>

<style scoped>
  .nav-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1.25rem;
  }

  .nav-card {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
    text-decoration: none;
  }

  .nav-card:hover {
    color: white;
  }

  .nav-card-content h2 {
    margin: 0 0 0.45rem 0;
    font-size: 1.35rem;
  }

  .nav-card-content p {
    margin: 0;
    color: var(--text-muted-light);
    line-height: 1.5;
    font-size: 0.98rem;
  }

  @media (max-width: 900px) {
    .nav-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
