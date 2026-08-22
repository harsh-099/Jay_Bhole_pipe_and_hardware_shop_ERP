from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum
from decimal import Decimal
from reportlab.pdfgen import canvas
from accounts.decorators import allowed_roles
from purchases.models import Purchase, PurchaseItem
from products.models import Product
from shopsettings.models import ShopSettings
from suppliers.models import SupplierLedger

from .models import PurchaseReturn, PurchaseReturnItem


@allowed_roles(["Admin", "Manager", "Accountant", ])
def purchase_return_list(request):

    purchases = Purchase.objects.order_by("-id")

    returns = PurchaseReturn.objects.select_related(
        "purchase",
        "purchase__supplier"
    ).order_by("-id")

    return render(
        request,
        "purchasereturn/list.html",
        {
            "purchases": purchases,
            "returns": returns,
        },
    )


@allowed_roles(["Admin", "Manager", "Accountant", ])
def purchase_return(request, purchase_id):

    purchase = get_object_or_404(
        Purchase,
        id=purchase_id
    )

    items = PurchaseItem.objects.filter(
        purchase=purchase
    )

    if request.method == "POST":

        purchase_return = PurchaseReturn.objects.create(
            purchase=purchase,
            total_return=0
        )

        total_return = Decimal("0.00")

        for item in items:

            qty = request.POST.get(f"qty_{item.id}")

            if not qty:
                continue

            qty = int(qty)

            if qty <= 0:
                continue

            if qty > item.quantity:
                qty = item.quantity

            amount = qty * item.price

            PurchaseReturnItem.objects.create(
                purchase_return=purchase_return,
                purchase_item=item,
                quantity=qty,
                amount=amount
            )

            # Product Stock Decrease
            product = item.product
            product.quantity -= qty
            product.save()

            # Purchase Item Qty Reduce
            item.quantity -= qty
            item.save()

            total_return += amount

        # Purchase Amount Update
        purchase.total_amount -= total_return

        if purchase.total_amount < 0:
            purchase.total_amount = 0

        purchase.save()

        # Return Number
        purchase_return.total_return = total_return
        purchase_return.return_no = f"PR-{purchase_return.id:05d}"

        remaining_qty = PurchaseItem.objects.filter(
            purchase=purchase
        ).aggregate(
            total=Sum("quantity")
        )["total"] or 0

        if remaining_qty == 0:
            purchase_return.status = "Full"
        else:
            purchase_return.status = "Partial"

        purchase_return.save()

        # Supplier Ledger Entry
        last = SupplierLedger.objects.filter(
            supplier=purchase.supplier
        ).order_by("-id").first()

        balance = last.balance if last else 0

        SupplierLedger.objects.create(
            supplier=purchase.supplier,
            particular="Purchase Return",
            debit=0,
            credit=total_return,
            balance=balance - total_return,
            remarks=f"Purchase Return {purchase_return.return_no}"
        )

        return redirect("purchase_return_list")

    return render(
        request,
        "purchasereturn/return.html",
        {
            "purchase": purchase,
            "items": items,
        },
    )



@allowed_roles(["Admin", "Manager", "Accountant", ])
def purchase_return_print(request, return_id):

    purchase_return = get_object_or_404(
        PurchaseReturn,
        id=return_id
    )

    shop = ShopSettings.objects.first()

    return render(
        request,
        "purchasereturn/print.html",
        {
            "return_data": purchase_return,
            "shop": shop,
        },
    )



