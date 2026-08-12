<script setup lang="ts">
  import { computed, onMounted, ref } from "vue"
  import Header from "@/components/Header.vue"
  import { BackendAPI } from "@/api/backend"
  import type { Tournament, Scoreboard } from "@/models/tournament.model"
  import type Team from "@/models/teams.model"

  const tournaments = ref<Tournament[]>([])
  const currentTeam = ref<Team | null>(null)
  const rankings = ref<Record<number, number | string>>({})

  const isLoading = ref(true)
  const errorMessage = ref("")

  async function loadTournaments() {
    isLoading.value = true
    errorMessage.value = ""

    try {
      const apiService = new BackendAPI()

      const [teamResult, tournamentResult] = await Promise.all([
        apiService.getCurrentTeam(),
        apiService.getTournaments(),
      ])

      currentTeam.value = teamResult
      tournaments.value = tournamentResult

      const rankingEntries = await Promise.all(
        tournamentResult.map(async (tournament) => {
          const scoreboard: Scoreboard[] = await apiService.getScoreboard(tournament.slug).catch(() => [])

          const index = scoreboard.findIndex((team) => team.name === teamResult.name)

          return [tournament.id, index === -1 ? "-" : index + 1] as const
        }),
      )

      rankings.value = Object.fromEntries(rankingEntries)
    } catch (err) {
      console.error("Failed to load tournaments:", err)
      errorMessage.value = "Failed to load tournaments."
    } finally {
      isLoading.value = false
    }
  }

  const visibleTournaments = computed(() => {
    return tournaments.value.map((tournament) => ({
      ...tournament,
      currentPosition: rankings.value[tournament.id] ?? "-",
    }))
  })

  function formatDate(dateValue: string | null): string {
    if (!dateValue) {
      return "No date"
    }

    return new Date(dateValue).toLocaleString()
  }

  onMounted(loadTournaments)
</script>

<template>
  <div class="page">
    <Header :show-menu-button="true" :show-profile-button="true" />

    <main class="page-main">
      <section class="hero-card">
        <p class="hero-kicker">Overview</p>
        <h1>Tournament</h1>
        <p class="hero-text">View active tournaments, dates, and progress.</p>
      </section>

      <section class="tournament-list">
        <p v-if="isLoading" class="empty-state">Loading tournaments...</p>
        <p v-else-if="errorMessage" class="empty-state dark-card">{{ errorMessage }}</p>

        <template v-else>
          <router-link
            v-for="tournament in visibleTournaments"
            :key="tournament.id"
            :to="{ name: 'TournamentChallenges', params: { slug: tournament.slug } }"
            class="tournament-card dark-card tournament-link"
          >
            <div class="icon-box">
              <font-awesome-icon :icon="['fas', 'trophy']" />
            </div>

            <div class="tournament-content">
              <h2>{{ tournament.name }}</h2>
              <p>{{ formatDate(tournament.active_from) }} until {{ formatDate(tournament.active_until) }}</p>
              <p class="current-position">Current position: {{ tournament.currentPosition }}</p>
            </div>
          </router-link>

          <p v-if="visibleTournaments.length === 0" class="empty-state dark-card">No tournaments found.</p>
        </template>
      </section>
    </main>
  </div>
</template>

<style scoped>
  .tournament-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .tournament-link {
    color: white;
    text-decoration: none;
  }

  .tournament-card {
    display: flex;
    gap: 1rem;
    align-items: center;
  }

  .tournament-content {
    flex: 1;
  }

  .tournament-content h2 {
    margin: 0 0 0.45rem 0;
    font-size: clamp(1.7rem, 3vw, 2.35rem);
    font-family: "Gill Sans MT Condensed", sans-serif;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .tournament-content p {
    margin: 0;
    color: var(--text-muted-light);
    line-height: 1.5;
    font-size: 1rem;
  }

  .current-position {
    margin-top: 0.35rem !important;
    color: var(--primary) !important;
    font-family: "Gill Sans MT Condensed", sans-serif;
    font-size: 1.15rem !important;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;

    opacity: 0;
    max-height: 0;
    overflow: hidden;

    transition:
      opacity 0.2s ease,
      max-height 0.2s ease;
  }

  .tournament-card:hover .current-position {
    opacity: 1;
    max-height: 2rem;
  }

  .empty-state {
    margin: 0;
    text-align: center;
    padding: 2rem;
    color: var(--text-muted-light);
  }

  @media (hover: none) {
    .current-position {
      opacity: 1;
      max-height: 2rem;
    }
  }

  @media (max-width: 600px) {
    .tournament-card {
      align-items: flex-start;
    }
  }
</style>
