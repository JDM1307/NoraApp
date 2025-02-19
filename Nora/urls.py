from django.urls import path
from . import views

urlpatterns = [
    #Index
    path('', views.index, name='index'),
    path('api/mesas/', views.obtener_mesas, name='obtener_mesas'),

    #Base
    path('bases/', views.gestionar_bases, name='gestionar_bases'),
    path('bases/agregar/', views.agregar_base, name='agregar_base'),
    path('bases/editar/<int:base_id>/', views.editar_base, name='editar_base'),

    #Retiros
    path('retiros/', views.gestionar_retiros, name='gestionar_retiros'),
    path('retiros/agregar/', views.agregar_retiro, name='agregar_retiro'),
    path('retiros/editar/<int:retiro_id>/', views.editar_retiro, name='editar_retiro'),
    path('retiros/eliminar/<int:retiro_id>/', views.eliminar_retiro, name='eliminar_retiro'),

    #Arqueos
    path('arqueos/', views.arqueo_caja, name='arqueo_caja'),

    #Productos
    path('productos/', views.gestionar_productos, name='gestionar_productos'),
    path('productos/agregar/', views.agregar_producto, name='agregar_producto'),
    path('productos/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    
    #Grupos
    path('grupos/', views.gestionar_grupos, name='gestionar_grupos'),
    path('grupos/agregar/', views.agregar_grupo, name='agregar_grupo'),
    path('grupos/editar/<int:grupo_id>/', views.editar_grupo, name='editar_grupo'),
    path('grupos/eliminar/<int:grupo_id>/', views.eliminar_grupo, name='eliminar_grupo'),

    #Mesas
    path('mesas/', views.gestionar_mesas, name='gestionar_mesas'),
    path('mesas/agregar/', views.agregar_mesa, name='agregar_mesa'),
    path('mesas/editar/<int:mesa_id>/', views.editar_mesa, name='editar_mesa'),
    path('mesas/eliminar/<int:mesa_id>/', views.eliminar_mesa, name='eliminar_mesa'),

    #Pedidos
    path('pedidos/', views.gestionar_pedidos, name='gestionar_pedidos'),
    path('pedidos/agregar/<int:numero_mesa>/', views.agregar_pedido, name='agregar_pedido'),
    path('pedidos/ver/<int:numero_pedido>/', views.ver_pedido, name='ver_pedido'),
    path('pedidos/editar/<int:numero_pedido>/', views.editar_pedido, name='editar_pedido'),
    path('pedidos/eliminar/<int:numero_pedido>/', views.eliminar_pedido, name='eliminar_pedido'),

    #Cierres
    path('cierres/', views.gestionar_cierres, name='gestionar_cierres'),
    path('cierres/agregar/', views.agregar_cierre, name='agregar_cierre'),
    path('cierres/editar/<int:cierre_id>/', views.editar_cierre, name='editar_cierre'),

]