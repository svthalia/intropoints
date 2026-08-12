<script setup lang="ts">
  import { computed, onMounted, ref } from "vue"
  import { useRoute } from "vue-router"
  import Header from "@/components/Header.vue"
  import { BackendAPI } from "@/api/backend"
  import type { Store, StoreItem } from "@/models/store.model"
  import type Team from "@/models/teams.model"
  import type { TournamentAccount } from "@/models/account.model"
  import { useToast } from "vue-toastification"

  const route = useRoute()
  const toast = useToast()

  const store = ref<Store | null>(null)
  const marketItems = ref<StoreItem[]>([])
  const currentTeam = ref<Team | null>(null)
  const tournamentAccounts = ref<TournamentAccount[]>([])

  const isLoading = ref(true)
  const errorMessage = ref("")

  const tournamentCoins = computed(() => {
    const account = tournamentAccounts.value.find((account) => account.type === "coins")
    return account?.balance ?? 0
  })

  async function loadCurrentTeam() {
    const api = new BackendAPI()
    currentTeam.value = await api.getCurrentTeam()
  }

  async function loadMarketplace() {
    const api = new BackendAPI()
    const slug = route.params.slug as string

    const stores = await api.getStoreForTournament(slug)
    store.value = Array.isArray(stores) ? (stores[0] ?? null) : stores

    if (!store.value?.id) {
      throw new Error("Store has no id")
    }

    marketItems.value = await api.getItemsForStore(store.value.id)
  }

  async function loadTournamentAccounts() {
    const slug = route.params.slug as string

    if (!currentTeam.value || !slug) {
      tournamentAccounts.value = []
      return
    }

    const api = new BackendAPI()

    tournamentAccounts.value = await api.getTournamentAccountForTeamAndTournament(currentTeam.value.id, slug)
  }

  async function loadPage() {
    isLoading.value = true
    errorMessage.value = ""

    try {
      await loadCurrentTeam()
      await Promise.all([loadMarketplace(), loadTournamentAccounts()])
    } catch (err) {
      console.error("Failed to load marketplace:", err)
      errorMessage.value = "Failed to load marketplace."
    } finally {
      isLoading.value = false
    }
  }

  async function buyItem(item: StoreItem) {
    errorMessage.value = ""

    if (!currentTeam.value) {
      errorMessage.value = "Could not determine your team."
      return
    }

    try {
      const formData = new FormData()

      formData.append("team", String(currentTeam.value.id))
      formData.append("item", String(item.id))

      const api = new BackendAPI()
      await api.purchaseItem(formData)

      toast.success(`${item.name} purchased successfully.`)

      // Reload team so tournament coin balance updates after purchase
      await loadTournamentAccounts()
    } catch (err) {
      console.error("Failed to purchase item:", err) // TODO: Remove this log
      toast.error("Failed to purchase item.")
    }
  }

  onMounted(loadPage)
</script>

<template>
  <div class="page">
    <Header :show-menu-button="true" :show-profile-button="true" />

    <main class="page-main">
      <section class="hero-card featured-card">
        <div class="featured-top">
          <div>
            <p class="hero-kicker">Marketplace</p>
            <h1>{{ store?.name ?? "IntroPoints Store" }}</h1>
            <p class="hero-text">
              {{ store?.description ?? "Spend your coins on power-ups, surprises and special items." }}
            </p>
          </div>

          <div class="coin-balance">
            <font-awesome-icon :icon="['fas', 'coins']" />

            <div class="coin-balance-text">
              <span>{{ tournamentCoins }} coins</span>
            </div>
          </div>
        </div>
      </section>

      <section class="items-section">
        <div class="section-header">
          <p class="section-kicker">Shop</p>
          <h2>Available items</h2>
        </div>

        <p v-if="isLoading" class="empty-state dark-card">Loading marketplace...</p>

        <div v-if="!isLoading && !errorMessage" class="items-list">
          <article
            v-for="item in marketItems"
            :key="item.id"
            class="item-card dark-card"
            :class="{ 'without-thumbnail': !item.thumbnail }"
          >
            <img v-if="item.thumbnail" class="item-thumbnail" :src="item.thumbnail" :alt="item.name" />

            <div class="item-content">
              <div class="item-main">
                <div class="item-copy">
                  <h3>{{ item.name }}</h3>
                  <p>{{ item.description }}</p>
                </div>

                <div class="item-price">
                  <font-awesome-icon :icon="['fas', 'coins']" />
                  <span>{{ item.price }} coins</span>
                </div>
              </div>

              <div class="item-actions">
                <button class="primary-button" type="button" @click="buyItem(item)">Buy this item</button>
              </div>
            </div>
          </article>

          <p v-if="marketItems.length === 0" class="empty-state">No items available.</p>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
  .featured-card {
    display: flex;
    flex-direction: column;
    gap: 1.75rem;
  }

  .featured-top {
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

  .coin-balance-text {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
  }

  .coin-balance-text small {
    color: var(--text-muted-light);
    font-weight: 600;
  }

  .coin-balance svg,
  .item-price svg {
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

  .item-main {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
  }

  .item-copy h3 {
    margin: 0 0 0.35rem 0;
    font-size: 1.6rem;
    font-family: "Gill Sans MT Condensed", sans-serif;
    letter-spacing: 0.03em;
    text-transform: uppercase;
  }

  .item-copy p,
  .empty-state {
    margin: 0;
    color: var(--text-muted-light);
    line-height: 1.5;
  }

  .item-price {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 700;
    white-space: nowrap;
    padding-top: 0.15rem;
  }

  .item-actions {
    margin-top: 1rem;
  }

  .item-card {
    display: grid;
    grid-template-columns: 110px 1fr;
    gap: 1rem;
    align-items: flex-start;
  }

  .item-card.without-thumbnail {
    grid-template-columns: 1fr;
  }

  .item-thumbnail {
    width: 110px;
    height: 110px;
    object-fit: cover;
    border-radius: var(--radius-md);
    background: rgba(255, 255, 255, 0.08);
  }

  .item-content {
    min-width: 0;
  }

  .empty-state {
    text-align: center;
    padding: 2rem;
  }

  @media (max-width: 900px) {
    .featured-top,
    .item-main {
      flex-direction: column;
      align-items: flex-start;
    }

    .coin-balance,
    .item-price {
      white-space: normal;
    }

    .item-card {
      grid-template-columns: 1fr;
    }

    .item-thumbnail {
      width: 100%;
      height: 180px;
    }
  }
</style>
