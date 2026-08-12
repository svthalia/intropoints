<script setup lang="ts">
  import { useRouter } from "vue-router"
  import { ref, onMounted, onBeforeUnmount, computed } from "vue"
  import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome"
  import type User from "@/models/user.model"
  import type Team from "@/models/teams.model"
  import { BackendAPI } from "@/api/backend"

  const props = defineProps<{
    showMenuButton: boolean
    showProfileButton: boolean
  }>()

  const router = useRouter()

  const user = ref<User | null>(null)
  const team = ref<Team | null>(null)
  const showProfileDropdown = ref(false)
  const showTeamMembers = ref(false)
  const showSideMenu = ref(false)

  const profileMenuRef = ref<HTMLElement | null>(null)
  const menuRef = ref<HTMLElement | null>(null)

  const profileImageUrl = computed(() => user.value?.profile_photo ?? "")
  const userName = computed(() => user.value?.username ?? "Guest")
  const userTeam = computed(() => team.value?.name ?? "No team")
  const teamMembers = computed(() => team.value?.members ?? [])
  const userPoints = computed(() => team.value?.total_points ?? 0)
  const userInitial = computed(() => user.value?.initials ?? "G")

  const userPermissions = computed(() => {
    const permissions = user.value?.permissions ?? []

    if (permissions.includes("users.ic_member")) return "IC member"
    if (permissions.includes("users.mentor")) return "Mentor"
    if (permissions.includes("users.participant")) return "Participant"

    return ""
  })

  async function loadUser() {
    if (!props.showProfileButton) return

    try {
      const apiService = new BackendAPI()

      user.value = await apiService.getCurrentUser()

      try {
        const teams = await apiService.getTeams()
        team.value = teams.find((team) => team.members.includes(user.value?.username ?? "")) ?? null
      } catch (err) {
        console.error("Failed to load team:", err)
        team.value = null
      }
    } catch (err) {
      console.error("Failed to load user:", err)
      user.value = null
      team.value = null
    }
  }

  async function logout() {
    try {
      const apiService = new BackendAPI()
      await apiService.logout()
    } catch (err) {
      console.error("Logout failed:", err)
    } finally {
      user.value = null
      team.value = null
      window.location.href = "/"
    }
  }

  function toggleProfileDropdown() {
    showProfileDropdown.value = !showProfileDropdown.value
  }

  function closeProfileDropdown() {
    showProfileDropdown.value = false
    showTeamMembers.value = false
  }

  function toggleTeamMembers() {
    showTeamMembers.value = !showTeamMembers.value
  }

  function toggleSideMenu() {
    showSideMenu.value = !showSideMenu.value
  }

  function closeSideMenu() {
    showSideMenu.value = false
  }

  function navigateTo(routeName: string) {
    router.push({ name: routeName })
    closeSideMenu()
  }

  function navigateExternal(url: string) {
    window.location.href = url
  }

  function handleClickOutside(event: MouseEvent) {
    const target = event.target as Node

    if (profileMenuRef.value && !profileMenuRef.value.contains(target)) {
      closeProfileDropdown()
    }

    if (showSideMenu.value && menuRef.value && !menuRef.value.contains(target)) {
      closeSideMenu()
    }
  }

  onMounted(async () => {
    await loadUser()
    document.addEventListener("click", handleClickOutside)
  })

  onBeforeUnmount(() => {
    document.removeEventListener("click", handleClickOutside)
  })
</script>