@allowed_roles(["Admin", "Manager", "Accountant"])
def purchase_return_pdf(request, return_id):

    purchase_return = get_object_or_404(
        PurchaseReturn,
        id=return_id
    )

    shop = ShopSettings.objects.first()

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'inline; filename="{purchase_return.return_no}.pdf"'
    )

    p = canvas.Canvas(response)

    width = 595
    y = 810

    # ===============================
    # SHOP HEADER
    # ===============================

    if shop:

        if shop.logo:

            try:

                p.drawImage(

                    shop.logo.path,

                    40,

                    y - 55,

                    width=55,

                    height=55,

                    preserveAspectRatio=True

                )

            except:

                pass

        p.setFont(
            "Helvetica-Bold",
            18
        )

        p.drawCentredString(
            width / 2,
            y,
            shop.shop_name
        )

        y -= 18

        p.setFont(
            "Helvetica",
            10
        )

        p.drawCentredString(
            width / 2,
            y,
            shop.address
        )

        y -= 14

        p.drawCentredString(
            width / 2,
            y,
            f"Mobile : {shop.mobile}"
        )

        y -= 14

        p.drawCentredString(
            width / 2,
            y,
            f"GST : {shop.gst_number}"
        )

    y -= 25

    p.line(
        30,
        y,
        565,
        y
    )

    y -= 28

    p.setFont(
        "Helvetica-Bold",
        16
    )

    p.drawCentredString(
        width / 2,
        y,
        "PURCHASE RETURN"
    )

    y -= 30

        # ===============================
    # PURCHASE RETURN DETAILS
    # ===============================

    p.setFont(
        "Helvetica",
        11
    )

    p.drawString(
        40,
        y,
        f"Return No : {purchase_return.return_no}"
    )

    p.drawRightString(
        550,
        y,
        f"Date : {purchase_return.created_at.strftime('%d-%m-%Y')}"
    )

    y -= 20

    p.drawString(
        40,
        y,
        f"Purchase No : {purchase_return.purchase.id}"
    )

    p.drawRightString(
        550,
        y,
        f"Status : {purchase_return.status}"
    )

    y -= 20

    p.drawString(
        40,
        y,
        f"Supplier : {purchase_return.purchase.supplier.name}"
    )

    y -= 30

    # ===============================
    # TABLE HEADER
    # ===============================

    p.setFont(
        "Helvetica-Bold",
        11
    )

    p.rect(40, y - 18, 35, 18)
    p.rect(75, y - 18, 250, 18)
    p.rect(325, y - 18, 70, 18)
    p.rect(395, y - 18, 80, 18)
    p.rect(475, y - 18, 80, 18)

    p.drawCentredString(
        57,
        y - 13,
        "Sr"
    )

    p.drawCentredString(
        200,
        y - 13,
        "Product"
    )

    p.drawCentredString(
        360,
        y - 13,
        "Qty"
    )

    p.drawCentredString(
        435,
        y - 13,
        "Rate"
    )

    p.drawCentredString(
        515,
        y - 13,
        "Amount"
    )

    y -= 18

    # ===============================
    # TABLE DATA
    # ===============================

    p.setFont(
        "Helvetica",
        10
    )

    sr = 1

    for item in purchase_return.items.all():

        y -= 18

        p.rect(40, y, 35, 18)
        p.rect(75, y, 250, 18)
        p.rect(325, y, 70, 18)
        p.rect(395, y, 80, 18)
        p.rect(475, y, 80, 18)

        p.drawCentredString(
            57,
            y + 5,
            str(sr)
        )

        p.drawString(
            80,
            y + 5,
            item.purchase_item.product.name[:35]
        )

        p.drawCentredString(
            360,
            y + 5,
            str(item.quantity)
        )

        rate = item.amount / item.quantity if item.quantity else 0

        p.drawRightString(
            468,
            y + 5,
            f"{rate:.2f}"
        )

        p.drawRightString(
            548,
            y + 5,
            f"{item.amount:.2f}"
        )

        sr += 1

            # ===============================
    # TOTAL SECTION
    # ===============================

    y -= 35

    p.setFont(
        "Helvetica-Bold",
        12
    )

    p.rect(
        365,
        y - 22,
        190,
        22
    )

    p.drawString(
        375,
        y - 7,
        "Total Return Amount"
    )

    p.drawRightString(
        545,
        y - 7,
        f"Rs. {purchase_return.total_return:.2f}"
    )

    y -= 60

    # ===============================
    # TERMS & CONDITIONS
    # ===============================

    p.setFont(
        "Helvetica-Bold",
        11
    )

    p.drawString(
        40,
        y,
        "Terms & Conditions"
    )

    y -= 18

    p.setFont(
        "Helvetica",
        10
    )

    p.drawString(
        45,
        y,
        "• Returned goods once accepted cannot be claimed again."
    )

    y -= 15

    p.drawString(
        45,
        y,
        "• Amount adjusted as per supplier policy."
    )

    y -= 15

    p.drawString(
        45,
        y,
        "• This is a computer generated Purchase Return."
    )

    # ===============================
    # SIGNATURE
    # ===============================

    y -= 70

    p.line(
        390,
        y,
        550,
        y
    )

    y -= 15

    p.setFont(
        "Helvetica",
        10
    )

    p.drawCentredString(
        470,
        y,
        "Authorized Signature"
    )

        # ===============================
    # FOOTER
    # ===============================

    p.setFont(
        "Helvetica",
        9
    )

    p.drawCentredString(
        width / 2,
        55,
        "THANK YOU • VISIT AGAIN"
    )

    p.drawCentredString(
        width / 2,
        40,
        f"Printed On : {purchase_return.created_at.strftime('%d-%m-%Y %H:%M')}"
    )

    p.drawCentredString(
        width / 2,
        25,
        f"Purchase Return No : {purchase_return.return_no}"
    )

    # ===============================
    # SAVE PDF
    # ===============================

    p.showPage()

    p.save()

    return response