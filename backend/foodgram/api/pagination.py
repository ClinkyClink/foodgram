from recipes.constants import PAGE_PAGINATION
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = PAGE_PAGINATION
