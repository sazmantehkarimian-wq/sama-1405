import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies=[
        ('operations','0014_commission_frozen_core'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations=[
        migrations.CreateModel(
            name='AuctionInstruction',
            fields=[
                ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
                ('source',models.CharField(choices=[('COMMISSION','کمیسیون'),('MANAGER','مدیر'),('AUTHORIZED_MANUAL','ورود دستی مجاز')],max_length=30)),
                ('direction',models.CharField(choices=[('INCLUDE','ورود'),('EXCLUDE','عدم ورود')],max_length=20)),
                ('reason',models.TextField()),('reference',models.CharField(max_length=255)),
                ('effective_from',models.CharField(max_length=10)),('effective_to',models.CharField(blank=True,max_length=10)),
                ('active',models.BooleanField(default=True)),('created_at',models.DateTimeField(auto_now_add=True)),
                ('commission_decision',models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='auction_instructions',to='operations.commissiondecision')),
                ('created_by',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='created_auction_instructions',to=settings.AUTH_USER_MODEL)),
                ('space',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='auction_instructions',to='properties.commercialspace')),
            ],
            options={'ordering':['-effective_from','-id']},
        ),
    ]
