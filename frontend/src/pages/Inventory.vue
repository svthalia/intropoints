<script setup lang="ts">
  import { computed, onMounted, ref, watch } from "vue"
  import { useRouter } from "vue-router"
  import Header from "@/components/Header.vue"
  import { BackendAPI } from "@/api/backend"
  import type Team from "@/models/teams.model"
  import type { Tournament, Scoreboard } from "@/models/tournament.model"
  import type { Inventory } from "@/models/store.model"
  import type { TournamentAccount, AccountTransaction } from "@/models/account.model"

  const router = useRouter()

  const currentTeam = ref<Team | null>(null)
  const tournaments = ref<Tournament[]>([])
  const selectedTournamentSlug = ref("")
  const inventory = ref<Inventory | null>(null)
  const tournamentAccounts = ref<TournamentAccount[]>([])
  const transactions = ref<AccountTransaction[]>([])
  const scoreboard = ref<Scoreboard[]>([])

  const isLoading = ref(true)
  const errorMessage = ref("")

  const showAllItems = ref(false)
  const showAllTransactions = ref(false)
  const showFullRanking = ref(false)

  const inventoryItems = computed(() => inventory.value?.items ?? [])

  const visibleItems = computed(() => {
    return showAllItems.value ? inventoryItems.value : inventoryItems.value.slice(0, 3)
  })

  const visibleTransactions = computed(() => {
    return showAllTransactions.value ? transactions.value : transactions.value.slice(0, 3)
  })

  const visibleRanking = computed(() => {
    return showFullRanking.value ? scoreboard.value : scoreboard.value.slice(0, 3)
  })

  const selectedCoins = computed(() => {
    const account = tournamentAccounts.value.find((account) => account.type === "coins")
    return account?.balance ?? 0
  })

  const selectedPoints = computed(() => {
    const account = tournamentAccounts.value.find((account) => account.type === "points")
    return account?.balance ?? 0
  })

  const currentTeamRank = computed(() => {
    if (!currentTeam.value) {
      return null
    }

    const index = scoreboard.value.findIndex((team) => team.name === currentTeam.value?.name)
    return index === -1 ? null : index + 1
  })

  async function loadCurrentTeam() {
    const api = new BackendAPI()
    currentTeam.value = await api.getCurrentTeam()
  }

  async function loadTournaments() {
    const api = new BackendAPI()
    tournaments.value = await api.getTournaments()

    const firstTournament = tournaments.value[0]

    if (firstTournament) {
      selectedTournamentSlug.value = firstTournament.slug
    }
  }

  async function loadInventory() {
    if (!currentTeam.value || !selectedTournamentSlug.value) {
      inventory.value = null
      return
    }

    const api = new BackendAPI()
    inventory.value = await api.getInventoryForTeamAndTournament(currentTeam.value.id, selectedTournamentSlug.value)
  }

  async function loadTournamentAccounts() {
    if (!currentTeam.value || !selectedTournamentSlug.value) {
      tournamentAccounts.value = []
      return
    }

    const api = new BackendAPI()
    tournamentAccounts.value = await api.getTournamentAccountForTeamAndTournament(
      currentTeam.value.id,
      selectedTournamentSlug.value,
    )
  }

  async function loadTransactions() {
    if (!currentTeam.value || !selectedTournamentSlug.value) {
      transactions.value = []
      return
    }

    const api = new BackendAPI()
    transactions.value = await api.getTransactionsForTeamAndTournament(
      currentTeam.value.id,
      selectedTournamentSlug.value,
    )
  }

  async function loadScoreboard() {
    if (!selectedTournamentSlug.value) {
      scoreboard.value = []
      return
    }

    const api = new BackendAPI()
    scoreboard.value = await api.getScoreboard(selectedTournamentSlug.value)
  }

  async function loadTournamentData() {
    await Promise.all([loadInventory(), loadTournamentAccounts(), loadTransactions(), loadScoreboard()])
  }

  async function loadPage() {
    isLoading.value = true
    errorMessage.value = ""

    try {
      await Promise.all([loadCurrentTeam(), loadTournaments()])
      await loadTournamentData()
    } catch (err) {
      console.error("Failed to load inventory:", err)
      errorMessage.value = "Failed to load inventory."
    } finally {
      isLoading.value = false
    }
  }

  async function useItem(usableItemId: number) {
    const api = new BackendAPI()

    try {
      await api.useUsableItem(usableItemId)
      await loadInventory()
    } catch (err) {
      console.error("Failed to use item:", err)
      errorMessage.value = "Failed to use item."
    }
  }

  function goToStore() {
    if (!selectedTournamentSlug.value) {
      return
    }

    router.push(`/marketplace/${selectedTournamentSlug.value}`)
  }

  function formatDate(dateValue: string): string {
    return new Date(dateValue).toLocaleString("en-GB", {
      day: "numeric",
      month: "long",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  function toggleItems() {
    showAllItems.value = !showAllItems.value
  }

  function toggleTransactions() {
    showAllTransactions.value = !showAllTransactions.value
  }

  function toggleRanking() {
    showFullRanking.value = !showFullRanking.value
  }

  watch(selectedTournamentSlug, async () => {
    if (!isLoading.value) {
      showAllItems.value = false
      showAllTransactions.value = false
      showFullRanking.value = false
      await loadTournamentData()
    }
  })

  onMounted(loadPage)
</script>

<template>
  <div class="page">
    <Header :show-menu-button="true" :show-profile-button="true" />

    <main class="page-main">
      <p v-if="isLoading" class="empty-state dark-card">Loading inventory...</p>

      <p v-else-if="errorMessage" class="empty-state dark-card">
        {{ errorMessage }}
      </p>

      <template v-else>
        <section class="hero-card inventory-hero">
          <p class="hero-kicker">Inventory</p>
          <h1>{{ currentTeam?.name ?? "No team found" }}</h1>

          <label class="tournament-select-label" for="tournament-select">Tournament</label>

          <select id="tournament-select" v-model="selectedTournamentSlug" class="tournament-select">
            <option v-for="tournament in tournaments" :key="tournament.id" :value="tournament.slug">
              {{ tournament.name }}
            </option>
          </select>

          <p class="hero-text">
            Total points: {{ selectedPoints }}<br />
            Total coins: {{ selectedCoins }}<br />
            <span v-if="currentTeamRank">Rank: #{{ currentTeamRank }}</span>
          </p>
        </section>

        <section class="dark-card">
          <div class="section-header">
            <h2>Tournament ranking</h2>
            <span v-if="currentTeamRank" class="rank-pill">Your rank: #{{ currentTeamRank }}</span>
          </div>

          <div v-if="scoreboard.length > 0" class="ranking-list">
            <div
              v-for="(team, index) in visibleRanking"
              :key="team.name"
              class="ranking-row"
              :class="{ current: team.name === currentTeam?.name }"
            >
              <strong>#{{ index + 1 }}</strong>
              <span>{{ team.name }}</span>
              <span>{{ team.points }} points</span>
            </div>
          </div>

          <p v-else class="empty-state">No ranking found for this tournament yet.</p>

          <button
            v-if="scoreboard.length > 3"
            class="primary-button center-button"
            type="button"
            @click="toggleRanking"
          >
            {{ showFullRanking ? "Show less ranking" : "Show full ranking" }}
          </button>
        </section>

        <section class="dark-card">
          <h2>Group members</h2>

          <p v-if="!currentTeam">No team found.</p>

          <p v-for="member in currentTeam?.members ?? []" :key="member">
            {{ member }}
          </p>
        </section>

        <section class="dark-card">
          <div class="section-header">
            <h2>Usable items</h2>
            <button class="secondary-button" type="button" @click="goToStore">Go to store</button>
          </div>

          <div v-if="inventoryItems.length > 0" class="inventory-items">
            <article
              v-for="usableItem in visibleItems"
              :key="usableItem.id"
              class="inventory-item-card"
              :class="{ 'without-thumbnail': !usableItem.item.thumbnail }"
            >
              <img
                v-if="usableItem.item.thumbnail"
                class="inventory-item-thumbnail"
                :src="usableItem.item.thumbnail"
                :alt="usableItem.item.name"
              />

              <div class="inventory-item-content">
                <div class="inventory-item-header">
                  <div>
                    <h3>{{ usableItem.item.name }}</h3>
                  </div>

                  <div class="item-actions-top">
                    <span class="badge badge-unused">Available</span>

                    <button class="primary-button use-button" type="button" @click="useItem(usableItem.id)">
                      Use item
                    </button>
                  </div>
                </div>

                <p>{{ usableItem.item.description }}</p>

                <strong class="item-price">{{ usableItem.item.price }} coins</strong>
              </div>
            </article>
          </div>

          <p v-else class="empty-state">No usable items for this tournament yet.</p>

          <button
            v-if="inventoryItems.length > 3"
            class="primary-button center-button"
            type="button"
            @click="toggleItems"
          >
            {{ showAllItems ? "Show less items" : "Show all items" }}
          </button>
        </section>

        <section class="dark-card">
          <div class="section-header">
            <h2>Latest transactions</h2>
          </div>

          <div v-if="transactions.length > 0" class="transactions-preview">
            <div v-for="transaction in visibleTransactions" :key="transaction.id" class="transaction-row">
              <div>
                <span>{{ transaction.description }}</span>
                <small>{{ formatDate(transaction.requested_at) }}</small>
              </div>

              <strong
                class="transaction-amount"
                :class="{
                  positive: transaction.amount > 0,
                  negative: transaction.amount < 0,
                }"
              >
                {{ transaction.amount > 0 ? `+ ${transaction.amount}` : transaction.amount }}
              </strong>
            </div>
          </div>

          <p v-else class="empty-state">No transactions for this tournament yet.</p>

          <button
            v-if="transactions.length > 3"
            class="primary-button center-button"
            type="button"
            @click="toggleTransactions"
          >
            {{ showAllTransactions ? "Show less transactions" : "Show all transactions" }}
          </button>
        </section>
      </template>
    </main>
  </div>
</template>

<style scoped>
  .inventory-hero {
    text-align: center;
  }

  .tournament-select-label {
    display: block;
    margin: 1.5rem 0 0.4rem;
    color: var(--text-muted-light);
    font-weight: 700;
  }

  .tournament-select {
    width: min(100%, 360px);
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 999px;
    padding: 0.75rem 1rem;
    background: rgba(255, 255, 255, 0.08);
    color: var(--text-light);
    font-weight: 700;
    text-align: center;
  }

  .tournament-select option {
    color: var(--dark);
  }

  .dark-card h2 {
    margin: 0 0 1rem;
    font-family: "Gill Sans MT Condensed", sans-serif;
    font-size: clamp(1.6rem, 3vw, 2.25rem);
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }

  .dark-card p {
    color: var(--text-muted-light);
    font-size: 1rem;
    line-height: 1.5;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
  }

  .ranking-list,
  .inventory-items,
  .transactions-preview {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-top: 1.5rem;
  }

  .ranking-row {
    display: grid;
    grid-template-columns: max-content 1fr max-content;
    gap: 1rem;
    align-items: center;
    color: var(--text-muted-light);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: var(--radius-md);
    padding: 0.9rem 1rem;
    background: rgba(255, 255, 255, 0.04);
  }

  .ranking-row.current {
    border-color: var(--primary);
  }

  .rank-pill {
    color: var(--primary);
    font-weight: 700;
  }

  .inventory-item-card {
    display: grid;
    grid-template-columns: 110px 1fr;
    gap: 1rem;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: var(--radius-md);
    padding: 1rem;
    background: rgba(255, 255, 255, 0.04);
  }

  .inventory-item-card.without-thumbnail {
    grid-template-columns: 1fr;
  }

  .inventory-item-thumbnail {
    width: 110px;
    height: 110px;
    object-fit: cover;
    border-radius: var(--radius-md);
    background: rgba(255, 255, 255, 0.08);
  }

  .inventory-item-content {
    min-width: 0;
  }

  .inventory-item-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
  }

  .inventory-item-header h3 {
    margin: 0;
    font-size: 1.5rem;
    font-family: "Gill Sans MT Condensed", sans-serif;
    letter-spacing: 0.03em;
    text-transform: uppercase;
  }

  .inventory-item-header small,
  .transaction-row small {
    display: block;
    margin-top: 0.25rem;
    color: var(--text-muted-light);
    font-weight: 700;
  }

  .item-actions-top {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.75rem;
  }

  .item-price {
    display: block;
    margin-top: 0.75rem;
    color: var(--primary);
  }

  .use-button {
    margin: 0;
  }

  .transaction-row {
    display: grid;
    grid-template-columns: 1fr max-content;
    align-items: center;
    column-gap: 2rem;
    color: var(--text-muted-light);
    font-size: 1rem;
    line-height: 1.5;
  }

  .badge {
    color: white;
    border-radius: 999px;
    padding: 0.3rem 0.8rem;
    font-size: 0.8rem;
    font-weight: 700;
    text-align: center;
    min-width: 100px;
    white-space: nowrap;
  }

  .badge-unused,
  .transaction-amount.positive {
    background: #5a8f68;
  }

  .transaction-amount.negative {
    background: #b94a48;
  }

  .transaction-amount {
    min-width: 100px;
    text-align: center;
    color: white;
    border-radius: 999px;
    padding: 0.3rem 0.8rem;
    font-size: 0.8rem;
    font-weight: 700;
    background: rgba(255, 255, 255, 0.12);
  }

  .center-button {
    display: block;
    margin: 1.5rem auto 0;
  }

  .empty-state {
    text-align: center;
    padding: 2rem;
    color: var(--text-muted-light);
  }

  @media (max-width: 600px) {
    .section-header,
    .inventory-item-header {
      flex-direction: column;
    }

    .item-actions-top {
      align-items: flex-start;
    }

    .ranking-row,
    .transaction-row {
      grid-template-columns: 1fr;
      gap: 0.5rem;
    }

    .inventory-item-card {
      grid-template-columns: 1fr;
    }

    .inventory-item-thumbnail {
      width: 100%;
      height: 180px;
    }

    .badge,
    .transaction-amount {
      justify-self: flex-start;
    }
  }
</style>
