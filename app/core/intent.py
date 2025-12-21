def detect_intent(query: str) -> str:
    q = query.lower()

    if any(k in q for k in [
        "scholarship", "stipend", "grant",
        "financial aid", "kanyashree", "aikyashree"
    ]):
        return "scholarship"

    if any(k in q for k in [
        "canteen", "food", "mess", "cafeteria"
    ]):
        return "canteen"

    if any(k in q for k in [
        "rule", "allowed", "fine", "penalty",
        "banned", "policy"
    ]):
        return "rules"

    if any(k in q for k in [
        "holiday", "vacation", "leave", "closed",
        "break", "semester break", "off day"
    ]):
        return "holiday"

    return "general"
