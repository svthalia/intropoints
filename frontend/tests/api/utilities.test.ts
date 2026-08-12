import { afterEach, describe, expect, test, vi } from "vitest"

import { EnvironmentUtilities } from "@/api/utilities"

describe("EnvironmentUtilities", () => {
  afterEach(() => {
    vi.unstubAllEnvs()
  })

  test("getBaseURI returns the window origin", () => {
    expect(EnvironmentUtilities.getBaseURI()).toBe(window.location.origin)
  })

  test("getLoginURL is built from the base URI", () => {
    const expected = `${window.location.origin}/login/start/?oauth_app=frontend`

    expect(EnvironmentUtilities.getLoginURL()).toBe(expected)
  })

  test("getLogoutURL is built from the base URI", () => {
    const expected = `${window.location.origin}/logout/`

    expect(EnvironmentUtilities.getLogoutURL()).toBe(expected)
  })

  test("getEnvVar returns a defined environment variable", () => {
    vi.stubEnv("SOME_TEST_VAR", "test-value")

    expect(EnvironmentUtilities.getEnvVar("SOME_TEST_VAR")).toBe("test-value")
  })

  test("getEnvVar throws when the variable is not defined", () => {
    expect(() => EnvironmentUtilities.getEnvVar("DEFINITELY_NOT_DEFINED")).toThrowError(
      "Environment variable DEFINITELY_NOT_DEFINED is not defined.",
    )
  })
})
