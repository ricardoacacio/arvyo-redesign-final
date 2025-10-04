# financeiro_api/admin.py

from django.contrib import admin
from .models import Conta, Cartao, Lancamento, Floresta

# O código mais simples para registrar os modelos no Admin:
admin.site.register(Conta)
admin.site.register(Cartao)
admin.site.register(Lancamento)
admin.site.register(Floresta)