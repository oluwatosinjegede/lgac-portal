from django.contrib.auth.decorators import user_passes_test

def lga_officer_required(view_func):
    return user_passes_test(
        lambda user: user.is_authenticated and user.is_lga_officer,
        login_url="/accounts/login/"
    )(view_func)
