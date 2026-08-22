from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .models import Product
from .forms import ProductForm
from django.http import HttpResponse
import openpyxl
from django.contrib import messages
from openpyxl import load_workbook
from accounts.decorators import allowed_roles

@allowed_roles(["Admin","Manager","Accountant",])
def product_list(request):

    search = request.GET.get("search")

    products = Product.objects.all().order_by("name")

    if search:

        products = products.filter(
            name__icontains=search
        )

    paginator = Paginator(
        products,
        10
    )

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    context = {

        "products": page_obj,

        "search": search,

        "total_products": Product.objects.count()

    }

    return render(
        request,
        "products/product_list.html",
        context
    )


@allowed_roles(["Admin","Manager","Accountant",])
def add_product(request):

    if request.method == "POST":

        form = ProductForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Product Added Successfully."
            )

            return redirect("product_list")

        else:

            messages.error(
                request,
                "Product already exists."
            )

    else:

        form = ProductForm()

    return render(
        request,
        "products/add_product.html",
        {
            "form": form
        }
    )

@allowed_roles(["Admin","Manager","Accountant",])
def edit_product(request, id):

    product = Product.objects.get(id=id)

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            instance=product
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Product Updated Successfully."
            )

            return redirect("product_list")

        else:

            messages.error(
                request,
                "Another product with this name already exists."
            )

    else:

        form = ProductForm(
            instance=product
        )

    return render(
        request,
        "products/edit_product.html",
        {
            "form": form
        }
    )

@allowed_roles(["Admin","Manager","Accountant",])
def delete_product(request, id):

    product = Product.objects.get(id=id)

    product.delete()

    return redirect("product_list")

@allowed_roles(["Admin","Manager","Accountant",])
def export_products_excel(request):

    wb = openpyxl.Workbook()

    ws = wb.active

    ws.title = "Products"

    ws.append([
        "ID",
        "Product",
        "Category",
        "Purchase Price",
        "Selling Price",
        "Stock",
        "Unit"
    ])

    products = Product.objects.all()

    for p in products:

        ws.append([
            p.id,
            p.name,
            p.category,
            p.purchase_price,
            p.selling_price,
            p.quantity,
            p.unit
        ])

    response = HttpResponse(

        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )

    response["Content-Disposition"] = 'attachment; filename="Products.xlsx"'

    wb.save(response)

    return response


from decimal import Decimal, InvalidOperation

def to_decimal(value):

    if value in (None, "", "-", " "):
        return Decimal("0")

    try:
        return Decimal(str(value).replace(",", "").replace("₹", "").strip())

    except (InvalidOperation, ValueError):
        return Decimal("0")
from decimal import Decimal, InvalidOperation

from openpyxl import load_workbook

from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.decorators import allowed_roles
from .models import Product

@allowed_roles(["Admin", "Manager", "Accountant"])
def import_products_excel(request):

    if request.method != "POST":
        return render(
            request,
            "products/import_products.html"
        )

    excel_file = request.FILES.get("excel_file")

    if not excel_file:
        messages.error(request, "Please Select Excel File.")
        return redirect("product_list")

    wb = load_workbook(excel_file)
    sheet = wb.active

    imported = 0
    updated = 0
    skipped = 0

    for row_no, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):

        try:

            if row[1] is None:
                skipped += 1
                continue

            name = str(row[1]).strip()

            category = str(row[2]).strip() if row[2] else ""

            purchase_price = to_decimal(row[3])

            selling_price = to_decimal(row[4])

            quantity = int(row[5] or 0)

            unit = str(row[6]).strip() if row[6] else ""

            product = Product.objects.filter(
                name__iexact=name
            ).first()

            if product:

                product.category = category
                product.purchase_price = purchase_price
                product.selling_price = selling_price
                product.quantity = quantity
                product.unit = unit
                product.save()

                updated += 1

            else:

                Product.objects.create(

                    name=name,

                    category=category,

                    purchase_price=purchase_price,

                    selling_price=selling_price,

                    quantity=quantity,

                    unit=unit

                )

                imported += 1

            print(
                name,
                category,
                purchase_price,
                selling_price,
                quantity,
                unit
            )

        except Exception as e:

            skipped += 1

            print(f"Row {row_no} Error ->", e)

    messages.success(
        request,
        f"Imported : {imported} | Updated : {updated} | Skipped : {skipped}"
    )

    return redirect("product_list")

@allowed_roles(["Admin", "Manager", "Accountant"])
def low_stock_products(request):

    products = Product.objects.filter(
        quantity__lte=10
    ).order_by("quantity", "name")

    return render(
        request,
        "products/low_stock.html",
        {
            "products": products
        }
    )