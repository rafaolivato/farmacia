from datetime import date
import re

class DateInputMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST':
            post = request.POST.copy()
            for key, value in post.items():
                if 'data' in key or 'validade' in key:
                    # Verifica se a data está no formato DD/MM/YYYY
                    if re.match(r'\d{2}/\d{2}/\d{4}', value):
                        try:
                            day, month, year = map(int, value.split('/'))
                            post[key] = date(year, month, day).isoformat()
                        except ValueError:
                            # Se houver um erro na conversão,
                            # deixe o valor original e o formulário
                            # lidará com a validação.
                            pass
                    elif re.match(r'\d{4}-\d{2}-\d{2}', value):
                        # Verifica se a data está no formato YYYY-MM-DD
                        try:
                            year, month, day = map(int, value.split('-'))
                            post[key] = date(year, month, day).isoformat()
                        except ValueError:
                            pass
                    else:
                        # Se o formato não corresponder a nenhum dos esperados,
                        # deixe o valor original e o formulário lidará com a validação.
                        pass

            request.POST = post

        response = self.get_response(request)
        return response