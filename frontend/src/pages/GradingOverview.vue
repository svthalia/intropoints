<script setup lang="ts">
  import { computed, onMounted, ref, watch } from "vue"
  import Header from "@/components/Header.vue"
  import { BackendAPI } from "@/api/backend"
  import type { SubmissionPreview } from "@/models/submission.model"
  import SubmissionCard from "@/components/SubmissionCard.vue"
  import { useRouter } from "vue-router"

  const router = useRouter()

  const selectedTeam = ref("all")
  const selectedTournament = ref("all")
  const selectedChallenge = ref("all")
  const searchQuery = ref("")

  const submissions = ref<SubmissionPreview[]>([])

  const isLoading = ref(true)
  const errorMessage = ref("")

  async function loadSubmissions() {
    isLoading.value = true
    errorMessage.value = ""

    try {
      const apiService = new BackendAPI()
      submissions.value = await apiService.getAllSubmissionsForGrading()
    } catch (err) {
      console.error("Failed to load submissions:", err) // TODO: Remove this log
      errorMessage.value = "Failed to load submissions."
    } finally {
      isLoading.value = false
    }
  }

  const teams = computed(() => {
    return [...new Set(submissions.value.map((submission) => submission.team_name))].sort()
  })

  const tournaments = computed(() => {
    return [...new Set(submissions.value.map((submission) => submission.tournament_name))].sort()
  })

  const challenges = computed(() => {
    const visibleSubmissions =
      selectedTournament.value === "all"
        ? submissions.value
        : submissions.value.filter((submission) => submission.tournament_name === selectedTournament.value)

    return [...new Set(visibleSubmissions.map((submission) => submission.challenge_name))].sort()
  })

  watch(selectedTournament, () => {
    if (selectedChallenge.value !== "all" && !challenges.value.includes(selectedChallenge.value)) {
      selectedChallenge.value = "all"
    }
  })

  const filteredSubmissions = computed(() => {
    return submissions.value.filter((submission) => {
      const matchesStatus = submission.accepted === null

      const matchesTeam = selectedTeam.value === "all" || submission.team_name === selectedTeam.value

      const matchesTournament =
        selectedTournament.value === "all" || submission.tournament_name === selectedTournament.value

      const matchesChallenge =
        selectedChallenge.value === "all" || submission.challenge_name === selectedChallenge.value

      const search = searchQuery.value.toLowerCase().trim()

      const matchesSearch =
        search === "" ||
        submission.team_name.toLowerCase().includes(search) ||
        submission.tournament_name.toLowerCase().includes(search) ||
        submission.challenge_name.toLowerCase().includes(search) ||
        submission.created_by?.toLowerCase().includes(search)

      return matchesStatus && matchesTeam && matchesTournament && matchesChallenge && matchesSearch
    })
  })

  function startGrading(id: number) {
    router.push({
      name: "Grading",
      params: { id },
    })
  }

  onMounted(loadSubmissions)
</script>

<template>
  <div class="page">
    <Header :show-menu-button="true" :show-profile-button="true" />

    <main class="page-main">
      <section class="hero-card">
        <div class="hero-top">
          <div>
            <p class="hero-kicker">Admin</p>
            <h1>Grading Overview</h1>
            <p class="hero-text">Review all ungraded submissions and assign points.</p>
          </div>
        </div>

        <div class="submission-filters">
          <div class="filter-field">
            <label for="submission-search">Search</label>
            <input id="submission-search" v-model="searchQuery" type="text" placeholder="Search submissions..." />
          </div>

          <div class="filter-field">
            <label for="team-filter">Team</label>
            <select id="team-filter" v-model="selectedTeam">
              <option value="all">All teams</option>
              <option v-for="team in teams" :key="team" :value="team">
                {{ team }}
              </option>
            </select>
          </div>

          <div class="filter-field">
            <label for="tournament-filter">Tournament</label>
            <select id="tournament-filter" v-model="selectedTournament">
              <option value="all">All tournaments</option>
              <option v-for="tournament in tournaments" :key="tournament" :value="tournament">
                {{ tournament }}
              </option>
            </select>
          </div>

          <div class="filter-field">
            <label for="challenge-filter">Challenge</label>
            <select id="challenge-filter" v-model="selectedChallenge">
              <option value="all">All challenges</option>
              <option v-for="challenge in challenges" :key="challenge" :value="challenge">
                {{ challenge }}
              </option>
            </select>
          </div>
        </div>
      </section>

      <section class="submission-list">
        <p v-if="isLoading" class="empty-state dark-card">Loading submissions...</p>
        <p v-else-if="errorMessage" class="empty-state dark-card">{{ errorMessage }}</p>

        <template v-else>
          <div
            v-for="submission in filteredSubmissions"
            :key="submission.id"
            @click="startGrading(submission.id)"
            class="submission-link"
          >
            <SubmissionCard :submission="submission" />
          </div>
          <p v-if="filteredSubmissions.length === 0" class="empty-state dark-card">No ungraded submissions found.</p>
        </template>
      </section>
    </main>
  </div>
</template>

<style scoped>
  .hero-top {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
  }

  .submission-filters {
    margin-top: 1.5rem;
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 0.75rem;
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

  .submission-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .empty-state {
    margin: 0;
    color: var(--text-muted-light);
    line-height: 1.5;
    text-align: center;
    padding: 2rem;
  }

  @media (max-width: 900px) {
    .submission-filters {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  @media (max-width: 600px) {
    .hero-top {
      flex-direction: column;
    }

    .submission-filters {
      grid-template-columns: 1fr;
    }

    .submission-modal-overlay {
      padding: 0.5rem;
    }
  }
</style>
