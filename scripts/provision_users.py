import os,secrets,string
os.environ.setdefault('DJANGO_SETTINGS_MODULE','sama.settings')
import django;django.setup()
from django.contrib.auth import get_user_model
from domains.identity.models import UserProfile
USERS=[('aghorbani','اکبر','قربانی'),('amajidi','اکبر','مجیدی'),('mabdollahi','مجید','عبدالهی'),('zmohammadi','زهره','محمدی'),('mkarimian','سید محمد','کریمیان'),('admin','مدیر','سامانه')]
chars=string.ascii_letters+string.digits+'!@#$%'
for username,first,last in USERS:
 password=''.join(secrets.choice(chars) for _ in range(18));u,created=get_user_model().objects.get_or_create(username=username,defaults={'first_name':first,'last_name':last,'is_staff':username=='admin','is_superuser':username=='admin'})
 if created:u.set_password(password);u.save();UserProfile.objects.create(user=u,display_name=f'{first} {last}',must_change_password=True);print(f'{username}: {password}')
