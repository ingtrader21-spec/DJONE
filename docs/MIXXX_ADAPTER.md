# Mixxx Native Adapter Contract

## Decision
DJONE does not automate the Mixxx GUI. The production adapter must use Mixxx's native ControlObject/controller scripting surface so actions and readback share the same canonical engine state.

## Required controls
Deck groups map to `[Channel1]` through `[Channel4]`. Initial staging controls: play/pause, sync, rate/tempo, gain, key, loops and hotcues. Loading a user-selected track is separately allowlisted.

## Readback rule
A command is never marked executed from transport success alone. The adapter must read the corresponding ControlObject after mutation and persist requested value, observed value and timestamp. Timeout/mismatch => failed_readback.

## Host boundary
The native adapter runs in the logged-in `codestra` user session alongside Mixxx. Docker calls only a loopback Unix/TCP endpoint owned by that adapter. The adapter must not expose arbitrary script/shell execution.

## Staging certification
1. Mixxx process and audio engine healthy.
2. Native adapter authenticated locally.
3. Read Deck 1 play state.
4. Send a reversible test command with no live music loaded.
5. Read state independently and prove requested == observed.
6. Exercise idempotency and duplicate suppression.
7. Exercise emergency stop/manual override.
8. Persist request/result/readback in PostgreSQL.
9. Only then set MIXXX_EXECUTION_ENABLED=true for staging.
