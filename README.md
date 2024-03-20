# JFrog OIDC exchange GitHub Action

This action allows you to obtain JFrog's credentials from JFfrog platform in the form of variables -> `JFROG_SERVICE_USERNAME` & `JFROG_SERVICE_JWT`. The credentials can be used to publish platform-specific distribution packages into JFrog artifactory without needing to store them on GitHub.

## Usage

### OIDC exchange

To perform OIDC exchange with this action, [Identity Mappings](https://jfrog.com/help/r/jfrog-platform-administration-documentation/configure-an-oidc-integration) inside the [OIDC Integration](https://jfrog.com/help/r/jfrog-platform-administration-documentation/configure-an-oidc-integration) must already be configured on JFrog.

```yml
jobs:
  jfrog-publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write # REQUIRED: Mandatory for OIDC exchange!
      #contents: read # OPTIONAL: Required if checkout action is used!
      #packages: read # OPTIONAL: Required if the job is using a container image.
    steps:
      - name: Perform oidc-exchange to obtain JFrog's credentials.
        uses: jzizka91/action-jfrog-oidc-exchange/v0.1
      - name: Publish platform-specific distribution packages
        run: <publish-code>
```

> [!NOTE]
> This GitHub action only performs OIDC exchange to obtain JFrog credentials. -> Users are responsible for preparing the step(s) that perform publishing for platform-specific distribution packages.

> [!TIP]
> If your `publish-code` supports authorization with a bearer token, use the `JFROG_SERVICE_JWT` variable. If authorization with a bearer token is not supported, use the basic authentication method instead by using `JFROG_SERVICE_USERNAME` as the username and `JFROG_SERVICE_JWT` as the password.

> [!IMPORTANT]
> Since this GitHub Action is Docker-based, it can only
> be used from within GNU/Linux based jobs in GitHub Actions CI/CD
> workflows. This is by design and is unlikely to change any time soon.
>
> This should not stop one from publishing platform-specific
> distribution packages, though. It is strongly advised to separate jobs
> for building the OS-specific wheels from the publish job.
