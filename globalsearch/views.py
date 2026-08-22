from django.http import JsonResponse

from django.db.models import Q

from products.models import Product
from customers.models import Customer
from suppliers.models import Supplier
from billing.models import Bill


def global_search(request):

    query = request.GET.get(
        "q",
        ""
    ).strip()

    data = []

    if query:

        # ---------------- Products ----------------

        products = Product.objects.filter(
            name__icontains=query
        )[:5]

        for p in products:

            data.append({

                "type": "Product",

                "title": p.name,

                "subtitle": f"Stock : {p.quantity}",

                "url": f"/products/"

            })

        # ---------------- Customers ----------------

        customers = Customer.objects.filter(

            name__icontains=query

        )[:5]

        for c in customers:

            data.append({

                "type": "Customer",

                "title": c.name,

                "subtitle": c.mobile,

                "url": f"/customers/ledger/{c.id}/"
            })

        # ---------------- Suppliers ----------------

        suppliers = Supplier.objects.filter(

            name__icontains=query

        )[:5]

        for s in suppliers:

            data.append({

                "type": "Supplier",

                "title": s.name,

                "subtitle": s.mobile,

                "url": f"/suppliers/ledger/{s.id}/"

            })

        # ---------------- Bills ----------------

        bills = Bill.objects.filter(

            invoice_no__icontains=query

        )[:5]

        for b in bills:

            data.append({

                "type": "Invoice",

                "title": b.invoice_no,

                "subtitle": f"₹{b.final_amount}",

                "url": f"/billing/invoice/{b.id}/"

            })

    return JsonResponse(data, safe=False)