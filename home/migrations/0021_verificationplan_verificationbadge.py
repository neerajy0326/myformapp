# Generated by Django 4.2.3 on 2023-08-12 18:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0020_delete_wallet'),
    ]

    operations = [
        migrations.CreateModel(
            name='VerificationPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('duration_days', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='VerificationBadge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verified', models.BooleanField(default=False)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.verificationplan')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='verification_badge', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
