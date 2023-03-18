from __future__ import annotations

from homeassistant.backports.enum import StrEnum

from typing import Protocol
from homeassistant.helpers.entity_registry import RegistryEntry

from homeassistant.const import CONF_DOMAIN


class FilterOperator(StrEnum):
    AND = "and"
    OR = "or"


def create_filter(filter_config: dict) -> IncludeEntityFilter:
    """Create filter class"""
    filters = []
    if CONF_DOMAIN in filter_config:
        domain_config = filter_config.get(CONF_DOMAIN)
        if type(domain_config) == list:
            filters.append(CompositeFilter([DomainFilter(domain) for domain in domain_config], FilterOperator.OR))
        else:
            filters.append(DomainFilter(domain_config))

    return CompositeFilter(filters, FilterOperator.AND)


class IncludeEntityFilter(Protocol):
    def is_valid(self, entity: RegistryEntry) -> bool:
        """Return True when the entity should be included, False when it should be discarded"""
        pass


class DomainFilter(IncludeEntityFilter):
    def __init__(self, config):
        self.domain: str = config

    def is_valid(self, entity: RegistryEntry) -> bool:
        return entity.domain == self.domain


class CompositeFilter(IncludeEntityFilter):
    def __init__(self, filters: list[IncludeEntityFilter], operator: FilterOperator):
        self.filters = filters
        self.operator = operator

    def is_valid(self, entity: RegistryEntry) -> bool:
        evaluations = [entity_filter.is_valid(entity) for entity_filter in self.filters]
        if self.operator == FilterOperator.OR:
            return any(evaluations)

        return all(evaluations)
