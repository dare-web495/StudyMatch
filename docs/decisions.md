# Design Decisions

## 1. on_delete behavior
**Decision:** Cascade only on rows that are meaningless without their parent
(availabilities, enrollments by user, memberships, attendances,
sessions by group, ratings by rated user). Restrict on course links and
peer_ratings.session. Set null on created_by (groups, sessions) and rater.
**Why:** Cascade everywhere would let one deletion silently wipe groups,
sessions, and ratings, and change other people's reliability scores.
**Alternatives considered:** Cascade on every relationship (rejected: too destructive).

## 2. Accounts are deactivated, not deleted
**Decision:** Users are deactivated via is_active. Hard deletion is not a normal path.
**Why:** Preserves ratings and group history. The on_delete rules are a safety net.

## 3. Groups are archived, not deleted
**Decision:** study_groups.is_archived hides a group. Groups with rated sessions
cannot be hard-deleted because peer_ratings.session restricts.
**Why:** Ratings feed reliability scores, so history must survive.

## 4. Owner source of truth
**Decision:** The active membership with role=owner controls the group.
created_by is history only. If the owner leaves, the longest-standing active
member is promoted. If no active members remain, the group is archived.
**Why:** created_by can be null (set null), so it cannot be the authority.
**Alternatives considered:** Transfer only on owner request (rejected: leaves groups ownerless).

## 5. Reliability score type and default
**Decision:** Stored as float, derived by code, never edited by hand.
New users start at a neutral 3.0 on the 1-5 scale.
**Why:** It is an approximate derived value, not money. Neutral start avoids
punishing or rewarding users with no history.

## 6. University and semester are plain text
**Decision:** Free text for now. Course uniqueness is (code, university).
**Why:** A separate University or Semester table adds complexity before it is needed.
**Revisit when:** Inconsistent spellings start causing duplicate courses.

## 7. Times are stored in UTC
**Decision:** All datetimes stored in UTC and converted to the user's timezone for display.
**Why:** Avoids daylight-saving and cross-timezone bugs.

## 8. Duplicate ratings after rater is nulled
**Decision:** Accepted limitation. Databases treat nulls as distinct, so the
unique rule cannot block duplicates once rater is null.
**Why:** Rare edge case that only arises after account removal.

## 9. Courses are created by admins only
**Decision:** Only staff create courses (Django admin or seed script). Students
can search and enroll but not create.
**Why:** Matching depends on students sharing the same course row. Open creation
would produce duplicates ("CS101", "cs 101") and break matching.
**Revisit when:** Students regularly can't find their course. Then add a
"suggest a course" flow that an admin approves.

## 10. Any active group member can create a session
**Decision:** Any active member can schedule a session. The creator or the group
owner can edit or cancel it.
**Why:** Study groups work better when anyone can propose a time. The owner
override means a session never becomes uncontrollable if its creator leaves.
**Alternatives considered:** Owner only (rejected: makes the owner a bottleneck).

## 11. Attendance is self-reported
**Decision:** Each member marks their own attendance, only after the session start time.
**Why:** Simplest to build and doesn't make the owner police everyone.
**Known weakness:** A member can claim attendance they didn't earn.
Mitigation: see "Consequences" below.

## D12. Rating window is 24 hours after the session ends
**Decision:** Ratings can be submitted from the session's end until 24 hours later.
**Why:** Ratings are most honest while the session is fresh, and it keeps
reliability scores from shifting long after the fact.
**Alternatives considered:** 7 days (rejected: ratings become less accurate and scores stay in flux).