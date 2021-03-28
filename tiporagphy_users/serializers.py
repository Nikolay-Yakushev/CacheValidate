from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from django.db.transaction import atomic
from django.forms import forms
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from tiporagphy_users.models import Profile

# from tiporagphy_users.user_enums import UserGroupsEnums

""" User creation Serializers """


class ProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = (
            "date_joined",
            "user",
        )


class UserCreationSerializer(serializers.ModelSerializer):
    profile = ProfileCreateSerializer()
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all()), EmailValidator],
    )

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.fields["username"].validators = [
            UniqueValidator(queryset=User.objects.all()),
            self.validate_username_startswith,
        ]

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        user.set_password(validated_data["password"])
        user.save()
        user_groups = validated_data["profile"].pop("group")
        profile = validated_data["profile"]
        Profile.objects.create(user=user, **profile)
        for group in user_groups:
            group.user_set.add(user)
        validated_data["profile"]["group"] = user_groups
        return user

    def validate_username_startswith(self, value):
        if value.startswith("@"):
            return value
        raise serializers.ValidationError("username should startswith @")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "password2",
            "email",
            "first_name",
            "last_name",
            "profile",
        ]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            "password": {"write_only": True},
        }


"""Authenticate User"""


class AuthenticateUserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


"""Check if UserInGroup"""


class CustomPKRelatedField(serializers.PrimaryKeyRelatedField):
    """A PrimaryKeyRelatedField derivative that uses named field for the display value."""

    def __init__(self, **kwargs):
        self.display_field = kwargs.pop("display_field", "name")
        super(CustomPKRelatedField, self).__init__(**kwargs)

    def display_value(self, instance):
        # Use a specific field rather than model stringification
        return getattr(instance, self.display_field)


class GroupsSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        grs = [
            (name, name)
            for name in self.Meta.model.objects.all().values_list("name", flat=True)
        ]
        return grs

    class Meta:
        model = Group
        exclude = ("permissions",)


class UserInGroupSerializer(serializers.ModelSerializer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields["groups"].choices = self.get_groups()
        self.fields["username"].choices = self.get_users()

    username = serializers.ChoiceField(choices=[])
    groups = serializers.MultipleChoiceField(choices=[])

    def get_groups(self):
        return [
            (name, name) for name in Group.objects.all().values_list("name", flat=True)
        ]

    def get_users(self):
        users = [name for name in User.objects.all().values_list("id", "username")]
        return users

    def validate(self, data):
        validators = [self.validate_username_startswith, self.validate_user_exists]
        for validator in validators:
            validator(data)
        return data

    def validate_username_startswith(self, attrs):
        if attrs["username"] == "admin":
            raise serializers.ValidationError("Can not check user name admin")
        return attrs

    def validate_user_exists(self, attrs):
        if not User.objects.filter(id=int(attrs["username"])).exists():
            raise serializers.ValidationError("User does not exits")
        return attrs

    class Meta:
        model = User
        fields = ["username", "groups"]


"""Serializers For User Management"""


class UserManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "groups"]
