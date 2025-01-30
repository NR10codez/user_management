from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import cache_control
from django.contrib.auth.models import User


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def register_page(request):
    if request.user.is_authenticated:
        return redirect("home_page")
     
    if request.method == "POST":
        username = request.POST["username"].strip()
        email = request.POST["email"].strip()
        password1 = request.POST["password1"].strip()
        password2 = request.POST["password2"].strip()

        # Validation
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("register_page")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register_page")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register_page")

        # Create user with hashed password automatically handled by User model
        User.objects.create_user(username=username, email=email, password=password1)

        messages.success(request, "Registration successful. Please log in.")
        return redirect("login_page")

    return render(request, "register.html")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login_page(request):
    if request.user.is_authenticated:
        return redirect("home_page")

    if request.method == "POST":
        username = request.POST["username"].strip()
        password = request.POST["password"].strip()

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Log the user in and create session
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("home_page")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


@login_required(login_url="login_page")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home_page(request):
    return render(request, "home.html", {"name": request.user.username})


def log_out(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("login_page")


# Admin page


def is_admin(user):
    return user.is_authenticated and user.is_staff


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("admin_page")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect("admin_page")
        else:
            messages.error(request, "Invalid credentials or insufficient permissions.")

    return render(request, "admin_login.html")


@login_required
@user_passes_test(is_admin, login_url="admin_login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_page(request):
    search_query = request.GET.get("search")
    if search_query:
        users = User.objects.filter(username__istartswith=search_query).exclude(
            is_staff=True
        )
    else:
        users = User.objects.all().exclude(is_staff=True)

    response = render(
        request, "admin_page.html", {"users": users, "search_query": search_query}
    )
    return response


@login_required
@user_passes_test(is_admin, login_url="admin_login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_create_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if (
            not username.strip()
            or not email.strip()
            or not password1.strip()
            or not password2.strip()
        ):
            messages.error(request, "All fields must have valid data (no spaces only).")
            return redirect("admin_edit_user", user_id=user.id)

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("admin_create_user")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("admin_create_user")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("admin_create_user")

        user = User.objects.create_user(
            username=username, email=email, password=password1
        )
        user.save()
        messages.success(request, "User created successfully.")
        return redirect("admin_page")

    response = render(request, "admin_create_user.html")
    return response


@login_required
@user_passes_test(is_admin, login_url="admin_login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if (
            not username.strip()
            or not email.strip()
            or not password1.strip()
            or not password2.strip()
        ):
            messages.error(request, "All fields must have valid data (no spaces only).")
            return redirect("admin_edit_user", user_id=user.id)

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("admin_edit_user", user_id=user.id)

        if User.objects.filter(username=username).exclude(id=user_id).exists():
            messages.error(request, "Username already exists.")
            return redirect("admin_edit_user", user_id=user.id)

        if User.objects.filter(email=email).exclude(id=user_id).exists():
            messages.error(request, "Email already exists.")
            return redirect("admin_edit_user", user_id=user.id)

        user.username = username
        user.email = email
        if password1:
            user.set_password(password1)
        user.save()
        messages.success(request, "User updated successfully.")
        return redirect("admin_page")

    response = render(request, "admin_edit_user.html", {"user": user})
    return response


@login_required
@user_passes_test(is_admin, login_url="admin_login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST" and request.POST.get("confirm") == "yes":
        user.delete()
        messages.success(request, "User deleted successfully.")
        return redirect("admin_page")

    response = render(request, "delete_confirmation.html", {"user": user})
    return response


@login_required
@user_passes_test(is_admin, login_url="admin_login")
def admin_logout(request):
    logout(request)
    return redirect("admin_login")
