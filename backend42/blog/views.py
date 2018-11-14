from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.forms.widgets import HiddenInput
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from blog.forms import PostForm, ForkPostForm
from .models import Post, Like, Profile, Follow


def home(request):
    # all_posts = Post.objects.all()
    all_posts = Post.objects.filter(origin_id=None)
    template = 'home.html'
    context = {'all_posts': reversed(all_posts)}
    return render(request, template, context)


def user_profile(request, username):
    if User.objects.get(username=username):
        profile = Profile.objects.get(user=User.objects.get(username=username))
        current_user = User.objects.get(username=request.user.username)
        is_follower = False
        followers = profile.get_followers()
        for follower in followers:
            if current_user.username == follower.follower.user.username:
                is_follower = True
        posts = Post.objects.filter(author=profile)
        template = 'blog/user/profile.html'
        context = {'profile': profile,
                   'posts': posts,
                   'is_follower': is_follower}
        return render(request, template, context)
    else:
        return JsonResponse({'message': 'User not found'})


@login_required
@api_view(['GET'])
def like(request, post_id, username):
    print('Came in method')
    if request.method == 'GET':
        if request.user.username == username:
            post = Post.objects.get(id=post_id)
            user = User.objects.get(username=username)
            profile = Profile.objects.get(user=user)
            if Like.objects.filter(profile=profile, post=post):
                liked_by_user = Like.objects.filter(profile=profile, post=post)
                liked_by_user.delete()
                return Response({'PostId': post_id, 'status': False},
                                status=status.HTTP_200_OK
                                )
            else:
                post.like(username)
                return Response({'PostId': post_id, 'status': True},
                                status=status.HTTP_200_OK
                                )
        else:
            msg = "User: " + username + " invalid or currently not logged in"
            return Response(status=status.HTTP_403_FORBIDDEN)


@login_required
def follow(request, username):
    user = User.objects.get(username=username)
    follower = request.user.profile
    following = user.profile
    if request.user.username != username:
        if Follow.objects.filter(follower=follower, following=following):
            followed_by_user = Follow.objects.filter(follower=follower,
                                                     following=following)
            followed_by_user.delete()
        else:
            follower.follow(username)
        return JsonResponse({'message': 'success'})
    else:
        msg = 'Have you lost your path?'
        return JsonResponse({'message': msg})


@login_required
def post_view(request, post_id):
    threads = []
    likes = []
    if Post.objects.filter(id=post_id):
        all_leaf_posts = Post.objects.filter(
            title=Post.objects.get(id=post_id).title, is_daddu=True)
       # print(all_leaf_posts)
        for leaf_post in all_leaf_posts:
            thread = []
            like_count = leaf_post.like_set.count()
            thread.append(leaf_post)
            while leaf_post.origin_id:
                target_post = get_object_or_404(Post, id=leaf_post.origin_id)
                leaf_post = target_post
                # print(leaf_post)
                like_count += target_post.like_set.count()
                thread.append(target_post)

            threads.append(thread)
            likes.append(like_count)
        # print(threads, likes)
        thread_like = zip(threads, likes)

        print(thread_like)
        thread_like = list(sorted(thread_like, key=lambda t: t[1]))[::-1]
        print(thread_like)
        for i in range(len(thread_like)):
            threads[i] = thread_like[i][0]

        # posts = []
        target_post = Post.objects.get(id=post_id)
        profile = User.objects.get(username=target_post.author.user.username)
        # posts.append(target_post)
        # while target_post.origin_id:
        #     target_post = Post.objects.get(id=target_post.origin_id)
        #     posts.append(target_post)
        # thread = Post.objects.get(id=post_id)
        # print(threads)
        for i in range(len(threads)):
            threads[i] = threads[i][::-1]
        # print(threads)
        posts = threads[0]
        template = 'blog/post/post_page.html'
        context = {'posts': posts,
                   'profile': profile}
        return render(request, template, context)
    else:
        return JsonResponse({'message': 'Post not found'})


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            words = post.content.split()
            if len(words) > 42:
                msg = 'Max allowed words are 42.'
                return JsonResponse({'message': msg})
            post.author = request.user.profile
            post.slug = post.id
            post.seo_description = post.title
            post.seo_title = post.title
            post.save()
            return redirect(post.get_absolute_url())
    else:
        form = PostForm()
    return render(request, 'blog/post/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    if Post.objects.filter(id=post_id):
        post = get_object_or_404(Post, id=post_id)
        if request.method == "POST":
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                words = post.content.split()
                if len(words) > 42:
                    msg = 'Max allowed words are 42.'
                    return JsonResponse({'message': msg})
                post.save()
                return redirect(post.get_absolute_url())
        elif post.author.user.username == request.user.username:
            form = PostForm(instance=post)
            return render(request, 'blog/post/create_post.html', {'form': form})
        else:
            return JsonResponse({'message': 'You can\'t edit this post'})
    else:
        return JsonResponse({'message': 'Post not found'})


@login_required
def fork(request, post_id):
    if Post.objects.filter(id=post_id):
        parent_posts = []
        temp_post = get_object_or_404(Post, id=post_id)
        while temp_post.is_forked:
            parent_posts.append(temp_post)
            temp_post = get_object_or_404(Post, id=temp_post.origin_id)
        parent_posts.append(temp_post)

        if len(parent_posts) >= 10:
            return JsonResponse({'message': 'Reached max no of forks, 10'})

        size_pp = len(parent_posts)

        if request.method == "POST":
            parent_post = Post.objects.get(id=post_id)
            form = ForkPostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                words = post.content.split()
                if len(words) > 42:
                    msg = 'Max allowed words are 42.'
                    return JsonResponse({'message': msg})
                post.is_forked = True
                post.origin_id = post_id
                post.author = request.user.profile
                post.slug = post.id
                post.seo_description = post.title
                post.seo_title = post.title
                post.title = parent_post.title
                post.is_daddu = True
                post.save()
                temp_post = get_object_or_404(Post, id=post_id)
                temp_post.is_daddu = False
                temp_post.save()
                return redirect(post.get_absolute_url())
        else:
            form = ForkPostForm()
        return render(request, 'blog/post/create_post.html', {'form': form, 'parent_posts': reversed(parent_posts), 'size_pp': size_pp})


@login_required
def post_delete(request, post_id):
    if Post.objects.filter(id=post_id):
        target_post = Post.objects.get(id=post_id)

        if target_post.origin_id:
            child_posts = Post.objects.filter(origin_id=post_id)
            for child_post in child_posts:
                child_post.origin_id = target_post.origin_id
                child_post.save()
            target_post.delete()
        else:
            return JsonResponse({'message': 'Sorry, you can not delete a thread'})
    if Post.objects.filter(id=post_id):
        return JsonResponse({'message': 'Something went wrong'})
    else:
        return JsonResponse({'message': 'deleted'})
