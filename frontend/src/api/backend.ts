import { EnvironmentUtilities } from "@/api/utilities"
import type Challenge from "@/models/challenge.model"
import type { Submission, SubmissionPreview } from "@/models/submission.model"
import type { StorageFile, StorageRequest } from "@/models/files.model"
import type User from "@/models/user.model"
import type { Tournament, Scoreboard } from "@/models/tournament.model"
import type Team from "@/models/teams.model"
import type { Store, StoreItem, Purchase, Inventory } from "@/models/store.model"
import type { AccountTransaction, TournamentAccount } from "@/models/account.model"

// -------------- //
// API interfaces //
// -------------- //

/*
 *
 *  Interface that represents a virtual login session.
 *  The login session essentially is a wrapper around the
 *  access token cookie that contains more essential data.
 *
 */
interface LoginSession {
  token: string
  tokenType: string
  scope: Array<string>
}

// ------------------------------- //
// API utilities for Backend class //
// ------------------------------- //

/*
 *
 * Handles interactions between the Frontend and
 * Backend through pre-established API-enpoints, resource-
 * points.
 *
 */
class BackendAPI {
  loginSession: null | LoginSession

  /*
   *
   *  Initializes the Backend API endpoint by:
   *
   *    - Trying to retrieve the current login session, if it fails
   *      then said session is set to null.
   */
  constructor() {
    this.loginSession = this._retrieveLoginSession("loginSession")
  }

  //  # Helpers

