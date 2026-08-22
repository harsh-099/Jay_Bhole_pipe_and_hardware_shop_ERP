from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from suppliers.models import Supplier, SupplierLedger
from .models import PurchaseOrder, PurchaseOrderItem
from purchases.models import Purchase, PurchaseItem
from suppliers.models import Supplier
from products.models import Product
from accounts.decorators import allowed_roles
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from shopsettings.models import ShopSettings

@allowed_roles(["Admin", "Manager", "Accountant"])
def purchase_order_list(request):

    search = request.GET.get("search")

    orders = PurchaseOrder.objects.select_related(
        "supplier"
    ).order_by("-id")

    if search:

        orders = orders.filter(
            po_no__icontains=search
        )

    return render(

        request,

        "purchaseorder/list.html",

        {

            "orders": orders,

            "search": search,

        }

    )


@allowed_roles(["Admin", "Manager", "Accountant"])
def add_purchase_order(request):

    suppliers = Supplier.objects.all().order_by("name")

    products = Product.objects.all().order_by("name")

    cart = request.session.get("po_cart", [])

    subtotal = Decimal("0.00")

    for item in cart:

        subtotal += Decimal(str(item["total"]))

    last = PurchaseOrder.objects.order_by("-id").first()

    if last:

        no = int(
            last.po_no.replace("PO", "")
        ) + 1

    else:

        no = 1

    next_po_no = f"PO{no:04d}"

    context = {

        "suppliers": suppliers,

        "products": products,

        "cart": cart,

        "subtotal": subtotal,

        "next_po_no": next_po_no,

    }

    return render(

        request,

        "purchaseorder/add.html",

        context

    )


@allowed_roles(["Admin", "Manager", "Accountant"])
def add_item(request, id):

    product = get_object_or_404(
        Product,
        id=id
    )

    cart = request.session.get(
        "po_cart",
        []
    )

    found = False

    for item in cart:

        if item["id"] == product.id:

            item["quantity"] += 1

            item["total"] = round(

                item["quantity"] *

                item["price"],

                2

            )

            found = True

            break

    if not found:

        cart.append({

            "id": product.id,

            "name": product.name,

            "price": float(
                product.purchase_price
            ),

            "quantity": 1,

            "total": float(
                product.purchase_price
            )

        })

    request.session["po_cart"] = cart

    request.session.modified = True

    return redirect(
        "add_purchase_order"
    )

@allowed_roles(["Admin", "Manager", "Accountant"])
def update_quantity(request, id):

    qty = int(request.GET.get("qty", 1))

    if qty < 1:
        qty = 1

    cart = request.session.get("po_cart", [])

    for item in cart:

        if item["id"] == id:

            item["quantity"] = qty
            item["total"] = round(item["price"] * qty, 2)
            break

    request.session["po_cart"] = cart
    request.session.modified = True

    return redirect("add_purchase_order")

@allowed_roles(["Admin", "Manager", "Accountant"])
def remove_item(request, id):

    cart = request.session.get(
        "po_cart",
        []
    )

    cart = [

        item

        for item in cart

        if item["id"] != id

    ]

    request.session["po_cart"] = cart

    request.session.modified = True

    return redirect(
        "add_purchase_order"
    )

@allowed_roles(["Admin", "Manager", "Accountant"])
def save_purchase_order(request):

    if request.method != "POST":
        return redirect("add_purchase_order")

    # -----------------------------
    # Cart Validation
    # -----------------------------

    cart = request.session.get("po_cart", [])

    if not cart:

        messages.warning(
            request,
            "Please add at least one product."
        )

        return redirect("add_purchase_order")

    # -----------------------------
    # Supplier Validation
    # -----------------------------

    supplier_id = request.POST.get("supplier")

    if not supplier_id:

        messages.error(
            request,
            "Please select Supplier."
        )

        return redirect("add_purchase_order")

    supplier = get_object_or_404(
        Supplier,
        id=supplier_id
    )

    # -----------------------------
    # Expected Delivery Validation
    # -----------------------------

    expected_delivery = request.POST.get(
        "expected_delivery"
    )

    if not expected_delivery:

        messages.error(
            request,
            "Please select Expected Delivery Date."
        )

        return redirect("add_purchase_order")

    # -----------------------------
    # Generate PO Number
    # -----------------------------

    last = PurchaseOrder.objects.order_by("-id").first()

    if last:

        no = int(
            last.po_no.replace(
                "PO",
                ""
            )
        ) + 1

    else:

        no = 1

    po_no = f"PO{no:04d}"

    # -----------------------------
    # Calculate Totals
    # -----------------------------

    subtotal = Decimal("0.00")

    for item in cart:

        subtotal += Decimal(
            str(item["total"])
        )

    discount = Decimal(

        request.POST.get(
            "discount",
            "0"
        )

    )

    final_amount = subtotal - discount

    # -----------------------------
    # Payment Details
    # -----------------------------

    payment_method = request.POST.get(
        "payment_method",
        "Credit"
    )

    paid_amount = Decimal(

        request.POST.get(
            "paid_amount",
            "0"
        )

    )

    # Paid amount validation

    if paid_amount < 0:
        paid_amount = Decimal("0.00")

    if paid_amount > final_amount:
        paid_amount = final_amount

    balance_amount = final_amount - paid_amount

    # -----------------------------
    # Save Purchase Order
    # -----------------------------

    po = PurchaseOrder.objects.create(

        po_no=po_no,

        supplier=supplier,

        expected_delivery=expected_delivery,

        subtotal=subtotal,

        discount=discount,

        final_amount=final_amount,

        payment_method=payment_method,

        paid_amount=paid_amount,

        balance_amount=balance_amount,

        remarks=request.POST.get(
            "remarks"
        ),

        status="Pending"

    )

    # -----------------------------
    # Save Items
    # -----------------------------

    for item in cart:

        product = Product.objects.get(
            id=item["id"]
        )

        PurchaseOrderItem.objects.create(

            purchase_order=po,

            product=product,

            quantity=item["quantity"],

            price=item["price"],

            total=item["total"]

        )

    # -----------------------------
    # Supplier Ledger Update
    # -----------------------------

    last_ledger = SupplierLedger.objects.filter(
        supplier=supplier
    ).order_by("-id").first()

    balance = (
        last_ledger.balance
        if last_ledger
        else Decimal("0.00")
    )

    # Purchase Order Entry
    balance += final_amount

    SupplierLedger.objects.create(

        supplier=supplier,

        particular="Purchase",

        debit=final_amount,

        credit=Decimal("0.00"),

        balance=balance,

        remarks=f"Purchase Order {po.po_no}"

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

            remarks=f"Payment Against {po.po_no}"

        )

    supplier.balance = balance
    supplier.ledger_balance = balance
    supplier.save()   

    # -----------------------------
    # Clear Cart
    # -----------------------------

    request.session["po_cart"] = []

    request.session.modified = True

    # -----------------------------
    # Success Message
    # -----------------------------

    messages.success(

        request,

        f"Purchase Order {po.po_no} saved successfully."

    )

    # -----------------------------
    # Save OR Save & Print
    # -----------------------------

    action = request.POST.get("action")

    if action == "print":

        return redirect(
            "print_purchase_order",
            po.id
        )

    return redirect(
        "view_purchase_order",
        po.id
    )

