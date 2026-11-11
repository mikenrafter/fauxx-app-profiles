# Contributing (draft)

This project is an early draft and is not accepting real app profiles yet.
Feedback on the schema and the safety rules is welcome as issues.

When profiles open up, a submission will need:

1. **A lab capture.** Run the app in an emulator or an isolated Android
   profile with a throwaway account. No personal accounts, contacts, photos,
   real location or real payment methods. Record network metadata only
   (hosts, request counts, sizes, timing), not payloads.
2. **Provenance.** App version, the APK signer's SHA-256 fingerprint (from
   `apksigner verify --print-certs`), capture date and method.
3. **A distilled profile** that passes `python3 tools/validate.py`. Use
   ranges wide enough to cover what you saw across several sessions, never one
   exact trace.
4. **A short capture note** in the pull request: device or emulator image,
   how many sessions, what you did in the app, and anything you left out.

Apps rated `high` invasiveness (broad permissions, heavy tracking SDKs) are
published with host kinds only, no domains.

Profiles describe connections and content fetches. A profile meant to send
fabricated ad clicks, installs, conversions, purchases or analytics events
will be rejected.
