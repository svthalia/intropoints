export interface Tournament {
  id: number
  name: string
  slug: string
  active_from: string | null
  active_until: string | null
}

export interface Scoreboard {
  id: number
  name: string
  points: number
}
