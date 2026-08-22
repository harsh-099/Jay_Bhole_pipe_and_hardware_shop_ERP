from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from accounts.decorators import allowed_roles
from .models import Expense


@allowed_roles(["Admin", "Manager", "Accountant",])
def expense_list(request):

    search = request.GET.get("search")

    expenses = Expense.objects.all().order_by("-id")

    if search:

        expenses = expenses.filter(
            category__icontains=search
        )

    paginator = Paginator(
        expenses,
        10
    )

    page = request.GET.get("page")

    expenses = paginator.get_page(page)

    context = {

        "expenses": expenses,

        "search": search,

        "total_expense": Expense.objects.count()

    }

    return render(

        request,

        "expenses/list.html",

        context

    )


@allowed_roles(["Admin", "Manager", "Accountant",])
def add_expense(request):

    if request.method == "POST":

        Expense.objects.create(

            category=request.POST.get(
                "category"
            ),

            amount=request.POST.get(
                "amount"
            ),

            description=request.POST.get(
                "description"
            )

        )

        return redirect(
            "expense_list"
        )

    return render(
        request,
        "expenses/add.html"
    )