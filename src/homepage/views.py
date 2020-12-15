from django.shortcuts import render
from posts.models import AGPost


def show_homepage(request):

    # Get three latest posts to display on homepage.
    # If less than three posts exist, just display however
    # many exist.
    agp_count = AGPost.objects.all().count()
    if agp_count >= 3:
        newest_count = 3
    else:
        newest_count = agp_count
    latest_agposts = AGPost.objects.order_by('-date')[:newest_count]
    return render(request, 'index.html', {'latest_agposts': latest_agposts})


def show_policy(request):

    # Display AAAHHHghosts privacy policy
    return render(request, 'policy.html', {})