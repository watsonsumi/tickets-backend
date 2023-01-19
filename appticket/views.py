from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from appticket.models import Ticket, Servicio, Subgerencia, Usuario, Ventanilla, Talonario, Monitor, Configuracion
from appticket.renderers import EmberJSONRenderer
from appticket.serializers import TicketSerializer, SubgerenciaSerializer, ServicioSerializer, \
    UsuarioSerializer, VentanillaSerializer, TalonarioSerializer, VentanillaServicioSerializer, MonitorSerializer, \
    AuthCustomTokenSerializer, ConfiguracionSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.views import APIView
from datetime import datetime, date



class TalonarioViewSet(viewsets.ModelViewSet):
    model = Talonario
    queryset = Talonario.objects.all()
    serializer_class = TalonarioSerializer
    renderer_classes = (EmberJSONRenderer, )
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)



class UsuarioFilter(django_filters.FilterSet):
    nombres = django_filters.CharFilter(field_name="first_name")
    apellidos = django_filters.CharFilter(field_name="last_name")
    estado = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = Usuario
        fields = ['email','nombres','apellidos','estado','subgerencia__id','tipo_de_usuario']



class UsuarioViewSet(viewsets.ModelViewSet):
    model = Usuario
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    renderer_classes = (EmberJSONRenderer, )
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    filterset_class = UsuarioFilter
    filter_backends = (DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter)
    search_fields = ['email','first_name','last_name','tipo_de_usuario', 'celular', 'subgerencia__nombre','subgerencia__id']
    ordering_fields = '__all__'
    ordering = ['-date_joined']


class VentanillaViewSet(viewsets.ModelViewSet):
    model = Ventanilla
    queryset = Ventanilla.objects.all()
    serializer_class = VentanillaSerializer
    renderer_classes = (EmberJSONRenderer, )
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    filter_backends = (DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter)
    filterset_fields = {'nombre':['gte', 'lte', 'exact', 'gt', 'lt'],
                        'estado':['gte', 'lte', 'exact', 'gt', 'lt']}
    search_fields = ['nombre', 'servicio__nombre', 'usuario__username']
    ordering_fields = '__all__'
    ordering = ['-creado_en']



class VentanillaServicioViewSet(viewsets.ModelViewSet):
    model = Ventanilla
    queryset = Ventanilla.objects.exclude(usuario__isnull=True).exclude(servicio=None)
    serializer_class = VentanillaServicioSerializer
    renderer_classes = (EmberJSONRenderer, )
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    filter_backends = (DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter)
    filterset_fields = {'nombre':['gte', 'lte', 'exact', 'gt', 'lt'],
                        'estado':['gte', 'lte', 'exact', 'gt', 'lt']}
    ordering_fields = '__all__'
    ordering = ['-creado_en']


