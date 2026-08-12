<script lang="ts" setup>
  import { BackendAPI } from "@/api/backend"
  import { useToast } from "vue-toastification"
  import Loader from "@/components/Loader.vue"
  import Header from "@/components/Header.vue"
  import { computed, onMounted, ref, toRef } from "vue"
  import type Challenge from "@/models/challenge.model"
  import type { SubmissionPreview } from "@/models/submission.model"
  import type Team from "@/models/teams.model"
  import SubmissionCard from "@/components/SubmissionCard.vue"

  const props = defineProps<{ slug: string }>()

  const APIInstance = new BackendAPI()
  const toast = useToast()

  const challengeLoading = ref<boolean | null>(true)
  const challenge = ref<Challenge | null>(null)
  const availUntil = ref<string | null>(null)

  const submissions = ref<SubmissionPreview[]>([])
  const isLoading = ref(true)
  const errorMessage = ref("")

  const doesTeamHaveAcceptedSubmission = ref<boolean | null>(false)
  const MAX_FILE_SIZE = 500 * 1024 * 1024 // 500 MB

  const id = toRef(props, "slug")

  const file = ref<File | null>(null)
  const fileField = ref<HTMLInputElement | null>(null)

  const userTeam = ref<Team | null>(null)

  const uploadingFile = ref<boolean>(false)

  const challengeIsActive = computed(() => {
    if (challenge.value === null) {
      return false
    }

    const today = new Date()

    if (challenge.value.available_from !== null) {
      const activeFromDate = new Date(challenge.value.available_from)
      if (activeFromDate > today) {
        return false
      }
    }

    if (challenge.value.active_until !== null) {
      const activeUntilDate = new Date(challenge.value.active_until)
      if (activeUntilDate < today) {
        return false
      }
    }

    return true
  })

  function hasUserTeamSubmission(submissions: SubmissionPreview[], userTeam: Team | null): boolean {
    if (!userTeam) {
      return false
    }

    return submissions.some((submission) => submission.team_name === userTeam.name)
  }

  onMounted(async () => {
    await loadUserTeam()

    try {
      const result = await APIInstance.getChallenge(id.value)

      challenge.value = result

      if (challenge.value.active_until) {
        availUntil.value = new Date(challenge.value.active_until).toLocaleString("en-GB")
      }

      challengeLoading.value = false
    } catch (err: unknown) {
      console.error("Challenge request failed:", err)
      challengeLoading.value = null
    }

    await loadSubmissions()

    if (challenge.value?.submission_visibility == 2) {
      doesTeamHaveAcceptedSubmission.value = hasUserTeamSubmission(submissions.value, userTeam.value)
    }
  })

  async function loadUserTeam() {
    try {
      userTeam.value = await APIInstance.getCurrentTeam()
      console.log(userTeam.value)
    } catch (err) {
      console.error("Failed to load user team:", err)
      userTeam.value = null
    }
  }

  function changeFile(event: Event): void {
    const target = event.target

    if (!(target instanceof HTMLInputElement)) {
      return
    }

    const selectedFile = target.files?.[0]

    if (!selectedFile) {
      file.value = null
      return
    }

    if (selectedFile.size > MAX_FILE_SIZE) {
      toast.error("File size must not exceed 500 MB.")

      target.value = ""
      file.value = null
      return
    }

    file.value = selectedFile

    if (file.value) {
      file.value = new File([file.value], file.value.name.trim().replace(/\s+/g, "_"), { type: file.value.type })
    }
  }

  async function createSubmission(file: File): Promise<boolean> {
    if (challenge.value !== null && userTeam.value !== null) {
      const file_id = await APIInstance.postFile(file, "submissions")

      const submissionFormData = new FormData()
      submissionFormData.append("challenge", String(challenge.value.id)) //Add a row called "challenge" which contains the challenge id
      submissionFormData.append("file", String(file_id)) //Add a row called "file" which contains the file
      submissionFormData.append("team", String(userTeam.value.id)) //Add a row called "team" which contains the id for the team
      return APIInstance.postSubmission(submissionFormData)
        .then(() => {
          return true
        })
        .catch(() => {
          return false
        })
    } else {
      return false
    }
  }

  function fileUpload() {
    if (challenge.value !== null && file.value !== null && userTeam.value !== null) {
      uploadingFile.value = true

      createSubmission(file.value)
        .then((result) => {
          if (result) {
            file.value = null

            if (fileField.value !== null) {
              fileField.value.value = ""
            }

            toast.success("Submission uploaded successfully!")
            void loadSubmissions()
          } else {
            toast.error("Failed to process submission, please try again.")
          }
        })
        .catch(() => {
          toast.error("An error occurred during submission processing, please try again.")
        })
        .finally(() => {
          uploadingFile.value = false
        })
    }
  }

  async function loadSubmissions() {
    isLoading.value = true
    errorMessage.value = ""

    try {
      submissions.value = await APIInstance.getSubmissionsForChallenge(id.value)
    } catch (err) {
      console.error("Failed to load submissions:", err)
      errorMessage.value = "Failed to load submissions."
    } finally {
      isLoading.value = false
    }
  }
