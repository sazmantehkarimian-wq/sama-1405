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
