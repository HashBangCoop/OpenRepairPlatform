from django.urls import Resolver404, resolve


def is_valid_path(path: str) -> bool:
    if not isinstance(path, str):
        return False
    try:
        # this call throws if the redirect is not registered in urls.py
        resolve(path)
        return True
    except Resolver404:
        return False


class RedirectQueryParamView:
    def get_success_url(self):
        redirect = self.request.GET.get("redirect")
        default_redirect = super().get_success_url()
        if is_valid_path(redirect):
            return redirect
        else:
            return default_redirect
