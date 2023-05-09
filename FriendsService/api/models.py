from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    password = models.CharField("password", max_length=200)


class Relationship(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="from_user"
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="to_user"
    )
    # status == False => friend request sent, but not accepted
    # status == True => friend request accepted
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.from_user} --> {self.to_user}"
