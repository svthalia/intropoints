<script setup lang="ts">
  import { computed, onBeforeUnmount, onMounted, ref } from "vue"
  import { useRouter } from "vue-router"
  import Header from "@/components/Header.vue"
  import { BackendAPI } from "@/api/backend"
  import { useToast } from "vue-toastification"
  import type { SubmissionPreview } from "@/models/submission.model"
  import type User from "@/models/user.model"
  import type Challenge from "@/models/challenge.model"

  const props = defineProps<{ id: number }>()

  const router = useRouter()
  const toast = useToast()

  const user = ref<User | null>(null)
  const submission = ref<SubmissionPreview | null>(null)
  const challenge = ref<Challenge | null>(null)

  const isLoading = ref(true)
  const errorMessage = ref("")

  const grade = ref<number>(0)
  const showFullMedia = ref(false)

  const isIcMember = computed(() => {
    return user.value?.permissions?.includes("users.ic_member") ?? false
  })

  async function loadPage() {
    isLoading.value = true
    errorMessage.value = ""

    try {
      const apiService = new BackendAPI()

      user.value = await apiService.getCurrentUser()
      submission.value = await apiService.getSubmissionForGrading(props.id)
      challenge.value = await apiService.getChallenge(submission.value.challenge_slug)
    } catch (error) {
      console.error("Failed to load submission for grading.", error)
      errorMessage.value =
        "Unable to load the submission. Either there is currently a lock on the submission or the submission id was not found."
    } finally {
      isLoading.value = false
    }
  }

  function getSubmissionImage(submission: SubmissionPreview): string {
    return submission.file?.source ?? ""
  }

  function getImageThumbnail(submission: SubmissionPreview): string {
    if (submission.file?.thumbnail !== "" && submission.file?.thumbnail != null) {
      return submission.file.thumbnail
    }

    if (submission.file?.source != null && submission.file.type.startsWith("image")) {
      return submission.file.source
    }

    return ""
  }

  function isVideo(): boolean {
    return submission.value?.file?.type?.startsWith("video") ?? false
  }

  function openFullMedia(): void {
    showFullMedia.value = true
  }

  function closeFullMedia(): void {
    showFullMedia.value = false
  }

  function formatDate(dateValue: string): string {
    return new Date(dateValue).toLocaleString("en-GB")
  }

  async function gradeSubmission(accepted: boolean): Promise<boolean> {
    let finalGrade = 0
    let fdAccepted = "False"

    if (accepted && challenge.value && grade.value >= 0) {
      finalGrade = Math.min(grade.value, challenge.value.points)
      fdAccepted = "True"
    }

    if (submission.value === null || !isIcMember.value) {
      return false
    }

    try {
      const APIInstance = new BackendAPI()
      const formData = new FormData()

      formData.append("submission_id", String(props.id))
      formData.append("accepted", fdAccepted)
      formData.append("points", String(finalGrade))

      await APIInstance.putGrade(formData)

      toast.success("Submission graded successfully!")
      return true
    } catch (error) {
      console.error("Failed to upload grade to backend", error)
      toast.error("An error occurred during grading, please try again.")
      return false
    }
  }

  async function cancelGrading(): Promise<void> {
    try {
      const APIInstance = new BackendAPI()
      await APIInstance.releaseLock(props.id)
      await router.push({ name: "GradingOverview" })
    } catch (error) {
      console.error("Failed to cancel grading", error)
      toast.error("Unable to cancel grading")
    }
  }

  function warnBeforeRefresh(event: BeforeUnloadEvent) {
    event.preventDefault()
    event.returnValue = ""
  }

  onMounted(() => {
    loadPage()
    window.addEventListener("beforeunload", warnBeforeRefresh)
  })

  onBeforeUnmount(() => {
    window.removeEventListener("beforeunload", warnBeforeRefresh)
  })
</script>

<template>
  <div class="page">
    <Header :show-menu-button="true" :show-profile-button="true" />

    <main class="page-main">
      <section class="hero-card hero-card-with-action">
        <div>
          <p class="hero-kicker">Admin</p>
          <h1>Grading Panel</h1>
          <p class="hero-text">
            Assign a grade to the submission. Note: if you want to cancel grading, please use the respective button to
            release the lock.
          </p>
        </div>

        <button
          v-if="submission && !errorMessage"
          class="secondary-button hero-action-button"
          type="button"
          @click="cancelGrading"
        >
          Cancel
        </button>
      </section>

      <p v-if="isLoading" class="empty-state dark-card">Loading grading panel...</p>

      <p v-else-if="errorMessage" class="empty-state dark-card">{{ errorMessage }}</p>

      <p v-else-if="!isIcMember" class="empty-state dark-card">You do not have permission to view this page.</p>

      <section v-else class="submission-list">
        <article v-if="submission" class="dark-card submission-card">
          <div v-if="getImageThumbnail(submission)" class="submission-media-wrapper" @click="openFullMedia">
            <img class="submission-image" :src="getImageThumbnail(submission)" :alt="`Submission ${submission.id}`" />

            <div class="media-overlay">Click to view full size</div>
          </div>

          <div v-else class="submission-image-placeholder">No file available</div>

          <div class="submission-body">
            <div class="submission-top-row">
              <div class="submission-info">
                <h2>Team: {{ submission.team_name }}</h2>
                <h4>{{ formatDate(submission.created_time) }}</h4>
                <p><b>Tournament:</b> {{ submission.tournament_name }}</p>
                <p><b>Challenge:</b> {{ submission.challenge_name }}</p>
                <p v-if="challenge"><b>Challenge Description:</b> {{ challenge.description }}</p>
              </div>

              <div class="submission-side-panel">
                <div class="submission-actions">
                  <div class="status-badge accepted">Max points: {{ challenge?.points ?? 0 }}</div>

                  <div class="status-badge pending">Ungraded</div>
                </div>

                <div class="grading-controls">
                  <div class="points-group">
                    <label for="grade">Points</label>

                    <input id="grade" v-model.number="grade" type="number" min="0" class="points-input" />
                  </div>

                  <div class="grading-buttons">
                    <button class="primary-button" type="button" @click="gradeSubmission(true)">Accept</button>

                    <button class="secondary-button" type="button" @click="gradeSubmission(false)">Reject</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </article>

        <p v-if="!submission" class="empty-state dark-card">Unable to load submission for grading.</p>
      </section>

      <div v-if="showFullMedia && submission" class="media-modal" @click="closeFullMedia">
        <button class="media-modal-close" type="button" @click="closeFullMedia">×</button>

        <video
          v-if="isVideo()"
          class="media-modal-content"
          :src="getSubmissionImage(submission)"
          controls
          autoplay
          @click.stop
        />

        <img
          v-else
          class="media-modal-content"
          :src="getSubmissionImage(submission)"
          :alt="`Submission ${submission.id}`"
          @click.stop
        />
      </div>
    </main>
  </div>
