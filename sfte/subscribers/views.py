from utils.views import render_to
from django.shortcuts import redirect

from forms import SubscriberForm


@render_to('subscr_user.html')
def subscribe(request):
    if request.method == "POST":
        form = SubscriberForm(request.POST)
        if form.is_valid() and form.clean_email():
            form.save()
            return redirect("/")
        return {'user_form': form}
    return {'user_form': SubscriberForm()}
