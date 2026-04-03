from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incidents', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profilutilisateur',
            name='derniere_activite',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