</template>

<style scoped>
  .submission-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .submission-card {
    padding: 0;
    overflow: hidden;
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

  .submission-media-wrapper {
    position: relative;
    cursor: pointer;
  }

  .submission-media-wrapper:hover .media-overlay {
    opacity: 1;
  }

  .media-overlay {
    position: absolute;
    right: 1rem;
    bottom: 1rem;
    border-radius: var(--radius-sm);
    padding: 0.45rem 0.75rem;
    background: rgba(0, 0, 0, 0.75);
    color: white;
    font-weight: 700;
    opacity: 0;
    transition: opacity 0.2s ease;
    pointer-events: none;
  }

  .media-modal {
    position: fixed;
    inset: 0;
    z-index: 9999;
    display: grid;
    place-items: center;
    padding: 2rem;
    background: rgba(0, 0, 0, 0.85);
  }

  .media-modal-content {
    max-width: 95vw;
    max-height: 90vh;
    object-fit: contain;
    border-radius: var(--radius-sm);
    background: black;
  }

  .media-modal-close {
    position: fixed;
    top: 1rem;
    right: 1.5rem;
    border: 0;
    background: transparent;
    color: white;
    font-size: 3rem;
    font-weight: 700;
    cursor: pointer;
  }

  .submission-image-placeholder {
    display: grid;
    place-items: center;
    background: rgba(255, 255, 255, 0.08);
    color: var(--text-muted-light);
    font-weight: 700;
  }

  .submission-body {
    padding: 1.35rem;
  }

  .submission-top-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 3rem;
  }

  .submission-info {
    flex: 1;
    min-width: 0;
  }

  .submission-info p {
    margin: 0.2rem 0;
    line-height: 1.35;
  }

  .submission-info h4 {
    margin: 0 0 0.75rem;
    font-family: "Gill Sans MT Condensed", sans-serif;
    font-size: clamp(1.1rem, 2vw, 1.6rem);
    font-weight: 600;
    letter-spacing: 0.03em;
    color: var(--text-muted-light);
  }

  .submission-side-panel {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 4rem;
    flex-shrink: 0;
  }

  .submission-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-shrink: 0;
  }

  .submission-header h2 {
    margin: 0 0 0.45rem;
    font-family: "Gill Sans MT Condensed", sans-serif;
    font-size: clamp(1.7rem, 3vw, 2.35rem);
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .submission-header p,
  .empty-state {
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

  .status-badge.pending {
    background: #c58b1f;
  }

  .status-badge.accepted {
    background: var(--primary);
  }

  .submission-main-content {
    display: flex;
    align-items: center;
    gap: 4rem;
    flex: 1;
  }

  .grading-controls {
    margin-top: 0;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 1rem;
  }

  .points-group {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .grading-controls label {
    color: var(--primary);
    font-family: "Gill Sans MT Condensed", sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  .points-input {
    width: 5rem;
    border: 0;
    border-radius: var(--radius-sm);
    padding: 0.65rem 0.85rem;
    background: rgba(255, 255, 255, 0.08);
    color: white;
    font-weight: 700;
  }

  .grading-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
  }

  .empty-state {
    text-align: center;
    padding: 2rem;
  }

  .hero-card-with-action {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 2rem;
  }

  .hero-action-button {
    flex-shrink: 0;
  }

  @media (max-width: 600px) {
    .submission-top-row {
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }

    .submission-side-panel {
      display: contents;
    }

    .submission-actions {
      order: 1;
      width: 100%;
      justify-content: center;
      flex-wrap: wrap;
    }

    .submission-info {
      order: 2;
      width: 100%;
    }

    .grading-controls {
      order: 3;
      width: 100%;
      align-items: stretch;
      margin-top: 0;
    }

    .grading-buttons {
      flex-direction: column;
      width: 100%;
    }

    .grading-buttons button {
      width: 100%;
    }

    .status-badge {
      align-self: center;
    }

    .points-group,
    .grading-buttons {
      justify-content: flex-start;
    }

    .points-group {
      justify-content: center;
    }

    .hero-card-with-action {
      flex-direction: column;
      align-items: flex-start;
    }
  }
</style>
