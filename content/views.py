import urllib
from time import sleep
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404

from content.forms import CommentForm, SeekingAdForm
from content.models import MusicianBandChoice, SeekingAd
from bands.views import _get_items_per_page, _get_page_num

# Create your views here.


def comment(request):
    if request.method == "GET":
        form = CommentForm()

    else:
        form = CommentForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            name = cd["name"]
            comment = cd["comment"]

            message = f"""\
                Received comment from {name}\n\n
            """

            send_mail(
                "Received comment",
                message,
                "admin@example.com",
                ["admin@example.com"],
                fail_silently=False,
            )

            return redirect("comment_accepted")

    data = {"form": form}

    return render(request, "comment.html", data)


def comment_accepted(request):
    data = {
        "content": """
                <h1>Comment Accepted</h1>

                <p>Thanks for submitting a comment to <i>RiffMates</i></p>
        """
    }

    return render(request, "general.html", data)


def list_ads(request):
    data = {
        "seeking_musician": SeekingAd.objects.filter(
            seeking=MusicianBandChoice.MUSICIAN
        ),
        "seeking_band": SeekingAd.objects.filter(seeking=MusicianBandChoice.BAND),
    }

    return render(request, "list_ads.html", data)


@login_required
def seeking_ad(request, ad_id=0):
    ad = None

    if ad_id != 0:
        ad = get_object_or_404(SeekingAd, id=ad_id)
        can_edit = (
            request.user.is_staff
            or request.user.is_superuser
            or ad.owner == request.user
        )
        if not can_edit:
            return redirect("list_ads")

    if request.method == "POST":
        form = SeekingAdForm(request.POST, instance=ad, user=request.user)
        if form.is_valid():
            ad = form.save(commit=False)
            if ad_id == 0:
                ad.owner = request.user
            ad.save()
            return redirect("list_ads")

    else:
        form = SeekingAdForm(instance=ad, user=request.user)

    data = {"form": form}

    return render(request, "seeking_ad.html", data)


def search_ads(request):
    search_text = request.GET.get("search_text", "")
    search_text = urllib.parse.unquote(search_text)
    search_text = search_text.strip()

    ads = []

    if search_text:
        parts = search_text.split()

        q = (
            Q(date__istartswith=parts[0])
            | Q(owner__username__istartswith=parts[0])
            | Q(seeking__istartswith=parts[0])
            | Q(musician__first_name__istartswith=parts[0])
            | Q(musician__last_name__istartswith=parts[0])
            | Q(band__name__istartswith=parts[0])
            | Q(content__icontains=parts[0])
        )

        # Add the rest of the parts
        for part in parts[1:]:
            q |= (
                Q(date__istartswith=part)
                | Q(owner__username__istartswith=part)
                | Q(seeking__istartswith=part)
                | Q(musician__first_name__istartswith=part)
                | Q(musician__last_name__istartswith=part)
                | Q(band__name__istartswith=part)
                | Q(content__icontains=part)
            )

        ads = SeekingAd.objects.filter(q)

    items_per_page = _get_items_per_page(request)
    paginator = Paginator(ads, items_per_page)
    page_num = _get_page_num(request, paginator)
    page = paginator.page(page_num)

    data = {
        "search_text": search_text,
        "ads": page.object_list,
        "has_more": page.has_next(),
        "next_page": page_num + 1,
    }

    if request.htmx:
        if page_num > 1:
            sleep(2)
        return render(request, "partials/ad_results.html", data)

    return render(request, "search_ads.html", data)


# date, owner, seeking, musician, band, content
