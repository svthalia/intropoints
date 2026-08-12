<script setup lang="ts">
  import { computed, onMounted, ref } from "vue"
  import { useRouter } from "vue-router"
  import Header from "@/components/Header.vue"
  import { BackendAPI } from "@/api/backend"
  import type { Store } from "@/models/store.model"
  import type Team from "@/models/teams.model"
  import type { TournamentAccount } from "@/models/account.model"

  const router = useRouter()

  const stores = ref<Store[]>([])
  const currentTeam = ref<Team | null>(null)
  const isLoading = ref(true)
  const errorMessage = ref("")
  const tournamentAccounts = ref<Record<string, TournamentAccount[]>>({})

  const totalPoints = computed(() => {
    return currentTeam.value?.total_points ?? 0
  })

  async function loadCurrentTeam() {
    const apiService = new BackendAPI()
    currentTeam.value = await apiService.getCurrentTeam()
  }

  async function loadTournamentAccounts() {
    if (!currentTeam.value) {
      return
    }

    const api = new BackendAPI()

    const accountEntries = await Promise.all(
      stores.value.map(async (store) => {
        const accounts = await api.getTournamentAccountForTeamAndTournament(
          currentTeam.value!.id,
          store.tournament_slug,
        )

        return [store.tournament_slug, accounts]
      }),
    )

    tournamentAccounts.value = Object.fromEntries(accountEntries)
  }

  async function loadStores() {
    isLoading.value = true
    errorMessage.value = ""

    try {
      const apiService = new BackendAPI()

      await loadCurrentTeam()

      stores.value = await apiService.getStores()

      await loadTournamentAccounts()
    } catch (err) {
      console.error("Failed to load marketplaces:", err) // TODO: Remove this log
      errorMessage.value = "Failed to load marketplaces."
    } finally {
      isLoading.value = false
    }
  }

  function getCoinsForStore(store: Store): number {
    const accounts = tournamentAccounts.value[store.tournament_slug] ?? []

    const coinsAccount = accounts.find((account) => account.type === "coins")

    return coinsAccount?.balance ?? 0
  }

  function openStore(store: Store) {
    router.push(`/marketplace/${store.tournament_slug}`)
  }

  onMounted(loadStores)
</script>

<template>
  <div class="page">
    <Header :show-menu-button="true" :show-profile-button="true" />

    <main class="page-main">
      <section class="hero-card">
        <div class="hero-top">
          <div>
            <p class="hero-kicker">Marketplaces</p>
            <h1>IntroPoints Stores</h1>
            <p class="hero-text">Choose a tournament marketplace and spend your coins on items for that tournament.</p>
          </div>

          <div class="coin-balance">
            <font-awesome-icon :icon="['fas', 'coins']" />
            <span>{{ totalPoints }} total points</span>
          </div>
        </div>
      </section>

      <section class="items-section">
        <div class="section-header">
          <p class="section-kicker">Stores</p>
          <h2>Available marketplaces</h2>
        </div>

        <p v-if="isLoading" class="empty-state dark-card">Loading marketplaces...</p>
        <p v-else-if="errorMessage" class="empty-state dark-card">{{ errorMessage }}</p>

        <div v-else class="items-list">
          <article v-for="store in stores" :key="store.id" class="store-card dark-card" @click="openStore(store)">
            <div class="store-main">
              <div class="store-copy">
                <h3>{{ store.name }}</h3>
              </div>

              <div class="store-coins">
                <font-awesome-icon :icon="['fas', 'coins']" />
                <span>{{ getCoinsForStore(store) }} coins available</span>
              </div>
            </div>
          </article>

          <p v-if="stores.length === 0" class="empty-state dark-card">No marketplaces found.</p>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
  .hero-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
  }

  .coin-balance {
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 0.85rem 1rem;
    border-radius: 14px;
    font-weight: 700;
    white-space: nowrap;
  }

  .coin-balance svg,
  .store-copy svg,
  .store-coins svg {
    color: var(--primary);
  }

  .items-section {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .section-header h2 {
    margin: 0;
    font-size: 1.9rem;
    color: var(--dark);
    font-family: "Gill Sans MT Condensed", sans-serif;
    letter-spacing: 0.03em;
  }

  .items-list {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .store-card {
    cursor: pointer;
  }

  .store-main {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
  }

  .store-copy h3 {
    margin: 0;
    font-size: 1.6rem;
    font-family: "Gill Sans MT Condensed", sans-serif;
    letter-spacing: 0.03em;
    text-transform: uppercase;
  }

  .store-coins {
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 0.65rem 0.9rem;
    border-radius: 14px;
    font-weight: 700;
    white-space: nowrap;
  }

  .store-copy p,
  .empty-state {
    margin: 0;
    color: var(--text-muted-light);
    line-height: 1.5;
  }

  .empty-state {
    text-align: center;
    padding: 2rem;
  }

  @media (max-width: 900px) {
    .hero-top,
    .store-main {
      flex-direction: column;
      align-items: flex-start;
    }

    .coin-balance,
    .store-coins {
      white-space: normal;
    }
  }
</style>
