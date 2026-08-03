from enum import IntEnum


class EvidenceLevel(IntEnum):
    """EGS §3.4. Ordered most to least certain; the int value is the ordering key."""

    STRUCTURAL = 0
    CONSISTENCY = 1
    HEURISTIC = 2
    INTERPRETIVE = 3


def least_certain(*levels: EvidenceLevel) -> EvidenceLevel:
    """RES §4.3. The least-certain (highest-ordinal) level among the given levels."""
    if not levels:
        raise ValueError("least_certain requires at least one EvidenceLevel")
    return max(levels)
