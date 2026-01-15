# Generated manually to add missing fields

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('parking_monitor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='parkingstatus',
            name='total_spaces',
            field=models.IntegerField(default=15, help_text='Quota total de places', validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='parkingstatus',
            name='occupancy_rate',
            field=models.FloatField(default=0.0, help_text='Pourcentage d\'occupation'),
        ),
        migrations.AddField(
            model_name='parkingstatus',
            name='image_path',
            field=models.CharField(blank=True, help_text='Chemin de l\'image ESP32-CAM', max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='parkingstatus',
            name='source',
            field=models.CharField(choices=[('esp32', 'ESP32-CAM'), ('video', 'Vidéo temps réel'), ('api', 'API manuelle')], db_index=True, default='esp32', max_length=50),
        ),
    ]
