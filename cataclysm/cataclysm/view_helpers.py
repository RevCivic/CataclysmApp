from __future__ import annotations

from typing import Callable

from django.db.models import Q
from django.http import HttpRequest, HttpResponse

from tags.models import Tag

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
        self._search_query = self.request.GET.get('q', '').strip()
        if self._search_query:
            query = Q()
            for field in self.search_fields:
                query |= Q(**{f'{field}__icontains': self._search_query})
            qs = qs.filter(query)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_query'] = getattr(self, '_search_query', '')
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


class TagFilterMixin:
    """Mixin for ListView subclasses that filters by ?tag=<id> for tags M2M."""

    tag_field_name = 'tags'

    def get_queryset(self):
        qs = super().get_queryset()
        self._selected_tag_ids = [int(tag_id) for tag_id in self.request.GET.getlist('tag') if tag_id.isdigit()]
        if self._selected_tag_ids:
            qs = qs.filter(**{f'{self.tag_field_name}__id__in': self._selected_tag_ids}).distinct()
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tags'] = Tag.objects.order_by('name')
        ctx['selected_tag_ids'] = getattr(self, '_selected_tag_ids', [])
        return ctx


def add_tags_from_input(instance, raw_tags: str) -> None:
    if not raw_tags or not hasattr(instance, 'tags'):
        return

    seen = set()
    cleaned_names = []
    for part in raw_tags.replace(';', ',').replace('\n', ',').split(','):
        name = part.strip()
        if not name:
            continue
        normalized = name.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        cleaned_names.append(name)

    if not cleaned_names:
        return

    tags = []
    for name in cleaned_names:
        tag = Tag.objects.filter(name__iexact=name).first()
        if tag is None:
            tag = Tag.objects.create(name=name)
        tags.append(tag)
    instance.tags.add(*tags)


class AddTagsFromInputMixin:
    new_tags_field_name = 'new_tags'

    def form_valid(self, form):
        response = super().form_valid(form)
        add_tags_from_input(self.object, self.request.POST.get(self.new_tags_field_name, ''))
        return response
