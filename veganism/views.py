from django.shortcuts import render


# View to display animal rights index page
def veganism_index(request):

    return render(request, 'veganism.html')
