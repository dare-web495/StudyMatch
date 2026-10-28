# StudyMatch API Endpoints

The contract between the Django backend and the React frontend, and the checklist for Phases 2 to 6.

## Conventions

- **Base path:** `/api/v1/`
- **Auth:** JWT access token in the `Authorization: Bearer <token>` header, plus a refresh token.
- **Resources vs actions:** reading and editing data uses standard methods on a noun (`GET /groups/`). Actions that change state (join, approve, cancel) are `POST .../action/`.
- **Pagination:** every list endpoint uses the same paginated response shape.
- **Errors:** one consistent shape, e.g. `{"detail": "...", "field_errors": {...}}`.
- **Status codes:**
  - `400` validation error
  - `401` not logged in
  - `403` logged in but not allowed
  - `404` does not exist, or you are not allowed to know it exists (use for invite-only groups and non-member session access)
  - `409` conflict (group full, already a member, already rated)

**Permission vocabulary:** *Public*, *Authenticated*, *Self*, *Member* (active membership), *Owner* (active owner membership), *Creator or Owner*.

---

## 1. Auth (Phase 2)

| Method | Path | Permission | Notes |
|---|---|---|---|
| POST | `/auth/register/` | Public | Creates the user. Rejects duplicate username or email. |
| POST | `/auth/login/` | Public | Returns access and refresh tokens. Same error for wrong username or wrong password. |
| POST | `/auth/token/refresh/` | Public | Exchanges a valid refresh token for a new access token. |
| POST | `/auth/logout/` | Authenticated | Blacklists the refresh token. |

## 2. Profile, courses, availability (Phase 2)

| Method | Path | Permission | Notes |
|---|---|---|---|
| GET | `/users/me/` | Authenticated | Full own profile. |
| PATCH | `/users/me/` | Self | `reliability_score` is read-only. |
| GET | `/users/{id}/` | Authenticated | Limited public fields only. |
| GET | `/courses/` | Authenticated | Search by name or code, filter by university. Paginated. |
| POST | `/courses/` | Per decision | Admin-only is the safest default. |
| GET, POST | `/users/me/enrollments/` | Self | Unique per user, course, semester. |
| DELETE | `/users/me/enrollments/{id}/` | Self | Own enrollments only. |
| GET, POST | `/users/me/availability/` | Self | Rejects `end_time` before `start_time` and overlapping slots on the same day. |
| PATCH, DELETE | `/users/me/availability/{id}/` | Self | Own slots only. |

## 3. Groups (Phase 3)

| Method | Path | Permission | Notes |
|---|---|---|---|
| GET | `/groups/` | Authenticated | Filters: `course`, `has_space`, `day`, `search`. Excludes archived and invite-only groups. Annotated with member count in one query. |
| POST | `/groups/` | Authenticated | Creates the group and the owner membership in one transaction. |
| GET | `/groups/{id}/` | Authenticated | Public groups visible to all. Invite-only: members only, otherwise 404. |
| PATCH | `/groups/{id}/` | Owner | `max_members` cannot go below the current active member count. |
| POST | `/groups/{id}/archive/` | Owner | Sets `is_archived`. Archived groups are read-only. |
| GET | `/groups/{id}/members/` | Authenticated | Active members with role and reliability score. |
| POST | `/groups/{id}/join/` | Authenticated | Creates a `pending` membership. 409 if already a member, pending, or archived. |
| POST | `/groups/{id}/leave/` | Member | If the leaver is the owner, apply decision D4. |
| GET | `/groups/{id}/requests/` | Owner | Pending membership requests. |
| POST | `/groups/{id}/requests/{membership_id}/approve/` | Owner | Re-checks capacity inside a transaction with a row lock. 409 if full. Sets `joined_at`. |
| POST | `/groups/{id}/requests/{membership_id}/reject/` | Owner | Only works on pending requests. |
| GET | `/users/me/memberships/` | Self | Feeds the Dashboard. Filter by status. |

## 4. Sessions and attendance (Phase 4)

| Method | Path | Permission | Notes |
|---|---|---|---|
| GET | `/groups/{id}/sessions/` | Member | Filter upcoming or past. |
| POST | `/groups/{id}/sessions/` | Owner (or any Member, per decision) | Start time must be in the future. Rejected on archived groups. |
| GET | `/sessions/{id}/` | Member of the session's group | Others get 404. |
| PATCH | `/sessions/{id}/` | Creator or Owner | Cannot edit a cancelled session. |
| POST | `/sessions/{id}/cancel/` | Creator or Owner | Sets `cancelled`. RSVPs stay as history. |
| PUT | `/sessions/{id}/rsvp/` | Member | Creates or updates your attendance as `going`. Idempotent. Blocked once cancelled. |
| POST | `/sessions/{id}/attendance/` | Per decision (self or Owner) | Only after the start time. Sets `attended` or `no_show`. |
| GET | `/users/me/sessions/upcoming/` | Self | Feeds the Dashboard. |

## 5. Ratings and reliability (Phase 4)

| Method | Path | Permission | Notes |
|---|---|---|---|
| GET | `/sessions/{id}/rateable/` | Member who attended | Other attendees you have not rated yet. Excludes yourself. |
| POST | `/sessions/{id}/ratings/` | Member who attended | Score 1 to 5. Only after the session ended and inside the rating window. Both people must have attended. No self-rating. No duplicates. |
| GET | `/users/{id}/rating-summary/` | Authenticated | Average and count only, no individual comments. |

Saving a rating triggers the reliability score recalculation (a signal).

## 6. Matches (Phase 5)

| Method | Path | Permission | Notes |
|---|---|---|---|
| GET | `/matches/` | Self | Ranked candidates, `limit` parameter (default 10). Clear empty response if the user has no courses or availability. |

## 7. Chat and dashboard (later phases)

| Method | Path | Permission | Notes |
|---|---|---|---|
| GET | `/groups/{id}/messages/` | Member | Paginated history, newest first. |
| POST | `/auth/ws-ticket/` | Authenticated | Short-lived single-use ticket for opening the WebSocket. |
| WS | `/ws/groups/{id}/?ticket=...` | Member | Rejects non-members at connect time. |

A combined `GET /dashboard/` endpoint is optional. The Dashboard can call the separate endpoints above, so skip it until the React side shows it is needed.

---

## Business rules to enforce and test

1. A user cannot join the same group twice, or join an archived group.
2. Approval fails when the group is full, and two simultaneous approvals cannot exceed `max_members`.
3. Only the owner can approve, reject, edit, or archive.
4. Non-members get 404 on sessions and chat, not 403.
5. A group always has exactly one active owner.
6. RSVP and attendance are blocked on cancelled sessions.
7. Ratings need both people to have attended, exclude self-rating, and respect the rating window.
8. `reliability_score` is never writable through any endpoint.

## Open decisions (record answers in `decisions.md`)

- [ ] Who creates courses?
- [ ] Who creates sessions: only the owner, or any member?
- [ ] Who marks attendance: each person themselves, or the owner?
- [ ] How long is the rating window after a session ends?