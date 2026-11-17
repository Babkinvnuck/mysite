from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Blog(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blogs",
        verbose_name="Владелец",
    )
    title = models.CharField("Название", max_length=200)
    slug = models.SlugField("Слаг", unique=True, blank=True)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Картинка", upload_to="blog_images/", blank=True, null=True)
    content = models.TextField("Текст блога", blank=True)
    views = models.IntegerField("Просмотры", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REGION_CHOICES = [
        ("africa", "Африка"),
        ("australia", "Австралия"),
        ("america", "Америка"),
        ("europe", "Европа"),
        ("antarctica", "Антарктика"),
    ]
    region = models.CharField("Тема", max_length=20, choices=REGION_CHOICES, blank=True, default="")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title) or "blog"
            original_slug = self.slug
            counter = 1
            while Blog.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blogs:blog_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Блог"
        verbose_name_plural = "Блоги"


class Comment(models.Model):
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Блог",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )
    text = models.TextField("Комментарий")
    created_at = models.DateTimeField(auto_now_add=True)

    def author_avatar(self):
        if hasattr(self.author, "profile") and self.author.profile.avatar:
            return self.author.profile.avatar.url
        return ""

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f"Комментарий от {self.author} к блогу '{self.blog.title}'"


class Like(models.Model):
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="Блог",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["blog", "user"], name="unique_like")
        ]
        verbose_name = "Лайк"
        verbose_name_plural = "Лайки"

    def __str__(self):
        return f"Лайк от {self.user} на {self.blog}"