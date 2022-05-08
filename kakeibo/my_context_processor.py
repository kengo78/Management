from django.utils import timezone

def common_context(request):
    """共通コンテキスト"""
    now = timezone.now()
    
    return {"now_year": now.year,
            "now_month": now.month}