"""Configuration type catalog and Monaco mapping."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class ConfigTypeDefinition:
    key: str
    label: str
    monaco_apis: List[str]


CONFIG_TYPES: Dict[str, ConfigTypeDefinition] = {
    "alerting": ConfigTypeDefinition(
        key="alerting",
        label="Alerting Profiles",
        monaco_apis=["alerting-profile"],
    ),
    "dashboards": ConfigTypeDefinition(
        key="dashboards",
        label="Dashboards",
        monaco_apis=["dashboard"],
    ),
    "slo": ConfigTypeDefinition(
        key="slo",
        label="SLO",
        monaco_apis=["slo"],
    ),
    "rules": ConfigTypeDefinition(
        key="rules",
        label="Rules",
        monaco_apis=[
            "request-naming-service",
            "service-resource-naming",
            "conditional-naming-service",
            "conditional-naming-processgroup",
            "conditional-naming-host",
        ],
    ),
    "maintenance": ConfigTypeDefinition(
        key="maintenance",
        label="Maintenance Windows",
        monaco_apis=["maintenance-window"],
    ),
    "notification": ConfigTypeDefinition(
        key="notification",
        label="Notification Channels",
        monaco_apis=["notification"],
    ),
    "management_zone": ConfigTypeDefinition(
        key="management_zone",
        label="Management Zones",
        monaco_apis=["management-zone"],
    ),
    "anomaly_detection": ConfigTypeDefinition(
        key="anomaly_detection",
        label="Anomaly Detection",
        monaco_apis=[
            "anomaly-detection-metrics",
            "anomaly-detection-applications",
            "anomaly-detection-services",
            "anomaly-detection-hosts",
            "anomaly-detection-vmware",
            "anomaly-detection-aws",
            "anomaly-detection-database-services",
            "anomaly-detection-disks",
            "frequent-issue-detection",
        ],
    ),
    "auto_tags": ConfigTypeDefinition(
        key="auto_tags",
        label="Auto Tags",
        monaco_apis=["auto-tag"],
    ),
    "application_detection": ConfigTypeDefinition(
        key="application_detection",
        label="Application Detection Rules",
        monaco_apis=["app-detection-rule", "app-detection-rule-host"],
    ),
    "service_detection": ConfigTypeDefinition(
        key="service_detection",
        label="Service Detection Rules",
        monaco_apis=[
            "service-detection-full-web-request",
            "service-detection-full-web-service",
            "service-detection-opaque-web-request",
            "service-detection-opaque-web-service",
        ],
    ),
    "request_attributes": ConfigTypeDefinition(
        key="request_attributes",
        label="Request Attributes",
        monaco_apis=["request-attributes"],
    ),
    "metric_events": ConfigTypeDefinition(
        key="metric_events",
        label="Metric Events",
        monaco_apis=["anomaly-detection-metrics"],
    ),
    "synthetic_monitors": ConfigTypeDefinition(
        key="synthetic_monitors",
        label="Synthetic Monitors",
        monaco_apis=["synthetic-monitor", "synthetic-location"],
    ),
    "extensions": ConfigTypeDefinition(
        key="extensions",
        label="Extensions",
        monaco_apis=["extension"],
    ),
}

CONFIG_PRESETS: Dict[str, List[str]] = {
    "core": [
        "alerting",
        "dashboards",
        "slo",
        "maintenance",
        "notification",
        "management_zone",
    ],
    "ops": [
        "alerting",
        "dashboards",
        "slo",
        "anomaly_detection",
        "metric_events",
    ],
    "full": ["all"],
}


def list_config_types() -> List[Dict[str, object]]:
    return [
        {"key": definition.key, "label": definition.label, "monaco_apis": definition.monaco_apis}
        for definition in CONFIG_TYPES.values()
    ]


def list_config_presets() -> Dict[str, List[str]]:
    return CONFIG_PRESETS.copy()


def resolve_config_types(
    config_types: Optional[List[str]],
    config_type: Optional[str],
    config_preset: Optional[str],
) -> List[str]:
    if config_preset:
        preset = CONFIG_PRESETS.get(config_preset)
        if not preset:
            raise ValueError(f"Unknown config preset: {config_preset}")
        return preset

    if config_types:
        return config_types

    if config_type:
        return [config_type]

    return []


def build_monaco_api_filters(config_types: List[str]) -> Optional[List[str]]:
    if not config_types or "all" in config_types:
        return []

    apis: List[str] = []
    for config_type in config_types:
        definition = CONFIG_TYPES.get(config_type)
        if not definition:
            return None
        apis.extend(definition.monaco_apis)

    return sorted(set(apis))
