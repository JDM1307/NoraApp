from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import DatabaseError, IntegrityError
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import localtime, now, make_aware
from datetime import datetime, timedelta
import json
from .models import Producto, Grupo, Mesa, Pedido, PedidoProducto, Base, Retiro, Cierre

#LOGIN
def login(request):
    try:
        if request.method == 'POST':
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                auth_login(request, user)
                hoy = localtime(now()).date()
                inicio_dia = make_aware(datetime.combine(hoy, datetime.min.time()))  # 00:00:00
                fin_dia = make_aware(datetime.combine(hoy, datetime.max.time()))    # 23:59:59
                base_hoy = Base.objects.filter(
                    creado_en__range=(inicio_dia, fin_dia)
                ).exists()
                messages.success(request, f'{user.username} Ha iniciado sesion')
                if base_hoy:
                    return redirect('index')
                else:
                    return redirect('agregar_base')
            else:
                messages.error(request, 'Usuario y/o contraseña incorrectos')
        else:
            form = AuthenticationForm()
    except Exception as e:
        messages.error(request, f'Ocurrió un error: {e}')
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    return render(request, 'registration/login.html', {'form': form})


#INDEX
@login_required
def index(request):
    try:
        mesas = Mesa.objects.all().order_by('numero_mesa')

        # Agregar total_pedido y responsable a cada mesa si tiene un pedido asociado
        for mesa in mesas:
            if mesa.pedido_asociado:
                pedido = Pedido.objects.filter(numero_pedido=mesa.pedido_asociado).first()
                mesa.total_pedido = pedido.total_pedido if pedido else None
                mesa.responsable = pedido.usuario if pedido else "?"
            else:
                mesa.total_pedido = None
                mesa.responsable = "?"

        return render(request, 'index/index.html', {'mesas': mesas})

    except Exception as e:
        messages.error(request, f'Ocurrió un error: {e}')
        return render(request, 'errores/error_general.html', {'error_message': str(e)})

def obtener_mesas(request):
    mesas = Mesa.objects.all().order_by('numero_mesa')
    data = []

    for mesa in mesas:
        pedido = Pedido.objects.filter(numero_pedido=mesa.pedido_asociado).first() if mesa.pedido_asociado else None
        data.append({
            'numero_mesa': mesa.numero_mesa,
            'estado_mesa': mesa.estado_mesa,
            'responsable': pedido.usuario.username if pedido else "?",
            'total_pedido': pedido.total_pedido if pedido else 0
        })

    return JsonResponse({'mesas': data})


