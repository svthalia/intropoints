<script setup lang="ts">
  import ChallengeCard from "@/components/ChallengeCard.vue"
  import { computed, onMounted, ref } from "vue"
  import type Challenge from "@/models/challenge.model"
  import type { Scoreboard } from "@/models/tournament.model"
  import type Team from "@/models/teams.model"
  import Loader from "@/components/Loader.vue"
  import Header from "@/components/Header.vue"
  import { BackendAPI } from "@/api/backend"

  const props = defineProps<{
    slug?: string
  }>()

  const api = new BackendAPI()

  const challenges = ref<Challenge[] | null>(null)
  const challengesLoading = ref<boolean | null>(true)

  const scoreboard = ref<Scoreboard[]>([])
  const scoreboardLoading = ref<boolean>(true)
  const currentTeam = ref<Team | null>(null)

  const showFullRanking = ref(false)
  const selectedCompletion = ref("all")

  const topThreeScoreboard = computed(() => {
    return scoreboard.value.slice(0, 3)
  })

  const fullScoreboard = computed(() => {
    return scoreboard.value
  })

  function isCurrentTeam(team: Scoreboard): boolean {
    return team.name === currentTeam.value?.name
  }

  onMounted(async () => {
    const tournamentSlug = props.slug ?? ""

    try {
      const currentTeam = await api.getCurrentTeam()
      const challengeRequest = props.slug ? api.getChallengesForTournament(props.slug) : api.getChallenges()

      const [challengeResult, submissionResult, scoreboardResult] = await Promise.all([
        challengeRequest,
        currentTeam ? api.getSubmissionsForTeam(currentTeam.name).catch(() => []) : Promise.resolve([]),
        api.getScoreboard(tournamentSlug).catch(() => []),
      ])

      challenges.value = challengeResult
        .filter((challenge) => {
          if (challenge.active_until !== null) {
            return !(Date.parse(String(challenge.active_until)) < Date.parse(new Date().toISOString()))
          }

          return true
        })
        .map((challenge) => {
          challenge.completed = submissionResult.some((submission) => {
            return submission.challenge_slug === challenge.slug && submission.accepted
          })

          return challenge
        })

      scoreboard.value = scoreboardResult
      scoreboardLoading.value = false
      challengesLoading.value = false
    } catch (err) {
      console.error("Failed to load challenges:", err)
      scoreboardLoading.value = false
      challengesLoading.value = null
    }
  })

  const filteredChallenges = computed(() => {
    if (challenges.value === null) {
      return []
    }

    return challenges.value.filter((challenge) => {
      return (
        selectedCompletion.value === "all" ||
        (selectedCompletion.value === "completed" && challenge.completed) ||
        (selectedCompletion.value === "not_completed" && !challenge.completed)
      )
    })
  })
</script>

<template>
  <div class="page">
    <Header :show-menu-button="true" :show-profile-button="true" />

    <main class="page-main">
      <section class="scoreboard-card dark-card">
        <div class="scoreboard-header">
          <p class="scoreboard-kicker">Leaderboard</p>
          <h2>Top 3 Teams</h2>
        </div>

        <div v-if="scoreboardLoading" class="scoreboard-loading">
          <Loader size="50px" background-color="#ffffff" />
        </div>

        <p v-else-if="topThreeScoreboard.length === 0" class="scoreboard-empty">No teams on the scoreboard yet.</p>

        <template v-else>
          <div class="scoreboard-list">
            <article
              v-for="(team, index) in topThreeScoreboard"
              :key="team.name"
              class="scoreboard-team"
              :class="{ current: isCurrentTeam(team) }"
            >
              <div class="scoreboard-rank">
                {{ index + 1 }}
              </div>

              <div class="scoreboard-info">
                <h3>{{ team.name }}</h3>
                <p>{{ team.points }} points</p>
              </div>
            </article>
          </div>

          <button class="scoreboard-button" @click="showFullRanking = !showFullRanking">
            {{ showFullRanking ? "Hide Full Ranking" : "Show Full Ranking" }}
          </button>

          <div v-if="showFullRanking" class="full-scoreboard">
            <article
              v-for="(team, index) in fullScoreboard"
              :key="team.name"
              class="full-scoreboard-team"
              :class="{ current: isCurrentTeam(team) }"
            >
              <div class="full-scoreboard-rank">#{{ index + 1 }}</div>

              <div class="full-scoreboard-info">
                <h3>{{ team.name }}</h3>
                <p>{{ team.points }} points</p>
              </div>
            </article>
          </div>
        </template>
      </section>

      <section class="hero-card">
        <p class="hero-kicker">Overview</p>
        <h1>Challenges</h1>
        <p class="hero-text">Browse available challenges and track which ones your team has completed.</p>

        <div class="challenge-filter">
          <div class="filter-field">
            <label for="challenge-filter">Challenges</label>
            <select id="challenge-filter" v-model="selectedCompletion">
              <option value="all">All challenges</option>
              <option value="completed">Completed challenges</option>
              <option value="not_completed">Not completed challenges</option>
            </select>
          </div>
        </div>
      </section>

      <section class="challenge-list">
        <div v-if="challengesLoading === true" class="loader-state dark-card">
          <Loader size="60px" background-color="#ffffff" />
          <p>Loading challenges...</p>
        </div>

        <p v-else-if="challengesLoading === null" class="empty-state dark-card">
          Failed to load challenges, please try again.
        </p>

        <p v-else-if="filteredChallenges.length === 0" class="empty-state dark-card">
          There are no challenges for this tournament yet.
        </p>

        <ChallengeCard v-else v-for="challenge in filteredChallenges" :key="challenge.id" :challenge="challenge" />
      </section>
    </main>
  </div>
