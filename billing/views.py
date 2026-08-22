from urllib import request
from requests import request
from activitylog.utils import log_activity
from django.shortcuts import render, redirect
from .models import Bill, BillItem
from products.models import Product
from customers.models import Customer
from django.http import HttpResponse
from decimal import Decimal
from shopsettings.models import ShopSettings
from reportlab.pdfgen import canvas
from inventory.models import StockLedger
from django.contrib import messages
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.utils import timezone
from datetime import timedelta
from accounts.decorators import allowed_roles
from customers.models import CustomerLedger

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from decimal import Decimal, InvalidOperation

def D(value):
    try:
        return Decimal(str(value or "0"))
    except InvalidOperation:
        print("INVALID DECIMAL VALUE =>", repr(value))
        raise




@allowed_roles(roles=["Admin", "Cashier", "Manager"])
def billing(request):

    products = Product.objects.all().order_by("name")

    customers = Customer.objects.all().order_by("name")

    cart = request.session.get("cart", [])

    grand_total = Decimal("0.00")

    for item in cart:

        grand_total += D(item["total"])

    bills = Bill.objects.order_by("-id")[:10]
    shop = ShopSettings.objects.first()


    context = {

        "products": products,

        "customers": customers,

        "cart": cart,

        "grand_total": grand_total,

        "bills": bills,
        "shop": shop,

    }

    return render(
        request,
        "billing/billing.html",
        context
    )


@allowed_roles(["Admin","Manager","Cashier"])
def add_to_bill(request, product_id):

    product = Product.objects.get(id=product_id)

    cart = request.session.get("cart", [])

    found = False

    for item in cart:

        if item["id"] == product.id:

            item["quantity"] += 1

            item["total"] = float(

                item["quantity"] *

                float(item["price"])

            )

            found = True

            break

    if not found:

        cart.append({

            "id": product.id,

            "name": product.name,

            "price": float(product.selling_price),

            "quantity": 1,

            "stock": product.quantity,

            "total": float(product.selling_price),

        })

    request.session["cart"] = cart

    return redirect("billing")


@allowed_roles(["Admin","Manager","Cashier"])
def increase_qty(request, product_id):

    cart = request.session.get("cart", [])

    for item in cart:

        if item["id"] == product_id:

            if item["quantity"] < item["stock"]:

                item["quantity"] += 1

            item["total"] = float(

                item["quantity"] *

                float(item["price"])

            )

            break
    

    request.session["cart"] = cart

    return redirect("billing")

@allowed_roles(["Admin","Manager","Cashier"])
def decrease_qty(request, product_id):

    cart = request.session.get("cart", [])

    for item in cart:

        if item["id"] == product_id:

            if item["quantity"] > 1:

                item["quantity"] -= 1

                item["total"] = float(

                    item["quantity"] *

                    float(item["price"])

                )

            break

    request.session["cart"] = cart

    return redirect("billing")
@allowed_roles(["Admin","Manager","Cashier"])
def remove_item(request, product_id):

    cart = request.session.get("cart", [])

    cart = [

        item

        for item in cart

        if item["id"] != product_id

    ]

    request.session["cart"] = cart

    return redirect("billing")
from decimal import Decimal as D

