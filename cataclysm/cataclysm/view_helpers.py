from __future__ import annotations

from typing import Callable

from django.http import HttpRequest, HttpResponse

_VALID_PER_PAGE = ('50', '100', '500', 'all')


def make_index_view(app_label: str) -> Callable[[HttpRequest], HttpResponse]:
    """Return a view that renders the default index message for an app."""
    message = f"Hello, world. You're at the {app_label} index."

    def view(request: HttpRequest) -> HttpResponse:
        return HttpResponse(message)

    return view


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
