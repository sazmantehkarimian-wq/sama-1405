from pathlib import Path
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
class ForcePasswordChangeMiddleware:
 def __init__(self,get_response): self.get_response=get_response
 def __call__(self,request):
  allowed={reverse('login'),reverse('logout'),reverse('password-change')}
  if request.user.is_authenticated and getattr(request.user,'profile',None) and request.user.profile.must_change_password and request.path not in allowed and not request.path.startswith('/static/'):
   return redirect('password-change')
  return self.get_response(request)
class AuditRequestMiddleware:
 def __init__(self,get_response): self.get_response=get_response
 def __call__(self,request): return self.get_response(request)

class MaintenanceWriteLockMiddleware:
 """Reject writes while an offline restore owns the filesystem lock."""
 def __init__(self,get_response):
  self.get_response=get_response
  self.lock_file=Path(settings.DATABASES['default']['NAME']).parent/'.maintenance-lock'
 def __call__(self,request):
  if request.method not in {'GET','HEAD','OPTIONS'} and self.lock_file.exists():
   return JsonResponse({'detail':'سامانه برای بازیابی پشتیبان موقتاً در حالت فقط خواندنی است.'},status=503)
  return self.get_response(request)
