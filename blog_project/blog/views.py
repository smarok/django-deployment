from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import (TemplateView, ListView,
                                DetailView, CreateView,
                                 UpdateView, DeleteView)
from .forms import PostForm, CommentForm, UserForm
from .models import Comment, Post

# Create your views here.
class AboutView(TemplateView):
    template_name = 'about.html'

class PostListView(ListView):
    model = Post

    # We are creating a function s that we can return all Posts with datetime less than today and order them by newest
    # Go to django documentation /topics/db/queries and Field loopups topic for more info
    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')

class PostDetailView(DetailView):
    model = Post

# to make sure that only logged in users are able to create a post, we added a built in class LoginRequiredMixin
class CreatePostView(LoginRequiredMixin, CreateView):
    login_url = '/login/' # is person is not logged in, they will go here
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post
    #fields = ['title','text']
    # setting inital data to author field
    # def get_initial(self):
    #     return {'author':self.request.user}

    # this is how to set a value
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/login/' # is person is not logged in, they will go here
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy("post_list")

class DraftListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_list.html'
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('create_date')

@login_required
def add_comment_to_post(request,pk):
    post = get_object_or_404(Post,pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', pk=post.pk)

    else:
        form = CommentForm()
    return render(request, 'blog/comment_form.html',{'form':form})

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment,pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment,pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)

def register(request):

    registered = False

    if request.method == "POST":
        user_form = UserForm(data = request.POST)
        # profile_form = UserProfileInfoForm(data = request.POST)

        if user_form.is_valid():

             user = user_form.save()
             user.set_password(user.password)
             user.save()

             # profile = profile_form.save(commit=False)
             # profile.user = user
             #
             # if 'profile_pic' in request.FILES:
             #     profile.profile_pic = request.FILES['profile_pic']
             # profile.save()

             registered = True

        else:
            print(user_form.errors)

    else:
        user_form = UserForm()
        # profile_form = UserProfileInfoForm()

    return render(request,'registration/registration.html',
                        {'user_form':user_form,'registered':registered})
