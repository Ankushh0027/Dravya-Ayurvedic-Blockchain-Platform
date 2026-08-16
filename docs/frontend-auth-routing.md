# Phase A: Frontend Authentication & Routing Foundation

## 1. Final Route Architecture

### Public Routes
- `/` - Home
- `/login` - Login page
- `/register` - Registration page
- `/verify/[code]` - Dynamic QR verification (shell created)
- `/unauthorized` - 403 Forbidden page
- `/not-found` (404) - Page not found

### Protected Role Routes (Dashboard Shells)
- **Producer**: `/producer/dashboard`
- **Verification Authority**: `/authority/dashboard`
- **Lab**: `/lab/dashboard`
- **Distributor**: `/distributor/dashboard`
- **Admin**: `/admin/dashboard`

*(Other nested workflow pages are out of scope for Phase A and will be built subsequently).*

## 2. Authentication Flow

The frontend authentication follows this lifecycle:

1. **Login Request**: User submits credentials at `/login`.
2. **API Call**: `LoginForm.tsx` sends a `POST /api/auth/login` request to the backend.
3. **Response Parsing**: The backend validates credentials and returns a `{ user, token }` payload if successful.
4. **Token Storage**: The JWT token is securely stored in:
   - `localStorage` (as `token`) for Axios interceptors (legacy support/API layer).
   - `document.cookie` (as `auth_token`) for Next.js Middleware route protection.
5. **State Hydration**: The Zustand store (`authStore.ts`) hydrates the `user` state globally.
6. **Role Redirect**: The user is evaluated by `getDashboardRoute(role)` and automatically redirected to their specific `/role/dashboard`.

## 3. Role Definitions

The system relies strictly on the following authoritative roles established by the backend RBAC model:

- `ADMIN`
- `PRODUCER`
- `VERIFICATION_AUTHORITY`
- `LAB`
- `DISTRIBUTOR`

*(Obsolete domains such as FARMER, MANUFACTURER, RETAILER, and PROCESSOR have been thoroughly pruned).*

## 4. Role Redirects

The utility function `getDashboardRoute(role)` located in `client/src/utils/routes.ts` controls all post-login navigations.

| Role | Target Route |
|------|--------------|
| `ADMIN` | `/admin/dashboard` |
| `PRODUCER` | `/producer/dashboard` |
| `VERIFICATION_AUTHORITY` | `/authority/dashboard` |
| `LAB` | `/lab/dashboard` |
| `DISTRIBUTOR` | `/distributor/dashboard` |

## 5. Route Protection (Middleware)

Frontend routes are protected strictly by `client/src/middleware.ts` running on the Next.js Edge runtime.

- **Unauthenticated Access**: Attempts to access any protected `/role/*` route without an `auth_token` cookie redirects to `/login`.
- **Role-Based Access Control (RBAC)**: The middleware performs a lightweight client-side verification by Base64 decoding the JWT payload (`atob`) to extract the user's role.
  - If a `PRODUCER` attempts to access `/admin/dashboard`, the middleware intercepts the request and instantly redirects to `/unauthorized`.
  - The `ADMIN` role retains cross-access capabilities for testing or auditing.

**Important Note**: This middleware is purely for UX navigation flow. The backend API verifies the cryptographic signature of the JWT and enforces true security boundaries.

## 6. Token Storage Approach

As identified in the audit, Phase A balances the existing Axios architecture with the requirements of Next.js App Router middleware:

- **Security Limitation Documented**: The JWT token is duplicated in `localStorage` and `document.cookie`.
  - The `cookie` is required because Next.js Edge Middleware cannot read `localStorage` during SSR or routing.
  - `localStorage` was preserved to prevent breaking the existing `axios.ts` interceptor mechanism until a full transition to cookie-based Next.js server actions or proxying is prioritized.

## 7. Logout Flow

The universal logout function (accessible from dashboards and the `/unauthorized` page):
1. Immediately resets the `auth_token` cookie with an expired date.
2. Removes `token` from `localStorage`.
3. Clears the Zustand `useAuthStore`.
4. Forces a router redirect to `/login`.

## 8. Error Handling

- Form validation is preserved securely using Zod schemas.
- On `POST /api/auth/login` failure (invalid credentials, inactive account), Axios catches the `401`/`403` and Sonner `toast.error()` displays the safe backend message without exposing stack traces.

## 9. Adding a New Protected Route

1. Define the route structure in `client/src/app/(role)`.
2. Open `client/src/middleware.ts`.
3. Add the route prefix and allowed roles to the `protectedRoutes` mapping object.

```typescript
const protectedRoutes = {
  // Example:
  '/new-feature': ['ADMIN', 'PRODUCER'],
}
```

## 10. Known Limitations (Phase A)

- **QR Dynamic Route**: `/verify/[code]` is purely a shell. It does not fetch backend data yet.
- **Workflow Pages**: Batch creation, verification approvals, and lab testing UIs do not exist yet.
- **Dashboard Data**: All role dashboards are currently minimal placeholders with a logout button and "Coming in next phase" messages.
