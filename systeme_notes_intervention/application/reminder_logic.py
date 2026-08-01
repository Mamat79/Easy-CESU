"""Calculs de dates pour les rappels Easy CESU.

Ce module ne dépend pas de SQLite ni de l'interface : il peut donc être testé
indépendamment des données réelles de l'application.
"""

from __future__ import annotations

import calendar
from datetime import date


RECURRENCES = {"once", "monthly", "yearly"}
ANTICIPATION_UNITS = {"days", "weeks", "months"}


def parse_iso_date(value: object, field_name: str = "Date") -> date:
    try:
        return date.fromisoformat(str(value or ""))
    except ValueError as exc:
        raise ValueError(f"{field_name} invalide.") from exc


def add_months(reference: date, months: int) -> date:
    """Ajoute des mois en conservant le jour de référence quand il existe.

    Exemple : un rappel prévu le 31 janvier est placé le 28 février, puis le
    31 mars. On ne réutilise donc jamais le 28 comme nouveau jour de référence.
    """

    year = reference.year + (reference.month - 1 + months) // 12
    month = (reference.month - 1 + months) % 12 + 1
    day = min(reference.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def occurrence_for_index(reference: date, recurrence_type: str, interval: int, index: int) -> date:
    if recurrence_type == "once":
        return reference
    if recurrence_type == "monthly":
        return add_months(reference, interval * index)
    if recurrence_type == "yearly":
        year = reference.year + interval * index
        day = min(reference.day, calendar.monthrange(year, reference.month)[1])
        return date(year, reference.month, day)
    raise ValueError("Type de récurrence invalide.")


def next_occurrence_after(reference: date, recurrence_type: str, interval: int, after: date) -> date | None:
    """Retourne la première occurrence strictement postérieure à ``after``."""

    if recurrence_type == "once":
        return None
    index = 0
    # Une borne défensive évite une boucle silencieuse avec des données corrompues.
    while index < 10_000:
        candidate = occurrence_for_index(reference, recurrence_type, interval, index)
        if candidate > after:
            return candidate
        index += 1
    raise ValueError("Récurrence trop ancienne ou invalide.")


def occurrence_dates_until(reference: date, recurrence_type: str, interval: int, until: date, limit: int = 240) -> list[date]:
    """Matérialise les échéances jusqu'à une date, sans doublon ni boucle infinie."""

    dates: list[date] = []
    index = 0
    while len(dates) < limit:
        candidate = occurrence_for_index(reference, recurrence_type, interval, index)
        if candidate > until:
            break
        dates.append(candidate)
        if recurrence_type == "once":
            break
        index += 1
    return dates
