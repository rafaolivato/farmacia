from datetime import date

class DateInputMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST':
            post = request.POST.copy()  # Cria uma cópia mutável do request.POST
            for key, value in post.items():
                if key.endswith('validade'):
                    day, month, year = map(int, value.split('/'))
                    post[key] = date(year, month, day).isoformat()
            request.POST = post  # Substitui o request.POST original pela cópia modificada
        response = self.get_response(request)
        return response