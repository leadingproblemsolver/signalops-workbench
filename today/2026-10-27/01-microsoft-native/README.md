# Microsoft-native technical rep

Target: microsoft/agent-framework issue #9321

Links:
- https://github.com/microsoft/agent-framework/issues/9321
- https://github.com/microsoft/agent-framework/blob/main/python/packages/foundry_local/agent_framework_foundry_local/_foundry_local_client.py
- https://github.com/microsoft/Foundry-Local/blob/main/sdk_v2/python/README.md

FIRST REP
Map old adapter assumptions to current SDK lifecycle. Do not implement until transport/lifecycle compatibility is understood.

Invariant to reconstruct:
The dependency pin is only the symptom. The adapter depends on the old SDK manager lifecycle and endpoint contract; a safe migration must preserve Agent Framework observable behavior across initialization, model selection, preparation, and transport.

Exit gate:
- compatibility table complete
- one focused failing/compatibility test or maintainer-ready technical note
- no blind dependency widening