<template>
  <div class="header sticky-top">
    <div class="feed-container header-inner mx-auto">
      <div class="header-left">
        <font-awesome-icon
          v-if="props.showMenuButton"
          :icon="['fas', 'bars']"
          @click.stop="toggleSideMenu"
          class="clickable"
        />
      </div>

      <div class="header-center">
        <router-link :to="{ name: 'Navigation' }">
          <h1>SCAVENGER HUNT</h1>
        </router-link>
      </div>

      <div class="header-right profile-header-zone">
        <div
          v-if="props.showProfileButton"
          ref="profileMenuRef"
          class="profile-menu-anchor"
          :class="{ open: showProfileDropdown }"
        >
          <div class="profile-shell">
            <div class="profile-expand-row">
              <transition name="profile-name-fade">
                <div v-if="showProfileDropdown" class="profile-name-panel">
                  <span class="profile-trigger-name">{{ userName }}</span>
                </div>
              </transition>

              <button
                type="button"
                class="profile-avatar-button"
                @click.stop="toggleProfileDropdown"
                :aria-expanded="showProfileDropdown"
                aria-label="Open profile menu"
              >
                <div class="profile-avatar">
                  <img
                    v-if="profileImageUrl"
                    :src="profileImageUrl"
                    alt="Profile picture"
                    class="profile-avatar-image"
                  />
                  <span v-else>{{ userInitial }}</span>
                </div>
              </button>
            </div>

            <div v-if="showProfileDropdown" class="profile-dropdown-body">
              <div class="profile-info">
                <p><strong>Role:</strong> {{ userPermissions }}</p>

                <div class="team-dropdown">
                  <button type="button" class="team-dropdown-button" @click.stop="toggleTeamMembers">
                    <span><strong>Team:</strong> {{ userTeam }}</span>
                    <font-awesome-icon
                      :icon="['fas', showTeamMembers ? 'chevron-up' : 'chevron-down']"
                      class="team-dropdown-icon"
                    />
                  </button>

                  <ul v-if="showTeamMembers" class="team-members-list">
                    <li v-if="teamMembers.length === 0">No members found</li>
                    <li v-for="member in teamMembers" :key="member">
                      {{ member }}
                    </li>
                  </ul>
                </div>

                <p>
                  <strong>Points: </strong>
                  <span>{{ userPoints }}</span>
                  <font-awesome-icon :icon="['fas', 'star']" />
                </p>
              </div>

              <div class="profile-actions">
                <font-awesome-icon
                  v-if="showProfileDropdown"
                  :icon="['fas', 'sign-out']"
                  @click="logout"
                  class="clickable"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showSideMenu" class="side-menu-overlay" @click="closeSideMenu"></div>

    <div ref="menuRef" :class="['side-menu', { open: showSideMenu }]">
      <div class="side-menu-header">
        <strong>Navigation</strong>
        <font-awesome-icon :icon="['fas', 'xmark']" @click="closeSideMenu" class="clickable" />
      </div>

      <nav class="side-menu-links">
        <button class="menu-link" @click="navigateTo('Navigation')">
          <font-awesome-icon :icon="['fas', 'house']" class="menu-icon" />
          <span>Home</span>
        </button>

        <button class="menu-link" @click="navigateTo('Submissions')">
          <font-awesome-icon :icon="['fas', 'paper-plane']" class="menu-icon" />
          <span>Submissions</span>
        </button>

        <button class="menu-link" @click="navigateTo('Tournament')">
          <font-awesome-icon :icon="['fas', 'medal']" class="menu-icon" />
          <span>Tournament</span>
        </button>

        <button class="menu-link" @click="navigateTo('Marketplaces')">
          <font-awesome-icon :icon="['fas', 'shopping-cart']" class="menu-icon" />
          <span>Marketplaces</span>
        </button>

        <button class="menu-link" @click="navigateTo('Inventory')">
          <font-awesome-icon :icon="['fas', 'box-open']" class="menu-icon" />
          <span>Inventory</span>
        </button>

        <div v-if="userPermissions === 'IC member' || userPermissions === 'Mentor'">
          <button class="menu-link" @click="navigateExternal('https://scavengerhunt.thalia.nu/admin')">
            <font-awesome-icon :icon="['fas', 'cog']" class="menu-icon" />
            <span>Admin</span>
          </button>
        </div>

        <div v-if="userPermissions === 'IC member'">
          <button class="menu-link" @click="navigateTo('GradingOverview')">
            <font-awesome-icon :icon="['fas', 'clipboard-check']" class="menu-icon" />
            <span>Grading</span>
          </button>
        </div>
      </nav>
    </div>
  </div>
</template>

<style>
  .header-center a {
    text-decoration: none;
    color: inherit;
  }
</style>
