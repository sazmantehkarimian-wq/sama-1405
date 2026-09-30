from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Count
from domains.properties.models import CommercialSpace,Region,Center,MotherProperty
from domains.registry.models import Discrepancy
from domains.identity.models import UserProfile
from queries.spaces import filter_spaces
from services.file_movement import current_holder
from reporting.engine import excel,docx,pdf
@login_required
def dashboard(request):
 context={'space_count':CommercialSpace.objects.count(),'active_count':CommercialSpace.objects.filter(status='ACTIVE').count(),'inactive_count':CommercialSpace.objects.filter(status='OUT_OF_CYCLE').count(),'property_count':MotherProperty.objects.count(),'discrepancy_count':Discrepancy.objects.exclude(status='RESOLVED').count()}
 return render(request,'ui/dashboard.html',context)
@login_required
def space_list(request):
 qs=filter_spaces(request.GET);page=Paginator(qs,25).get_page(request.GET.get('page'))
 return render(request,'ui/space_list.html',{'page':page,'regions':Region.objects.all(),'centers':Center.objects.filter(is_special=True),'total':qs.count()})
@login_required
def space_detail(request,code):
 s=get_object_or_404(CommercialSpace.objects.select_related('region','center').prefetch_related('status_history','contracts','beneficiary_assignments__beneficiary','appraisals','auctions','utilities','timeline','alerts','file_movements','property_links__mother_property'),code=code)
 return render(request,'ui/space_detail.html',{'space':s,'holder':current_holder(s)})
def _query(request): return filter_spaces(request.GET)[:5000]
@login_required
def spaces_excel(request):return HttpResponse(excel(_query(request),request.GET.getlist('blank')),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={'Content-Disposition':'attachment; filename="spaces.xlsx"'})
@login_required
def spaces_docx(request):return HttpResponse(docx(_query(request),request.GET.getlist('blank')),content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',headers={'Content-Disposition':'attachment; filename="spaces.docx"'})
@login_required
def spaces_pdf(request):return HttpResponse(pdf(_query(request)),content_type='application/pdf',headers={'Content-Disposition':'attachment; filename="spaces.pdf"'})
@login_required
@user_passes_test(lambda u:u.is_staff)
def user_list(request):
 from django.contrib.auth import get_user_model
 return render(request,'ui/user_list.html',{'users':get_user_model().objects.select_related('profile')})
@login_required
def password_change(request):
 form=PasswordChangeForm(request.user,request.POST or None)
 if request.method=='POST' and form.is_valid():
  user=form.save(); UserProfile.objects.update_or_create(user=user,defaults={'must_change_password':False,'display_name':user.get_full_name() or user.username});update_session_auth_hash(request,user);return redirect('dashboard')
 return render(request,'ui/password_change.html',{'form':form})
