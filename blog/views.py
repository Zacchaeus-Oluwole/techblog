from django.shortcuts import render, get_object_or_404
from . models import Post, Comment

from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.postgres.search import SearchVector,SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity

from . forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail

from taggit.models import Tag
from django.db.models import Count

class PostListView(ListView):
     queryset = Post.published.all()
     context_object_name = 'posts'
     paginate_by = 3
     template_name = 'blog/post/list.html'

# Create your views here.

#def base(request):
    #return render(request,'base.html')

def post_list(request, tag_slug=None):
    #posts = Post.published.all()
    object_list = Post.published.all()
    common_tag = Post.tags.most_common()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3) # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
    # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)

    context={'page':page,'posts': posts, 'common_tag': common_tag, 'tag':tag}

    return render(request,'blog/post/list.html', context )

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
    status='published',
    publish__year=year,
    publish__month=month,
    publish__day=day)

    # List of active comments for this post
    comments = post.comments.filter(active=True)
    new_comment = None
    comment_form = CommentForm()
    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
        else:
            comment_form = CommentForm()

    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:5]

    context = {'post': post,'comments': comments,
                'new_comment': new_comment,'comment_form': comment_form,
                'similar_posts': similar_posts,}

    return render(request,'blog/post/detail.html', context )


def post_share(request, post_id):
    #Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method =='POST':
        #Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            #Form field passed validation
            cd = form.cleaned_data
            # ...send email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" f"{cd['name']} 's comments: {cd['comments']}"
            send_mail(subject, message, 'zacchaeusoluwole@gmail.com',[cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    context = {'post': post, 'form':form,'sent': sent}

    return render(request, 'blog/post/share.html', context )

def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)

            results = Post.published.annotate(
                similarity=TrigramSimilarity('title', query),
                ).filter(similarity__gt=0.1).order_by('-similarity')

    context = {'form':form, 'query':query, 'results':results}

    return render(request, 'blog/post/search.html',context )

#def post_home(request):
    #return render(request,'blog/post/home.html')


def notifications(request):
    return render(request,'blog/post/notifications.html')

def post_about_us(request):
    return render(request,'blog/post/about_us.html')


def tagged (request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    #Filter posts by tag name
    posts = Post.objects.filter(tags=tag)

    context = {
        'tag': tag,
        'posts': posts,
    }
    return render(request, 'list.html', context)