# middleware.py

from datetime import date
import re

class DateInputMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST':
            post = request.POST.copy()  # Cria uma cópia mutável do request.POST
            for key, value in post.items():
                if key.endswith('validade'):
                    # Verifica se a data está no formato YYYY-MM-DD
                    if re.match(r'\d{4}-\d{2}-\d{2}', value):
                        year, month, day = map(int, value.split('-'))
                    # Verifica se a data está no formato DD/MM/YYYY
                    elif re.match(r'\d{2}/\d{2}/\d{4}', value):
                        day, month, year = map(int, value.split('/'))
                    else:
                        # Lida com um formato de data inválido
                        raise ValueError("Formato de data inválido")
                    
                    # Converte a data para o formato ISO (YYYY-MM-DD)
                    post[key] = date(year, month, day).isoformat()
            
            # Substitui o request.POST original pela cópia modificada
            request.POST = post  
        
        # Processa a requisição
        response = self.get_response(request)
        return response