class TicketViewSet(viewsets.ModelViewSet):
    model = Ticket
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    renderer_classes = (EmberJSONRenderer, )
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    filter_backends = (DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter)
    filterset_fields = {'fecha':['gte', 'lte', 'exact', 'gt', 'lt'],
                        'ticket_nro':['gte', 'lte', 'exact', 'gt', 'lt'],
                        'dni':['gte', 'lte', 'exact', 'gt', 'lt'],
                        'ruc':['gte', 'lte', 'exact', 'gt', 'lt'],
                        'razon_social':['gte', 'lte', 'exact', 'gt', 'lt'],
                        'nombres':['gte', 'lte', 'exact', 'gt', 'lt'],
                        'apellidos':['gte', 'lte', 'exact', 'gt', 'lt'],
                        'servicio__nombre':['gte', 'lte', 'exact', 'gt', 'lt'],
                        'ventanilla__usuario__id':['gte', 'lte', 'exact', 'gt', 'lt'],
                        'servicio__subgerencia__id':['gte', 'lte', 'exact', 'gt', 'lt'],
                        }
    search_fields = ['ticket_nro', 'dni','ruc','razon_social','nombres', 'apellidos','fecha',
                     'servicio__nombre','dni','ventanilla__nombre','ventanilla__usuario__id']
    ordering_fields = '__all__'
    ordering = ['-creado_en']


    def partial_update(self, request, *args, **kwargs):
        ticket_object = self.get_object()
        data = request.data
        estado = data.get("estado")
        if estado=='CO' or estado=='CA':
            ventanilla_object = ticket_object.ventanilla
            servicios = ventanilla_object.servicio.all()
            if Ticket.objects.filter(estado='PE',servicio__in=servicios,fecha=timezone.localtime(timezone.now()).date()).count()> 0:
                configuracion = Configuracion.objects.get(nombre="proporcion")
                proporcion = int(configuracion.valor)
                ticket = None
                if Ticket.objects.filter(estado='PE',servicio__in=servicios,fecha=timezone.localtime(timezone.now()).date()).count()>0:

                    if Ticket.objects.filter(estado='PE',servicio__in=servicios,preferencial=True,fecha=timezone.localtime(timezone.now()).date()).count()>0:
                        if ventanilla_object.contador_preferencial >= proporcion:
                            ventanilla_object.contador_preferencial=0
                            if Ticket.objects.filter(estado='PE',servicio__in=servicios,preferencial=False,fecha=timezone.localtime(timezone.now()).date()).count()>0:
                                ticket = Ticket.objects.filter(estado='PE',servicio__in=servicios,preferencial=False,
                                                       fecha=timezone.localtime(timezone.now()).date()).order_by('creado_en').first()
                            else:
                                ticket = Ticket.objects.filter(estado='PE',servicio__in=servicios,preferencial=True,
                                                       fecha=timezone.localtime(timezone.now()).date()).order_by('creado_en').first()
                                ventanilla_object.contador_preferencial+=1
                        else:    
                            ticket = Ticket.objects.filter(estado='PE',servicio__in=servicios,preferencial=True,
                                                       fecha=timezone.localtime(timezone.now()).date()).order_by('creado_en').first()
                            ventanilla_object.contador_preferencial+=1
                        
                    else:
                        ticket = Ticket.objects.filter(estado='PE',servicio__in=servicios,preferencial=False,
                                                       fecha=timezone.localtime(timezone.now()).date()).order_by('creado_en').first()
                        ventanilla_object.contador_normal+=1

                ticket.fecha_ea = timezone.localtime(timezone.now())
                ticket.estado= 'EA'
                ticket.ventanilla = ventanilla_object
                ticket.fin_en = timezone.localtime(timezone.now())
                ticket.save()
                ventanilla_object.save()

            else:
                ventanilla_object.ocupada = False
                ventanilla_object.save()

            ticket_object.atendido_por = ventanilla_object.usuario
            ticket_object.fin_en = timezone.localtime(timezone.now())
            ticket_object.save()
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        filter_backends = (DjangoFilterBackend,filters.SearchFilter, filters.OrderingFilter)
        estado = self.request.query_params.get('estado', None)
        servicio = self.request.query_params.get('servicio', None)
        if estado is not None:
            estado = estado.split('|')
            q_part = Q()
            for x in estado:
                q_part = q_part | Q(estado=x)
            queryset = queryset.filter(q_part)

        if servicio is not None:
            servicio = servicio.split('|')
            q_part_s = Q()
            for x in servicio:
                q_part_s = q_part_s | Q(servicio=x)
            queryset = queryset.filter(q_part_s)

        for backend in list(filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        return queryset


class ServicioViewSet(viewsets.ModelViewSet):
    model = Servicio
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    renderer_classes = (EmberJSONRenderer, )
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    filter_backends = (DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter)
    filterset_fields = {'estado':['gte', 'lte', 'exact', 'gt', 'lt'],
                        'subgerencia__id':['gte', 'lte', 'exact', 'gt', 'lt'],
                        'nombre': ['gte', 'lte', 'exact', 'gt', 'lt']}
    search_fields = ['estado', 'nombre', 'subgerencia__nombre','descripcion',]
    ordering_fields = '__all__'
    ordering = ['-creado_en']


class SubgerenciaViewSet(viewsets.ModelViewSet):
    model = Subgerencia
    queryset = Subgerencia.objects.all()
    serializer_class = SubgerenciaSerializer
    renderer_classes = (EmberJSONRenderer, )
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    filter_backends = (DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter)
    filterset_fields = {'nombre':['gte', 'lte', 'exact', 'gt', 'lt'],
                        'estado':['gte', 'lte', 'exact', 'gt', 'lt'],
                        'descripcion':['gte', 'lte', 'exact', 'gt', 'lt'],
                        'serie':['gte', 'lte', 'exact', 'gt', 'lt'],
                        'monitor__id':['gte', 'lte', 'exact', 'gt', 'lt'],}
    search_fields = ['nombre', 'estado', 'descripcion','serie','monitor__id',]
    ordering_fields = '__all__'
    ordering = ['-creado_en']

class MonitorViewSet(viewsets.ModelViewSet):
    model =  Monitor
    queryset =  Monitor.objects.all()
    serializer_class =  MonitorSerializer
    renderer_classes = (EmberJSONRenderer, )
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    filter_backends = (DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter)
    filterset_fields = {'nombre':['gte', 'lte', 'exact', 'gt', 'lt'],
                        'mensaje':['gte', 'lte', 'exact', 'gt', 'lt'],}
    search_fields = ['nombre', 'mensaje',]
    ordering_fields = '__all__'
    ordering = ['-creado_en']


class ConfiguracionViewSet(viewsets.ModelViewSet):
    model =  Configuracion
    queryset =  Configuracion.objects.all()
    serializer_class =  ConfiguracionSerializer
    renderer_classes = (EmberJSONRenderer, )
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    filter_backends = (DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter)
    ordering_fields = '__all__'
    ordering = ['-creado_en']


class AuthToken(ObtainAuthToken):
    renderer_classes = (EmberJSONRenderer, )

    def post(self, request, *args, **kwargs):
        serializer = AuthCustomTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'usuario': UsuarioSerializer(user).data,
        })



