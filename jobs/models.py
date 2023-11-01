import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, \
    MaxValueValidator, FileExtensionValidator, MaxLengthValidator
from django.db import models
from django.db.models import UniqueConstraint

from shared.models import BaseModel
from users.models import User

WORKER_NEED, WORK_NEED = ("worker_need", 'work_need')

JobUser = get_user_model()


# Create your models here.
class Job(BaseModel):
    user = models.ForeignKey(JobUser, models.CASCADE, null=False, blank=False)
    name = models.CharField(max_length=200)
    description = models.TextField(validators=[MaxLengthValidator(2000)])
    pic = models.ImageField(verbose_name='user_images', upload_to='job_photos',
                            validators=[FileExtensionValidator(allowed_extensions=[
                                'jpeg', 'jpg', 'png'
                            ])])

    min_price = models.IntegerField(validators=[MinValueValidator(10000)])
    max_price = models.IntegerField(validators=[MinValueValidator(10001),
                                                MaxValueValidator(1e8)])

    JOB_TYPES = (
        (WORK_NEED, "work_need"),
        (WORKER_NEED, "worker_need"),
    )
    job_type = models.CharField(max_length=32,
                                choices=JOB_TYPES,
                                default=WORK_NEED,
                                )

    def __str__(self):
        return f"{self.user}: {self.name}"

    class Meta:
        db_table = 'jobs'
        verbose_name = 'job'
        verbose_name_plural = 'jobs'


class CommentModel(BaseModel):
    post = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(JobUser, on_delete=models.CASCADE, related_name='comments',
                             default=User)
    body = models.TextField(null=False, blank=False)
    active = models.BooleanField(default=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='child',
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_time']
        db_table = 'comments'
        verbose_name = 'comment'
        verbose_name_plural = 'comments'

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.user)


class JobLike(BaseModel):
    user = models.ForeignKey(JobUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'post'],
                name='JobLikeUnique'

            )
        ]


class CommentLike(BaseModel):
    user = models.ForeignKey(JobUser, on_delete=models.CASCADE)
    comment = models.ForeignKey(CommentModel, on_delete=models.CASCADE,
                                related_name='likes')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'comment'],
                name='CommentLikeUnique',

            )
        ]
