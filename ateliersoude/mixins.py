from django.urls import Resolver404, resolve


class RedirectQueryParamView:
    def get_success_url(self):
        redirect = self.request.GET.get('redirect')
        default_redirect = super().get_success_url()
        if not redirect:
            return default_redirect
        try:
            # this call throws if the redirect is not registered in urls.py
            resolve(redirect)
            return redirect
        except Resolver404:
            return default_redirect
