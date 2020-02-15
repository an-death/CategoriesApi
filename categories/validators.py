import abc
from typing import Any, Iterable

from rest_framework import serializers

from categories.models import Category


class Validator(abc.ABC):

    @abc.abstractmethod
    def validate(self, attrs: Any):
        pass


class UniqueCategoriesNameInRequest(Validator):
    """
    Validating that in request all names are unique.

    That should be reduce queries to DB.
    But that only is pre-validation and cannot be true in the last instance.
    """

    def validate(self, attrs: dict):
        names = self._get_names(attrs)
        if self._is_unique_set(names):
            raise serializers.ValidationError()

    def _get_names(self, data: dict):
        yield data['name']
        yield from self._get_names(data.get('children', ()))

    @staticmethod
    def _is_unique_set(names: Iterable[str]):
        return len(names) != len(set(names))


class UniqueCategoriesNameInDB(UniqueCategoriesNameInRequest):
    """
    Validating that names in requests
    not conflicted with names in DB.

    That's mean that we should add Index on `name` field.
    """

    def validate(self, attrs: Any):
        names = self._get_names(attrs)
        if self._lookup_names(names):
            raise serializers.ValidationError()

    @staticmethod
    def _lookup_names(names: Iterable[str]) -> bool:
        return Category.objects.filter(name__in=names).count()
