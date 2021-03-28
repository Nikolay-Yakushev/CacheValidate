from django.contrib.auth.models import User, Group
from django.db import models
from django.utils import timezone

# Create your models here.
# from tiporagphy_users.user_enums import UserTypesEnums, UserGroupsEnums


# class Group(models.Model):
#     group_name = models.CharField(
#         max_length=256, choices=UserGroupsEnums.get_group_types()
#     )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(
        max_length=256,
        choices=[
            (name_gr, name_gr)
            for name_gr in Group.objects.all().values_list("name", flat=True)
        ],
    )
    date_joined = models.DateField(default=timezone.now)
    group = models.ManyToManyField(Group, related_name="grp")

    # def _do_update(self, base_qs, using, pk_val, values, update_fields, forced_update):

    def __str__(self):
        return f"{self.user.username}"
