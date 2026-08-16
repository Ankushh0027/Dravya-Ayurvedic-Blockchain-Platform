# DRAVYA — CLIENT-SIDE AUDIT REPORT

## 1. Current Frontend Architecture
- **Framework**: Next.js 16.3 (Turbopack) utilizing the App Router (`app/` directory).
- **State Management**: Zustand (`store/authStore.ts`, `store/batchStore.ts`).
- **API Client**: Axios (`services/api/axios.ts`).
- **Structure**: Feature-sliced design methodology (`features/auth`, `features/producer`, `features/batch`, etc.).
- **Styling & UI**: Tailwind CSS v4, Shadcn UI, Radix UI.
- **i18n**: Configured with `react-i18next`.
- **Responsive**: Tailwind classes and custom hooks (`hooks/use-mobile.ts`) are set up for mobile-first responsive web design.

## 2. Existing Pages
| Page | Route | Exists | Complete | Role | API Connected | Notes |
|------|-------|--------|----------|------|---------------|-------|
| Home | `/` | YES | COMPLETE | PUBLIC | N/A | Landing page with video/demo sections. |
| Verify | `/verify` | YES | PARTIAL | PUBLIC | NO | Misses dynamic routing `/:code`. Currently a static page `verify/page.tsx`. |
| Register | `/(auth)/register` | YES | PARTIAL | PUBLIC | NO | Form exists in features, UI is rendered. |
| Producer Batches | `/dashboard/producer/batches` | YES | PARTIAL | PRODUCER | NO | Skeleton/Layout only. |
| Producer Register | `/dashboard/producer/register` | YES | PARTIAL | PRODUCER | NO | |
| Lab Dashboard | `/dashboard/lab` | YES | PLACEHOLDER | LAB | NO | Empty placeholder component. |
| VA Dashboard | `/dashboard/verification-authority` | YES | PLACEHOLDER | VA | NO | Empty placeholder component. |

## 3. Missing Pages
The following strictly required pages are entirely **MISSING**:
- `/login` (Component `LoginForm.tsx` exists, but there is no dedicated `app/(auth)/login` route).
- `/producer/dashboard` (Using nested `/dashboard/producer/` instead of the flat requested architecture).
- `/producer/profile`
- `/producer/verification`
- `/producer/herbs`
- `/producer/batches/create`
- `/producer/batches/:id`
- `/authority/dashboard`
- `/authority/verifications`
- `/authority/verifications/:id`
- `/authority/inspections`
- `/authority/inspections/:id`
- `/lab/dashboard`
- `/lab/tests`
- `/lab/tests/:id`
- `/lab/tests/:id/results`
- `/lab/tests/:id/report`
- `/distributor/dashboard`
- `/distributor/batches`
- `/distributor/batches/:id`
- `/admin/*` (All admin routes: dashboard, users, verifications, inspections, lab, distributors, herbs, qr, blockchain, audit).
- `/profile`, `/notifications`, `/settings`, `/unauthorized`, `/404`.

## 4. Partial Pages
- **`/verify`**: Exists as a static folder, but it lacks the dynamic route parameter segment (`[code]`) required to fetch specific QR verification data.
- **Producer Batches**: The page exists but does not fetch or submit data to the backend.

## 5. Outdated Pages / Artifacts
- The `features/` directory contains outdated domains:
  - `features/manufacturers`
  - `features/retailers`
- The routing structure `app/dashboard/<role>` is used instead of the requested flat routes (e.g., `app/producer/dashboard`, `app/admin/dashboard`).

## 6. Required Pages
*(See Section 3 for the list of missing required pages that need to be built).*

## 7. Backend API Mapping
Based on backend route inspection, the frontend needs to connect to the following (currently unconnected):
- **Auth**: `POST /api/auth/login`, `POST /api/auth/register`
- **Producer**: 
  - `GET /api/producers/me`, `PATCH /api/producers/me`
  - `GET /api/producers/me/dashboard`, `GET /api/producers/me/verification`
  - `POST /api/producers/me/verification/request`
