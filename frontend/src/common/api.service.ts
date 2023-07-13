import type Announcement from "@/models/announcement.model";
import type User from "@/models/user.model";
import type Submission from "@/models/submission.model";
import {useUserStore} from "@/stores/user.module";
import type ChallengeUser from "@/models/challengeUser.model";
import type Challenge from "@/models/challenge.model";
import type _Challenge from "@/models/api/_challenge.model";
import type Team from "@/models/team.model";

class _ApiService {
  authorizationEndpoint: string;
  baseUri: string;
  clientId: string;
  redirectUri: string;
  authStore: ReturnType<typeof useUserStore>;

  constructor(
    clientId: string,
    baseUri: string,
    authorizationEndpoint: string,
    redirectUri: string,
    authStore: ReturnType<typeof useUserStore>,
  ) {
    this.clientId = clientId;
    this.baseUri = baseUri;
    this.authorizationEndpoint = authorizationEndpoint;
    this.redirectUri = redirectUri;
    this.authStore = authStore;
  }

  getAuthorizationUri(): string {
    return `${this.baseUri}${this.authorizationEndpoint}`;
  }

  getAuthorizeRedirectURL(
    state: null | string,
    codeChallenge: null | string,
    isSHA256Challenge = false
  ): string {
    const authURL = new URL(this.getAuthorizationUri());
    authURL.searchParams.append("client_id", this.clientId);
    authURL.searchParams.append("redirect_uri", this.redirectUri);
    authURL.searchParams.append("response_type", "token");
    if (state !== null) {
      authURL.searchParams.append("state", state);
    }
    if (codeChallenge !== null) {
      authURL.searchParams.append("code_challenge", codeChallenge);
      if (isSHA256Challenge) {
        authURL.searchParams.append("code_challenge_method", "S256");
      } else {
        authURL.searchParams.append("code_challenge_method", "plain");
      }
    }
    return authURL.href;
  }

  getAuthorizationHeader(headersInit: Headers | null = null): Headers {
    let requestHeaders: Headers;
    if (headersInit === null) {
      requestHeaders = new Headers();
    } else {
      requestHeaders = headersInit;
    }
    const accessToken = this.authStore.accessToken;
    if (accessToken !== null) {
      requestHeaders.set("Authorization", `Bearer ${accessToken}`);
    }
    return requestHeaders;
  }

  async getAnnouncements(): Promise<Announcement[]> {
    return this.get<Announcement[]>("/announcements/");
  }

  async getUsersMe(): Promise<User> {
    return this.get<User>("/users/me/");
  }

  _addParametersToResource(resource: string, parameters: URLSearchParams | null): string {
    if (parameters !== null) {
      return `${resource}?${parameters.toString()}`;
    } else {
      return resource;
    }
  }

  async getChallengesSubmissions(parameters: URLSearchParams | null = null): Promise<Submission[]> {
    return this.get<Submission[]>(this._addParametersToResource("/challenges/submissions/", parameters));
  }

  async postChallengesSubmissions(data: FormData, headers: Headers | null = null): Promise<Submission> {
    return this.post<Submission>("/challenges/submissions/", data, headers);
  }

  async getChallengesTeams(): Promise<Team[]> {
    return this.get<Team[]>("/challenges/teams/");
  }

  async getChallengesUsersMe(): Promise<ChallengeUser> {
    return this.get<ChallengeUser>("/challenges/users/me/");
  }

  async getChallenges(): Promise<Challenge[]> {
    return this.get<Challenge[]>("/challenges/");
  }

  async getChallenge(id: number): Promise<Challenge> {
    return this.get<Challenge>(`/challenges/${id}/`);
  }

  async fetch<T>(resource: string, method: string, data: BodyInit|null, headers: Headers|null = null): Promise<T> {
    let apiCall = null;
    if (data !== null) {
      apiCall = fetch(`${this.baseUri}/api/v1${resource}`, {
        method: method,
        headers: this.getAuthorizationHeader(headers),
        body: data,
      });
    } else {
       apiCall = fetch(`${this.baseUri}/api/v1${resource}`, {
        method: method,
        headers: this.getAuthorizationHeader(headers)
      });
    }
    return apiCall.then(response => {
      if (response.ok) {
        return response;
      } else {
        throw response;
      }
    }).then(result => {
      return result.json() as Promise<T>;
    });
  }

  async get<T>(resource: string, headers: Headers|null = null): Promise<T> {
    return this.fetch<T>(resource, 'GET', null, headers);
  }

  async post<T>(resource: string, data: BodyInit|null, headers: Headers|null = null): Promise<T> {
    return this.fetch<T>(resource, 'POST', data, headers);
  }

  async put<T>(resource: string, data: BodyInit|null, headers: Headers|null = null): Promise<T> {
    return this.fetch<T>(resource, 'PUT', data, headers);
  }

  async patch<T>(resource: string, data: BodyInit|null, headers: Headers|null = null): Promise<T> {
    return this.fetch<T>(resource, 'PATCH', data, headers);
  }

  async delete<T>(resource: string, headers: Headers|null = null): Promise<T> {
    return this.fetch<T>(resource, 'DELETE', null, headers);
  }
}

const useApiService = (authStore: ReturnType<typeof useUserStore>) => {
  return new _ApiService(
      import.meta.env.VITE_API_OAUTH_CLIENT_ID,
      import.meta.env.VITE_API_BASE_URI,
      import.meta.env.VITE_API_AUTHORIZATION_ENDPOINT,
      import.meta.env.VITE_API_OAUTH_REDIRECT_URI,
      authStore
  )
}

export default useApiService;
