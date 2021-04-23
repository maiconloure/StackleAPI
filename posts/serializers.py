from rest_framework import serializers
from .models import Category, Post, Tag, Comment
from accounts.serializers import UserSerializer

class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    category_icon_url = serializers.URLField(required=False)
    name = serializers.CharField()


class TagSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    tag_icon_url = serializers.URLField(required=False)
    name = serializers.CharField()


class PostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField()
    cover = serializers.URLField(required=False)
    author = serializers.CharField()
    public = serializers.BooleanField(required=False)
    category = CategorySerializer(required=False, many=True)
    tags = TagSerializer(required=False, many=True)
    content = serializers.CharField()
    likes = serializers.IntegerField()
    stars = serializers.IntegerField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Post
        fields = ('id',
                'title',
                'cover',
                'public', 
                'category', 
                'tags',
                'author', 
                'content', 
                'likes', 
                'stars', 
                'created_at', 
                'updated_at')


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    post = serializers.CharField()
    user = serializers.CharField()
    comment = serializers.CharField()
    likes = serializers.IntegerField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


    class Meta:
        model = Comment
        fields = ('id',
                'post',
                'user',
                'comment', 
                'likes', 
                'created_at', 
                'updated_at')