class ListTicketMonitor(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    renderer_classes = (EmberJSONRenderer, )

    def get(self, request, format=None):
        subgerencia_id = request.query_params.get('subgerencia_id')
        print(subgerencia_id)
        subgerencia = None
        if Subgerencia.objects.filter(id=subgerencia_id): 
            subgerencia = Subgerencia.objects.get(id=subgerencia_id)
            print(subgerencia)

            subgerencias = Subgerencia.objects.filter(monitor=subgerencia.monitor)
            monitor_obtenido = subgerencia.monitor
            print(subgerencias)
        #subgerencia_id = monitor.subgerencia.id


            tickets_normales = Ticket.objects.filter(preferencial=False, estado='PE', fecha=timezone.localtime(timezone.now()).date(),
                                                 servicio__subgerencia__id__in=subgerencias).order_by('creado_en')[0:5]
            serializer_normales = TicketSerializer(tickets_normales, many=True)
            tickets_preferenciales = Ticket.objects.filter(preferencial=True, estado='PE',fecha=timezone.localtime(timezone.now()).date(),
                                                       servicio__subgerencia__id__in=subgerencias).order_by('creado_en')[0:5]
            serializer_preferenciales = TicketSerializer(tickets_preferenciales, many=True)
            ultimos_llamados = Ticket.objects.filter(fecha=timezone.localtime(timezone.now()).date(),servicio__subgerencia__id__in=subgerencias,fecha_ea__isnull=False).order_by('-fecha_ea')[0:6]
            serializer_ultimos_llamados = TicketSerializer(ultimos_llamados, many=True)


            return Response({'nombre_de_monitor': monitor_obtenido.nombre,
                            'id_de_monitor': monitor_obtenido.id,
                        "tickets_normales":serializer_normales.data,
                         "tickets_preferenciales":serializer_preferenciales.data,
                         "ultimos_llamados": serializer_ultimos_llamados.data
                         })
        return Response({'nombre_de_monitor': '',
                        'id_de_monitor': '',
                        "tickets_normales":'',
                         "tickets_preferenciales":'',
                         "ultimos_llamados": ''
                         },)

class ListTicketParaMonitor(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    renderer_classes = (EmberJSONRenderer, )

    def get(self, request, format=None):
        monitor_id = request.query_params.get('monitor_id')
        print(monitor_id)
        subgerencia = None
        if Monitor.objects.filter(id=monitor_id): 
            monitor = Monitor.objects.get(id=monitor_id)
            print(monitor)

            subgerencias = Subgerencia.objects.filter(monitor=monitor)
            monitor_obtenido = monitor
            print(subgerencias)
        #subgerencia_id = monitor.subgerencia.id


            tickets_normales = Ticket.objects.filter(preferencial=False, estado='PE', fecha=timezone.localtime(timezone.now()).date(),
                                                 servicio__subgerencia__id__in=subgerencias).order_by('creado_en')[0:5]
            serializer_normales = TicketSerializer(tickets_normales, many=True)
            tickets_preferenciales = Ticket.objects.filter(preferencial=True, estado='PE',fecha=timezone.localtime(timezone.now()).date(),
                                                       servicio__subgerencia__id__in=subgerencias).order_by('creado_en')[0:5]
            serializer_preferenciales = TicketSerializer(tickets_preferenciales, many=True)
            ultimos_llamados = Ticket.objects.filter(fecha=timezone.localtime(timezone.now()).date(),servicio__subgerencia__id__in=subgerencias,fecha_ea__isnull=False).order_by('-fecha_ea')[0:6]
            serializer_ultimos_llamados = TicketSerializer(ultimos_llamados, many=True)


            return Response({'nombre_de_monitor': monitor_obtenido.nombre,
                        'id_de_monitor': monitor_obtenido.id,
                        "tickets_normales":serializer_normales.data,
                         "tickets_preferenciales":serializer_preferenciales.data,
                         "ultimos_llamados": serializer_ultimos_llamados.data
                         })
        return Response({'nombre_de_monitor': '',
                        'id_de_monitor': '',
                        "tickets_normales":'',
                         "tickets_preferenciales":'',
                         "ultimos_llamados": ''
                         },)


class ApiConfiguracion(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    renderer_classes = (EmberJSONRenderer, )

    def get(self, request, format=None):
        snippets = Configuracion.objects.all()
        serializer = ConfiguracionSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request):
        con_impresion = request.data.get('con_impresion')
        proporcion = request.data.get('proporcion')
        titulo = request.data.get('titulo')
        descripcion = request.data.get('descripcion')
        email = request.data.get('email')
        direccion = request.data.get('direccion')
        celular = request.data.get('celular')
        derechos_de_autor = request.data.get('derechos_de_autor')
        mensaje_monitor = request.data.get('mensaje-monitor')
        direccion_monitor = request.data.get('direccion-monitor')
        formato_tiempo = request.data.get('formato-tiempo')
        formato_fecha = request.data.get('formato-fecha')
        cantidad_llamadas = request.data.get('cantidad-llamadas')

        if con_impresion:
            configuracion, created = Configuracion.objects.get_or_create(nombre='con_impresion')
            configuracion.valor = con_impresion
            configuracion.save()

        if proporcion:
            configuracion, created = Configuracion.objects.get_or_create(nombre='proporcion')
            configuracion.valor = proporcion
            configuracion.save()

        if titulo:
            configuracion, created = Configuracion.objects.get_or_create(nombre='titulo')
            configuracion.valor = titulo
            configuracion.save()

        if descripcion:
            configuracion, created = Configuracion.objects.get_or_create(nombre='descripcion')
            configuracion.valor = descripcion
            configuracion.save()

        if email:
            configuracion, created = Configuracion.objects.get_or_create(nombre='email')
            configuracion.valor = email
            configuracion.save()

        if direccion:
            configuracion, created = Configuracion.objects.get_or_create(nombre='direccion')
            configuracion.valor = direccion
            configuracion.save()

        if celular:
            configuracion, created = Configuracion.objects.get_or_create(nombre='celular')
            configuracion.valor = celular
            configuracion.save()

        if derechos_de_autor:
            configuracion, created = Configuracion.objects.get_or_create(nombre='derechos_de_autor')
            configuracion.valor = derechos_de_autor
            configuracion.save()
        
        if mensaje_monitor:
            configuracion, created = Configuracion.objects.get_or_create(nombre='mensaje-monitor')
            configuracion.valor = mensaje_monitor
            configuracion.save()
        
        if direccion_monitor:
            configuracion, created = Configuracion.objects.get_or_create(nombre='direccion-monitor')
            configuracion.valor = direccion_monitor
            configuracion.save()

        if formato_tiempo:
            configuracion, created = Configuracion.objects.get_or_create(nombre='formato-tiempo')
            configuracion.valor = formato_tiempo
            configuracion.save()

        if formato_fecha:
            configuracion, created = Configuracion.objects.get_or_create(nombre='formato-fecha')
            configuracion.valor = formato_fecha
            configuracion.save()
        
        if cantidad_llamadas:
            configuracion, created = Configuracion.objects.get_or_create(nombre='cantidad-llamadas')
            configuracion.valor = cantidad_llamadas
            configuracion.save()

        configuraciones = Configuracion.objects.all()
        serializer_configuraciones = ConfiguracionSerializer(configuraciones, many=True)

        return Response(serializer_configuraciones.data)


class VentanillasServicios(APIView, LimitOffsetPagination):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    renderer_classes = (EmberJSONRenderer, )

    def get(self, request):
        search = request.GET.get('search')
        type = request.GET.get('type')

        ventanillas = Ventanilla.objects.all()

        if type == "3":
            ventanillas = Ventanilla.objects.filter(nombre__icontains=search)

        if type == "4":
            ventanillas = Ventanilla.objects.filter(usuario__first_name__icontains=search)

        if type == "5":
            ventanillas = Ventanilla.objects.filter(usuario__id=search)

        lista_datos =[]
        for ventanilla in ventanillas:
            servicios = ventanilla.servicio.all()
            if type == "1":
                servicios = ventanilla.servicio.filter(subgerencia__nombre__icontains=search)
            if type == "2":
                servicios = ventanilla.servicio.filter(nombre__icontains=search)
            for servicio in servicios:
                    lista_datos.append({'ventanilla': ventanilla,'servicio': servicio})


        if request.GET.get('limit') and request.GET.get('offset'):
            limit = int(request.GET.get('limit'))
            offset = int(request.GET.get('offset'))
            resultados = lista_datos[offset:(limit + offset if limit is not None else None)]
        else:
            resultados = lista_datos

        count = len(lista_datos)
        resultados_paginados = VentanillaServicioSerializer(resultados, many=True).data
        respuesta = {"count": count,
                      "results": resultados_paginados
                     }
        return Response(respuesta)

    def delete(self, request, *args, **kwargs):
        ventanilla = get_object_or_404(Ventanilla, pk=kwargs['ventanilla_id'])
        servicio = get_object_or_404(Servicio, pk=kwargs['servicio_id'])
        ventanilla.servicio.remove(servicio)
        if ventanilla.servicio.all().count() == 0:
            ventanilla.usuario = None
            ventanilla.save()
        return Response("Registro eliminado")



class ApiUsuarioServiciosVentanilla(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    renderer_classes = (EmberJSONRenderer, )

    def get(self, request, format=None):
        usuario_id = request.query_params.get('usuario_id')

        try:
            ventanilla = Ventanilla.objects.get(usuario__id=usuario_id)
            ventanilla_serializer = VentanillaSerializer(ventanilla)
        except Ventanilla.DoesNotExist:
            return Response({'ventanilla':  [],
                         "servicios": [],
                         })

        lista_servicios = ventanilla.servicio.all()

        lista_servicios_serializer=ServicioSerializer(lista_servicios, many=True)

        return Response({'ventanilla': ventanilla_serializer.data,
                         "servicios":lista_servicios_serializer.data,
                         })






