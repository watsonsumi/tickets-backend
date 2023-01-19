from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models
from datetime import datetime, date


# Modelos.
from django.utils import timezone


class Monitor(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length= 255, null= True, blank=True)
    creado_en = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    actualizado_en = models.DateTimeField(blank=True, null=True,auto_now=True)
    mensaje = models.CharField(max_length= 100, null= True, blank=True)


    def __str__(self):
        return self.nombre or ''

    class Meta:
        verbose_name = "Monitor"
        verbose_name_plural = "Monitores"

class Subgerencia(models.Model):
    id = models.AutoField(primary_key=True)
    creado_en = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    actualizado_en = models.DateTimeField(blank=True, null=True,auto_now=True)
    nombre = models.CharField(max_length= 100, null= False, blank=False, unique= True)
    descripcion = models.CharField(max_length= 200, null= True, blank=True)
    serie = models.CharField(max_length= 2, null= False, blank=False,unique= True)
    estado = models.BooleanField(blank=False)
    monitor = models.ForeignKey(Monitor,on_delete = models.SET_NULL,null=True)


    def __str__(self):
        return self.nombre or ''

    class Meta:
        verbose_name = "Subgerencia"
        verbose_name_plural = "Subgerencias"


class Talonario(models.Model):
    id = models.AutoField(primary_key=True)
    fecha_de_registro = models.DateField(blank=True, null=True, auto_now_add=True)
    subgerencia = models.ForeignKey(Subgerencia,on_delete = models.SET_NULL,null=True)
    numero_actual = models.IntegerField(null= False, blank=False, default=0)


class Servicio(models.Model):
    id = models.AutoField(primary_key=True)
    creado_en = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    actualizado_en = models.DateTimeField(blank=True, null=True,auto_now=True)
    nombre = models.CharField(max_length= 50, null= False, blank=False, unique= True)
    descripcion = models.CharField(max_length= 200, null= True, blank=True)
    estado = models.BooleanField(blank=False)
    subgerencia = models.ForeignKey(Subgerencia,on_delete = models.SET_NULL,null=True, blank=False)

    def __str__(self):
        return self.nombre or ''

    class Meta:
        verbose_name = "Servicios"
        verbose_name_plural = "Servicios"


class Usuario(AbstractUser):
    TIPOS_USUARIO = [
        ('AS', 'Asesor'),
        ('RE', 'Recepcionista'),
        ('AD', 'Administrador'),
        ('SU', 'Subgerente'),
        ('MO', 'Monitor'),
    ]
    celular = models.IntegerField(blank=True, null=True)
    tipo_de_usuario = models.CharField(
        max_length=2,
        choices=TIPOS_USUARIO,
        default='AD',
    )

    subgerencia = models.ForeignKey(Subgerencia, on_delete = models.SET_NULL,null=True)


    @property
    def estado(self):
        return self.is_active


    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"



class Ventanilla(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length= 100,null= False, blank=False,unique=True)
    creado_en = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    actualizado_en = models.DateTimeField(blank=True, null=True,auto_now=True)
    estado = models.BooleanField(blank=False)
    servicio = models.ManyToManyField(Servicio, related_name="servicios",blank=True)
    usuario = models.ForeignKey(Usuario, on_delete = models.SET_NULL,null=True)
    ocupada = models.BooleanField(default=False)
    contador_normal= models.IntegerField(blank=True, null=True, default=0)
    contador_preferencial= models.IntegerField(blank=True, null=True, default=0)
    contador_total= models.IntegerField(blank=True, null=True, default=0)

    def __str__(self):
        return str(self.nombre) or ''

    class Meta:
        verbose_name = "Ventanilla"
        verbose_name_plural = "Ventanillas"

    def get_servicios(self):
        return ",".join([str(p) for p in self.servicio.all()])

