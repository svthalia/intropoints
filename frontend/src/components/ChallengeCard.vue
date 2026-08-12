<script setup lang="ts">
  import { RouterLink } from "vue-router"
  import type Challenge from "@/models/challenge.model"

  const { challenge } = defineProps<{ challenge: Challenge }>()

  const current_time = Date.parse(new Date().toISOString())

  function startTimeOfChallenge(challenge: Challenge): string {
    if (challenge.available_from) {
      const start_date = new Date(challenge.available_from)

      return `${start_date.toLocaleDateString("en-GB")}, ${start_date.toLocaleTimeString("en-GB", {
        hour: "2-digit",
        minute: "2-digit",
      })}`
    }

    return ""
  }

  function shortenedDescription(description: string): string {
    if (description.length < 100) {
      return description
    }

    return description.substring(0, 100) + "..."
  }
</script>

<template>
  <!-- Challenge not yet available -->
  <div
    v-if="Date.parse(String(challenge.available_from)) > current_time"
    class="dark-card challenge-card disabled-card"
  >
    <div class="challenge-header">
      <div>
        <h2 :class="{ completed: challenge.completed }">
          {{ challenge.name }}
        </h2>

        <p class="challenge-points">{{ challenge.points }} points</p>
      </div>

      <div class="status-badge pending">Upcoming</div>
    </div>

    <p class="challenge-description">Available from {{ startTimeOfChallenge(challenge) }}</p>
  </div>

  <!-- Challenge expired -->
  <div
    v-else-if="Date.parse(String(challenge.active_until)) < current_time"
    class="dark-card challenge-card disabled-card"
  >
    <div class="challenge-header">
      <div>
        <h2 :class="{ completed: challenge.completed }">
          {{ challenge.name }}
        </h2>

        <p class="challenge-points">{{ challenge.points }} points</p>
      </div>

      <div class="status-badge rejected">Expired</div>
    </div>

    <p class="challenge-description">Not available anymore</p>
  </div>

  <!-- Active challenge -->
  <router-link v-else :to="{ name: 'ChallengeSubmission', params: { slug: challenge.slug } }" class="challenge-link">
    <article class="dark-card challenge-card active-card">
      <div class="challenge-header">
        <div>
          <h2 :class="{ completed: challenge.completed }">
            {{ challenge.name }}
          </h2>

          <p class="challenge-points">{{ challenge.points }} points</p>
        </div>

        <div v-if="challenge.submission_visibility === 2 && !challenge.completed" class="status-badge rejected">
          Hidden submissions
        </div>

        <div v-else-if="challenge.completed" class="status-badge accepted">Completed</div>
      </div>

      <p class="challenge-description">
        {{ shortenedDescription(challenge.description) }}
      </p>
    </article>
  </router-link>
</template>

<style scoped>
  .challenge-link {
    text-decoration: none;
    color: inherit;
  }

  .challenge-card {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .active-card {
    cursor: pointer;
  }

  .disabled-card {
    opacity: 0.7;
  }

  .challenge-header {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    align-items: flex-start;
  }

  .challenge-header h2 {
    margin: 0;
    font-family: "Gill Sans MT Condensed", sans-serif;
    font-size: clamp(1.8rem, 3vw, 2.6rem);
    letter-spacing: 0.03em;
    text-transform: uppercase;
    color: white;
  }

  .challenge-points {
    margin: 0.35rem 0 0;
    color: var(--primary);
    font-family: "Open Sans Condensed", sans-serif;
    font-size: 1.15rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  .challenge-description {
    margin: 0;
    color: var(--text-muted-light);
    line-height: 1.6;
  }

  .status-badge {
    flex-shrink: 0;
    color: white;
    border-radius: var(--radius-sm);
    padding: 0.45rem 0.8rem;
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    white-space: nowrap;
  }

  .status-badge.accepted {
    background: #16a34a;
    color: white;
  }

  .status-badge.pending {
    background: #c58b1f;
  }

  .status-badge.rejected {
    background: #9f2f2f;
  }

  @media (max-width: 600px) {
    .challenge-header {
      flex-direction: column;
    }

    .status-badge {
      align-self: flex-start;
    }
  }
</style>
