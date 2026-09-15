from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from .models import Quotation, QuotationItem
from products.models import Product
from customers.models import Customer
from django.utils import timezone
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from shopsettings.models import ShopSettings
from billing.models import Bill, BillItem
from inventory.models import StockLedger
from accounts.decorators import allowed_roles

@allowed_roles(["Admin","Manager","Cashier"])
def quotation_list(request):

    quotations = Quotation.objects.order_by("-id")

    return render(

        request,

        "quotation/list.html",

        {

            "quotations": quotations

        }

    )


@allowed_roles(["Admin","Manager","Cashier"])
def add_quotation(request):

    products = Product.objects.all().order_by("name")

    customers = Customer.objects.all().order_by("name")

    cart = request.session.get(
        "quotation_cart",
        []
    )

    grand_total = Decimal("0.00")

    for item in cart:

        grand_total += Decimal(
            str(item["total"])
        )

    context = {

        "products": products,

        "customers": customers,

        "cart": cart,

        "grand_total": grand_total

    }

    return render(

        request,

        "quotation/quotation.html",

        context

    )

@allowed_roles(["Admin","Manager","Cashier"])
def add_to_quotation(request, product_id):

    product = Product.objects.get(
        id=product_id
    )

    cart = request.session.get(
        "quotation_cart",
        []
    )

    found = False

    for item in cart:

        if item["id"] == product.id:

            item["quantity"] += 1

            item["total"] = float(item["price"]) * item["quantity"]

            found = True

            break

    if not found:

        cart.append({

            "id": product.id,

            "name": product.name,

            "price": float(product.selling_price),

            "quantity": 1,

            "total": float(product.selling_price)

        })

    request.session["quotation_cart"] = cart

    return redirect("add_quotation")


@allowed_roles(["Admin","Manager","Cashier"])
def increase_qty(request, product_id):

    cart = request.session.get(
        "quotation_cart",
        []
    )

    for item in cart:

        if item["id"] == product_id:

            item["quantity"] += 1

            item["total"] = item["price"] * item["quantity"]

            break

    request.session["quotation_cart"] = cart

    return redirect("add_quotation")

@allowed_roles(["Admin","Manager","Cashier"])
def decrease_qty(request, product_id):

    cart = request.session.get(
        "quotation_cart",
        []
    )

    for item in cart:

        if item["id"] == product_id:

            if item["quantity"] > 1:

                item["quantity"] -= 1

                item["total"] = item["price"] * item["quantity"]

            break

    request.session["quotation_cart"] = cart

    return redirect("add_quotation")

@allowed_roles(["Admin","Manager","Cashier"])
def remove_item(request, product_id):

    cart = request.session.get(
        "quotation_cart",
        []
    )

    cart = [

        item

        for item in cart

        if item["id"] != product_id

    ]

    request.session["quotation_cart"] = cart

    return redirect("add_quotation")



@allowed_roles(["Admin","Manager","Cashier"])

def save_quotation(request):

    if request.method != "POST":
        return redirect("add_quotation")

    cart = request.session.get("quotation_cart", [])

    if not cart:
        return redirect("add_quotation")

    # ----------------------------
    # Quotation No Generate
    # ----------------------------
    last = Quotation.objects.order_by("-id").first()

    if last:

        last_no = int(last.quotation_no.replace("EST", ""))
        quotation_no = f"EST{last_no + 1:04d}"

    else:

        quotation_no = "EST0001"

    # ----------------------------
    # Customer Logic
    # ----------------------------

    customer_id = request.POST.get("customer")
    customer_name = request.POST.get("customer_name")
    mobile = request.POST.get("mobile")
    address = request.POST.get("address")
    save_customer = request.POST.get("save_customer")

    customer = None

    if customer_id:

        customer = Customer.objects.get(id=customer_id)

    else:

        # runtime customer (temporary / quotation only)
        if customer_name:

            customer = Customer.objects.create(
                name=customer_name,
                mobile=mobile,
                address=address,
                credit_balance=0
            )

        else:

            customer = None

    # ----------------------------
    # Create Quotation
    # ----------------------------

    quotation = Quotation.objects.create(

        quotation_no=quotation_no,
        customer=customer,
        total_amount=Decimal("0.00"),
        created_at=timezone.now()

    )

    total = Decimal("0.00")

    # ----------------------------
    # Items Save
    # ----------------------------

    for item in cart:

        product = Product.objects.get(id=item["id"])

        qty = int(item["quantity"])
        price = Decimal(str(item["price"]))
        amount = qty * price

        QuotationItem.objects.create(

            quotation=quotation,
            product=product,
            quantity=qty,
            price=price,
            total=amount

        )

        total += amount

    # ----------------------------
    # Update total
    # ----------------------------

    quotation.total_amount = total
    quotation.save()

    # ----------------------------
    # Clear Cart
    # ----------------------------

    request.session["quotation_cart"] = []

    return redirect("quotation_list")

@allowed_roles(["Admin","Manager","Cashier"])
def quotation_detail(request, id):

    quotation = Quotation.objects.get(id=id)

    items = QuotationItem.objects.filter(
        quotation=quotation
    )

    return render(

        request,

        "quotation/detail.html",

        {

            "quotation": quotation,

            "items": items

        }

    )
@allowed_roles(["Admin", "Manager", "Cashier"])
def quotation_pdf(request, id):

    quotation = get_object_or_404(
        Quotation,
        id=id
    )

    items = QuotationItem.objects.filter(
        quotation=quotation
    )

    shop = ShopSettings.objects.first()

    context = {
        "quotation": quotation,
        "items": items,
        "shop": shop,
    }

    return render(
        request,
        "quotation/quotation_print.html",
        context
    )

@allowed_roles(["Admin","Manager","Cashier"])
def delete_quotation(request,id):

    quotation=Quotation.objects.get(id=id)

    quotation.delete()

    return redirect("quotation_list")


@allowed_roles(["Admin","Manager","Cashier"])

def convert_to_bill(request, id):

    quotation = Quotation.objects.get(id=id)

    if quotation.status == "Converted":

        return redirect("quotation_list")

    # ----------------------------
    # Invoice Number
    # ----------------------------

    last = Bill.objects.order_by("-id").first()

    if last:

        no = int(

            last.invoice_no.replace(
                "INV",
                ""
            )

        )

        invoice = f"INV{no+1:04d}"

    else:

        invoice = "INV0001"

    # ----------------------------
    # Bill Create
    # ----------------------------

    bill = Bill.objects.create(

        invoice_no=invoice,

        customer=quotation.customer,

        payment_method="Cash",

        total_amount=quotation.total_amount

    )

    # ----------------------------
    # Bill Items
    # ----------------------------

    items = QuotationItem.objects.filter(

        quotation=quotation

    )

    for item in items:

        BillItem.objects.create(

            bill=bill,

            product=item.product,

            quantity=item.quantity,

            price=item.price,

            total=item.total

        )

        # Stock Reduce

        product = item.product

        product.quantity -= item.quantity

        product.save()

        StockLedger.objects.create(

            product=product,

            transaction_type="OUT",

            quantity=item.quantity,

            remarks=f"Quotation {quotation.quotation_no}"

        )

    quotation.status = "Converted"

    quotation.save()

    return redirect(
        "invoice_detail",
        bill.id
    )