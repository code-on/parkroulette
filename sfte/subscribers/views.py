from utils.views import render_to
from django.shortcuts import redirect

from forms import SubscrubierForm


@render_to('subscr_user.html')
def subscribe(request):
    if request.method == "POST":
        form = SubscrubierForm(request.POST)
        if form.is_valid() and form.clean_email():
            form.save()
            return redirect("/")
        return {'user_form': form}
    return {'user_form': SubscrubierForm()}
