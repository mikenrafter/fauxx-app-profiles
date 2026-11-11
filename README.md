# fauxx-app-profiles

> **Early draft. Not ready for use.** The schema, the review process and the
> safety rules below are proposals. Nothing here has been tested against real
> apps yet, the format will change without notice, and no app consumes these
> files today. Please don't build on it yet; issues and discussion are welcome.

A shared, reviewed catalog of **app behavior profiles**: data that describes
how a real Android app tends to use the network, so that privacy tools such as
[Fauxx](https://github.com/digital-grease/fauxx) can generate decoy activity
that looks like that app, without every user having to run the app themselves.

## Why a shared catalog

Learning what an app's traffic looks like means running it, watching it and
summarizing the result. If every user did that on their own phone:

- it would cost each of them time, data and battery;
- they would run code they have not vetted, and an invasive app could quietly
  undo the privacy the decoys are meant to protect;
- thousands of near-identical captures would themselves become a pattern.

Doing it once, in a lab, and sharing the summary avoids all three.

## How it is meant to work

1. **Capture in a lab, never on a personal device.** A contributor runs the
   real app in an emulator or an isolated profile with a throwaway account, no
   personal data, no real location and no real contacts, and records network
   metadata.
2. **Distill to data.** The capture becomes a declarative profile: which
   kinds of hosts the app contacts, in what order, typical request sizes and
   timing, session lengths and how often a session happens. No code, no
   recorded payloads, no identifiers.
3. **Review and sign.** A profile carries its provenance (app version, APK
   signer fingerprint, capture date, capture method) and goes through review
   before it is merged.
4. **Consume as a pinned version.** A tool loads a specific release, checks it
   against the schema, and samples from the ranges in each profile, mixing in
   its own local timing. Profiles describe ranges, never one exact trace, so
   devices using the same profile do not all look alike.

## Safety rules (draft)

- **Data only.** Profiles cannot contain code, scripts, URLs with query
  strings, headers, cookies, tokens or request bodies. A consumer must reject
  any field the schema does not define.
- **Shape, not events.** Profiles describe connections and content fetches.
  They must not drive fabricated ad clicks, installs, conversions, purchases or
  analytics events into ad or attribution systems. That crosses from privacy
  protection into ad fraud.
- **No personal data, ever.** Captures use throwaway accounts. A profile that
  contains anything traceable to a person is removed.
- **Invasive apps stay in the lab.** Apps with broad permissions or heavy
  tracking SDKs are captured only in isolation and published at the coarsest
  level (host categories and timing only).
- **Provenance is required.** A profile without app version, signer
  fingerprint and capture method is not accepted.

## Layout

```
schema/profile.schema.json   JSON Schema for a profile (draft)
profiles/examples/           Synthetic examples that show the format; NOT real apps
tools/validate.py            Checks profiles against the schema and the rules above
CONTRIBUTING.md              How to capture, distill and submit (draft)
```

## Status

| Part | State |
| --- | --- |
| Profile schema | Draft, will change |
| Validator | Minimal; stdlib-only checks |
| Real app profiles | None yet |
| Lab capture tooling | Not started |
| Signing and release process | Not started |
| Consumers | None; Fauxx integration is planned |

## License

Profile data (`profiles/`, `schema/`) is released under
[CC0 1.0](LICENSE-DATA). Tooling (`tools/`) is under the [MIT License](LICENSE).
Both are permissive so any privacy tool can use them.
