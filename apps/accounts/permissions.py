from django.contrib.auth.decorators import user_passes_test


# =====================================================
# ROLE CHECKS (PURE FUNCTIONS)
# =====================================================
def is_authenticated(user):
    return user.is_authenticated


def is_citizen(user):
    return user.is_authenticated and user.is_citizen


def is_lga_officer(user):
    return user.is_authenticated and user.is_lga_officer


def is_admin(user):
    return user.is_authenticated and user.is_admin_user


def is_lga_staff(user):
    """
    LGA operational staff:
    - LGA Officers
    - Admins
    """
    return user.is_authenticated and (
        user.is_lga_officer or user.is_admin_user
    )


# =====================================================
# DECORATORS (SAFE & REUSABLE)
# =====================================================
citizen_required = user_passes_test(
    is_citizen,
    login_url="/login/",
    redirect_field_name=None,
)

lga_officer_required = user_passes_test(
    is_lga_officer,
    login_url="/login/",
    redirect_field_name=None,
)

lga_staff_required = user_passes_test(
    is_lga_staff,
    login_url="/login/",
    redirect_field_name=None,
)

admin_required = user_passes_test(
    is_admin,
    login_url="/login/",
    redirect_field_name=None,
)
