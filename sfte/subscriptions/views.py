from utils.views import render_to
from django.shortcuts import redirect
from forms import CitySubscriptionForm


@render_to('subscr_city.html')
def create(request):
    if request.method == "POST":
        form = CitySubscriptionForm(request.POST)
        if form.is_valid() and form.not_exists():
            form.save()
            return redirect("/")
        return {'city_form': form}
    return {'city_form': CitySubscriptionForm()}
