from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Task, Bid


def home(request):
    tasks = Task.objects.filter(status='Open').order_by('-created_at')

    return render(request, 'tasks/home.html', {
        'tasks': tasks
    })
def register_view(request):

    if request.method == 'POST':

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            return render(request, 'tasks/register.html', {
                'error': 'Username already exists'
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        return redirect('home')

    return render(request, 'tasks/register.html')
def login_view(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('home')

        return render(request, 'tasks/login.html', {
            'error': 'Invalid username or password'
        })

    return render(request, 'tasks/login.html')
# Create your views here.

def logout_view(request):

    logout(request)

    return redirect('home')
@login_required
def create_task(request):

    if request.method == 'POST':

        title = request.POST['title']
        description = request.POST['description']
        category = request.POST['category']
        budget = request.POST['budget']

        Task.objects.create(
            title=title,
            description=description,
            category=category,
            budget=budget,
            created_by=request.user
        )

        return redirect('home')

    return render(request, 'tasks/create_task.html')

def task_detail(request, task_id):

    task = get_object_or_404(Task, id=task_id)

    return render(request, 'tasks/task_detail.html', {
        'task': task
    })
@login_required
def place_bid(request, task_id):

    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':

        amount = request.POST['amount']
        message = request.POST['message']

        Bid.objects.create(
            task=task,
            freelancer=request.user,
            amount=amount,
            message=message
        )

        return redirect(
            'task_detail',
            task_id=task.id
        )

    return render(request, 'tasks/place_bid.html', {
        'task': task
    })
@login_required
def task_bids(request, task_id):

    task = get_object_or_404(Task, id=task_id)

    if task.created_by != request.user:
        return redirect('home')

    bids = task.bids.all()

    return render(request, 'tasks/task_bids.html', {
        'task': task,
        'bids': bids
    })
@login_required
def choose_winner(request, bid_id):

    bid = get_object_or_404(Bid, id=bid_id)

    task = bid.task

    if task.created_by != request.user:
        return redirect('home')

    task.status = 'Assigned'
    task.save()

    return redirect(
        'task_bids',
        task_id=task.id
  )
