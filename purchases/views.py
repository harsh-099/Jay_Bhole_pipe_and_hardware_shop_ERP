from decimal import Decimal
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from reportlab.lib.units import inch
from .models import Purchase, PurchaseItem
from suppliers.models import Supplier, SupplierLedger
from products.models import Product
from inventory.models import StockLedger
from decimal import Decimal
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from shopsettings.models import ShopSettings
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader
import os
from django.conf import settings
from xhtml2pdf import pisa
from django.shortcuts import get_object_or_404
from accounts.decorators import allowed_roles

@allowed_roles(["Admin", "Manager", "Accountant", ])
def add_purchase(request):

    suppliers = Supplier.objects.all().order_by("name")

    products = Product.objects.all().order_by("name")

    cart = request.session.get("purchase_cart", [])

    context = {

        "suppliers": suppliers,

        "products": products,

        "cart": cart,

    }

    return render(

        request,

        "purchases/add.html",

        context

    )

@allowed_roles(["Admin", "Manager", "Accountant", ])
def add_purchase_item(request, id):

    product = Product.objects.get(id=id)

    cart = request.session.get("purchase_cart", [])

    found = False

    for item in cart:

        if item["id"] == product.id:

            item["quantity"] += 1

            found = True

            break

    if not found:

        cart.append({

            "id": product.id,

            "name": product.name,

            "price": float(product.purchase_price),

            "quantity": 1,

        })

    request.session["purchase_cart"] = cart

    return redirect("add_purchase")

@allowed_roles(["Admin", "Manager", "Accountant", ])
def remove_purchase_item(request, id):

    cart = request.session.get("purchase_cart", [])

    cart = [

        item

        for item in cart

        if item["id"] != id

    ]

    request.session["purchase_cart"] = cart

    return redirect("add_purchase")


@allowed_roles(["Admin", "Manager", "Accountant"])
def save_purchase(request):

    if request.method != "POST":
        return redirect("add_purchase")

    cart = request.session.get("purchase_cart", [])

    if not cart:
        return redirect("add_purchase")

    supplier = Supplier.objects.get(
        id=request.POST.get("supplier")
    )

    payment_method = request.POST.get("payment_method")

    paid_amount = Decimal(
        request.POST.get(
            "paid_amount",
            "0"
        )
    )

    last = (
        Purchase.objects
        .exclude(purchase_no="")
        .exclude(purchase_no__isnull=True)
        .order_by("-id")
        .first()
    )

    if last:
        no = int(last.purchase_no.replace("PUR", "")) + 1
    else:
        no = 1

    purchase = Purchase.objects.create(
        purchase_no=f"PUR{no:04d}",
        supplier=supplier,
        payment_method=payment_method,
        paid_amount=0,
        balance_amount=0,
        total_amount=0,
        final_amount=0,
    )

    grand_total = Decimal("0.00")

    for item in cart:

        product = Product.objects.get(
            id=item["id"]
        )

        qty = item["quantity"]

        price = Decimal(
            str(product.purchase_price)
        )

        total = qty * price

        PurchaseItem.objects.create(
            purchase=purchase,
            product=product,
            quantity=qty,
            price=price,
            total=total,
        )

        product.quantity += qty
        product.save()

        StockLedger.objects.create(
            product=product,
            transaction_type="IN",
            quantity=qty,
            remarks=f"Purchase {purchase.purchase_no}"
        )

        grand_total += total

    if payment_method != "Credit":
        paid_amount = grand_total

    purchase.total_amount = grand_total
    purchase.final_amount = grand_total
    purchase.paid_amount = paid_amount
    purchase.balance_amount = grand_total - paid_amount

    purchase.save()

    # =====================================
    # SUPPLIER LEDGER UPDATE
    # =====================================

    last_ledger = (
        SupplierLedger.objects
        .filter(supplier=supplier)
        .order_by("-id")
        .first()
    )

    balance = (
        last_ledger.balance
        if last_ledger
        else Decimal("0.00")
    )

    # Purchase Entry
    balance += grand_total

    SupplierLedger.objects.create(
        supplier=supplier,
        particular="Purchase",
        debit=grand_total,
        credit=Decimal("0.00"),
        balance=balance,
        remarks=f"Purchase {purchase.purchase_no}"
    )

    # Payment Entry
    if paid_amount > 0:

        balance -= paid_amount

        SupplierLedger.objects.create(
            supplier=supplier,
            particular="Payment",
            debit=Decimal("0.00"),
            credit=paid_amount,
            balance=balance,
            remarks=f"Payment Against {purchase.purchase_no}"
        )

    supplier.balance = balance
    supplier.ledger_balance = balance
    supplier.save()

    request.session["purchase_cart"] = []

    return redirect(
        "purchase_details",
        purchase.id
    )


@allowed_roles(["Admin", "Manager", "Accountant", ])
def purchase_details(request, id):

    purchase = Purchase.objects.get(id=id)

    items = PurchaseItem.objects.filter(
        purchase=purchase
    )

    shop = ShopSettings.objects.first()

    return render(

        request,

        "purchases/details.html",

        {

            "purchase": purchase,

            "items": items,

            "shop": shop,

        }

    )

@allowed_roles(["Admin", "Manager", "Accountant", ])
def print_purchase(request, id):

    purchase = get_object_or_404(
        Purchase,
        id=id
    )

    items = PurchaseItem.objects.filter(
        purchase=purchase
    )

    shop = ShopSettings.objects.first()

    template = get_template(
        "purchases/purchase_pdf.html"
    )

    html = template.render({

        "purchase": purchase,

        "items": items,

        "shop": shop,

    })

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (

        f'inline; filename="{purchase.purchase_no}.pdf"'

    )

    pisa.CreatePDF(

        html,

        dest=response

    )

    return response


@allowed_roles(["Admin", "Manager", "Accountant"])
def update_quantity(request, id):

    if request.method == "POST":

        qty = int(request.POST.get("quantity", 1))

        cart = request.session.get("po_cart", [])

        for item in cart:

            if item["id"] == id:

                item["quantity"] = qty

                item["total"] = round(

                    item["price"] * qty,

                    2

                )

                break

        request.session["po_cart"] = cart

    return redirect("add_purchase_order")