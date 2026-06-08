from __future__ import annotations

from dataclasses import dataclass

from diag.core.models import RiskLevel


@dataclass(frozen=True)
class SandboxDecision:
    action: str
    reason: str


@dataclass(frozen=True)
class SandboxProfile:
    name: str
    description: str
    allow_risks: tuple[RiskLevel, ...]
    ask_risks: tuple[RiskLevel, ...]
    allow_patterns: tuple[str, ...] = ()


PROFILES: dict[str, SandboxProfile] = {
    "safe-read": SandboxProfile(
        "safe-read",
        "Only safe read-only observation commands.",
        (RiskLevel.SAFE_READONLY,),
        (),
    ),
    "ops-read": SandboxProfile(
        "ops-read",
        "Read service configs, logs, docker state and safe validation commands.",
        (RiskLevel.SAFE_READONLY,),
        (RiskLevel.LOW_RISK,),
        ("nginx -t", "systemctl cat"),
    ),
    "lab-write": SandboxProfile(
        "lab-write",
        "Allow low-risk writes only inside fault-lab or sandbox workflows.",
        (RiskLevel.SAFE_READONLY,),
        (RiskLevel.LOW_RISK,),
        ("fault-lab", "sandbox"),
    ),
    "admin-confirm": SandboxProfile(
        "admin-confirm",
        "Ask before real low-risk operations; dangerous operations remain blocked.",
        (RiskLevel.SAFE_READONLY,),
        (RiskLevel.LOW_RISK,),
    ),
}


def get_sandbox_profile(name: str | None) -> SandboxProfile:
    return PROFILES.get(name or "safe-read", PROFILES["safe-read"])


def list_sandbox_profiles() -> list[dict[str, str]]:
    return [{"name": profile.name, "description": profile.description} for profile in PROFILES.values()]


def evaluate_sandbox(profile_name: str | None, command: str, risk: RiskLevel) -> SandboxDecision:
    profile = get_sandbox_profile(profile_name)
    lowered = command.lower()
    if risk == RiskLevel.BLOCKED or risk == RiskLevel.HIGH_RISK:
        return SandboxDecision("deny", f"{profile.name}: dangerous operations are blocked")
    if risk in profile.allow_risks:
        return SandboxDecision("allow", f"{profile.name}: allowed {risk.value}")
    if risk in profile.ask_risks:
        if profile.name == "ops-read" and any(pattern in lowered for pattern in profile.allow_patterns):
            return SandboxDecision("allow", f"{profile.name}: allowed ops-read validation command")
        return SandboxDecision("ask", f"{profile.name}: requires confirmation for {risk.value}")
    return SandboxDecision("deny", f"{profile.name}: {risk.value} is not allowed")
