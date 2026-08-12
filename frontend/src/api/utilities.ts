// --------------------- //
// Environment Utilities //
// --------------------- //

/*
 *
 *  Utility class that offers easy access to the
 *  frontend's environment
 *
 */
class EnvironmentUtilities {
  //  # Getters

  /*
   *  Retrieves an environment variable from the
   *  set '.env' file. If it fails, it throws an error.
   *
   *  @param name : string -> the name of the variable to retrieve;
   *
   *  @return              -> the variable's value;
   */
  static getEnvVar(name: string): string {
    // @ts-expect-error This variable is set in production.
    if (window?.__env__?.[name]) {
      // @ts-expect-error This variable is set in production.
      return window?.__env__?.[name]
    } else if (import.meta.env[name]) {
      return import.meta.env[name]
    } else {
      throw new Error(`Environment variable ${name} is not defined.`)
    }
  }

  /*
   *  Retrieve's the website's base URI.
   *
   *  @param  -> none;
   *
   *  @return -> the base URI as a string;
   */
  static getBaseURI() {
    return window.location.origin
  }

  /*
   *  Retrieves the login endpoint URL where the
   *  backend can pick up the process from.
   *
   *  @param  -> none;
   *
   *  @return -> the login endpoint as a string;
   */
  static getLoginURL() {
    return `${EnvironmentUtilities.getBaseURI()}/login/start/?oauth_app=frontend`
  }

  /*
   *  Retrieves the logout endpoint URL where the
   *  backend can pick up the process from.
   *
   *  @param  -> none;
   *
   *  @return -> the logout endpoint as a string;
   */
  static getLogoutURL() {
    return `${EnvironmentUtilities.getBaseURI()}/logout/`
  }
}

// ------- //
// Exports //
// ------- //

export { EnvironmentUtilities }
