from django.contrib import admin

# Register your models here.
from appticket.models import Subgerencia, Servicio, Ticket, Usuario, Talonario, Monitor, Ventanilla
from django.contrib.auth.admin import UserAdmin

class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_nro','creado_en','fecha','fecha_ea','estado','ventanilla','servicio','preferencial')
    list_filter = ('ticket_nro','creado_en','fecha','fecha_ea','estado','ventanilla','servicio','preferencial')


class VentanillaAdmin(admin.ModelAdmin):
    list_display = ('nombre','ocupada','estado','get_servicios','contador_normal','contador_preferencial','usuario')
    list_filter = ('nombre','ocupada','estado','servicio','contador_normal','contador_preferencial','usuario')


class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre','subgerencia')
    list_filter = ('nombre','subgerencia')


class TalonarioAdmin(admin.ModelAdmin):
    list_display = ('fecha_de_registro','subgerencia','subgerencia')
    list_filter = ('fecha_de_registro','subgerencia','subgerencia')


admin.site.register(Usuario, UserAdmin)
admin.site.register(Ticket,TicketAdmin)
admin.site.register(Servicio,ServicioAdmin)
admin.site.register(Subgerencia)
admin.site.register(Talonario,TalonarioAdmin)
admin.site.register(Monitor)
admin.site.register(Ventanilla, VentanillaAdmin)