- **Batches**:
  - `POST /api/batches` (Create)
  - `GET /api/batches` (List)
  - `GET /api/batches/:id`
  - `POST /api/batches/:id/submit`
  - `POST /api/batches/:id/inspection/request`
- **Authority**:
  - `GET /api/authority/verifications`, `PATCH /api/authority/verifications/:id/approve`
  - `GET /api/authority/inspections`
- **Lab & Distributor**: Defined in backend routes, awaiting UI implementation.
- **Public**: `GET /api/public/verify/:code`

## 8. RBAC Mapping
| Page | ADMIN | PRODUCER | VA | LAB | DISTRIBUTOR | PUBLIC |
|------|-------|----------|----|-----|-------------|--------|
| `/` | Y | Y | Y | Y | Y | Y |
| `/login` | Y | Y | Y | Y | Y | Y |
| `/dashboard/producer/*`| N | Y | N | N | N | N |
| `/dashboard/lab/*` | N | N | N | Y | N | N |

**Findings**:
- `authStore.ts` currently stores `{ id, name, email, role }`, but there is **no middleware** or strict frontend Route Guard enforcing these RBAC rules to prevent unauthorized navigation.
- Role redirects after login are not fully wired up.

## 9. Dashboard Audit
- **Producer Dashboard**: Currently a placeholder. Missing API connection to `/api/producers/me/dashboard`.
- **VA Dashboard**: Empty placeholder (`page.tsx`).
- **Lab Dashboard**: Empty placeholder (`page.tsx`).
- **Admin & Distributor Dashboards**: Do not exist.
- **Data Status**: All current dashboards are either completely empty or using mock/static placeholders. No real data integration exists.

## 10. Workflow Gaps
The SIH end-to-end workflow **breaks immediately** after the home page because:
- The `/login` page route is missing (only the component exists on the home page).
- A Producer cannot create a batch (missing UI).
- A Producer cannot request an inspection (missing UI).
- Verification Authority has no UI to approve verification or inspect lots.

## 11. Blockchain UI Gaps
- **Missing entirely.** No components exist to display Blockchain anchor status, verification integrity, or Transaction IDs safely to consumers or admins.

## 12. QR UI Gaps
- **Missing entirely.** 
- No QR generation UI for producers/admins.
- Public `/verify` does not support dynamic `:code` lookup.

## 13. Responsive/Mobile Readiness
- **Ready but unpopulated.** The frontend is using Tailwind and responsive UI components (Shadcn), plus `hooks/use-mobile.ts`. It is well-positioned for mobile responsiveness once the missing pages are built.

## 14. Design System Issues
- **Consistent Foundation**: Tailwind CSS, Shadcn, and Lucide icons provide a very solid, cohesive design system.
- **Inconsistencies**: Forms and layout compositions need to be standardized for the dashboards (currently missing).

## 15. Integration Blockers
- **Blocker 1**: The actual page routes (e.g., `/producer/dashboard`, `/authority/dashboard`) do not exist.
- **Blocker 2**: The frontend lacks an RBAC-enforcing middleware to protect these routes.
- **Blocker 3**: The dynamic QR verification route (`/verify/[code]`) must be created before public verification integration can happen.

## 16. Recommended Implementation Order (SIH Priority Flow)
1. **P0**: Fix Routing Structure (Move `/dashboard/producer` to `/producer/dashboard`, create missing dashboard shells).
2. **P0**: Setup Next.js Middleware/Route Guards for Frontend RBAC based on `authStore.ts`.
3. **P0**: Create the `/login` route utilizing `LoginForm.tsx`, and wire the role-based redirects upon login.
4. **P0**: Build Producer Pages (`/producer/batches/create`, `/producer/batches/:id`).
5. **P0**: Build VA Pages (`/authority/verifications`, `/authority/inspections`).
6. **P0**: Build Lab Pages (`/lab/tests`, test parameter entry).
7. **P0**: Build Distributor Pages (Receive/Dispatch).
8. **P0**: Convert `/verify/page.tsx` to `/verify/[code]/page.tsx` and integrate `GET /api/public/verify/:code`.
9. **P1**: Build Admin monitoring & blockchain UI.
