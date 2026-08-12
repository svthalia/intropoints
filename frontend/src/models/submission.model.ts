interface SubmissionFile {
  id: string
  source: string
  thumbnail: string
  name: string
  type: string
}

// This model is used to represent the data received by the (regular) Submission Serializer
export interface Submission {
  id: number
  challenge: number // Note that this is the challenge id
  tournament: string //Note that this is the tournament id
  team: string // Note that this is the team id
  accepted: boolean | null
  created_by: string | null
  updated_by: string | null
  created_time: string
}

// This model is used to represent the data received by the Submission PreviewSerializer
// The biggest difference with the regular serializer is that this serializer retrieves the names
// instead of the id's.
export interface SubmissionPreview {
  id: number
  challenge_name: string
  challenge_slug: string
  challenge_submission_visibility: number
  tournament_name: string
  team_name: string
  created_by: string | null
  created_time: string
  file: SubmissionFile
  accepted: boolean | null
}
