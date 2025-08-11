// Placeholder OIDC config; wire up oidc-client-ts as needed
export const oidcConfig = {
  authority: 'http://localhost:8081/realms/master',
  client_id: 'frontend',
  redirect_uri: window.location.origin,
  scope: 'openid profile email'
}