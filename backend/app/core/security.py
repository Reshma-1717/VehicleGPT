import re
import logging
from typing import Tuple

logger = logging.getLogger("vehiclegpt.security")

# Strictly forbidden SQL keywords for analytical query execution
DISALLOWED_SQL_PATTERNS = [
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bDROP\b",
    r"\bALTER\b",
    r"\bCREATE\b",
    r"\bTRUNCATE\b",
    r"\bREPLACE\b",
    r"\bATTACH\b",
    r"\bDETACH\b",
    r"\bPRAGMA\b",
    r"\bVACUUM\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r";.*"  # Disallow multiple chained queries
]

class SecurityEnforcer:
    """
    Enforces automotive safety boundaries:
    1. Prohibits any control or actuator write commands.
    2. Ensures read-only access for all analytical query planning.
    3. Blocks malicious SQL injection attempts.
    """

    @staticmethod
    def validate_read_only_query(query: str) -> Tuple[bool, str]:
        """Verify that an SQL query is strictly read-only SELECT."""
        trimmed = query.strip().rstrip(";")
        if not (trimmed.upper().startswith("SELECT") or trimmed.upper().startswith("WITH")):
            return False, "Query violation: Only SELECT or WITH statements are permitted."

        for pattern in DISALLOWED_SQL_PATTERNS:
            if re.search(pattern, trimmed, re.IGNORECASE):
                # allow ';' at the very end only
                if pattern == r";.*" and trimmed.count(";") == 0:
                    continue
                return False, f"Query violation: Disallowed keyword or pattern detected ('{pattern}')."

        return True, "Valid read-only query."

    @staticmethod
    def assert_vehicle_actuator_blocked(command: str) -> None:
        """
        Hard safety check ensuring no actuator/brake/steering writes can occur.
        Always raises PermissionError if called with an execution intent.
        """
        logger.critical(f"SECURITY ALERT: Attempted write command to vehicle bus blocked: {command}")
        raise PermissionError(
            "SAFETY VIOLATION: VehicleGPT operates strictly in read-only observation mode. "
            "Write operations to vehicle buses, actuators, ECUs, steering, or braking are strictly blocked."
        )
