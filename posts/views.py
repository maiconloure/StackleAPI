from rest_framework import status
from django.contrib.auth import authenticate, logout
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .permissions import RightUserOnly
from .models import Category, Comment, Post, Tag
from .serializers import CategorySerializer, TagSerializer, PostSerializer, CommentSerializer
from guardian.shortcuts import assign_perm
from datetime import timedelta, datetime


class CategoryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, RightUserOnly]

    def get(self, request):
        try: 
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as errors:
            return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            category = Category.objects.create(**request.data)
            return Response({'message': f'Category created.'}, status=status.HTTP_201_CREATED)
        except Exception as errors:
            return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST)

class TagView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, RightUserOnly]

    def get(self, request):
        categories = Tag.objects.all()
        serializer = TagSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        category = Tag.objects.create(**request.data)
        return Response({'message': f'Tag created.'}, status=status.HTTP_201_CREATED)

class CommentView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        try:
            if id is not None:
                comments = [cmt for cmt in Comment.objects.all() if cmt.post.id == id]
                serializer = CommentSerializer(comments, many=True)
                

                return Response(serializer.data, status=status.HTTP_200_OK)

            comments = Comment.objects.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as errors:
            return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, id):
        try:
            user = self.request.user
            post = Post.objects.get(id=id)
            serializer = CommentSerializer(data={**request.data, 'post': post.title, 'user': user.username})
            if serializer.is_valid():
                comment = Comment.objects.create(**request.data, user=user, post=post)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response({'error': 'invalid data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as errors:
            return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, id):
        try:
            user = self.request.user
            comment = Comment.objects.get(id=id)
            serializer = CommentSerializer(comment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK)
            
            else:
                return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as errors:
            return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            comment = Comment.objects.get(id=id)
            comment.delete()
            return Response(status=status.HTTP_200_OK)
        
        except Exception as errors:
            return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST)
   


class PostView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, RightUserOnly]

    def get(self, request, post_id=None):
        if self.request.user.is_authenticated and post_id is not None:
            try:
                post = Post.objects.get(id=post_id)
                serializer = PostSerializer(post)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as errors:
                return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            posts = Post.objects.all()
            serializer = PostSerializer(posts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        author = self.request.user
        serializer = PostSerializer(data={**request.data, 'author': author.username})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            post = Post.objects.create(
                title=request.data['title'],
                content=request.data['content'],
                cover=request.data.get('cover'),
                likes=request.data['likes'],
                stars=request.data['likes'],
                author=author)

            assign_perm('author', request.user, post)
            if len(request.data.get('category')) > 0:
                category = Category.objects.filter(name=request.data['category'][0]['name']).first()
                post.category.add(category)

            if len(request.data.get('tags')) > 0:
                for tag in request.data['tags']:
                    tags = Tag.objects.get(name=tag['name'])
                    post.tags.add(tags)

            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as errors:
                return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, post_id):
        if not isinstance(post_id, int):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:    
            post = Post.objects.get(id=post_id)
            if not request.user.has_perm('posts.author', post):
                return Response({'errors': 'you are not the author of this post'}, status=status.HTTP_403_FORBIDDEN)
            updated = datetime.now()
            serializer = PostSerializer(post, data={**request.data, 'updated_at': updated}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Post updated successfully'}, status=status.HTTP_200_OK)

            else:
                return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as errors:
            return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id):
        try:
            if Post.objects.filter(id=post_id):
                post = Post.objects.get(id=post_id)
                if not request.user.has_perm('posts.author', post):
                    return Response({'errors': 'you are not the author of this post'}, status=status.HTTP_403_FORBIDDEN)
                post.delete()
                return Response({'message': 'Post deleted successfully'}, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)

        except Exception as errors:
            return Response({'error': str(errors)}, status=status.HTTP_400_BAD_REQUEST)
