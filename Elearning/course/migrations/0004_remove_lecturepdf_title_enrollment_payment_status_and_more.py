# Generated by Django 5.1.3 on 2024-11-14 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0003_alter_morelecturepdf_pdf_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lecturepdf',
            name='title',
        ),
        migrations.AddField(
            model_name='enrollment',
            name='payment_status',
            field=models.CharField(default='Pending', max_length=20),
        ),
        migrations.DeleteModel(
            name='MoreLecturePDF',
        ),
    ]