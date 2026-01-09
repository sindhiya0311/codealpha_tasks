from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Post, Profile, Comment, FollowRequest, Notification
from django.contrib.auth.decorators import login_required

def signup_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.create_user(username=username, password=password)
        Profile.objects.create(user=user)
        login(request, user)
        return redirect('feed')
    return render(request, 'signup.html')


def login_view(request):
    if request.method == "POST":
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('feed')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def feed(request):
    posts = Post.objects.all().order_by('-created')
    return render(request, 'feed.html', {'posts': posts})


@login_required
def like_post(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('feed')


@login_required
def comment_post(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.method == "POST":
        Comment.objects.create(
            post=post,
            user=request.user,
            text=request.POST['comment']
        )
    return redirect('feed')


@login_required
def profile(request, username):
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    posts = Post.objects.filter(user=user)

    follow_label = None

    if request.user != user:
        if request.user in profile.followers.all():
            follow_label = "Unfollow"
        elif FollowRequest.objects.filter(
            from_user=request.user,
            to_user=user
        ).exists():
            follow_label = "Cancel request"
        else:
            follow_label = "Follow"

    return render(request, 'profile.html', {
        'profile': profile,
        'posts': posts,
        'follow_label': follow_label,
    })


@login_required
def follow_user(request, username):
    target_user = User.objects.get(username=username)
    target_profile = Profile.objects.get(user=target_user)

    if request.user in target_profile.followers.all():
        target_profile.followers.remove(request.user)
    else:
        target_profile.followers.add(request.user)

    return redirect('profile', username=username)


@login_required
def follow_user(request, username):
    to_user = User.objects.get(username=username)

    if request.user == to_user:
        return redirect('profile', username=username)

    # If already following → unfollow
    profile = Profile.objects.get(user=to_user)
    if request.user in profile.followers.all():
        profile.followers.remove(request.user)
        return redirect('profile', username=username)

    # If request exists → cancel request
    fr = FollowRequest.objects.filter(
        from_user=request.user,
        to_user=to_user
    )
    if fr.exists():
        fr.delete()
        return redirect('profile', username=username)

    # Else → send request
    FollowRequest.objects.create(
        from_user=request.user,
        to_user=to_user
    )

    Notification.objects.create(
        user=to_user,
        text=f"{request.user.username} sent you a follow request"
    )

    return redirect('profile', username=username)


    return redirect('profile', username=username)

@login_required
def handle_request(request, request_id, action):
    fr = FollowRequest.objects.get(id=request_id)

    if action == "accept":
        profile = Profile.objects.get(user=fr.to_user)
        profile.followers.add(fr.from_user)

        Notification.objects.create(
            user=fr.from_user,
            text=f"{fr.to_user.username} accepted your follow request"
        )

    fr.delete()
    return redirect('notifications')

@login_required
def notifications(request):
    follow_requests = FollowRequest.objects.filter(to_user=request.user)
    notifications = Notification.objects.filter(user=request.user).order_by('-created')

    return render(request, 'notifications.html', {
        'follow_requests': follow_requests,
        'notifications': notifications
    })


@login_required
def followers_list(request, username):
    user = User.objects.get(username=username)
    followers = Profile.objects.get(user=user).followers.all()
    return render(request, 'followers.html', {'users': followers})


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile


@login_required
def following_list(request, username):
    user = get_object_or_404(User, username=username)

    # users THIS user is following
    profiles_followed = Profile.objects.filter(followers=user)
    users = [profile.user for profile in profiles_followed]

    return render(request, "followers.html", {
        "users": users,
        "title": "Following"
    })

from django.contrib.auth.models import User
from django.db.models import Q

@login_required
def search(request):
    query = request.GET.get('q', '').strip()
    users = []

    if query:
        users = User.objects.filter(
            Q(username__icontains=query)
        ).exclude(username=request.user.username)

    return render(request, 'search.html', {
        'users': users,
        'query': query
    })

@login_required
def profile(request, username):
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    posts = Post.objects.filter(user=user)

    follow_label = None

    if request.user != user:
        if request.user in profile.followers.all():
            follow_label = "Unfollow"
        elif FollowRequest.objects.filter(
            from_user=request.user,
            to_user=user
        ).exists():
            follow_label = "Cancel request"
        else:
            follow_label = "Follow"

    return render(request, 'profile.html', {
        'profile': profile,
        'posts': posts,
        'follow_label': follow_label,
    })

@login_required
def create_post(request):
    if request.method == "POST":
        image = request.FILES.get('image')
        caption = request.POST.get('caption')

        if image:
            Post.objects.create(
                user=request.user,
                image=image,
                caption=caption
            )
            return redirect('feed')

    return render(request, 'create_post.html')


@login_required
def edit_profile(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        username = request.POST.get('username')
        bio = request.POST.get('bio')

        if username:
            request.user.username = username
            request.user.save()

        profile.bio = bio
        profile.save()

        return redirect('profile', username=request.user.username)

    return render(request, 'edit_profile.html', {'profile': profile})