</template>

<style scoped>
  .scoreboard-card {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  .scoreboard-header {
    text-align: center;
  }

  .scoreboard-kicker {
    margin: 0 0 0.25rem;
    color: var(--primary);
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .scoreboard-header h2 {
    margin: 0;
    color: var(--text-light);
    font-size: 2rem;
  }

  .scoreboard-loading,
  .scoreboard-empty {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 120px;
    margin: 0;
    color: var(--text-muted-light);
    text-align: center;
  }

  .scoreboard-list {
    display: flex;
    justify-content: center;
    align-items: flex-end;
    gap: 1rem;
    margin-top: 1rem;
  }

  .scoreboard-team {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    padding: 1rem;
    border-radius: 1.25rem 1.25rem 0 0;
    background: rgba(255, 255, 255, 0.08);
    width: 180px;
    text-align: center;
    position: relative;
    transition: transform 0.2s ease;
  }

  .scoreboard-team.current {
    border: 2px solid var(--primary);
  }

  .scoreboard-team.current .scoreboard-rank,
  .full-scoreboard-team.current .full-scoreboard-rank {
    color: white;
  }

  .full-scoreboard-team.current {
    border: 2px solid var(--primary);
    background: rgba(230, 34, 114, 0.16);
  }

  .scoreboard-team:hover {
    transform: translateY(-4px);
  }

  .scoreboard-team:nth-child(1) {
    order: 2;
    min-height: 260px;
    background: linear-gradient(180deg, #ffd70022 0%, rgba(255, 255, 255, 0.08) 100%);
  }

  .scoreboard-team:nth-child(2) {
    order: 1;
    min-height: 210px;
  }

  .scoreboard-team:nth-child(3) {
    order: 3;
    min-height: 180px;
  }

  .scoreboard-rank {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 3.5rem;
    height: 3.5rem;
    border-radius: 50%;
    background: var(--primary);
    color: var(--text-light);
    font-size: 1.5rem;
    font-weight: 800;
    margin-bottom: 1rem;
  }

  .scoreboard-team:nth-child(1) .scoreboard-rank {
    width: 4.25rem;
    height: 4.25rem;
    font-size: 2rem;
  }

  .scoreboard-info {
    min-width: 0;
  }

  .scoreboard-info h3 {
    margin: 0;
    color: var(--text-light);
    font-size: 1.15rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .scoreboard-info p {
    margin: 0.35rem 0 0;
    color: var(--text-muted-light);
  }

  .challenge-filter {
    margin-top: 1.5rem;
    display: grid;
    grid-template-columns: 1fr;
  }

  .filter-field {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    min-width: 0;
  }

  .filter-field label {
    color: var(--primary);
    font-family: "Gill Sans MT Condensed", sans-serif;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .filter-field select,
  .filter-field input {
    width: 100%;
    border: 0;
    border-radius: var(--radius-sm);
    padding: 0.85rem 1.1rem;
    background: var(--primary);
    color: white;
    font-weight: 700;
  }

  .filter-field input::placeholder {
    color: rgba(255, 255, 255, 0.75);
  }

  .scoreboard-button {
    align-self: center;
    padding: 0.85rem 1.4rem;
    border: none;
    border-radius: 999px;
    background: var(--primary);
    color: white;
    font-weight: 700;
    cursor: pointer;
    transition:
      transform 0.2s ease,
      opacity 0.2s ease;
  }

  .scoreboard-button:hover {
    transform: translateY(-2px);
    opacity: 0.9;
  }

  .full-scoreboard {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-top: 1rem;
  }

  .full-scoreboard-team {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 1rem 1.25rem;
    border-radius: 1rem;
    background: rgba(255, 255, 255, 0.06);
  }

  .full-scoreboard-rank {
    color: var(--primary);
    font-weight: 800;
    font-size: 1.1rem;
  }

  .full-scoreboard-info {
    flex: 1;
    min-width: 0;
  }

  .full-scoreboard-info h3 {
    margin: 0;
    color: var(--text-light);
    font-size: 1rem;
  }

  .full-scoreboard-info p {
    margin: 0.25rem 0 0;
    color: var(--text-muted-light);
    font-size: 0.9rem;
  }

  .challenge-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-top: 1.5rem;
  }

  .loader-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .loader-state p,
  .empty-state {
    margin: 0;
    color: var(--text-muted-light);
    text-align: center;
    line-height: 1.5;
  }

  .empty-state {
    padding: 2rem;
  }

  @media (max-width: 800px) {
    .scoreboard-list {
      display: flex;
      flex-direction: row;
      align-items: flex-end;
      gap: 0.5rem;
    }

    .scoreboard-team {
      width: 33%;
      padding: 0.75rem 0.4rem;
      border-radius: 1rem 1rem 0 0;
    }

    .scoreboard-team:nth-child(1) {
      order: 2;
      min-height: 220px;
    }

    .scoreboard-team:nth-child(2) {
      order: 1;
      min-height: 170px;
    }

    .scoreboard-team:nth-child(3) {
      order: 3;
      min-height: 140px;
    }

    .scoreboard-rank {
      width: 2.75rem;
      height: 2.75rem;
      font-size: 1.25rem;
    }

    .scoreboard-team:nth-child(1) .scoreboard-rank {
      width: 3.25rem;
      height: 3.25rem;
      font-size: 1.5rem;
    }

    .scoreboard-info h3 {
      max-width: 100%;
      font-size: 0.9rem;
    }

    .scoreboard-info p {
      font-size: 0.8rem;
    }

    .full-scoreboard-team {
      padding: 0.85rem;
    }
  }
</style>
