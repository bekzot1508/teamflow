from django.contrib.auth import get_user_model

User = get_user_model()


def register_user(*, email, username, full_name, password):
    user = User.objects.create_user(
        email=email,
        username=username,
        full_name=full_name,
        password=password,
    )
    return user