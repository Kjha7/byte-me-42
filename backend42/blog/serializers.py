from rest_framework import serializers

from .models import *


class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.user')
    likes = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'is_forked', 'origin_id', 'is_published', 'title', 'slug',
            'content', 'author', 'created', 'likes', 'likes_count')

    def get_likes(self, obj):
        print(obj)
        likes = Like.objects.filter(post=obj)
        list_user = []
        for x in likes:
            list_user.append(x.profile.user.username)
        return list_user

    def get_likes_count(self, obj):
        likes = Like.objects.filter(post=obj)
        return likes.count()

# class FOllowSerializer(serializers.ModelSerializer):
#     user = serializers.CharField(source='user.username', read_only='True')
#     following = serializers.SerializerMethodField()
#     followers = serializers.SerializerMethodField()
#
#     def get_following(self, user):
#         f = Follow.objects.filter(follower=user)
#         print(f)
#         listy = []
#         for x in f:
#             listy.append(x.following.user.username)
#
#         return listy
#
#     def get_followers(self, user):
#         f = Follow.objects.filter(following=user)
#         print(f)
#         listy = []
#         for x in f:
#             listy.append(x.follower.user.username)
#         return listy


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only='True')
    post = PostSerializer(many=True)
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

    def get_following(self, user):
        f = Follow.objects.filter(follower=user)
        print(f)
        listy = []
        for x in f:
            listy.append(x.following.user.username)

        return listy

    def get_followers(self, user):
        f = Follow.objects.filter(following=user)
        print(f)
        listy = []
        for x in f:
            listy.append(x.follower.user.username)
        return listy

    class Meta:
        model = Profile
        fields = (
            'id', 'user', 'bio', 'location', 'birth_date', 'post', 'following', 'followers')





# from rest_framework import serializers
#
# from .models import Profile, Post, Like, Follow
#
#
# class LikeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Like
#         fields = '__all__'
#
#
# class PostSerializer(serializers.ModelSerializer):
#     author = serializers.CharField(source='author.username', read_only=True)
#     id = id
#
#     lik = serializers.SerializerMethodField('get_likey')
#
#     def get_likey(self, id):
#         likey = Like.objects.filter(post=id)
#         print(likey)
#
#         like_list = []
#
#         for indi_like in likey:
#             like_list.append(indi_like.profile.user.username)
#
#         return [like_list, len(like_list)]
#
#     class Meta:
#         model = Post
#         fields = (
#             'id', 'is_forked', 'origin_id', 'is_published', 'title', 'slug',
#             'content', 'author', 'created', 'lik')
#
#
# class FollowSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Follow
#         fields = ('follower', 'following', 'since')
#
#
# class ProfileSerializer(serializers.ModelSerializer):
#     user = serializers.CharField(source='user.username', read_only='True')
#     post = PostSerializer(many=True)
#
#     following = serializers.SerializerMethodField('get_followin')
#     followers = serializers.SerializerMethodField('ge_followers')
#
#     def get_followin(self, user):
#         f = Follow.objects.filter(follower=user)
#         print(f)
#         listy = []
#         for x in f:
#             listy.append(x.following.user.username)
#
#         return listy
#
#     def ge_followers(self, user):
#         f = Follow.objects.filter(following=user)
#         print(f)
#         listy = []
#         for x in f:
#             listy.append(x.follower.user.username)
#
#         return listy
#
#     class Meta:
#         model = Profile
#         fields = (
#             'id', 'user', 'bio', 'location', 'birth_date', 'post',
#             'following', 'followers')


class TimelineSerializer(serializers.Serializer):
    profile = ProfileSerializer(many=True)
    posts = PostSerializer(many=True)


