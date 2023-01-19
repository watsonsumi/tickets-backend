from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from appticket.models import Ticket, Servicio, Subgerencia, Usuario, Ventanilla, Monitor, Configuracion
from rest_framework.generics import get_object_or_404
from rest_framework import viewsets


class SubgerenciaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subgerencia
        fields = ('id','creado_en','actualizado_en','nombre','descripcion','serie','estado','monitor')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['monitor'] = MonitorSerializer(instance.monitor).data
        return response


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ('id','creado_en','actualizado_en','nombre','descripcion','subgerencia','estado')


    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['subgerencia'] = SubgerenciaSerializer(instance.subgerencia).data
        return response

class TalonarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ventanilla
        fields = ('id','fecha_de_registro','numero_actual','subgerencia')

class VentanillaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ventanilla
        fields = ('id','nombre','creado_en','actualizado_en','estado','usuario','ocupada','servicio')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['usuario'] = UsuarioSerializer(instance.usuario).data
        return response

class VentanillaServicioSerializer(serializers.Serializer):
    ventanilla = VentanillaSerializer()
    servicio = ServicioSerializer()


class UsuarioSerializer(serializers.ModelSerializer):
    creado_en = serializers.SerializerMethodField()
    actualizado_en = serializers.SerializerMethodField()
    estado = serializers.BooleanField(source='is_active')
    nombres = serializers.CharField(source='first_name')
    apellidos = serializers.CharField(source='last_name')
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            if self.context['request'].method in ['GET']:
                self.fields['tipo_de_usuario'] = serializers.SerializerMethodField()
        except KeyError:
            pass

    class Meta:
        model = Usuario
        fields = ('id','email', 'password','password2','creado_en', 'actualizado_en','nombres','apellidos',
                  'celular', 'tipo_de_usuario','estado','subgerencia')

    def validate(self, attrs):
        password1 = attrs.get('password1') or ''
        password2 = attrs.get('password2') or ''
        if password1 and password2:
            if attrs['password'] != attrs['password2']:
                raise serializers.ValidationError({"password": "Passwords no coinciden"})


        email = attrs.get('email') or ''
        if email:
            try:
                if self.partial == True:
                    users = Usuario.objects.exclude(email=attrs['email'])
                    user = users.get(email=attrs['email'])
                else:
                    user = Usuario.objects.get(email=attrs['email'])
            except Usuario.DoesNotExist:
                user = None
            if user:
                raise serializers.ValidationError({"email": "Ya existe este email"})

        return attrs

    def create(self, validated_data):
        user = Usuario.objects.create(
        email=validated_data['email'],
        username=validated_data['email'],
        celular=validated_data['celular'],
        is_active=validated_data['is_active'],
        first_name=validated_data['first_name'],
        last_name=validated_data['last_name'],
        tipo_de_usuario=validated_data['tipo_de_usuario'],
        subgerencia=validated_data['subgerencia'],
    )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        user = instance

        if "email" in validated_data:
            user.email=validated_data['email']
            user.username=validated_data['email']
        if "celular" in validated_data: user.celular=validated_data['celular']
        if "is_active" in validated_data: user.is_active=validated_data['is_active']
        if "first_name" in validated_data: user.first_name=validated_data['first_name']
        if "last_name" in validated_data: user.last_name=validated_data['last_name']
        if "tipo_de_usuario" in validated_data: user.tipo_de_usuario=validated_data['tipo_de_usuario']
        if "subgerencia" in validated_data: user.subgerencia=validated_data['subgerencia']

        if "password" in validated_data:
            user.set_password(validated_data['password'])
        user.save()
        return user


    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['subgerencia'] = SubgerenciaSerializer(instance.subgerencia).data
        return response

    def get_actualizado_en(self, obj):
        return obj.last_login

    def get_creado_en(self, obj):
        return obj.date_joined

    def get_tipo_de_usuario(self, obj):
        return obj.get_tipo_de_usuario_display()


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('id','creado_en','fecha','fecha_ea','fin_en','ruc','razon_social','ticket_nro','derivado','preferencial','nombres','apellidos','dni',
                  'servicio','ventanilla', 'estado')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['servicio'] = ServicioSerializer(instance.servicio).data
        response['ventanilla'] = VentanillaSerializer(instance.ventanilla).data
        return response



class MonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitor
        fields = ('id','creado_en','actualizado_en','nombre','mensaje')


class ConfiguracionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuracion
        fields = ('id','creado_en','actualizado_en','nombre','valor')


def validateEmail( email ):
    try:
        validate_email( email )
        return True
    except ValidationError:
        return False

class AuthCustomTokenSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Check if user sent email
            if validateEmail(email):
                try:
                    user_request = Usuario.objects.get(email=email)
                except Usuario.DoesNotExist:
                    msg = {'email': ['El email no existe.',]}
                    raise exceptions.ValidationError(msg)

                email = user_request.username
                user = authenticate(username=email, password=password)

                if user:
                    if not user.is_active:
                        msg = ('Tue cuenta esta desabilitada.')
                        raise exceptions.ValidationError(msg)
                else:
                    msg = ('No podemos iniciar session con estas credenciales.')
                    raise exceptions.ValidationError(msg)
            else:
                msg = {'email': ['El email no es valido.',]}
                raise exceptions.ValidationError(msg)
        else:
            msg = ('Debes incluir tu email y tu password"')
            raise exceptions.ValidationError(msg)

        attrs['user'] = user
        return attrs