@allowed_roles(["Admin", "Manager", "Accountant"])
def view_purchase_order(request, id):

    po = get_object_or_404(
        PurchaseOrder,
        id=id
    )

    items = PurchaseOrderItem.objects.filter(
        purchase_order=po
    )

    return render(

        request,

        "purchaseorder/view.html",

        {

            "po": po,

            "items": items,

        }

    )


@allowed_roles(["Admin", "Manager", "Accountant"])
def clear_po_cart(request):

    request.session["po_cart"] = []

    request.session.modified = True

    messages.success(
        request,
        "Cart Cleared Successfully."
    )

    return redirect(
        "add_purchase_order"
    )


@allowed_roles(["Admin", "Manager", "Accountant"])
def convert_to_purchase(request, id):

    po = get_object_or_404(
        PurchaseOrder,
        id=id
    )

    if po.status == "Received":

        messages.warning(
            request,
            "Purchase Order already converted."
        )

        return redirect(
            "view_purchase_order",
            id=po.id
        )

    items = PurchaseOrderItem.objects.filter(
        purchase_order=po
    )

    if not items.exists():

        messages.error(
            request,
            "No items found."
        )

        return redirect(
            "view_purchase_order",
            id=po.id
        )

    last_purchase = Purchase.objects.order_by(
        "-id"
    ).first()

    if last_purchase:

        no = int(

            last_purchase.purchase_no.replace(

                "PUR",

                ""

            )

        ) + 1

    else:

        no = 1

    purchase = Purchase.objects.create(

        purchase_no=f"PUR{no:04d}",

        supplier=po.supplier,

        total_amount=po.subtotal,

        discount=po.discount,

        final_amount=po.final_amount,

        payment_method=po.payment_method,

        paid_amount=po.paid_amount,

        balance_amount=po.balance_amount,

        remarks=po.remarks

    )

    grand_total = Decimal("0.00")

    for item in items:

        PurchaseItem.objects.create(

            purchase=purchase,

            product=item.product,

            quantity=item.quantity,

            price=item.price,

            total=item.total

        )

        item.product.quantity += item.quantity

        item.product.save()

        grand_total += item.total

    purchase.total_amount = grand_total

    purchase.final_amount = po.final_amount
    purchase.balance_amount = (

        purchase.final_amount -

        purchase.paid_amount

    )

    purchase.save()
    # -----------------------------
    # Supplier Ledger Link
    # -----------------------------

    purchase.total_amount = po.final_amount

    purchase.final_amount = po.final_amount

    purchase.paid_amount = po.paid_amount

    purchase.balance_amount = po.balance_amount

    purchase.save()

    po.status = "Received"

    po.save()

    messages.success(

        request,

        "Purchase Created Successfully."

    )

    return redirect(

        "purchase_details",

        purchase.id

    )

@allowed_roles(["Admin","Manager","Accountant"])
def print_purchase_order(request, id):

    po = get_object_or_404(

        PurchaseOrder,

        id=id

    )

    items = PurchaseOrderItem.objects.filter(

        purchase_order=po

    )

    shop = ShopSettings.objects.first()

    template = get_template(

        "purchaseorder/purchase_order_pdf.html"

    )

    html = template.render({

        "po": po,

        "items": items,

        "shop": shop,

    })

    response = HttpResponse(

        content_type="application/pdf"

    )

    response["Content-Disposition"] = (

        f'inline; filename="{po.po_no}.pdf"'

    )

    pisa.CreatePDF(

        html,

        dest=response

    )

    return response