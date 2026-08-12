import { RouterLinkStub, mount } from "@vue/test-utils"
import { describe, expect, test } from "vitest"

import ChallengeCard from "@/components/ChallengeCard.vue"
import type Challenge from "@/models/challenge.model"

const HOUR = 60 * 60 * 1000

function makeChallenge(overrides: Partial<Challenge> = {}): Challenge {
  const now = Date.now()

  return {
    name: "Test Challenge",
    slug: "test-challenge",
    enabled: true,
    active_until: new Date(now + HOUR).toISOString(),
    tournament: null,
    points: 10,
    id: 1,
    completed: false,
    thumbnail: null as unknown as Challenge["thumbnail"],
    description: "A short description.",
    available_from: new Date(now - HOUR).toISOString(),
    submission_visibility: 1,
    ...overrides,
  }
}

function mountCard(challenge: Challenge) {
  return mount(ChallengeCard, {
    props: { challenge },
    global: {
      stubs: { RouterLink: RouterLinkStub },
    },
  })
}

describe("ChallengeCard", () => {
  test("shows an upcoming badge for a challenge that is not yet available", () => {
    const wrapper = mountCard(makeChallenge({ available_from: new Date(Date.now() + 2 * HOUR).toISOString() }))

    expect(wrapper.text()).toContain("Upcoming")
    expect(wrapper.text()).toContain("Available from")
    expect(wrapper.findComponent(RouterLinkStub).exists()).toBe(false)
  })

  test("shows an expired badge for a challenge whose window has passed", () => {
    const wrapper = mountCard(
      makeChallenge({
        available_from: new Date(Date.now() - 2 * HOUR).toISOString(),
        active_until: new Date(Date.now() - HOUR).toISOString(),
      }),
    )

    expect(wrapper.text()).toContain("Expired")
    expect(wrapper.text()).toContain("Not available anymore")
  })

  test("renders an active challenge as a link to its submission page", () => {
    const wrapper = mountCard(makeChallenge())

    const link = wrapper.findComponent(RouterLinkStub)
    expect(link.exists()).toBe(true)
    expect(link.props("to")).toEqual({
      name: "ChallengeSubmission",
      params: { slug: "test-challenge" },
    })
  })

  test("renders the name and points for an active challenge", () => {
    const wrapper = mountCard(makeChallenge({ name: "Capture the Flag", points: 42 }))

    expect(wrapper.text()).toContain("Capture the Flag")
    expect(wrapper.text()).toContain("42 points")
  })

  test("truncates long descriptions to 100 characters with an ellipsis", () => {
    const longDescription = "a".repeat(150)
    const wrapper = mountCard(makeChallenge({ description: longDescription }))

    expect(wrapper.text()).toContain("a".repeat(100) + "...")
    expect(wrapper.text()).not.toContain("a".repeat(101))
  })

  test("keeps short descriptions intact", () => {
    const wrapper = mountCard(makeChallenge({ description: "Just a short one" }))

    expect(wrapper.text()).toContain("Just a short one")
    expect(wrapper.text()).not.toContain("...")
  })
})
