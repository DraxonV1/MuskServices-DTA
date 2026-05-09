# Changelog

## Mobile Mode Added

We added a new **Mobile Mode** built for worker-based solving through the Android app.

What this means:
- workers can now solve tasks directly from the mobile app
- mobile workers use their own worker keys
- mobile mode is separated from the usual AFK/private/worker account-generation flows
- mobile mode is focused on solving only, not account/token exporting

## MuskSWA Released

The new Android solver app is now available as:

**MuskSWA**

Full name:
- **Musk Solver Worker App**

What the app is for:
- logging in with a mobile worker key
- viewing available solve tasks
- claiming tasks
- solving hCaptcha tasks manually from the phone
- submitting solve results back to the system

## Mobile Worker System

Mobile workers now have a dedicated worker flow.

Included:
- separate worker key system
- separate mobile stats
- separate mobile payouts
- separate mobile leaderboard support
- separate device tracking and management

This keeps mobile solving isolated from the rest of the platform.

## Task Claiming

Mobile workers can now:
- fetch available tasks
- claim tasks
- solve claimed tasks
- submit solved or failed results

Task flow is designed for multiple workers, so tasks can stay available until they expire instead of being rejected too early when a worker is not immediately available.

## Auto Claim and Manual Open

The app supports a more flexible worker flow:
- workers can auto-claim tasks
- workers can keep manual task opening if they prefer
- auto-open is optional and controlled from app behavior/settings

This makes the app usable for both:
- active/manual workers
- higher-volume workers

## Solve Tracking

Mobile mode now tracks worker performance, including:
- successful solves
- failed solves
- pending payout balance
- activity per worker/device

This makes it easier for both workers and admins to understand performance and earnings.

## Payout System

Mobile mode includes dedicated payout tracking.

Current structure:
- each successful solve adds worker earnings
- payout progress is tracked separately for mobile workers
- payouts begin once the configured threshold is reached

Workers can track their progress, and admins can review payout-related activity more clearly.

## Device Management

Mobile mode now includes device-aware control.

Admins can:
- track devices used by workers
- flag suspicious devices
- block a device without necessarily disabling the whole worker key

This gives better control over abuse handling while keeping legitimate workers active.

## Better Worker Separation

The new system separates:
- client-side task usage
- mobile worker solving
- admin tracking and management

This makes the solver service easier to manage at scale and easier to understand for workers.

## Frontend and Service Updates

The solver platform now includes:
- updated mobile worker support
- a dedicated Android worker app
- a cleaner worker-oriented solving flow
- user-facing platform updates around mobile solving

## Summary

Main additions in this update:
- new **Mobile Mode**
- new **MuskSWA** Android app
- worker-based mobile solving
- dedicated mobile keys
- mobile stats and payouts
- mobile device tracking
- task claiming and solving support for mobile workers

This update expands the platform from account-generation-focused tooling into a more complete worker-based solving service.
