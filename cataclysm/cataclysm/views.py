from __future__ import annotations

from typing import Optional

from django.http import HttpRequest, HttpResponse
from django.views import View


class StaticIndexView(View):
    """A simple class-based view for static index messages."""

    message_template = "Hello, world. You're at the {app_label} index."
    message: Optional[str] = None
    app_label: Optional[str] = None

    def get_message(self) -> str:
        if self.message is not None:
            return self.message
        if self.app_label is None:
            raise ValueError(
                "StaticIndexView requires either 'message' or 'app_label' to be set."
            )
        return self.message_template.format(app_label=self.app_label)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return HttpResponse(self.get_message())
