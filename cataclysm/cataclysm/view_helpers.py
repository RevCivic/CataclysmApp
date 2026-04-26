from __future__ import annotations

from typing import Callable

from django.db.models import Q
from django.http import HttpRequest, HttpResponse

_VALID_PER_PAGE = ('50', '100', '500', 'all')


def make_index_view(app_label: str) -> Callable[[HttpRequest], HttpResponse]:
    """Return a view that renders the default index message for an app."""
    message = f"Hello, world. You're at the {app_label} index."

    def view(request: HttpRequest) -> HttpResponse:
        return HttpResponse(message)

    return view


class SearchMixin:
    """Mixin for ListView subclasses that filters by ?q= against search_fields."""

    search_fields: list[str] = ['name']

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            query = Q()
            for field in self.search_fields:
                query |= Q(**{f'{field}__icontains': q})
            qs = qs.filter(query)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_query'] = self.request.GET.get('q', '')
        return ctx


class PerPageMixin:
    """Mixin for ListView subclasses that adds 50/100/500/All per-page control."""

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get('per_page', '50')
        if per_page == 'all':
            return None
        if per_page in ('50', '100', '500'):
            return int(per_page)
        return 50

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        per_page = self.request.GET.get('per_page', '50')
        ctx['current_per_page'] = per_page if per_page in _VALID_PER_PAGE else '50'
        return ctx