</script>

<template>
  <div class="page">
    <Header :show-menu-button="true" :show-profile-button="true" />

    <main class="page-main">
      <section v-if="challenge !== null" class="hero-card">
        <div class="hero-top">
          <div>
            <p class="hero-kicker">Challenge</p>
            <h1>{{ challenge.name }}</h1>
            <p class="hero-text">{{ challenge.description }}</p>
          </div>

          <div class="points-badge">{{ challenge.points }} points</div>
        </div>

        <img
          v-if="challenge.thumbnail"
          class="challenge-image"
          :src="challenge.thumbnail.source"
          alt="Challenge image"
        />

        <form
          v-if="APIInstance.getAccessToken() !== null && userTeam !== null && challengeIsActive"
          class="upload-form"
        >
          <label for="file">Make a picture or a video</label>

          <div class="upload-row">
            <input
              id="file"
              ref="fileField"
              type="file"
              accept="image/*,video/*"
              aria-label="Upload"
              @change="changeFile($event)"
            />

            <button v-if="!uploadingFile" type="button" @click="fileUpload">Submit</button>

            <button v-else class="disabled" type="button" disabled>Submit <span class="loader"></span></button>
          </div>
        </form>

        <p v-if="availUntil !== null" class="active-until">Available until: {{ availUntil }}</p>
      </section>

      <section v-else-if="challengeLoading === true" class="dark-card loader-card">
        <Loader size="60px" background-color="#000000" />
      </section>

      <section v-else class="empty-state dark-card">Failed to load challenge, please try again.</section>

      <section class="section-header">
        <p class="section-kicker">Submissions</p>
        <h2>Recent uploads</h2>
      </section>

      <section class="submission-list">
        <p v-if="isLoading" class="empty-state dark-card">Loading submissions...</p>
        <p v-else-if="errorMessage" class="empty-state dark-card">{{ errorMessage }}</p>

        <template v-else>
          <div v-if="challenge?.submission_visibility === 2">
            <p v-if="!doesTeamHaveAcceptedSubmission" class="empty-state dark-card">
              Submissions are hidden for this challenge. They will be revealed once you have an accepted submission!
            </p>
            <p v-else-if="submissions.length === 0" class="empty-state dark-card">No submissions found.</p>
            <SubmissionCard v-else v-for="submission in submissions" :key="submission.id" :submission="submission" />
          </div>
          <div v-else>
            <p v-if="submissions.length === 0" class="empty-state dark-card">No submissions found.</p>
            <SubmissionCard v-else v-for="submission in submissions" :key="submission.id" :submission="submission" />
          </div>
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

  .points-badge {
    flex-shrink: 0;
    align-self: flex-start;
    border-radius: var(--radius-sm);
    padding: 0.85rem 1.1rem;
    background: var(--primary);
    color: white;
    font-weight: 700;
    white-space: nowrap;
  }

  .challenge-image {
    width: 100%;
    height: clamp(12rem, 30vw, 22rem);
    margin-top: 1.5rem;
    border-radius: var(--radius-sm);
    object-fit: cover;
    display: block;
  }

  .upload-form {
    margin-top: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .upload-form label {
    color: var(--primary);
    font-family: "Gill Sans MT Condensed", sans-serif;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .upload-row {
    display: flex;
    gap: 0.75rem;
  }

  .upload-row input {
    flex: 1;
    border: 0;
    border-radius: var(--radius-sm);
    padding: 0.85rem 1.1rem;
    background: rgba(255, 255, 255, 0.08);
    color: white;
  }

  .upload-row button {
    border: 0;
    border-radius: var(--radius-sm);
    padding: 0.85rem 1.1rem;
    background: var(--primary);
    color: white;
    font-weight: 700;
    cursor: pointer;
  }

  .upload-row button.disabled {
    cursor: not-allowed;
    opacity: 0.8;
  }

  .active-until {
    margin: 1rem 0 0;
    color: var(--text-muted-light);
    font-weight: 700;
    line-height: 1.5;
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

  .loader-card {
    display: flex;
    justify-content: center;
    padding: 2rem;
  }

  .loader {
    width: 20px;
    height: 20px;
    margin-left: 0.35rem;
    border: 2px solid white;
    border-bottom-color: transparent;
    border-radius: 50%;
    display: inline-block;
    vertical-align: middle;
    animation: rotation 1s linear infinite;
  }

  .section-header h2 {
    margin: 0;
    font-size: 1.9rem;
    color: var(--dark);
    font-family: "Gill Sans MT Condensed", sans-serif;
    letter-spacing: 0.03em;
  }

  @keyframes rotation {
    0% {
      transform: rotate(0deg);
    }

    100% {
      transform: rotate(360deg);
    }
  }

  @media (max-width: 600px) {
    .hero-top,
    .upload-row {
      flex-direction: column;
    }

    .points-badge {
      align-self: flex-start;
    }
  }
</style>
