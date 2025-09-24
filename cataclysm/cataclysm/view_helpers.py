from __future__ import annotations

from typing import Callable

from django.http import HttpRequest, HttpResponse


def make_index_view(app_label: str) -> Callable[[HttpRequest], HttpResponse]:
    """Return a view that renders the default index message for an app."""
    message = f"Hello, world. You're at the {app_label} index."

    def view(request: HttpRequest) -> HttpResponse:
        return HttpResponse(message)

    return view
