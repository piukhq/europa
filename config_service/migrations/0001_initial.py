# Generated by Django 2.0.7 on 2018-07-31 13:34

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0009_alter_user_last_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomUser",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=30, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",  # noqa
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                ("first_login", models.BooleanField(default=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",  # noqa
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.Group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.Permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Configuration",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("merchant_id", models.CharField(max_length=64)),
                ("merchant_url", models.CharField(max_length=256)),
                (
                    "handler_type",
                    models.IntegerField(
                        choices=[(0, "Update"), (1, "Join"), (2, "Validate")]
                    ),
                ),
                (
                    "integration_service",
                    models.IntegerField(choices=[(0, "Sync"), (1, "Async")]),
                ),
                (
                    "callback_url",
                    models.CharField(blank=True, max_length=256, null=True),
                ),
                ("retry_limit", models.IntegerField(default=0)),
                (
                    "log_level",
                    models.IntegerField(
                        choices=[
                            (0, "Debug"),
                            (1, "Info"),
                            (2, "Warning"),
                            (3, "Error"),
                            (4, "Critical"),
                        ],
                        default=0,
                    ),
                ),
                ("country", models.CharField(default="GB", max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name="SecurityCredential",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("bink_private_key", "Bink private key"),
                            ("bink_public_key", "Bink public key"),
                            ("merchant_public_key", "Merchant public key"),
                            ("compound_key", "Compound key"),
                        ],
                        max_length=32,
                    ),
                ),
                ("storage_key", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="SecurityService",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "request_type",
                    models.CharField(
                        choices=[("INBOUND", "Inbound"), ("OUTBOUND", "Outbound")],
                        max_length=16,
                    ),
                ),
                (
                    "type",
                    models.IntegerField(
                        choices=[
                            (0, "RSA"),
                            (1, "Open Auth (No Authentication)"),
                            (2, "OAuth"),
                        ]
                    ),
                ),
                (
                    "configuration",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="config_service.Configuration",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="securitycredential",
            name="security_service",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="config_service.SecurityService",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="configuration",
            unique_together={("merchant_id", "handler_type")},
        ),
        migrations.AlterUniqueTogether(
            name="securityservice",
            unique_together={("request_type", "configuration")},
        ),
    ]