@allowed_roles(["Admin", "Manager", "Cashier"])
def save_bill(request):

    

    if request.method != "POST":
        return redirect("billing")

    cart = request.session.get("cart", [])

    if not cart:

        messages.error(
            request,
            "Cart is empty."
        )

        return redirect("billing")

    # =====================================
    # Invoice Number
    # =====================================

    last_bill = Bill.objects.order_by(
        "-id"
    ).first()

    if last_bill:

        last_no = int(
            last_bill.invoice_no.replace(
                "INV",
                ""
            )
        )

        invoice_no = f"INV{last_no + 1:04d}"

    else:

        invoice_no = "INV0001"

    # =====================================
    # Customer
    # =====================================

    customer = None

    customer_id = request.POST.get(
        "customer"
    )

    if customer_id:

        customer = get_object_or_404(
            Customer,
            id=customer_id
        )

    # =====================================
    # Payment Method
    # =====================================

    payment_method = request.POST.get(
        "payment_method",
        "Cash"
    )

    
    # =====================================
    # Cart Total
    # =====================================

    total_amount = D("0.00")

    for item in cart:

        total_amount += D(
            str(item["total"])
        )

    # =====================================
    # Discount
    # =====================================

    discount_type = request.POST.get(
        "discount_type",
        "Amount"
    )



    discount = D(
        request.POST.get(
            "discount",
           
        )or "0"
    )

    discount_amount = D(
        request.POST.get(
            "discount_amount",
            
        )or "0"
    )

    final_amount = total_amount - discount_amount

    if final_amount < 0:

        final_amount = D("0.00")

    # =====================================
    # Payment Split
    # =====================================

    cash_amount = D(
        request.POST.get(
            "cash_amount",
            
        )or "0"
    )

    upi_amount = D(
        request.POST.get(
            "upi_amount",
            
        )or "0"
    )

    credit_amount = D(
        request.POST.get(
            "credit_amount",
            
        )or "0"
    )

    paid_amount = cash_amount + upi_amount

    balance_amount = final_amount - paid_amount

    if balance_amount < 0:

        balance_amount = D("0.00")

    change_amount = D("0.00")

    if paid_amount > final_amount:

        change_amount = paid_amount - final_amount

        paid_amount = final_amount

        balance_amount = D("0.00")

    # =====================================
    # Payment Status
    # =====================================

    if balance_amount == 0:

        payment_status = "Paid"

    elif paid_amount == 0:

        payment_status = "Pending"

    else:

        payment_status = "Partial"

   # =====================================
    # Credit Bill Validation
    # =====================================

    if payment_method == "Credit":

        if not customer:

            messages.error(
                request,
                "Please select a customer before creating a Credit Bill."
            )

            return redirect("billing")

        cash_amount = D("0.00")

        upi_amount = D("0.00")

        paid_amount = D("0.00")

        credit_amount = final_amount

        balance_amount = final_amount

        payment_status = "Pending"

    else:

        credit_amount = balance_amount

    # =====================================
    # Stock Validation
    # =====================================

    for item in cart:

        product = get_object_or_404(
            Product,
            id=item["id"]
        )

        qty = int(item["quantity"])

        if qty > product.quantity:

            messages.error(

                request,

                f"{product.name} Stock Available : {product.quantity}"

            )

            return redirect(
                "billing"
            )

    # ===== PART 2 CONTINUES =====
        # =====================================
    # Create Bill
    # =====================================

    bill = Bill.objects.create(

        invoice_no=invoice_no,

        customer=customer,

        payment_method=payment_method,

        total_amount=total_amount,

        discount_type=discount_type,

        discount=discount,

        discount_amount=discount_amount,

        final_amount=final_amount,

        cash_amount=cash_amount,

        upi_amount=upi_amount,

        credit_amount=credit_amount,

        paid_amount=paid_amount,

        balance_amount=balance_amount,

        payment_status=payment_status,

        change_amount=change_amount,

    )

    # =====================================
    # Customer Update
    # =====================================

    if customer:

        customer.credit_balance += balance_amount

        if balance_amount > 0:

            if not customer.due_days:

                customer.due_days = 30

            customer.due_date = (

                timezone.now().date()

                +

                timedelta(days=customer.due_days)

            )

        customer.save()

    # =====================================
    # Customer Ledger Entry
    # =====================================

    if customer:

        last_entry = CustomerLedger.objects.filter(

            customer=customer

        ).order_by(

            "-id"

        ).first()

        opening_balance = (

            last_entry.balance

            if last_entry

            else D("0.00")

        )

        closing_balance = (

            opening_balance

            +

            balance_amount

        )

        CustomerLedger.objects.create(

            customer=customer,

            particular="Sale",

            invoice_no=bill.invoice_no,

            debit=balance_amount,

            credit=D("0.00"),

            balance=closing_balance,

            remarks=f"Invoice {bill.invoice_no}"

        )

    # =====================================
    # Save Bill Items
    # =====================================

    for item in cart:

        product = Product.objects.get(

            id=item["id"]

        )

        qty = int(

            item["quantity"]

        )

        price = D(

            str(item["price"])

        )

        total = D(

            str(item["total"])

        )

        BillItem.objects.create(

            bill=bill,

            product=product,

            quantity=qty,

            price=price,

            purchase_price=product.purchase_price,

            total=total

        )

        product.quantity -= qty

        product.save()

        StockLedger.objects.create(

            product=product,

            transaction_type="OUT",

            quantity=qty,

            remarks=f"Invoice {bill.invoice_no}"

        )

    # ===== PART 3 CONTINUES =====
        # =====================================
    # Calculate Bill Profit
    # =====================================

    bill_profit = D("0.00")

    for item in bill.items.all():

        profit = (

            item.price

            -

            item.purchase_price

        ) * item.quantity

        bill_profit += profit

    # =====================================
    # Activity Log
    # =====================================

    log_activity(

        request=request,

        module="Billing",

        action="Invoice Created",

        document_no=bill.invoice_no,

        description=(
            f"Invoice {bill.invoice_no} "
            f"Amount ₹{bill.final_amount}"
        )

    )

    # =====================================
    # Clear Billing Cart
    # =====================================

    request.session["cart"] = []

    request.session.modified = True

    # =====================================
    # Success Message
    # =====================================

    messages.success(

        request,

        f"Invoice {bill.invoice_no} Created Successfully."

    )

    # =====================================
    # Redirect
    # =====================================

    return redirect(

        "invoice_detail",

        bill.id

    )

@allowed_roles(["Admin","Manager","Cashier"])
def invoice_detail(request, bill_id):

    bill = Bill.objects.get(id=bill_id)

    items = BillItem.objects.filter(

        bill=bill

    )

    shop = ShopSettings.objects.first()

    return render(

        request,

        "billing/invoice_detail.html",

        {

            "bill": bill,

            "items": items,

            "shop": shop

        }

    )

@allowed_roles(["Admin","Manager","Cashier"])
def download_invoice(request, bill_id):

    bill = Bill.objects.get(id=bill_id)

    items = BillItem.objects.filter(bill=bill)

    shop = ShopSettings.objects.first()

    template = get_template("billing/invoice_pdf.html")

    html = template.render({

        "bill": bill,

        "items": items,

        "shop": shop,

    })

    response = HttpResponse(content_type="application/pdf")

    response["Content-Disposition"] = f'attachment; filename="{bill.invoice_no}.pdf"'

    pisa.CreatePDF(

        BytesIO(html.encode("UTF-8")),

        dest=response,

        encoding="UTF-8"

    )

    return response

@allowed_roles(["Admin","Manager","Cashier"])
def update_qty(request, product_id):

    qty = int(request.GET.get("qty", 1))

    product = Product.objects.get(id=product_id)

    if qty > product.quantity:

        messages.error(
            request,
            f"{product.name} : Only {product.quantity} Qty Available. You entered {qty} Qty."
        )

        return redirect("billing")
    
    cart = request.session.get("cart", [])

    for item in cart:

        if item["id"] == product_id:

            item["quantity"] = qty

            price = Decimal(str(item["price"]))

            item["total"] = str(price * qty)

            break

    request.session["cart"] = cart

    return redirect("billing")

