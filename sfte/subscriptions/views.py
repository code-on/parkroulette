from utils.views import render_to
from django.shortcuts import redirect
from forms import CitySubscriptionForm


@render_to('subscr_city.html')
def create(request):
    if request.method == "POST":
        form = CitySubscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
        return {'form': form}
    return {'form': CitySubscriptionForm()}
