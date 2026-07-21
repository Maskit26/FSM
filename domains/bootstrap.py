"""
Загрузка активных доменов: импорт пакета → register_all(service_id) → Domain Validator.

v1: домены из FSM_DOMAINS; после register_all — валидация RAM (+ domain DB, если engine есть).
"""

from __future__ import annotations

import importlib
import logging
import os
from typing import Callable, Optional

from fsm_platform.host.domain_validator import (
    DomainValidationError,
    default_domain_validator,
    package_dir_from_entry,
)
from fsm_platform.host.engines import domain_session

logger = logging.getLogger(__name__)


def _load_register_all(entry: str) -> Callable[[str], None]:
    """
    Загружает callable register_all из строки entry.
    Форматы: domains.courier.processes:register_all или domains.courier (атрибут register_all).
    """
    if ":" in entry:
        module_name, attr = entry.split(":", 1)
    else:
        module_name, attr = entry, "register_all"
    module = importlib.import_module(module_name)
    fn = getattr(module, attr)
    if not callable(fn):
        raise TypeError(f"{entry} is not callable")
    return fn  # type: ignore[return-value]


def bootstrap_domain(service_id: str, entry: str) -> None:
    """
    register_all + Domain Validator для одного service_id.
    При ошибках валидации — DomainValidationError (домен не считается активным).
    """
    from fsm_platform.host.domain_validator import ValidationReport

    try:
        register_all = _load_register_all(entry)
    except Exception as exc:
        report = ValidationReport(service_id=service_id)
        report.add_error("ENTRY_IMPORT_FAILED", str(exc), where=entry)
        raise DomainValidationError(report) from exc

    logger.info("register_all service_id=%s entry=%s", service_id, entry)
    try:
        register_all(service_id)
    except Exception as exc:
        logger.exception("REGISTER_ALL_FAILED service_id=%s", service_id)
        report = ValidationReport(service_id=service_id)
        report.add_error("REGISTER_ALL_FAILED", str(exc), where=entry)
        raise DomainValidationError(report) from exc

    session = _try_domain_session(service_id)
    try:
        report = default_domain_validator.validate(
            service_id,
            entry=entry,
            package_dir=package_dir_from_entry(entry),
            session_domain=session,
        )
    finally:
        if session is not None:
            session.close()

    if not report.ok:
        logger.error(
            "domain validation failed service_id=%s errors=%s",
            service_id,
            report.to_dict()["errors"],
        )
        raise DomainValidationError(report)

    if report.warnings:
        logger.warning(
            "domain validation warnings service_id=%s warnings=%s",
            service_id,
            report.to_dict()["warnings"],
        )
    logger.info(
        "domain validation ok service_id=%s stats=%s",
        service_id,
        report.stats,
    )


def _try_domain_session(service_id: str) -> Optional[object]:
    """Открывает domain session если engine уже зарегистрирован; иначе None (только RAM-проверки)."""
    try:
        return domain_session(service_id)
    except KeyError:
        logger.warning(
            "no domain engine for %s — Validator skips DB checks",
            service_id,
        )
        return None


def bootstrap_from_env() -> None:
    """
    Читает FSM_DOMAINS и регистрирует домены в RAM-реестрах с валидацией.
    Пример: svc_courier_01=domains.courier.processes:register_all
    Несколько записей через точку с запятой.
    """
    raw = os.environ.get("FSM_DOMAINS", "").strip()
    if not raw:
        logger.warning("FSM_DOMAINS empty — no domains registered")
        return

    for item in raw.split(";"):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError(
                f"FSM_DOMAINS item must be service_id=module:register_all, got {item!r}"
            )
        service_id, entry = item.split("=", 1)
        bootstrap_domain(service_id.strip(), entry.strip())
