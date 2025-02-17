from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

#Base
class Base(models.Model):
    base_dia = models.IntegerField()
    base_observacion = models.CharField(max_length=100, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.base_dia, self.base_observacion, self.usuario.username


#Retiros de caja
class Retiro(models.Model):
    retiro_monto = models.IntegerField()
    retiro_observacion = models.CharField(max_length=100, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.retiro_monto, self.retiro_observacion, self.usuario.username

#Grupos
class Grupo(models.Model):
    nombre_grupo = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre_grupo

#Productos
class Producto(models.Model):
    nombre_producto = models.CharField(max_length=100)
    precio = models.IntegerField()
    descripcion = models.TextField(blank=True, null=True)
    grupo = models.ForeignKey(Grupo, on_delete=models.SET_NULL, null=True, related_name='productos')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre_producto

#Mesas
class Mesa(models.Model):
    numero_mesa = models.IntegerField(unique=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.numero_mesa
    
    @property
    def esta_ocupada(self):
        return self.pedidos.filter(estado_pedido=1).exists()

#Pedidos
class Pedido(models.Model):
    numero_pedido = models.AutoField(primary_key=True)
    mesa = models.ForeignKey('Mesa', on_delete=models.CASCADE, related_name='pedidos')
    productos = models.ManyToManyField('Producto', through='PedidoProducto', related_name='pedidos')  # Relación con el modelo intermedio
    total_pedido = models.IntegerField()
    estado_pedido = models.IntegerField(default=0)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.numero_pedido

class PedidoProducto(models.Model):
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE)  # Relación con Pedido
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)  # Relación con Producto
    cantidad = models.PositiveIntegerField()  # Cantidad de este producto en el pedido

    class Meta:
        unique_together = ('pedido', 'producto')  # Evita duplicados

    def __str__(self):
        return self.pedido.numero_pedido, self.producto.nombre, self.cantidad

#Cierres de caja
class Cierre(models.Model):
    base_cierre = models.IntegerField()
    retiros_cierre = models.IntegerField()
    vEfectivo_cierre = models.IntegerField()
    vNequi_cierre = models.IntegerField()
    vDavip_cierre = models.IntegerField()
    vTotal_cierre = models.IntegerField()
    tCaja_cierre = models.IntegerField()
    us_caja = models.IntegerField()
    obs_cierre = models.CharField(max_length=100, null=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.base_cierre, self.retiros_cierre, self.vEfectivo_cierre, self.vNequi_cierre, self.vDavip_cierre, self.vTotal_cierre, self.tCaja_cierre, self.us_caja, self.obs_cierre   