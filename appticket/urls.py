from rest_framework.routers import DefaultRouter
from appticket.views import TicketViewSet, SubgerenciaViewSet, ServicioViewSet, UsuarioViewSet, VentanillaViewSet, \
    VentanillaServicioViewSet, MonitorViewSet, ListTicketMonitor, ConfiguracionViewSet, ApiConfiguracion, \
    VentanillasServicios, ApiUsuarioServiciosVentanilla

from django.urls import path, include

router = DefaultRouter()
router.register('usuarios', UsuarioViewSet, 'Usuarios')
router.register('tickets', TicketViewSet, 'Ticket')
router.register('subgerencias', SubgerenciaViewSet, 'Subgerencia')
router.register('servicios', ServicioViewSet, 'Servicios')
router.register('ventanillas', VentanillaViewSet, 'Ventanillas')
router.register('monitores', MonitorViewSet, 'Monitores')

urlpatterns = [
    path('', include(router.urls)),
    path('tickets_monitor/', ListTicketMonitor.as_view()),
    path('configuracion/', ApiConfiguracion.as_view()),
    path('ventanillas_servicios/', VentanillasServicios.as_view()),
    path('ventanillas_servicios/<int:ventanilla_id>/<int:servicio_id>/', VentanillasServicios.as_view()),
    path('usuario_servicios_ventanilla/', ApiUsuarioServiciosVentanilla.as_view()),
]
