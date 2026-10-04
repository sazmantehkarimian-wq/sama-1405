from pathlib import Path
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from django.core.cache import cache
from django.core.exceptions import ValidationError
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

class LoginThrottleMiddleware:
 """Small LAN-safe defensive throttle without storing credentials or request bodies."""
 limit=5
 window=300
 def __init__(self,get_response): self.get_response=get_response
 def __call__(self,request):
  if request.path==reverse('login') and request.method=='POST':
   username=request.POST.get('username','').strip().lower()
   address=request.META.get('REMOTE_ADDR','unknown')
   key=f"login-fail:{address}:{username}"
   failures=cache.get(key,0)
   if failures>=self.limit:
    return render(request,'ui/error_status.html',{'status_code':429,'title':'تلاش بیش از حد','message':'تلاش‌های ناموفق بیش از حد مجاز است؛ پنج دقیقه بعد دوباره تلاش کنید.'},status=429)
   response=self.get_response(request)
   if response.status_code==200:
    cache.set(key,failures+1,self.window)
   else:
    cache.delete(key)
   return response
  return self.get_response(request)


class MaintenanceWriteLockMiddleware:
 """Reject writes while an offline restore owns the filesystem lock."""
 def __init__(self,get_response):
  self.get_response=get_response
  self.lock_file=Path(settings.DATABASES['default']['NAME']).parent/'.maintenance-lock'
 def __call__(self,request):
  if request.method not in {'GET','HEAD','OPTIONS'} and self.lock_file.exists():
   return render(request,'ui/error_status.html',{'status_code':503,'title':'سامانه موقتاً فقط‌خواندنی است','message':'سامانه برای بازیابی پشتیبان موقتاً در حالت فقط‌خواندنی است. چند دقیقه بعد دوباره تلاش کنید.'},status=503)
  return self.get_response(request)


class DocumentIntegrityMiddleware:
 """Fail closed before serving a stored document whose size/hash no longer matches metadata."""
 def __init__(self,get_response): self.get_response=get_response
 def __call__(self,request): return self.get_response(request)
 def process_view(self,request,view_func,view_args,view_kwargs):
  resolver=getattr(request,'resolver_match',None)
  if not resolver or resolver.url_name!='document-download' or not getattr(request,'user',None) or not request.user.is_authenticated:
   return None
  from domains.documents.models import Document
  from services.documents import open_verified_document
  document=Document.objects.filter(pk=view_kwargs.get('document_id')).first()
  if not document:return None
  try:
   handle=open_verified_document(document)
  except ValidationError as exc:
   return render(request,'ui/error_status.html',{'status_code':409,'title':'سند قابل ارائه نیست','message':' '.join(exc.messages)},status=409)
  handle.close()
  return None