class Ticket(models.Model):
    ESTADOS = [
        ('CO', 'Completado'),
        ('PE', 'Pendiente'),
        ('EA', 'En Atencion'),
        ('CA', 'Cancelado')
    ]
    id = models.AutoField(primary_key=True)
    creado_en = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    fecha = models.DateField(blank=True, null=True, default = timezone.localtime(timezone.now()).date())
    fin_en = models.DateTimeField(blank=True, null=True)
    fecha_ea = models.DateTimeField(blank=True, null=True,)
    ticket_nro = models.CharField(max_length= 10, null= False, blank=True)
    derivado = models.IntegerField(default=0)
    preferencial = models.BooleanField(default=False)
    nombres = models.CharField(max_length= 50, null= True, blank=True)
    apellidos = models.CharField(max_length= 50, null= True, blank=True)
    dni = models.CharField(blank=True, null=True,max_length= 8)
    ruc = models.CharField(blank=True, null=True,max_length= 11)
    razon_social = models.CharField(max_length= 100, null= True, blank=True)
    servicio = models.ForeignKey(Servicio,on_delete = models.SET_NULL,null=True)
    atendido_por = models.ForeignKey(Usuario, on_delete = models.SET_NULL,null=True, blank=True)

    ventanilla = models.ForeignKey(Ventanilla, on_delete = models.SET_NULL,null=True,blank=True)
    estado = models.CharField(
        max_length=2,
        choices=ESTADOS,
        default='PE',
    )

    def __str__(self):
        return self.ticket_nro or ''

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"

    def save(self, *args, **kwargs):

        if(self.estado=='PE'):
            subgerencia = self.servicio.subgerencia
            talonario,creado = Talonario.objects.get_or_create(subgerencia=subgerencia,fecha_de_registro=timezone.localtime(timezone.now()).date())
            if creado:
                Ventanilla.objects.filter(servicio__subgerencia=subgerencia).update(ocupada=0,contador_preferencial=0,contador_normal=0)

            if self.derivado==0:
                talonario.numero_actual = talonario.numero_actual + 1
                talonario.save()
                self.ticket_nro = subgerencia.serie + str(talonario.numero_actual).zfill(4)

            self.fecha = timezone.localtime(timezone.now()).date()
            self.fin_en = timezone.localtime(timezone.now())

        servicios = []
        if Ventanilla.objects.filter(estado=True,ocupada=False,servicio=self.servicio).count()>0:
            ventanilla_filtro = Ventanilla.objects.filter(estado=True,ocupada=False,servicio=self.servicio).first()
            servicios = ventanilla_filtro.servicio.all()
        if(self.estado=='PE' and Ticket.objects.filter(estado='PE',servicio__in=servicios,fecha=timezone.localtime(timezone.now()).date()).count()==0 and
            Ventanilla.objects.filter(estado=True,ocupada=False,servicio=self.servicio).count())>0:
            ventanilla_libre = Ventanilla.objects.filter(estado=True,ocupada=False,servicio=self.servicio).first()
            self.ventanilla = ventanilla_libre
            ventanilla_libre.ocupada = True
            if self.preferencial == 0:
                ventanilla_libre.contador_normal+=1
            if self.preferencial == 1:
                ventanilla_libre.contador_preferencial+=1

            self.fecha_ea = timezone.localtime(timezone.now())
            self.estado = 'EA'
            self.fin_en = timezone.localtime(timezone.now())
            ventanilla_libre.save()

        super(Ticket, self).save(*args, **kwargs)




class Configuracion(models.Model):
    id = models.AutoField(primary_key=True)
    creado_en = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    actualizado_en = models.DateTimeField(blank=True, null=True,auto_now=True)
    nombre = models.CharField(null= False, blank=False, max_length=100)
    valor = models.CharField(null= False, blank=False, max_length=200)

    def __str__(self):
        return self.nombre or ''

    class Meta:
        verbose_name = "Congiguracion"
        verbose_name_plural = "Configuraciones"


