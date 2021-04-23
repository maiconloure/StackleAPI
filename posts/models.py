from django.db import models
from accounts.models import User
from django.utils import timezone

class Category(models.Model):
    category_icon_url = models.URLField(max_length=255)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categories"

class Tag(models.Model):
    tag_icon_url = models.URLField(max_length=255)
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Tags"


class Post(models.Model):
    title = models.CharField(max_length=100)
    cover = models.URLField(max_length=200, blank=True, null=True)
    public = models.BooleanField(default=True)
    category = models.ManyToManyField(Category)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    tags = models.ManyToManyField(Tag)
    likes = models.IntegerField(default=0)
    stars = models.IntegerField(default=0)
    # comments = models.ForeignKey(Comment, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField()
    
    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ('author', 'author')
        ]

    def get_tags(self):
        return [tag.name for tag in self.tags.all()]

    def get_categories(self):
        return [category.name for category in self.category.all()]

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        return super(Post, self).save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    likes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return f"user_id: {self.name}, comment: {self.comment}, likes: {self.likes}, created_at: {self.created_at} updated_at: {self.updated_at}"
    
    class Meta:
        verbose_name_plural = "Comments"