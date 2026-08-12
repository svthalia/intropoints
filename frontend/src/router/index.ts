import { createRouter, createWebHistory } from "vue-router"

import Login from "../pages/Login.vue"
import Navigation from "../pages/Navigation.vue"
import Challenges from "../pages/Challenges.vue"
import Submissions from "../pages/Submissions.vue"
import Tournament from "../pages/Tournament.vue"
import ChallengeSubmission from "@/pages/ChallengeSubmission.vue"
import Marketplace from "@/pages/Marketplace.vue"
import Marketplaces from "@/pages/Marketplaces.vue"
import Inventory from "@/pages/Inventory.vue"
import GradingOverview from "@/pages/GradingOverview.vue"
import Grading from "@/pages/Grading.vue"

const routes = [
  { path: "/", name: "Login", component: Login },
  { path: "/navigation", name: "Navigation", component: Navigation },
  { path: "/challenges", name: "Challenges", component: Challenges },
  { path: "/submissions", name: "Submissions", component: Submissions },
  { path: "/tournament", name: "Tournament", component: Tournament },
  { path: "/tournament/:slug/challenges", name: "TournamentChallenges", component: Challenges, props: true },
  { path: "/challengesubmission/:slug", name: "ChallengeSubmission", component: ChallengeSubmission, props: true },
  { path: "/marketplace/:slug", name: "Marketplace", component: Marketplace, props: true },
  { path: "/marketplaces", name: "Marketplaces", component: Marketplaces },
  { path: "/inventory", name: "Inventory", component: Inventory },
  { path: "/gradingoverview", name: "GradingOverview", component: GradingOverview },
  { path: "/grading/:id", name: "Grading", component: Grading, props: true },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
