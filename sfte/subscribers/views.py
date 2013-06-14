from utils.views import render_to
from django.shortcuts import redirect
from forms import SubscrubierForm


@render_to('subscribe.html')
def subscribe(request):
    if request.method == "POST":
        form = SubscrubierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
        return {'form': form}
    return {'form': SubscrubierForm()}
