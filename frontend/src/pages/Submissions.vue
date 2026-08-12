<script setup lang="ts">
  import { computed, onMounted, ref, watch } from "vue"
  import Header from "@/components/Header.vue"
  import { BackendAPI } from "@/api/backend"
  import type { SubmissionPreview } from "@/models/submission.model"
  import SubmissionCard from "@/components/SubmissionCard.vue"
  import type Team from "@/models/teams.model"

  const selectedStatus = ref<"all" | "accepted" | "pending" | "rejected">("all")
  const selectedTeam = ref("all")
  const selectedTournament = ref("all")
  const selectedChallenge = ref("all")
  const searchQuery = ref("")

  const userTeam = ref<Team | null>(null)
  const submissions = ref<SubmissionPreview[]>([])

  const isLoading = ref(true)
  const errorMessage = ref("")

  async function loadUserTeam() {
    try {
      const apiService = new BackendAPI()
      userTeam.value = await apiService.getCurrentTeam()
    } catch (err) {
      console.error("Failed to load user team:", err)
      userTeam.value = null
    }
  }

  async function loadSubmissions() {
    isLoading.value = true
    errorMessage.value = ""

    try {
      const apiService = new BackendAPI()
      submissions.value = await apiService.getSubmissions()
    } catch (err) {
      console.error("Failed to load submissions:", err) // TODO: Remove this log
      errorMessage.value = "Failed to load submissions."
    } finally {
      isLoading.value = false
    }
  }

  const teamSubmissions = computed(() => {
    if (userTeam.value === null) {
      return []
    }

    return submissions.value.filter((submission) => {
      return submission.accepted === true && submission.team_name === userTeam.value?.name
    })
  })

  const acceptedChallengeSlugs = computed(() => {
    return new Set(teamSubmissions.value.map((submission) => submission.challenge_slug))
  })

  const visibleSubmissions = computed(() =>
    submissions.value.filter(
      (submission) =>
        submission.challenge_submission_visibility !== 2 || acceptedChallengeSlugs.value.has(submission.challenge_slug),
    ),
  )

  const teams = computed(() => {
    return [...new Set(visibleSubmissions.value.map((submission) => submission.team_name))].sort()
  })

  const tournaments = computed(() => {
    return [...new Set(visibleSubmissions.value.map((submission) => submission.tournament_name))].sort()
  })

  const challenges = computed(() => {
    const tournamentSubmissions =
      selectedTournament.value === "all"
        ? visibleSubmissions.value
        : visibleSubmissions.value.filter((submission) => submission.tournament_name === selectedTournament.value)

    return [...new Set(tournamentSubmissions.map((submission) => submission.challenge_name))].sort()
  })

  watch(selectedTournament, () => {
    if (selectedChallenge.value !== "all" && !challenges.value.includes(selectedChallenge.value)) {
      selectedChallenge.value = "all"
    }
  })

  const filteredSubmissions = computed(() => {
    return visibleSubmissions.value.filter((submission) => {
      const matchesStatus =
        selectedStatus.value === "all" ||
        (selectedStatus.value === "accepted" && submission.accepted === true) ||
        (selectedStatus.value === "pending" && submission.accepted === null) ||
        (selectedStatus.value === "rejected" && submission.accepted === false)

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

  onMounted(async () => {
    await loadUserTeam()
    await loadSubmissions()
  })
</script>

<template>
  <div class="page">
    <Header :show-menu-button="true" :show-profile-button="true" />

    <main class="page-main">
      <section class="hero-card">
        <div class="hero-top">
          <div>
            <p class="hero-kicker">Overview</p>
            <h1>Submissions</h1>
            <p class="hero-text">View submitted photos, videos, uploaders, and submission status.</p>
          </div>
        </div>

        <div class="submission-filters">
          <div class="filter-field">
            <label for="submission-search">Search</label>
            <input id="submission-search" v-model="searchQuery" type="text" placeholder="Search submissions..." />
          </div>

          <div class="filter-field">
            <label for="status-filter">Status</label>
            <select id="status-filter" v-model="selectedStatus">
              <option value="all">All statuses</option>
              <option value="accepted">Accepted</option>
              <option value="pending">Pending</option>
              <option value="rejected">Rejected</option>
            </select>
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
          <SubmissionCard v-for="submission in filteredSubmissions" :key="submission.id" :submission="submission" />

          <p v-if="filteredSubmissions.length === 0" class="empty-state dark-card">No submissions found.</p>
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