  /*
   *  Parses the client cookies and tries to retrieve
   *  the access token. If it fails, then it sets the access
   *  token to be null inside the API object.
   *
   *  @param cookieID : string -> the name of the access token cookie;
   *
   *  @return                  -> none;
   */
  _retrieveLoginSession(accessCookieID: string): LoginSession | null {
    // Retrieve all cookies
    const cookies = `; ${document.cookie}`

    // Retrieve the login session cookie and
    // check whether retrieval succeeded
    const rawCookie = cookies.split(`; ${accessCookieID}=`)
    if (rawCookie.length == 2) {
      // Extract the first cookie after the split
      let loginSessionCookie = rawCookie[1]?.split(";")[0]

      // Check whether cookie extraction succeeded
      if (!loginSessionCookie) {
        return null
      }

      // See whether the login session cookie is already in a
      // JSON format
      if (loginSessionCookie.startsWith('"') && loginSessionCookie.endsWith('"')) {
        loginSessionCookie = loginSessionCookie.slice(1, -1)
      }

      // Replace illegal characters
      loginSessionCookie = loginSessionCookie.replace(/\\054/g, ",").replace(/'/g, '"')

      // Return the parsed object
      return JSON.parse(loginSessionCookie!)
    }

    // If there is no cookie match, abort
    return null
  }

  // # Getters

  /*
   *  Tries to retrieves the access token from the
   *  the API object - if it fails, it returns null.
   *
   *  @param  -> none;
   *
   *  @return -> the access token or null;
   */
  getAccessToken(): string | null {
    if (this.loginSession) {
      return this.loginSession.token
    } else {
      return null
    }
  }

  getAuthorizationHeader(headersInit: Headers | undefined = undefined): Headers {
    let requestHeaders: Headers
    if (headersInit === undefined) {
      requestHeaders = new Headers()
    } else {
      requestHeaders = headersInit
    }
    const accessToken = this.getAccessToken()
    if (accessToken !== null) {
      requestHeaders.set("Authorization", `Bearer ${accessToken}`)
    }
    return requestHeaders
  }

  async call<T>(
    resource: string,
    method: string,
    data: BodyInit | null,
    headers: Headers | undefined = undefined,
  ): Promise<T> {
    let apiCall: Promise<Response>
    if (data !== null) {
      apiCall = fetch(`${EnvironmentUtilities.getBaseURI()}/api/${resource}`, {
        method,
        headers: this.getAuthorizationHeader(headers),
        body: data,
      })
    } else {
      apiCall = fetch(`${EnvironmentUtilities.getBaseURI()}/api/${resource}`, {
        method,
        headers: this.getAuthorizationHeader(headers),
      })
    }
    return apiCall
      .then((response) => {
        if (response.ok) {
          return response
        } else if (response.status === 403) {
          // When receiving a 403 response, the access token is not valid anymore so we should reset it.
          this.logout()
          throw response
        } else {
          throw response
        }
      })
      .then((result) => {
        return result.json() as Promise<T>
      })
  }

  async post<T>(resource: string, data: BodyInit | null, headers: Headers | undefined = undefined): Promise<T> {
    return this.call<T>(resource, "POST", data, headers)
  }

  async get<T>(resource: string, headers: Headers | undefined = undefined): Promise<T> {
    return this.call<T>(resource, "GET", null, headers)
  }

  async put<T>(resource: string, data: BodyInit | null, headers: Headers | undefined = undefined): Promise<T> {
    return this.call<T>(resource, "PUT", data, headers)
  }

  async getChallenge(slug: string): Promise<Challenge> {
    return this.get<Challenge>(`challenges/select/${slug}/`)
  }

  async requestFileStorage(data: FormData, headers: Headers | undefined = undefined): Promise<StorageRequest> {
    return this.post("files/request-storage/", data, headers)
  }

  async uploadFileToStorage(url: string, data: FormData, headers: Headers | undefined = undefined): Promise<Response> {
    return await fetch(url, {
      method: "POST",
      headers,
      body: data,
    })
  }

  async registerFileStorage(data: FormData, headers: Headers | undefined = undefined): Promise<StorageFile> {
    return this.post(`files/register-storage/`, data, headers)
  }

  async postFile(file: File, storage_folder: string = "files"): Promise<number> {
    const storageRequestData = new FormData()
    storageRequestData.append("name", file.name)
    storageRequestData.append("type", file.type)
    storageRequestData.append("storage_folder", storage_folder)

    const csrfToken = getCookie("csrftoken")
    const headers = new Headers()
    headers.append("X-CSRFToken", csrfToken!)
    const authHeaders = new Headers()
    authHeaders.append("X-CSRFToken", csrfToken!)
    this.getAuthorizationHeader(authHeaders)

    const storageRequest = await this.requestFileStorage(storageRequestData, authHeaders)
    const storageRequestID = storageRequest.id
    const presignedData = storageRequest.presigned_data

    const storageUploadData = new FormData()
    for (const key in presignedData.fields) {
      storageUploadData.append(key, presignedData.fields[key]!)
    }
    storageUploadData.append("file", file!)

    const storageResponse = await this.uploadFileToStorage(presignedData.url, storageUploadData, headers)
    if (!storageResponse.ok) {
      throw new Error("Couldn't upload to storage")
    }

    const registryData = new FormData()
    registryData.append("id", storageRequestID.toString())

    const registeredFile = await this.registerFileStorage(registryData, headers)

    return registeredFile.id
  }

  async postSubmission(data: FormData, headers: Headers | undefined = undefined): Promise<Submission> {
    return this.post<Submission>(`submissions/upload/`, data, headers)
  }

  async putGrade(data: FormData, headers: Headers | undefined = undefined): Promise<boolean> {
    return this.put<boolean>(`submissions/grade/update/`, data, headers)
  }

  async releaseLock(submissionId: number, headers: Headers | undefined = undefined): Promise<boolean> {
    return this.post<boolean>(`submissions/grade/release/${submissionId}/`, null, headers)
  }

  async getScoreboard(slug: string): Promise<Scoreboard[]> {
    return this.get<Scoreboard[]>(`teams/tournament-scoreboard-for/${slug}/`)
  }

  async getCurrentUser(): Promise<User> {
    return this.get<User>(`users/me/`)
  }

  async getCurrentTeam(): Promise<Team> {
    return this.get<Team>("teams/current/")
  }

  async getTeams(): Promise<Team[]> {
    return this.get<Team[]>("teams/all/")
  }

  async getTeam(teamID: number): Promise<Team> {
    return this.get<Team>(`teams/select/${teamID}/`)
  }

  async logout(): Promise<void> {
    const response = await fetch(EnvironmentUtilities.getLogoutURL(), {
      method: "GET",
      credentials: "include",
    })

    if (!response.ok) {
      throw new Error(`Logout failed: ${response.status} ${response.statusText}`)
    }

    this.loginSession = null
  }

  async getSubmissions(): Promise<SubmissionPreview[]> {
    return this.get<SubmissionPreview[]>(`submissions/all/`)
  }

  async getSubmissionsForChallenge(challenge_slug: string): Promise<SubmissionPreview[]> {
    return this.get<SubmissionPreview[]>(`submissions/for-challenge/${challenge_slug}/`)
  }

  async getSubmissionForGrading(submission_id: number): Promise<SubmissionPreview> {
    return this.get<SubmissionPreview>(`submissions/grade/get/${submission_id}/`)
  }

  async getAllSubmissionsForGrading(): Promise<SubmissionPreview[]> {
    return this.get<SubmissionPreview[]>(`submissions/grade/get/all/`)
  }

  async getChallenges(): Promise<Challenge[]> {
    return this.get<Challenge[]>("challenges/all/")
  }

  async getSubmissionsForTeam(teamName: string): Promise<SubmissionPreview[]> {
    return this.get<SubmissionPreview[]>(`submissions/for-team/${teamName}/`)
  }

  async getTournaments(): Promise<Tournament[]> {
    return this.get<Tournament[]>("tournaments/all/")
  }

  async getChallengesForTournament(slug: string): Promise<Challenge[]> {
    return this.get<Challenge[]>(`challenges/for-tournament/${slug}/`)
  }

  async getStores(): Promise<Store[]> {
    return this.get<Store[]>("stores/all/")
  }

  async getStoreForTournament(slug: string): Promise<Store[]> {
    return this.get<Store[]>(`stores/for-tournament/${slug}/`)
  }

  async getItems(): Promise<StoreItem[]> {
    return this.get<StoreItem[]>("stores/items/all/")
  }

  async getItemsForStore(storeId: number): Promise<StoreItem[]> {
    return this.get<StoreItem[]>(`stores/items/for-store/${storeId}/`)
  }

  async purchaseItem(data: FormData, headers: Headers | undefined = undefined): Promise<Purchase> {
    return this.post<Purchase>("stores/items/purchase/", data, headers)
  }

  async getInventoryForTeamAndTournament(teamId: number, tournamentSlug: string): Promise<Inventory> {
    return this.get<Inventory>(`stores/inventory/for-team-and-tournament/${teamId}/${tournamentSlug}/`)
  }

  async getTournamentAccountForTeamAndTournament(teamId: number, tournamentSlug: string): Promise<TournamentAccount[]> {
    return this.get<TournamentAccount[]>(`accounts/tournament/for-team-and-tournament/${teamId}/${tournamentSlug}/`)
  }

  async useUsableItem(usableItemId: number): Promise<{ success: boolean }> {
    return this.post<{ success: boolean }>(`stores/items/use/${usableItemId}/`, null)
  }

  async getTransactionsForTeamAndTournament(teamId: number, tournamentSlug: string): Promise<AccountTransaction[]> {
    return this.get<AccountTransaction[]>(`accounts/transactions/for-team-and-tournament/${teamId}/${tournamentSlug}/`)
  }
}

function getCookie(name: string) {
  let cookieValue = null
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i]!.trim()
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

// ------- //
// Exports //
// ------- //

export { BackendAPI }
