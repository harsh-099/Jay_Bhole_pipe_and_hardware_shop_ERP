from django.shortcuts import render
from django.core.paginator import Paginator
from .models import StockLedger
from accounts.decorators import allowed_roles

@allowed_roles(["Admin", "Manager", "Accountant", ])
def stock_ledger(request):

    search = request.GET.get("search")

    entries = StockLedger.objects.select_related(
        "product"
    ).order_by("-id")

    if search:

        entries = entries.filter(
            product__name__icontains=search
        )

    paginator = Paginator(
        entries,
        10
    )

    page = request.GET.get("page")

    entries = paginator.get_page(page)

    total_entries = StockLedger.objects.count()

    in_stock = StockLedger.objects.filter(
        transaction_type="IN"
    ).count()

    out_stock = StockLedger.objects.filter(
        transaction_type="OUT"
    ).count()

    context = {

        "entries": entries,

        "search": search,

        "total_entries": total_entries,

        "in_stock": in_stock,

        "out_stock": out_stock

    }

    return render(

        request,

        "inventory/ledger.html",

        context

    )