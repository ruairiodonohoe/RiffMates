from django.core.mail import send_mail
from django.shortcuts import render, redirect

from content.forms import CommentForm

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
