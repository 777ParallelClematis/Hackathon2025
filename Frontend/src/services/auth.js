export function isLoggedIn() {
  // When JWT is added, check token validity here.
  return sessionStorage.getItem("token") !== null;
}
