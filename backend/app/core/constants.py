"""Known categorical values. Wire format is the snake_case string; unknown
values from a future import still round-trip, these just drive ordering/zeroing.
"""

STATUS_ORDER = [
    "waiting_for_information",
    "to_send_invite",
    "invite_sent",
    "accepted",
    "declined",
]

GUEST_TYPES = ["broker", "client", "affinity_partner", "staff", "other"]