#BASE 
@login_required
def gestionar_bases(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    try:
        base = Base.objects.all().order_by('-creado_en')
        if fecha_inicio and fecha_fin:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            base = base.filter(creado_en__range=[fecha_inicio_dt, fecha_fin_dt])
    except Exception as e:
        messages.error(request, f'Hubo un error: {e}')
    return render(request, 'bases/gestionar_bases.html', {'base': base})

@login_required
def agregar_base(request):
    if request.method == 'POST':  
        valor = request.POST.get('base_dia')
        observacion = request.POST.get('base_observacion')

        # Validar que el valor sea un número y no esté vacío
        try:
            valor = int(valor)  # Convertir a entero
            if valor < 0:  # Verificar que no sea negativo
                raise ValueError
        except (ValueError, TypeError):
            messages.warning(request, 'Ingrese un valor numérico válido para la base.')
            return redirect('agregar_base')

        # Obtener la fecha actual en la zona horaria local
        hoy = localtime(now()).date()

        # Definir el rango de búsqueda (inicio y fin del día)
        inicio_dia = make_aware(datetime.combine(hoy, datetime.min.time()))  # 00:00:00
        fin_dia = make_aware(datetime.combine(hoy, datetime.max.time()))    # 23:59:59

        # Verificar si el usuario ya tiene una base registrada hoy
        existe_base = Base.objects.filter(creado_en__range=(inicio_dia, fin_dia)).exists()

        if existe_base:
            messages.error(request, "Ya existe una base para hoy")
            return redirect('index')

        try:
            base = Base(
                base_dia=valor,  # Ya convertido a entero
                base_observacion=observacion,
                usuario=request.user
            )
            base.save()
            messages.success(request, "Base grabada exitosamente.")
            return redirect('index')
        except Exception as e:
            messages.error(request, f'Hubo un error: {e}')

    return render(request, 'bases/agregar_base.html')

@login_required
def editar_base(request, base_id):
    base = get_object_or_404(Base, id=base_id)
    if request.method == 'POST':    
        valor = request.POST.get('base_dia')
        observacion = request.POST.get('base_observacion')
        usuario = request.user
        try: 
            if valor:
                base.base_dia = int(valor) 
            if observacion is not None:
                base.base_observacion = observacion
            base.usuario = usuario
            base.save()
        except Exception as e:
            messages.error(request, f'Hubo un error: {e}')

        messages.success(request, "Base actualizada exitosamente.")
        return redirect('gestionar_bases') 

    return render(request, 'bases/editar_base.html', {'base': base})


#RRETIROS DE CAJA
@login_required
def gestionar_retiros(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    try:
        retiros = Retiro.objects.all().order_by('-creado_en')
        if fecha_inicio and fecha_fin:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            retiros = retiros.filter(creado_en__range=[fecha_inicio_dt, fecha_fin_dt])
    except Exception as e:
        messages.error(request, f'Hubo un error: {e}')
    return render(request, 'retiros/gestionar_retiros.html', {'retiros': retiros})

@login_required
def agregar_retiro(request):
    if request.method == 'POST':
        valor = request.POST.get('retiro_monto')
        observacion = request.POST.get('retiro_observacion')

        if valor and observacion:
            try:
                retiro = Retiro(
                    retiro_monto=int(valor),
                    retiro_observacion=observacion,
                    usuario=request.user
                )
                retiro.save()
                messages.success(request, 'Retiro grabado exitosamente.')
                return redirect('gestionar_retiros')
            except Exception as e:
                messages.error(request, f'Hubo un error: {e}')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    return render(request, 'retiros/agregar_retiro.html')

@login_required
def editar_retiro(request, retiro_id):
    retiro = get_object_or_404(Retiro, id=retiro_id)
    if request.method == 'POST':
        valor = request.POST.get('retiro_monto')
        observacion = request.POST.get('retiro_observacion')
        usuario = request.user

        if valor and observacion:
            try:
                retiro.retiro_monto = int(valor)
                retiro.retiro_observacion = observacion
                retiro.usuario = usuario
                retiro.save()
                messages.success(request, 'Retiro actualizado exitosamente.')
                return redirect('gestionar_retiros')
            except Exception as e:
                messages.error(request, f'Hubo un error: {e}')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    else:
        return render(request, 'retiros/editar_retiro.html', {
            'retiro': retiro,
            'retiro_monto': retiro.retiro_monto,
            'retiro_observacion': retiro.retiro_observacion
        })

    return render(request, 'retiros/editar_retiro.html', {'retiro': retiro})

@login_required
def eliminar_retiro(request, retiro_id):
    retiro = get_object_or_404(Retiro, id=retiro_id)
    try:
        retiro.delete()
        messages.success(request, 'Retiro eliminado exitosamente.')
    except Exception as e:
        messages.error(request, f'Hubo un error: {e}')
    return redirect('gestionar_retiros')


#ARQUEO DE CAJA
@login_required
def arqueo_caja(request):
    hoy = localtime(now()).date()  # Fecha actual en la zona horaria local

    # Obtener fechas del GET y manejar el caso en que sean vacías
    fecha_inicio = request.GET.get("fecha_inicio") or hoy.strftime("%Y-%m-%d")
    fecha_fin = request.GET.get("fecha_fin") or hoy.strftime("%Y-%m-%d")

    try:
        # Convertir a datetime solo si no están vacías
        fecha_inicio = make_aware(datetime.strptime(fecha_inicio, "%Y-%m-%d"))
        fecha_fin = make_aware(datetime.strptime(fecha_fin, "%Y-%m-%d")).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        # Filtrar registros en el rango de fechas
        base = Base.objects.filter(creado_en__range=(fecha_inicio, fecha_fin))
        retiros = Retiro.objects.filter(creado_en__range=(fecha_inicio, fecha_fin))

        total_base = base.aggregate(total=Sum('base_dia'))['total'] or 0 #total bases
        total_retiros = retiros.aggregate(total=Sum('retiro_monto'))['total'] or 0 #total de retiros
        total_efectivo = Pedido.objects.filter(
            creado_en__range=(fecha_inicio, fecha_fin), estado_pedido=2
        ).aggregate(total=Sum('total_pedido'))['total'] or 0 #total de efectivo
        total_nequi = Pedido.objects.filter(
            creado_en__range=(fecha_inicio, fecha_fin), estado_pedido=3
        ).aggregate(total=Sum('total_pedido'))['total'] or 0 #total de nequi
        total_davip = Pedido.objects.filter(
            creado_en__range=(fecha_inicio, fecha_fin), estado_pedido=4
        ).aggregate(total=Sum('total_pedido'))['total'] or 0 #total de daviplata
        total_ventas = total_efectivo + total_nequi + total_davip #total de ventas
        total_caja = (total_base + total_efectivo) - total_retiros
    except Exception as e:
        messages.error(request, f'Hubo un error: {e}')
        return render(request, 'errores/error_general.html', {'error_message': str(e)})

    return render(request, 'arqueos/arqueo_caja.html', {
        'total_base': total_base,
        'total_retiros': total_retiros,
        'total_ventas': total_ventas,
        'total_efectivo': total_efectivo,
        'total_nequi': total_nequi,
        'total_davip': total_davip,
        'total_caja': total_caja,
        'fecha_inicio': fecha_inicio.date(),  # Pasar la fecha seleccionada a la plantilla
        'fecha_fin': fecha_fin.date(),
    })


#PRODUCTOS
@login_required
def gestionar_productos(request):
    query = request.GET.get('q', '')
    grupo_id = request.GET.get('grupo', '')
    try:
        productos = Producto.objects.filter(grupo__isnull=False)
        if query:
            productos = productos.filter(nombre_producto__icontains=query)
        if grupo_id:
            productos = productos.filter(grupo_id=grupo_id)
        productos = productos.order_by('nombre_producto')
    except DatabaseError as e:
        messages.error(request, f'Error en BD {e}')
        productos = []

    grupos = Grupo.objects.all()
    return render(request, 'productos/gestionar_productos.html', {
        'productos': productos,
        'query': query,
        'grupos': grupos,
        'grupo_id': grupo_id
    })

@login_required
def agregar_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_producto')
        precio = request.POST.get('precio_producto')
        descripcion = request.POST.get('descripcion_producto')
        grupo_id = request.POST.get('grupo_producto')

        if nombre and descripcion and precio and grupo_id:
            try:
                precio = int(precio)
                grupo = Grupo.objects.get(id=grupo_id)
                producto = Producto(
                    nombre_producto=nombre,
                    descripcion=descripcion,
                    precio=precio,
                    grupo=grupo
                )
                producto.save()
                messages.success(request, 'Producto agregado exitosamente.')
                return redirect('gestionar_productos')
            except Grupo.DoesNotExist:
                messages.error(request, 'El grupo seleccionado no existe.')
            except ValueError:
                messages.error(request, 'El precio ingresado no es válido.')
            except DatabaseError as e:
                messages.error(request, f'Error en BD: {e}')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')

    grupos = Grupo.objects.all()
    return render(request, 'productos/agregar_producto.html', {'grupos': grupos})

@login_required
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        nombre = request.POST.get('nombre_producto')
        precio = request.POST.get('precio_producto')
        descripcion = request.POST.get('descripcion_producto')
        grupo_id = request.POST.get('grupo_producto')

        if nombre and descripcion and precio and grupo_id:
            try:
                precio = int(precio)
                grupo = Grupo.objects.get(id=grupo_id)
                producto.nombre_producto = nombre
                producto.descripcion = descripcion
                producto.precio = precio
                producto.grupo = grupo
                producto.save()
                messages.success(request, 'Producto actualizado exitosamente.')
                return redirect('gestionar_productos')
            except Grupo.DoesNotExist:
                messages.error(request, 'El grupo seleccionado no existe.')
            except ValueError:
                messages.error(request, 'El precio ingresado no es válido.')
            except DatabaseError as e:
                messages.error(request, f'Error en BD: {e}')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    else:
        grupos = Grupo.objects.all()
        return render(request, 'productos/editar_producto.html', {
            'producto': producto,
            'grupos': grupos,
            'nombre_producto': producto.nombre_producto,
            'descripcion_producto': producto.descripcion,
            'precio_producto': producto.precio,
            'grupo_producto': producto.grupo.id
        })

    grupos = Grupo.objects.all()
    return render(request, 'productos/editar_producto.html', {
        'producto': producto,
        'grupos': grupos
    })

@login_required
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    try:
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente.')
    except DatabaseError as e:
        messages.error(request, f'Error en BD: {e}')
    return redirect('gestionar_productos')


#GRUPOS
@login_required
def gestionar_grupos(request):
    query = request.GET.get('q' , '')
    try:
        if query:
            grupos = Grupo.objects.filter(nombre_grupo__icontains=query)
        else:
            grupos = Grupo.objects.all()
        grupos = grupos.order_by('nombre_grupo')
    except DatabaseError as e:
        messages.error(request, f'Error en BD: {e}')
        grupos = []
    return render(request, 'grupos/gestionar_grupos.html', {'grupos': grupos})

@login_required
def agregar_grupo(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_grupo')

        if nombre:
            try:
                grupo = Grupo(nombre_grupo=nombre)
                grupo.save()
                messages.success(request, 'Grupo agregado exitosamente.')
                return redirect('gestionar_grupos')
            except DatabaseError as e:
                messages.error(request, f'Error en BD: {e}')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    return render(request, 'grupos/agregar_grupo.html')
        
@login_required
def editar_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    if request.method == 'POST':
        nombre = request.POST.get('nombre_grupo')

        if nombre:
            try:
                grupo.nombre_grupo = nombre
                grupo.save()
                messages.success(request, 'Grupo actualizado exitosamente.')
                return redirect('gestionar_grupos')
            except DatabaseError as e:
                messages.error(request, 'Error en BD: {e}')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    else:
        return render(request, 'grupos/editar_grupo.html', {
            'grupo': grupo,
            'nombre_grupo': grupo.nombre_grupo
            })

    return render(request, 'grupos/editar_grupo.html', {'grupo': grupo})

@login_required
def eliminar_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    try:
        grupo.delete()
        messages.success(request, 'Grupo eliminado exitosamente.')
    except DatabaseError as e:
        messages.error(request, f'Error en BD: {e}')
    return redirect('gestionar_grupos')


#MESAS
@login_required
def gestionar_mesas(request):
    query = request.GET.get('q' , '')
    try:
        if query:
            mesas = Mesa.objects.filter(numero_mesa__icontains=query).order_by('numero_mesa')
        else:
            mesas = Mesa.objects.all().order_by('numero_mesa')
    except DatabaseError as e:
        messages.error(request, f'Error en BD: {e}')
        mesas = []
    return render(request, 'mesas/gestionar_mesas.html', {'mesas': mesas})

@login_required
def agregar_mesa(request):
    if request.method == 'POST':
        numero = request.POST.get('numero_mesa')

        if numero:
            try:
                mesa = Mesa(numero_mesa=numero)
                mesa.save()
                messages.success(request, 'Mesa agregada exitosamente.')
                return redirect('gestionar_mesas')
            except IntegrityError:
                messages.warning(request, 'Esta mesa ya existe')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    return render(request, 'mesas/agregar_mesa.html')

@login_required
def editar_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    if request.method == 'POST':
        numero = request.POST.get('numero_mesa')

        if numero:
            try:
                mesa.numero_mesa = numero
                mesa.save()
                messages.success(request, 'Mesa actualizada exitosamente.')
                return redirect('gestionar_mesas')
            except IntegrityError:
                messages.warning(request, 'Esta mesa ya existe')
            except DatabaseError as e:
                messages.error(request, f'Error en BD: {e}')
        else:
            messages.error(request, 'Por favor, completa todos los campos.')
    else:
        return render(request, 'mesas/editar_mesa.html', {
            'mesa': mesa,
            'numero_mesa': mesa.numero_mesa
            })

    return render(request, 'mesas/editar_mesa.html', {'mesa': mesa})

@login_required
def eliminar_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    try:
        mesa.delete()
        messages.success(request, 'Mesa eliminada exitosamente.')
    except DatabaseError as e:
        messages.error(request, f'Error en BD: {e}')
    return redirect('gestionar_mesas')


#PEDIDOS
@login_required
def gestionar_pedidos(request):
    query = request.GET.get('q', '')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    medio_pago = request.GET.get('medio_pago')  # Capturar estado seleccionado

    try:
        pedidos = Pedido.objects.all().order_by('-numero_pedido')

        if query:
            pedidos = pedidos.filter(numero_pedido__icontains=query)

        if fecha_inicio and fecha_fin:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            pedidos = pedidos.filter(creado_en__range=[fecha_inicio_dt, fecha_fin_dt])

        if medio_pago in ['2', '3', '4']:  # Filtrar solo si el estado es válido
            pedidos = pedidos.filter(estado_pedido=medio_pago)

    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        pedidos = []

    return render(request, 'pedidos/gestionar_pedidos.html', {
        'pedidos': pedidos,
        'query': query,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'estado_pedido': medio_pago  # Pasar el estado seleccionado a la plantilla
    })
    
@login_required
def agregar_pedido(request, numero_mesa=None):
    if request.method == 'POST':
        mesa_id = request.POST.get('mesa')
        estado = request.POST.get('estado')
        nuevos_productos = request.POST.get('productos')

        # Verificar que hay datos en productos
        if not nuevos_productos:
            messages.warning(request, 'Debe seleccionar al menos 1 producto')
            return redirect('agregar_pedido')

        try:
            productos = json.loads(nuevos_productos)
        except json.JSONDecodeError:
            messages.error(request, 'Error en el formato de productos')
            return redirect('agregar_pedido')

        if mesa_id and productos and estado:
            try:
                mesa = get_object_or_404(Mesa, numero_mesa=mesa_id)

                # Obtener el siguiente número de pedido
                ultimo_pedido = Pedido.objects.order_by('numero_pedido').last()
                siguiente_numero_pedido = ultimo_pedido.numero_pedido + 1 if ultimo_pedido else 1

                pedido = Pedido.objects.create(
                    numero_pedido=siguiente_numero_pedido,
                    mesa=mesa,
                    total_pedido=0,  # Se actualizará después
                    estado_pedido=int(estado),
                    usuario=request.user
                )

                total_pedido = 0
                for producto_id, cantidad in productos.items():
                    try:
                        cantidad = int(cantidad)
                        if cantidad > 0:
                            producto = get_object_or_404(Producto, id=producto_id)
                            PedidoProducto.objects.create(pedido=pedido, producto=producto, cantidad=cantidad)
                            total_pedido += producto.precio * cantidad
                    except (ValueError, Producto.DoesNotExist):
                        messages.error(request, f'Error con el producto ID {producto_id}')
                        return redirect('agregar_pedido')

                # Actualizar total del pedido
                pedido.total_pedido = total_pedido
                pedido.save()

                # Actualizar estado de la mesa
                if int(estado) != 1:
                    mesa.estado_mesa = 0
                    mesa.pedido_asociado = None
                    messages.success(request, 'Pedido finalizado exitosamente')
                else:
                    mesa.estado_mesa = 1
                    mesa.pedido_asociado = siguiente_numero_pedido
                    messages.info(request, 'Pedido comandado exitosamente')

                mesa.save()
                return redirect('index')

            except Exception as e:
                messages.error(request, f'Error inesperado: {str(e)}')
        else:
            messages.warning(request, 'Debe seleccionar al menos 1 producto')

    # Método GET: Cargar datos para la plantilla
    grupos = Grupo.objects.all().order_by('nombre_grupo')
    productos = Producto.objects.all().order_by('nombre_producto')
    ultimo_pedido = Pedido.objects.order_by('numero_pedido').last()
    siguiente_numero_pedido = ultimo_pedido.numero_pedido + 1 if ultimo_pedido else 1

    return render(request, 'pedidos/agregar_pedido.html', {
        'grupos': grupos,
        'productos': productos,
        'mesa_seleccionada': numero_mesa,
        'siguiente_numero_pedido': siguiente_numero_pedido
    })

@login_required
def ver_pedido(request, numero_pedido):
    pedido = Pedido.objects.get(numero_pedido=numero_pedido)
    productos_con_cantidades = []
    try:
        # Recorrer los productos del pedido y obtener la cantidad de la tabla intermedia
        for producto in pedido.productos.all():
            cantidad = PedidoProducto.objects.get(pedido=pedido, producto=producto).cantidad
            total_producto = producto.precio * cantidad
            productos_con_cantidades.append({
                'producto': producto,
                'cantidad': cantidad,
                'total_producto': total_producto
            })
    except DatabaseError as e:
        messages.error(request, f'Error en BD: {e}')
    # Pasar los productos con sus cantidades al contexto
    return render(request, 'pedidos/ver_pedido.html', {
        'pedido': pedido,
        'productos_con_cantidades': productos_con_cantidades,
    })

@login_required
def editar_pedido(request, numero_pedido):
    pedido = get_object_or_404(Pedido, numero_pedido=numero_pedido)

    if request.method == 'POST':
        nuevos_productos = request.POST.get('productos')
        mesa_pedido = request.POST.get('mesa')
        estado = request.POST.get('estado')

        if not nuevos_productos:
            messages.warning(request, 'Debe seleccionar al menos 1 producto')
            return redirect('editar_pedido', numero_pedido=numero_pedido)

        try:
            productos = json.loads(nuevos_productos)
        except json.JSONDecodeError:
            messages.error(request, 'Error en el formato de productos')
            return redirect('editar_pedido', numero_pedido=numero_pedido)

        if mesa_pedido and productos and estado:
            try:
                mesa = get_object_or_404(Mesa, numero_mesa=mesa_pedido)

                # Limpiar productos existentes antes de actualizar
                PedidoProducto.objects.filter(pedido=pedido).delete()

                total_pedido = 0
                for producto_id, cantidad in productos.items():
                    try:
                        cantidad = int(cantidad)
                        if cantidad > 0:
                            producto = get_object_or_404(Producto, id=producto_id)
                            PedidoProducto.objects.create(pedido=pedido, producto=producto, cantidad=cantidad)
                            total_pedido += producto.precio * cantidad
                    except (ValueError, Producto.DoesNotExist):
                        messages.error(request, f'Error con el producto ID {producto_id}')
                        return redirect('editar_pedido', numero_pedido=numero_pedido)

                # Actualizar pedido
                pedido.total_pedido = total_pedido
                pedido.estado_pedido = int(estado)
                pedido.usuario = request.user
                pedido.save()

                # Actualizar estado de la mesa
                if int(estado) != 1:
                    mesa.estado_mesa = 0
                    mesa.pedido_asociado = None
                    messages.success(request, 'Pedido finalizado exitosamente.')
                else:
                    mesa.estado_mesa = 1
                    mesa.pedido_asociado = pedido.numero_pedido
                    messages.info(request, 'Pedido actualizado exitosamente.')

                mesa.save()
                return redirect('index')

            except Exception as e:
                messages.error(request, f'Error inesperado: {str(e)}')

        else:
            messages.error(request, 'Debe haber al menos 1 producto para guardar')

    # Método GET: Cargar datos actuales del pedido
    productos_pedido = PedidoProducto.objects.filter(pedido=pedido).select_related('producto')
    productos = Producto.objects.all().order_by('nombre_producto')
    grupos = Grupo.objects.all().order_by('nombre_grupo')

    # Preparar datos actuales para el formulario
    productos_actuales = {str(p.producto.id): p.cantidad for p in productos_pedido}
    productos_actuales_json = json.dumps(productos_actuales)

    # Calcular total de cada producto en el pedido
    for p in productos_pedido:
        p.precio_total = p.producto.precio * p.cantidad

    return render(request, 'pedidos/editar_pedido.html', {
        'grupos': grupos,
        'pedido': pedido,
        'productos': productos,
        'mesa_seleccionada': pedido.mesa.numero_mesa,
        'productos_pedido': productos_pedido,
        'productos_actuales': productos_actuales_json,
    })

@login_required
def eliminar_pedido(request, numero_pedido):
    pedido = get_object_or_404(Pedido, numero_pedido=numero_pedido)
    try:
        pedido.delete()
        messages.success(request, 'Pedido eliminado exitosamente.')
    except DatabaseError as e:
        messages.error(request, 'Error en BD: {e}')
    return redirect('gestionar_pedidos')

#CIERRES DE CAJA
@login_required
def gestionar_cierres(request):
    query = request.GET.get('q', '')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    try:
        cierres = Cierre.objects.all().order_by('-id')
        if query:
            cierres = cierres.filter(numero_pedido__icontains=query)

        if fecha_inicio and fecha_fin:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            cierres = cierres.filter(creado_en__range=[fecha_inicio_dt, fecha_fin_dt])
    except DatabaseError as e:
        messages.error(request, f'Error: {str(e)}')
    return render(request, 'cierres/gestionar_cierres.html', {
        'cierres': cierres,
        'query': query,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    })

@login_required
def agregar_cierre(request):
    hoy = localtime(now()).date()  # Fecha actual

    # Asignar fecha actual
    fecha_inicio = hoy.strftime("%Y-%m-%d")
    fecha_fin = hoy.strftime("%Y-%m-%d")

    # Generar arqueo con fecha actual
    fecha_inicio = make_aware(datetime.strptime(fecha_inicio, "%Y-%m-%d"))
    fecha_fin = make_aware(datetime.strptime(fecha_fin, "%Y-%m-%d")).replace(
        hour=23, minute=59, second=59, microsecond=999999
    )
    #listar bases y retiros
    base = Base.objects.filter(creado_en__range=(fecha_inicio, fecha_fin))
    retiros = Retiro.objects.filter(creado_en__range=(fecha_inicio, fecha_fin))
    total_base = base.aggregate(total=Sum('base_dia'))['total'] or 0 
    total_retiros = retiros.aggregate(total=Sum('retiro_monto'))['total'] or 0 
    #calcular ventas por medio de pago
    total_efectivo = Pedido.objects.filter(
        creado_en__range=(fecha_inicio, fecha_fin), estado_pedido=2
    ).aggregate(total=Sum('total_pedido'))['total'] or 0
    total_nequi = Pedido.objects.filter(
        creado_en__range=(fecha_inicio, fecha_fin), estado_pedido=3
    ).aggregate(total=Sum('total_pedido'))['total'] or 0
    total_davip = Pedido.objects.filter(
        creado_en__range=(fecha_inicio, fecha_fin), estado_pedido=4
    ).aggregate(total=Sum('total_pedido'))['total'] or 0
    #calcula total de ventas y total en caja
    total_ventas = total_efectivo + total_nequi + total_davip
    total_caja = (total_base + total_efectivo) - total_retiros
    try:
        if request.method == 'POST':
            #Crear cierre
            us_caja = request.POST.get('us_caja')
            obs_cierre = request.POST.get('obs_cierre')
            if us_caja:
                cierre = Cierre(
                    base_cierre=total_base,
                    retiros_cierre=total_retiros,
                    vEfectivo_cierre=total_efectivo,
                    vNequi_cierre=total_nequi,
                    vDavip_cierre=total_davip,
                    vTotal_cierre=total_ventas,
                    tCaja_cierre=total_caja,
                    us_caja=us_caja,
                    obs_cierre=obs_cierre,
                    usuario = request.user
                )
                cierre.save()
                messages.success(request, 'Cierre grabado exitosamente.')
            else:
                messages.warning(request, 'El campo "Validar Caja" es requerido')
                return redirect('agregar_cierre')
            return redirect('gestionar_cierres')
        
    except Exception as e:
        messages.error(request, f'Hubo un error: {e}')
        return render(request, 'errores/error_general.html', {'error_message': str(e)})

    return render(request, 'cierres/agregar_cierre.html', {
        'total_base': total_base,
        'total_retiros': total_retiros,
        'total_ventas': total_ventas,
        'total_efectivo': total_efectivo,
        'total_nequi': total_nequi,
        'total_davip': total_davip,
        'total_caja': total_caja,
        'fecha_inicio': fecha_inicio.date(),
        'fecha_fin': fecha_fin.date(),
    })

@login_required
def editar_cierre(request, cierre_id):
    fecha = Cierre.objects.get(id=cierre_id).creado_en.date()  # Fecha de creacion del cierre

    # Asignar fecha actual
    fecha_inicio = fecha.strftime("%Y-%m-%d")
    fecha_fin = fecha.strftime("%Y-%m-%d")

    # Generar arqueo con fecha actual
    fecha_inicio = make_aware(datetime.strptime(fecha_inicio, "%Y-%m-%d"))
    fecha_fin = make_aware(datetime.strptime(fecha_fin, "%Y-%m-%d")).replace(
        hour=23, minute=59, second=59, microsecond=999999
    )
    base = Base.objects.filter(creado_en__range=(fecha_inicio, fecha_fin))
    retiros = Retiro.objects.filter(creado_en__range=(fecha_inicio, fecha_fin))

    total_base = base.aggregate(total=Sum('base_dia'))['total'] or 0 #total base
    total_retiros = retiros.aggregate(total=Sum('retiro_monto'))['total'] or 0 #total de retiros
    total_efectivo = Pedido.objects.filter(
        creado_en__range=(fecha_inicio, fecha_fin), estado_pedido=2
    ).aggregate(total=Sum('total_pedido'))['total'] or 0 #total de efectivo
    total_nequi = Pedido.objects.filter(
        creado_en__range=(fecha_inicio, fecha_fin), estado_pedido=3
    ).aggregate(total=Sum('total_pedido'))['total'] or 0 #total de nequi
    total_davip = Pedido.objects.filter(
        creado_en__range=(fecha_inicio, fecha_fin), estado_pedido=4
    ).aggregate(total=Sum('total_pedido'))['total'] or 0 #total de daviplata
    total_ventas = total_efectivo + total_nequi + total_davip #total de ventas
    total_caja = (total_base + total_efectivo) - total_retiros #total en caja
    cierre = get_object_or_404(Cierre, id=cierre_id)
    try:
        if request.method == 'POST':
                us_caja = request.POST.get('us_caja')
                obs_cierre = request.POST.get('obs_cierre')
                usuario = request.user
                if us_caja:
                    cierre.us_caja = us_caja
                    cierre.obs_cierre = obs_cierre
                    cierre.usuario = usuario
                    cierre.save()
                    messages.success(request, 'Cierre actualizado exitosamente.')
                    return redirect('gestionar_cierres')
                else:
                    messages.warning(request, 'El campo "Validar Caja" es requerido')
                    return redirect('agregar_cierre')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return render(request, 'cierres/editar_cierre.html', {
        'cierre': cierre,
        'us_caja': cierre.us_caja,
        'obs_cierre': cierre.obs_cierre,
        'total_base': total_base,
        'total_retiros': total_retiros,
        'total_ventas': total_ventas,
        'total_efectivo': total_efectivo,
        'total_nequi': total_nequi,
        'total_davip': total_davip,
        'total_caja': total_caja,
        'fecha_inicio': fecha_inicio.date(),
        'fecha_fin': fecha_fin.date(),
    })

