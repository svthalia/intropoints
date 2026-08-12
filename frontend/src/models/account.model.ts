export interface TournamentAccount {
  tournament: number
  type: string
  balance: number
}

export interface AccountTransaction {
  id: number
  amount: number
  accepted: boolean
  requested_at: string
  description: string
}
