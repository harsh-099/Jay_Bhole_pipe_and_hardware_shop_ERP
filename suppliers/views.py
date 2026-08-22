from django.shortcuts import (
    render,
    redirect
)

from .models import Supplier
from .models import Supplier, SupplierLedger
from .forms import SupplierForm
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from shopsettings.models import ShopSettings
from accounts.decorators import allowed_roles

@allowed_roles(["Admin","Manager","Accountant",])
def supplier_list(request):

    suppliers = Supplier.objects.all().order_by(
        'name'
    )

    return render(

        request,

        'suppliers/list.html',

        {

            'suppliers': suppliers

        }

    )

@allowed_roles(["Admin","Manager","Accountant",])
def add_supplier(request):

    if request.method == 'POST':

        form = SupplierForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            return redirect(
                'supplier_list'
            )

    else:

        form = SupplierForm()

    return render(

        request,

        'suppliers/add.html',

        {

            'form': form

        }

    )

@allowed_roles(["Admin","Manager","Accountant",])
def edit_supplier(request, id):

    supplier = Supplier.objects.get(id=id)

    if request.method == 'POST':

        form = SupplierForm(
            request.POST,
            instance=supplier
        )

        if form.is_valid():

            form.save()

            return redirect(
                'supplier_list'
            )

    else:

        form = SupplierForm(
            instance=supplier
        )

    return render(

        request,

        'suppliers/add.html',

        {

            'form': form

        }

    )

@allowed_roles(["Admin","Manager","Accountant",])
def delete_supplier(request, id):

    supplier = Supplier.objects.get(
        id=id
    )

    supplier.delete()

    return redirect(
        'supplier_list'
    )

@allowed_roles(["Admin","Manager","Accountant",])
def supplier_ledger(request, supplier_id):

    supplier = Supplier.objects.get(
        id=supplier_id
    )

    ledger = SupplierLedger.objects.filter(
        supplier=supplier
    ).order_by("-date")

    return render(

        request,

        "suppliers/ledger.html",

        {

            "supplier": supplier,

            "ledger": ledger

        }

    )

@allowed_roles(["Admin","Manager","Accountant",])
def supplier_ledger_pdf(request, supplier_id):

    supplier = Supplier.objects.get(id=supplier_id)

    ledger = SupplierLedger.objects.filter(
        supplier=supplier
    ).order_by("-date")

    shop = ShopSettings.objects.first()

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{supplier.name}_Ledger.pdf"'
    )

    p = canvas.Canvas(response)

    y = 810

    if shop:

        p.setFont("Helvetica-Bold",18)
        p.drawCentredString(300,y,shop.shop_name)

        y -= 20

        p.setFont("Helvetica",10)
        p.drawCentredString(300,y,shop.address)

        y -= 15

        p.drawCentredString(
            300,
            y,
            f"Mobile : {shop.mobile}"
        )

        y -= 15

        p.drawCentredString(
            300,
            y,
            f"GST : {shop.gst_number}"
        )

        y -= 30

    p.setFont("Helvetica-Bold",16)

    p.drawCentredString(
        300,
        y,
        "SUPPLIER LEDGER"
    )

    y -= 30

    p.setFont("Helvetica",11)

    p.drawString(
        40,
        y,
        f"Supplier : {supplier.name}"
    )

    y -= 20

    p.drawString(
        40,
        y,
        f"Mobile : {supplier.mobile}"
    )

    y -= 30

    p.setFont("Helvetica-Bold",11)

    p.drawString(40,y,"Date")
    p.drawString(150,y,"Particular")
    p.drawString(280,y,"Debit")
    p.drawString(360,y,"Credit")
    p.drawString(450,y,"Balance")

    y -= 20

    p.setFont("Helvetica",10)

    for row in ledger:

        if y < 60:
            p.showPage()
            y = 800

        p.drawString(
            40,
            y,
            row.date.strftime("%d-%m-%Y")
        )

        p.drawString(
            150,
            y,
            row.particular
        )

        p.drawString(
            280,
            y,
            str(row.debit)
        )

        p.drawString(
            360,
            y,
            str(row.credit)
        )

        p.drawString(
            450,
            y,
            str(row.balance)
        )

        y -= 18

    p.save()

    return response

@allowed_roles(["Admin","Manager","Accountant",])
def supplier_ledger_print(request, supplier_id):

    supplier = Supplier.objects.get(id=supplier_id)

    ledger = SupplierLedger.objects.filter(
        supplier=supplier
    ).order_by("-date")

    shop = ShopSettings.objects.first()

    return render(

        request,

        "suppliers/ledger_print.html",

        {

            "supplier": supplier,

            "ledger": ledger,

            "shop": shop

        }

    )