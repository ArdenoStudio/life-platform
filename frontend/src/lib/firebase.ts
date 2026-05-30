import type { FirebaseApp } from 'firebase/app'
import type { Auth, GoogleAuthProvider } from 'firebase/auth'

type FirebaseRuntime = {
  app: FirebaseApp
  auth: Auth
  provider: GoogleAuthProvider
}

let runtime: FirebaseRuntime | null = null
let runtimePromise: Promise<FirebaseRuntime | null> | null = null

export function isTestAuthConfigured() {
  return Boolean(testAuthToken())
}

export function isFirebaseConfigured() {
  return Boolean(
    import.meta.env.VITE_FIREBASE_API_KEY &&
      import.meta.env.VITE_FIREBASE_AUTH_DOMAIN &&
      import.meta.env.VITE_FIREBASE_PROJECT_ID &&
      import.meta.env.VITE_FIREBASE_APP_ID,
  )
}

export async function getFirebaseRuntime(): Promise<FirebaseRuntime | null> {
  if (!isFirebaseConfigured()) return null
  if (runtime) return runtime
  if (runtimePromise) return runtimePromise
  runtimePromise = Promise.all([import('firebase/app'), import('firebase/auth')]).then(([appModule, authModule]) => {
    const app = appModule.initializeApp({
      apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
      appId: import.meta.env.VITE_FIREBASE_APP_ID,
      authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
      messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
      projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    })
    runtime = {
      app,
      auth: authModule.getAuth(app),
      provider: new authModule.GoogleAuthProvider(),
    }
    return runtime
  })
  return runtimePromise
}

export function testAuthToken() {
  const globalToken = (globalThis as { __ARIVA_TEST_AUTH_TOKEN__?: string; __LIFELK_TEST_AUTH_TOKEN__?: string }).__ARIVA_TEST_AUTH_TOKEN__
    || (globalThis as { __LIFELK_TEST_AUTH_TOKEN__?: string }).__LIFELK_TEST_AUTH_TOKEN__
  return import.meta.env.VITE_LIFE_TEST_AUTH_TOKEN || globalToken || null
}
