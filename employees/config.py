"""
Employees app configuration/constants.

Keep domain-level validation inputs here so they're reusable across serializers,
model-level validators, and future UI/API layers.
"""

# List of countries accepted by the API/serializer validation.
# Note: keep values user-facing (returned as-is when provided).
ACCEPTED_COUNTRIES = [
    "India",
    "United Kingdom",
    "United States",
]

