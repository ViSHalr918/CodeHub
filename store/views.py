from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render,redirect

from django.views.generic import View,TemplateView,UpdateView,CreateView,DetailView,ListView,FormView

from store.forms import SignupForm,LoginForm,UserProfileForm,ProjectForm,ReviewForm

from store.models import UserProfile,Project,WishListItems,OrderSummary,Review

from django.contrib import messages

# from decouple import config
import decouple

from django.urls import reverse,reverse_lazy


from django.contrib.auth import authenticate,login,logout


KEY_ID = decouple.config('KEY_ID')

KEY_SECRET = decouple.config('KEY_SECRET')


# Create your views here.

class SignupView(View):
    def get(self,request,*args,**kwargs):
        form_instance = SignupForm()
        return render(request,"store/signup.html",{"form":form_instance})
    
    def post(self,request,*args,**kwargs):
        form_instance = SignupForm(request.POST)
        if form_instance.is_valid():
            form_instance.save()
            print("registration success")
            messages.success(request,"Registration Success")
            return redirect("login")
        else:
            print("registration unsuccessful")
            messages.error(request,"Registration Failed")
            return render(request,"store/signup.html",{"form":form_instance})
        


class LoginView(View):
    def get(self,request,*args,**kwargs):

        form_instance=LoginForm()

        return render(request,"store/login.html",{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        form_instance = LoginForm(request.POST)

        if form_instance.is_valid():

            data=form_instance.cleaned_data

            user_obj=authenticate(request,**data)

            if user_obj:

                login(request,user_obj)

                print('login success')

                return redirect("index")
            
        print("login unsuccessful")          
        return render(request,"store/login.html",{"form":form_instance})
        

class IndexView(View):
    template_name = "store/index.html"

    def get(self,request,*args,**kwargs):
        qs = Project.objects.all().exclude(owner=request.user)

        return render(request,self.template_name,{"projects":qs})

class UserprofileUpdateView(UpdateView):

    model = UserProfile

    form_class = UserProfileForm

    template_name = "store/profile_edit.html"

    # success_url = reverse_lazy("index.html")
    def get_success_url(self) -> str:
        return reverse("index")
    
# class ProjectSellView(View):
#     def get(self,request,*args,**kwargs):
#         form_instance=ProjectForm()
#         return render(request,"store/project.html",{"form":form_instance})
    
#     def post(self,request,*args,**kwargs):
#         form_instance  = ProjectForm(request.POST)
#         if form_instance.is_valid():
#             form_instance.instance.owner=request.user
#             form_instance.save()
#             return render("index")
#         else:
#             return render(request,"store/project.html",{"form":form_instance})

class ProjectSellView(CreateView):
    model = Project

    form_class = ProjectForm

    template_name = "store/project.html"

    success_url =reverse_lazy("index")

    def form_valid(self, form):
        form.instance.owner=self.request.user
        return super().form_valid(form)


class ProjectListView(View):
    def get(self,request,*args,**kwargs):
        qs = Project.objects.filter(owner=request.user)
        return render(request,"store/project_list.html",{"works":qs})

class ProjectDeleteView(View):
    def get(self,request,*args,**kwargs):

        id = kwargs.get("pk")
        Project.objects.get(id=id).delete()
        return redirect("myworks")
            

class ProjectDetailView(DetailView):

    model = Project
    template_name = "store/project_detail.html"

    context_object_name = 'project'

class AddtoWishlist(View):
    def get(self,request,*args,**kwargs):
        id = kwargs.get("pk")
        project_obj = Project.objects.get(id=id)
        WishListItems.objects.create(
           wishlist_object = request.user.basket,
           project_object = project_obj
        )
        print("item has been added to wishlist")
        return redirect("index")


from django.db.models import Sum
class MyCartView(View):
    def get(self,request,*args,**kwargs):
        qs=request.user.basket.basket_items.filter(is_order_placed=False)
        total = request.user.basket.wishlist_total
        return render(request,"store/wishlist_summary.html",{"cartitems":qs,"total":total})


class WishListItemRemoveview(View):
    def get(self,request,*args,**kwargs):
        id = kwargs.get("pk")
        WishListItems.objects.get(id=id).delete()
        return redirect("cart-summary")
    
import razorpay
class CheckOutView(View):
    def get(self,request,*args,**kwargs):
        client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))
        amount = request.user.basket.wishlist_total*100
        data = { "amount": amount, "currency": "INR", "receipt": "order_rcptid_11" }
        payment = client.order.create(data=data)

        # create order object
        cart_items = request.user.basket.basket_items.filter(is_order_placed=False)
        order_summary_obj=OrderSummary.objects.create(
            user_object=request.user,
            order_id=payment.get("id")

        )
        # order_summary_obj.project_objects.add(cart_items.values("project_object__id"))

        for p in cart_items.values('project_object'):
            order_summary_obj.project_objects.add(p.get('id'))

        for ci in cart_items:
            ci.is_order_placed=True
            ci.save()
        order_summary_obj.save()

        


        print(payment)

        context={
            "key":KEY_ID,
            "amount":payment.get("amount"),
            "currency":payment.get("currency"),
            "order_id":payment.get("id")
        }
        return render(request,"store/payment.html",context)
    
from django.views.decorators.csrf import csrf_exempt

from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt,name='dispatch')
class PaymentVerificationView(View):
    def post(self,request,*args,**kwargs):
        print(request.POST)
        client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))
        order_summary_object=OrderSummary.objects.get(order_id=request.POST.get("razorpay_order_id"))
        login(request,order_summary_object.user_object)
        try: 
            # doubtful code
            client.utility.verify_payment_signature(request.POST)
            print("payment success")
            order_id = request.POST.get("razorpay_order_id")
            OrderSummary.objects.filter(order_id=order_id).update(is_paid=True)
        except:
            # handling code
            print("payment fail")


        return redirect("index")


class MyPurchaseView(View):
    model = OrderSummary
    context_object_name="orders"
    def get(self,request,*args,**kwargs):
        qs = OrderSummary.objects.filter(user_object=request.user,is_paid=True)
        return render(request,"store/ordersummary.html",{"orders":qs})



# url/localhost/8000/project/<int:pk>/review/add
class ReviewCreateView(FormView):
    template_name = 'store/review.html'
    form_class = ReviewForm

    def post(self,request,*args,**kwargs):

        id=kwargs.get('pk')

        project_object=Project.objects.get(id=id)
        
        form_instance = ReviewForm(request.POST)

        if form_instance.is_valid():

            form_instance.instance.user_object=(request.user)

            form_instance.instance.project_object__id=project_object

            form_instance.save()

            return redirect("index")
        
        else:
            
            return render(request,self.template_name,{"form":form_instance})