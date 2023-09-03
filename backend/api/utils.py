import io

from django.http import HttpResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def create_shopping_cart(ingredients_cart):
    """
    Создать PDF-файл с списком покупок.

    Функция создает PDF-файл с
    списком покупок на основе переданных ингредиентов и
    возвращает его в виде HTTP-ответа для скачивания.

    Аргументы:
        - `ingredients_cart` `(list)`: Список ингредиентов для списка покупок.

    Возвращает:
        - `HttpResponse`: HTTP-ответ с PDF-файлом в виде вложения.
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_cart.pdf"'
        )
    pdfmetrics.registerFont(TTFont('Arial', 'data/arial.ttf', 'UTF-8'))
    buffer = io.BytesIO()
    pdf_file = canvas.Canvas(buffer)
    pdf_file.setFont('Arial', 18)
    pdf_file.drawString(200, 800, 'Список покупок.')
    pdf_file.setFont('Arial', 12)
    from_bottom = 750
    for number, ingredient in enumerate(ingredients_cart, start=1):
        pdf_file.drawString(50, from_bottom, f"{number}.")
        pdf_file.drawString(
            70,
            from_bottom,
            f"{ingredient['ingredient__name']}: "
            f"{ingredient['ingredient_value']} "
            f"{ingredient['ingredient__measurement_unit']}.",
        )
        from_bottom -= 20
        if from_bottom <= 50:
            from_bottom = 800
            pdf_file.showPage()
            pdf_file.setFont('Arial', 14)
    pdf_file.showPage()
    pdf_file.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
