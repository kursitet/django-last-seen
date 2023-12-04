import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LastSeen',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('module', models.CharField(default=b'default', max_length=20)),
                ('last_seen', models.DateTimeField(default=django.utils.timezone.now)),
                ('site', models.ForeignKey(to='sites.Site', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('-last_seen',),
            },
        ),
        migrations.AlterUniqueTogether(
            name='lastseen',
            unique_together=set([('user', 'site', 'module')]),
        ),
    ]
