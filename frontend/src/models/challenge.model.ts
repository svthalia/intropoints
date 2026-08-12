import type { Tournament } from "@/models/tournament.model"

interface ChallengeFile {
  id: string
  source: string
  thumbnail: string
  name: string
  type: string
}

export default interface Challenge {
  name: string
  slug: string
  enabled: boolean
  active_until: string
  tournament: Tournament | null //TODO null should be removed as soon as tournaments are finished
  points: number
  id: number
  completed: boolean | null
  thumbnail: ChallengeFile
  description: string
  available_from: string
  submission_visibility: number
}
