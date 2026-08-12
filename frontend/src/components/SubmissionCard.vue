<script setup lang="ts">
  import { ref } from "vue"
  import type { SubmissionPreview } from "@/models/submission.model"

  const props = defineProps<{
    submission: SubmissionPreview
  }>()

  const showModal = ref(false)

  function openSubmission(): void {
    showModal.value = true
  }

  function closeSubmission(): void {
    showModal.value = false
  }

  function getImageThumnail(submission: SubmissionPreview): string {
    if (submission.file.thumbnail != "" && submission.file.thumbnail != null) {
      return submission.file.thumbnail
    } else if (submission.file.source != null && submission.file.type.startsWith("image")) {
      return submission.file.source
    } else {
      return ""
    }
  }

  function isVideo(): boolean {
    return props.submission.file?.type?.startsWith("video") ?? false
  }

  function formatDate(dateValue: string): string {
    return new Date(dateValue).toLocaleString("en-GB")
  }
</script>

<template>
  <article class="dark-card submission-card" @click="openSubmission">
    <img
      v-if="getImageThumnail(submission)"
      class="submission-image"
      :src="getImageThumnail(submission)"
      :alt="`Submission ${submission.id}`"
    />

    <div v-else class="submission-image-placeholder">No file available</div>

    <div class="submission-header">
      <div>
        <h2>Team: {{ submission.team_name }}</h2>
        <p>Tournament: {{ submission.tournament_name }}</p>
        <p>Challenge: {{ submission.challenge_name }}</p>
        <p>Uploaded by: {{ submission.created_by ?? "Unknown" }}</p>
        <p>{{ formatDate(submission.created_time) }}</p>
      </div>

      <div
        class="status-badge"
        :class="{
          accepted: submission.accepted === true,
          pending: submission.accepted === null,
          rejected: submission.accepted === false,
        }"
      >
        <template v-if="submission.accepted === true">Accepted</template>
        <template v-else-if="submission.accepted === false">Rejected</template>
        <template v-else>Pending</template>
      </div>
    </div>
  </article>

  <div v-if="showModal" class="submission-modal-overlay" @click="closeSubmission">
    <div class="submission-modal dark-card" @click.stop>
      <button class="modal-close" type="button" @click="closeSubmission">×</button>

      <video v-if="isVideo() && submission.file.source" class="modal-media" :src="submission.file.source" controls />

      <img
        v-else-if="submission.file.source"
        class="modal-media"
        :src="submission.file.source"
        :alt="`Submission ${submission.id}`"
      />

      <div v-else class="modal-placeholder">No file available</div>

      <div class="modal-info">
        <h2>Team: {{ submission.team_name }}</h2>
        <p><strong>Tournament:</strong> {{ submission.tournament_name }}</p>
        <p><strong>Challenge:</strong> {{ submission.challenge_name }}</p>
        <p><strong>Uploaded by:</strong> {{ submission.created_by ?? "Unknown" }}</p>
        <p><strong>Uploaded at:</strong> {{ formatDate(submission.created_time) }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
  .submission-header {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
  }

  .submission-card {
    padding: 0;
    overflow: hidden;
    cursor: pointer;
    transition: opacity 0.2s ease;
  }

  .submission-card:hover {
    opacity: 0.9;
  }

  .submission-image,
  .submission-image-placeholder {
    width: 100%;
    height: clamp(12rem, 30vw, 22rem);
  }

  .submission-image {
    object-fit: cover;
    display: block;
  }

  .submission-image-placeholder {
    display: grid;
    place-items: center;
    background: rgba(255, 255, 255, 0.08);
    color: var(--text-muted-light);
    font-weight: 700;
  }

  .submission-header {
    padding: 1.35rem;
    align-items: flex-start;
  }

  .submission-header h2 {
    margin: 0 0 0.45rem;
    font-family: "Gill Sans MT Condensed", sans-serif;
    font-size: clamp(1.7rem, 3vw, 2.35rem);
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .submission-header p {
    margin: 0;
    color: var(--text-muted-light);
    line-height: 1.5;
  }

  .status-badge {
    flex-shrink: 0;
    color: white;
    border-radius: var(--radius-sm);
    padding: 0.45rem 0.8rem;
    font-weight: 700;
    white-space: nowrap;
  }

  .status-badge.accepted {
    background: var(--primary);
  }

  .status-badge.pending {
    background: #c58b1f;
  }

  .status-badge.rejected {
    background: #9f2f2f;
  }

  .submission-modal-overlay {
    position: fixed;
    inset: 0;
    z-index: 2000;
    padding: 1rem;
    background: rgba(0, 0, 0, 0.75);
    display: grid;
    place-items: center;
  }

  .submission-modal {
    position: relative;
    width: min(100%, 1000px);
    max-height: 92vh;
    padding: 0;
    overflow: auto;
  }

  .modal-close {
    position: absolute;
    top: 0.75rem;
    right: 0.75rem;
    z-index: 1;
    width: 2.3rem;
    height: 2.3rem;
    border: 0;
    border-radius: 50%;
    background: var(--primary);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    cursor: pointer;
  }

  .modal-media,
  .modal-placeholder {
    width: 100%;
    max-height: 70vh;
  }

  .modal-media {
    display: block;
    object-fit: contain;
    background: black;
  }

  .modal-placeholder {
    min-height: 20rem;
    display: grid;
    place-items: center;
    color: var(--text-muted-light);
  }

  .modal-info {
    padding: 1.35rem;
  }

  .modal-info h2 {
    margin: 0 0 0.75rem;
    font-family: "Gill Sans MT Condensed", sans-serif;
    font-size: clamp(1.8rem, 3vw, 2.5rem);
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .modal-info p {
    margin: 0;
    color: var(--text-muted-light);
    line-height: 1.6;
  }

  @media (max-width: 600px) {
    .submission-header {
      flex-direction: column;
    }

    .status-badge {
      align-self: flex-start;
    }

    .submission-modal-overlay {
      padding: 0.5rem;
    }
  }
</style>
