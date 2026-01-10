from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied
from django.db import DatabaseError, IntegrityError
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.timezone import  localtime, now, make_aware
from datetime import datetime, timedelta
import json
from .models import Producto, Grupo, Mesa, Pedido, PedidoProducto, Base, Retiro, Cierre


# LOGIN
def login(request):
    try:
        if request.method == 'POST':
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                auth_login(request, user)
                messages.success(request, f'{user.username} Ha iniciado sesión')

                # Validar existencia de base
                hoy = localtime(now()).date()
                inicio_dia = make_aware(datetime.combine(hoy, datetime.min.time()))  # 00:00:00
                fin_dia = make_aware(datetime.combine(hoy, datetime.max.time()))    # 23:59:59
                base_hoy = Base.objects.filter(creado_en__range=(inicio_dia, fin_dia)).exists()
                
                if base_hoy:
                    return redirect('index')
                else:
                    return redirect('agregar_base')
            else:
                messages.error(request, 'Usuario y/o contraseña incorrectos')
        else:
            form = AuthenticationForm()
    
    except ObjectDoesNotExist as e:
        messages.error(request, f'Error: No se encontró el objeto. {str(e)}')
    except ValidationError as e:
        messages.error(request, f'Error de validación: {str(e)}')
    except PermissionDenied as e:
        messages.error(request, f'Permiso denegado: {str(e)}')
    except DatabaseError as e:
        messages.error(request, f'Error en la base de datos: {str(e)}')
    except IntegrityError as e:
        messages.error(request, f'Error de integridad: {str(e)}')
    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})

    return render(request, 'registration/login.html', {'form': form})


#INDEX
@login_required
def index(request):
    try:
        mesas = Mesa.objects.all().order_by('numero_mesa')
    
    except ObjectDoesNotExist as e:
        messages.error(request, f'Error: No se encontraron mesas. {str(e)}')
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    except DatabaseError as e:
        messages.error(request, f'Error en la base de datos: {str(e)}')
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    except ValidationError as e:
        messages.error(request, f'Error de validación: {str(e)}')
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    
    return render(request, 'index/index.html', {'mesas': mesas})

@login_required
def obtener_mesas(request):
    try:
        mesas = Mesa.objects.all().order_by('numero_mesa')
        data = []
        for mesa in mesas:
            pedido = Pedido.objects.filter(numero_pedido=mesa.pedido_asociado).first() if mesa.pedido_asociado else None
            data.append({
                'numero_mesa': mesa.numero_mesa,
                'estado_mesa': mesa.estado_mesa,
                'responsable': pedido.usuario.username if pedido else "?",
                'total_pedido': pedido.total_pedido if pedido else 0,
                'pedido_asociado': mesa.pedido_asociado if mesa.pedido_asociado else None
            })
        return JsonResponse({'mesas': data})
    
    except Exception as e:
        messages.error(request, f'Error al obtener las mesas: {str(e)}')
        return JsonResponse({'error': str(e)}, status=500)


#BASES
@login_required
def gestionar_bases(request):
    try:
        bases = Base.objects.all().order_by('-creado_en')
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        if fecha_inicio and fecha_fin:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            bases = bases.filter(creado_en__range=[fecha_inicio_dt, fecha_fin_dt])
    
    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    
    return render(request, 'bases/gestionar_bases.html', {'bases': bases})
    
@login_required
def agregar_base(request):
    # Validar existencia de una base para el dia actual
    hoy = localtime(now()).date()
    inicio_dia = make_aware(datetime.combine(hoy, datetime.min.time()))  # 00:00:00
    fin_dia = make_aware(datetime.combine(hoy, datetime.max.time()))    # 23:59:59
    existe_base = Base.objects.filter(creado_en__range=(inicio_dia, fin_dia)).exists()
    try:
        if request.method == 'POST':  
            base_dia = request.POST.get('base_dia')
            observacion = request.POST.get('base_observacion')
            if existe_base:
                messages.warning(request, 'Ya existe una base para el dia hoy')
                return redirect('index')
            else:
                try:
                    if not base_dia or not base_dia.strip():
                        raise ValueError('El monto de la base es requerido')
                    base_dia = int(base_dia)
                    if base_dia < 0:
                        raise ValueError(f'{base_dia} no es un valor válido')
                    base = Base(
                        base_dia=base_dia,
                        base_observacion=observacion,
                        usuario=request.user
                    )
                    base.save()
                    messages.success(request, f'La base fue grabada en ${base_dia}')
                    return redirect('index')
                except (ValueError, TypeError) as e:
                    messages.error(request, f'Error: {str(e)}')
                    return redirect('agregar_base')
    
    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    
    return render(request, 'bases/agregar_base.html', {'existe_base': existe_base})

@login_required
def editar_base(request, base_id):
    try:
        base = get_object_or_404(Base, id=base_id)
        if request.method == 'POST':    
            base_dia = request.POST.get('base_dia')
            observacion = request.POST.get('base_observacion')
            usuario = request.user
            try: 
                if not base_dia or not base_dia.strip():
                    raise ValueError('El monto de la base es requerido')
                base_dia = int(base_dia)
                if base_dia < 0:
                    raise ValueError(f'{base_dia} no es un valor válido')
                now = timezone.now()
                base.base_dia= base_dia
                base.base_observacion = observacion
                base.usuario = usuario
                base.actualizado_en = now
                base.save()
                messages.success(request, f'La base fue actualizada en ${base_dia}')
                return redirect('gestionar_bases') 
            except (ValueError, TypeError) as e:
                messages.error(request, f'Error: {str(e)}')
                return redirect('editar_base', base_id=base_id)
    
    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    
    return render(request, 'bases/editar_base.html', {'base': base})


#RRETIROS DE CAJA
@login_required
def gestionar_retiros(request):
    try:
        retiros = Retiro.objects.all().order_by('-creado_en')
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        if fecha_inicio and fecha_fin:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            retiros = retiros.filter(creado_en__range=[fecha_inicio_dt, fecha_fin_dt])
    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    
    return render(request, 'retiros/gestionar_retiros.html', {'retiros': retiros})

@login_required
def agregar_retiro(request):
    try:
        if request.method == 'POST':
            valor = request.POST.get('retiro_monto')
            observacion = request.POST.get('retiro_observacion')
            try:
                if not valor or not valor.strip():
                    raise ValueError('El monto del retiro es requerido')
                valor = int(valor)
                if valor < 0:
                    raise ValueError(f'{valor} no es un valor válido')
                if not observacion or not observacion.strip():
                    raise ValueError('Es necesario ingresar una observación')
                retiro = Retiro(
                    retiro_monto=valor,
                    retiro_observacion=observacion,
                    usuario=request.user
                )
                retiro.save()
                messages.success(request, f'Retiro "{observacion}" grabado exitosamente.')
                return redirect('gestionar_retiros')
            except (ValueError, TypeError) as e:
                messages.error(request, f'Error: {str(e)}')
                return redirect('agregar_retiro')

    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    
    return render(request, 'retiros/agregar_retiro.html')

@login_required
def editar_retiro(request, retiro_id):
    try:
        retiro = get_object_or_404(Retiro, id=retiro_id)
        if request.method == 'POST':
            valor = request.POST.get('retiro_monto')
            observacion = request.POST.get('retiro_observacion')
            usuario = request.user
            try:
                if not valor or not valor.strip():
                    raise ValueError('El monto del retiro es requerido')
                valor = int(valor)
                if valor < 0:
                    raise ValueError(f'{valor} no es un valor válido')
                if not observacion or not observacion.strip():
                    raise ValueError('Es necesario ingresar una observación')
                now = timezone.now()
                retiro.retiro_monto = valor
                retiro.retiro_observacion = observacion
                retiro.usuario = usuario
                retiro.actualizado_en = now
                retiro.save()
                messages.success(request, f'Retiro "{observacion}" actualizado exitosamente.')
                return redirect('gestionar_retiros')
            except (ValueError, TypeError) as e:
                messages.error(request, f'Error: {str(e)}')
                return redirect('editar_retiro', retiro_id=retiro_id)

    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    
    return render(request, 'retiros/editar_retiro.html', {'retiro': retiro})

@login_required
def eliminar_retiro(request, retiro_id):
    try:
        retiro = get_object_or_404(Retiro, id=retiro_id)
        retiro.delete()
        messages.success(request, f'Retiro "{retiro.retiro_observacion}" eliminado exitosamente.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('gestionar_retiros')


#ARQUEO DE CAJA
@login_required
def arqueo_caja(request):
    try:
        # Fecha actual en la zona horaria local
        hoy = localtime(now()).date()  
        # Obtener fechas del filtro y manejar el caso en que sean vacías
        fecha_inicio = request.GET.get("fecha_inicio") or hoy.strftime("%Y-%m-%d")
        fecha_fin = request.GET.get("fecha_fin") or hoy.strftime("%Y-%m-%d")
        # Convertir a datetime solo si no están vacías
        fecha_inicio = make_aware(datetime.strptime(fecha_inicio, "%Y-%m-%d"))
        fecha_fin = make_aware(datetime.strptime(fecha_fin, "%Y-%m-%d")).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        #Sumatoria de valores por fecha asignada 
        total_base = Base.objects.filter(
            creado_en__range=(fecha_inicio, fecha_fin)
        ).aggregate(total=Sum('base_dia'))['total'] or 0
        total_retiros = Retiro.objects.filter(
            creado_en__range=(fecha_inicio, fecha_fin)
        ).aggregate(total=Sum('retiro_monto'))['total'] or 0 
        total_efectivo = Pedido.objects.filter(
            creado_en__range=(fecha_inicio, fecha_fin), estado_pedido=2
        ).aggregate(total=Sum('total_pedido'))['total'] or 0 
        total_nequi = Pedido.objects.filter(
            creado_en__range=(fecha_inicio, fecha_fin), estado_pedido=3
        ).aggregate(total=Sum('total_pedido'))['total'] or 0 
        total_davip = Pedido.objects.filter(
            creado_en__range=(fecha_inicio, fecha_fin), estado_pedido=4
        ).aggregate(total=Sum('total_pedido'))['total'] or 0
        total_ventas = total_efectivo + total_nequi + total_davip 
        total_caja = (total_base + total_efectivo) - total_retiros
    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})

    return render(request, 'arqueos/arqueo_caja.html', {
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


#PRODUCTOS
@login_required
def gestionar_productos(request):
    try:
        productos = Producto.objects.all().order_by('nombre_producto')
        grupos = Grupo.objects.all()
        query = request.GET.get('q', '')
        grupo_id = request.GET.get('grupo', '')
        if query:
            productos = productos.filter(nombre_producto__icontains=query)
        if grupo_id:
            productos = productos.filter(grupo_id=grupo_id)
    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    
    return render(request, 'productos/gestionar_productos.html', {
            'productos': productos,
            'query': query,
            'grupos': grupos,
            'grupo_id': grupo_id
    })
        
@login_required
def agregar_producto(request):
    try:
        if request.method == 'POST':
            nombre = request.POST.get('nombre_producto')
            precio = request.POST.get('precio_producto')
            descripcion = request.POST.get('descripcion_producto')
            grupo_id = request.POST.get('grupo_producto')
            try:
                if not nombre or not nombre.strip():
                    raise ValueError('El nombre del producto es requerido')
                if not precio or not precio.strip():
                    raise ValueError('El precio del producto es requerido')
                if not grupo_id:
                    raise ValueError('Debe asignar un grupo al producto')
                precio = int(precio)
                if precio < 0:
                    raise ValueError(f'{precio} no es un valor válido')
                grupo = Grupo.objects.get(id=grupo_id)
                producto = Producto(
                    nombre_producto=nombre,
                    descripcion=descripcion,
                    precio=precio,
                    grupo=grupo,
                    usuario=request.user
                )
                producto.save()
                messages.success(request, f'Producto "{nombre}" agregado exitosamente.')
                return redirect('gestionar_productos')
            except (ValueError, TypeError) as e:
                messages.error(request, f'Error: {str(e)}')
                return redirect('agregar_producto')
        
    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    
    grupos = Grupo.objects.all()
    return render(request, 'productos/agregar_producto.html', {'grupos': grupos})

@login_required
def editar_producto(request, producto_id):
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        if request.method == 'POST':
            nombre = request.POST.get('nombre_producto')
            precio = request.POST.get('precio_producto')
            descripcion = request.POST.get('descripcion_producto')
            grupo_id = request.POST.get('grupo_producto')
            usuario = request.user
            try:
                if not nombre or not nombre.strip():
                    raise ValueError('El nombre del producto es requerido')
                if not precio or not precio.strip():
                    raise ValueError('El precio del producto es requerido')
                if not grupo_id:
                    raise ValueError('Debe asignar un grupo al producto')
                precio = int(precio)
                if precio < 0:
                    raise ValueError(f'{precio} no es un valor válido')
                now = timezone.now()
                precio = int(precio)
                grupo = Grupo.objects.get(id=grupo_id)
                producto.nombre_producto = nombre
                producto.descripcion = descripcion
                producto.precio = precio
                producto.grupo = grupo
                producto.usuario = usuario
                producto.actualizado_en = now
                producto.save()
                messages.success(request, f'Producto "{nombre}" actualizado exitosamente.')
                return redirect('gestionar_productos')
            except (ValueError, TypeError) as e:
                messages.error(request, f'Error: {str(e)}')
                return redirect('editar_producto', producto_id=producto_id)
            
    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    
    grupos = Grupo.objects.all()
    return render(request, 'productos/editar_producto.html', {
        'producto': producto,
        'grupos': grupos,
        'grupo_producto': producto.grupo.id,
    })

@login_required
def eliminar_producto(request, producto_id):
    try:
        producto = get_object_or_404(Producto, id=producto_id)
        producto.delete()
        messages.success(request, f'Producto "{producto.nombre_producto}" eliminado exitosamente.')
    except Exception as e:
        messages.error(request, f'Error: {e}')
    return redirect('gestionar_productos')


#GRUPOS
@login_required
def gestionar_grupos(request):
    try:
        grupos = Grupo.objects.all().order_by('nombre_grupo')
        query = request.GET.get('q' , '')
        if query:
            grupos = Grupo.objects.filter(nombre_grupo__icontains=query) 
    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    
    return render(request, 'grupos/gestionar_grupos.html', {'grupos': grupos})

@login_required
def agregar_grupo(request):
    try:
        if request.method == 'POST':
            nombre = request.POST.get('nombre_grupo')
            try:
                if not nombre or not nombre.strip():
                    raise ValueError('El nombre del grupo es requerido')
                grupo = Grupo(nombre_grupo=nombre)
                grupo.save()
                messages.success(request, f'Grupo "{nombre}" agregado exitosamente.')
                return redirect('gestionar_grupos')
            except IntegrityError:
                messages.error(request, f'Error: El grupo "{nombre}" ya existe')
            except (ValueError, TypeError,) as e:
                messages.error(request, f'Error: {str(e)}')
    
    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})

    return render(request, 'grupos/agregar_grupo.html')
    
@login_required
def editar_grupo(request, grupo_id):
    try:
        grupo = get_object_or_404(Grupo, id=grupo_id)
        if request.method == 'POST':
            nombre = request.POST.get('nombre_grupo')
            usuario = request.user
            try:
                if not nombre or not nombre.strip():
                    raise ValueError('El nombre del grupo es requerido')
                now = timezone.now()
                grupo.nombre_grupo = nombre
                grupo.usuario = usuario
                grupo.actualizado_en = now
                grupo.save()
                messages.success(request, f'Grupo "{nombre}" actualizado exitosamente.')
                return redirect('gestionar_grupos')
            except IntegrityError:
                messages.error(request, f'Error: El grupo "{nombre}" ya existe')
            except (ValueError, TypeError,) as e:
                messages.error(request, f'Error: {str(e)}')
            return redirect('editar_grupo', grupo_id=grupo_id)
    
    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    
    return render(request, 'grupos/editar_grupo.html', {'grupo': grupo})

@login_required
def eliminar_grupo(request, grupo_id):
    try:
        grupo = get_object_or_404(Grupo, id=grupo_id)
        grupo.delete()
        messages.success(request, f'Grupo "{grupo.nombre_grupo}" eliminado exitosamente.')
    except DatabaseError as e:
        messages.error(request, f'Error en BD: {e}')
    return redirect('gestionar_grupos')


#MESAS
@login_required
def gestionar_mesas(request):
    try:
        mesas = Mesa.objects.all().order_by('-numero_mesa')
        query = request.GET.get('q' , '')
        if query:
            mesas = Mesa.objects.filter(numero_mesa__icontains=query)
    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    
    return render(request, 'mesas/gestionar_mesas.html', {'mesas': mesas})

@login_required
def agregar_mesa(request):
    try:
        if request.method == 'POST':
            numero = request.POST.get('numero_mesa')  
            try:
                if not numero or not numero.strip():
                    raise ValueError("El numero de mesa es requerido")
                numero = int(numero)
                if numero < 0:
                    raise ValueError(f'El numero {numero} no es valido para una mesa')
                mesa = Mesa(
                    numero_mesa=numero,
                    estado_mesa=0,
                    usuario=request.user)
                mesa.save()
                messages.success(request, f'Mesa numero {numero} agregada exitosamente.')
                return redirect('gestionar_mesas')
            except IntegrityError:
                messages.error(request, f'Error: La mesa {numero} ya existe')
            except (ValueError, TypeError) as e:
                    messages.error(request, f'Error: {str(e)}')
    
    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})

    return render(request, 'mesas/agregar_mesa.html')
    
@login_required
def editar_mesa(request, mesa_id):
    try:
        mesa = get_object_or_404(Mesa, id=mesa_id)
        if request.method == 'POST':
            numero = request.POST.get('numero_mesa')
            usuario = request.user
            try:
                if not numero or not numero.strip():
                    raise ValueError("El numero de mesa es requerido")
                numero = int(numero)
                if numero < 0:
                    raise ValueError(f'El numero {numero} no es valido para una mesa')
                now = timezone.now()
                mesa.numero_mesa = numero
                mesa.usuario = usuario
                mesa.actualizado_en = now
                mesa.save()
                messages.success(request, f'Mesa {numero} actualizada exitosamente.')
                return redirect('gestionar_mesas')
            except IntegrityError:
                messages.error(request, f'Error: La mesa {numero} ya existe')
            except ValueError as e:
                messages.error(request, f'Error: {e}')
            return redirect('editar_mesa', mesa_id=mesa_id)

    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})

    return render(request, 'mesas/editar_mesa.html', {'mesa': mesa})

@login_required
def eliminar_mesa(request, mesa_id):
    try:
        mesa = get_object_or_404(Mesa, id=mesa_id)
        mesa.delete()
        messages.success(request, f'Mesa numero {mesa.numero_mesa} eliminada exitosamente.')
    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    return redirect('gestionar_mesas')


#PEDIDOS
@login_required
def gestionar_pedidos(request):
    try:
        pedidos = Pedido.objects.all().order_by('-numero_pedido')
        query = request.GET.get('q', '')
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        medio_pago = request.GET.get('medio_pago')
        if query:
            pedidos = pedidos.filter(numero_pedido__icontains=query)
        if fecha_inicio and fecha_fin:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            pedidos = pedidos.filter(creado_en__range=[fecha_inicio_dt, fecha_fin_dt])
        if medio_pago in ['2', '3', '4']:
            pedidos = pedidos.filter(estado_pedido=medio_pago)

    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})

    return render(request, 'pedidos/gestionar_pedidos.html', {'pedidos': pedidos,})
    
@login_required
def agregar_pedido(request, numero_mesa=None):
    try:
        if request.method == 'POST':
            mesa_id = request.POST.get('mesa')
            estado = request.POST.get('estado')
            nuevos_productos = request.POST.get('productos')
            mesa = get_object_or_404(Mesa, numero_mesa=mesa_id)
            # Validar: existencia de al menos 1 producto, existencia de mesa,existencia de pedido en mesa
            if mesa.estado_mesa != 0:
                messages.error(request, f'Error: La mesa {numero_mesa}, ya cuenta con un pedido en curso')
                return redirect('index')
            try:
                productos = json.loads(nuevos_productos)
                if not productos:
                    raise ValueError("Debe seleccionar al menos 1 producto para esta accion")
                if not mesa_id:
                    raise ValueError("Esta mesa no existe")
            except (ValueError) as e:
                messages.error(request, f'Error: {str(e)}')
                return redirect('agregar_pedido', numero_mesa=numero_mesa)
            # Obtener el siguiente número de pedido
            ultimo_pedido = Pedido.objects.order_by('numero_pedido').last()
            siguiente_numero_pedido = ultimo_pedido.numero_pedido + 1 if ultimo_pedido else 1
            # Crear el pedido antes de agregar productos
            pedido = Pedido.objects.create(
                numero_pedido=siguiente_numero_pedido,
                mesa=mesa,
                total_pedido=0,  # Se actualizará después
                estado_pedido=int(estado),
                usuario=request.user
            )
            # Calcular total del pedido y asociar productos
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
                    return redirect('agregar_pedido', numero_mesa=numero_mesa)
            # Actualizar total del pedido
            pedido.total_pedido = total_pedido
            pedido.save()
            # Actualizar estado de la mesa segun la accion
            if int(estado) != 1:
                mesa.estado_mesa = 0
                mesa.pedido_asociado = None
                messages.success(request, f'Mesa {numero_mesa}, Pedido #{siguiente_numero_pedido}, finalizado exitosamente')
                now = timezone.now()
                pedido.actualizado_en = now
                pedido.save()
            else:
                mesa.estado_mesa = 1
                mesa.pedido_asociado = siguiente_numero_pedido
                messages.info(request, f'Mesa {numero_mesa}, Pedido #{siguiente_numero_pedido}, comandado exitosamente')
            mesa.save()
            return redirect('index')

    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
        
    #Cargar datos para la plantilla
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
    try:
        pedido = Pedido.objects.get(numero_pedido=numero_pedido)
        productos_con_cantidades = []
        # Recorrer los productos del pedido y obtener la cantidad de la tabla intermedia
        for producto in pedido.productos.all():
            cantidad = PedidoProducto.objects.get(pedido=pedido, producto=producto).cantidad
            total_producto = producto.precio * cantidad
            productos_con_cantidades.append({
                'producto': producto,
                'cantidad': cantidad,
                'total_producto': total_producto
            })

    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    
    # Cargar datos a la plantilla
    return render(request, 'pedidos/ver_pedido.html', {
        'pedido': pedido,
        'productos_con_cantidades': productos_con_cantidades,
    })

@login_required
def editar_pedido(request, numero_pedido):
    pedido = get_object_or_404(Pedido, numero_pedido=numero_pedido)
    try:
        if request.method == 'POST':
            nuevos_productos = request.POST.get('productos')
            mesa_pedido = request.POST.get('mesa')
            estado = request.POST.get('estado')
            #Validar: existencia de al menos 1 producto
            productos = json.loads(nuevos_productos)
            try:
                if not productos:
                    raise ValueError("Debe seleccionar al menos 1 producto para esta accion")
                if not mesa_pedido:
                    raise ValueError("Esta mesa no existe")
            except (ValueError) as e:
                messages.error(request, f'Error: {str(e)}')
                return redirect('editar_pedido', numero_pedido=numero_pedido)
            # Limpiar productos existentes antes de actualizar
            PedidoProducto.objects.filter(pedido=pedido).delete()
            # Calcular total del pedido y asociar productos
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
            now = timezone.now()
            pedido.total_pedido = total_pedido
            pedido.estado_pedido = int(estado)
            pedido.usuario = request.user
            pedido.actualizado_en = now
            pedido.save()
            # Actualizar estado de la mesa segun accion
            mesa = get_object_or_404(Mesa, numero_mesa=mesa_pedido)
            if int(estado) != 1:
                mesa.estado_mesa = 0
                mesa.pedido_asociado = None
                messages.success(request, f'Mesa {mesa_pedido}, Pedido #{numero_pedido}, finalizado exitosamente.')
            else:
                mesa.estado_mesa = 1
                mesa.pedido_asociado = pedido.numero_pedido
                messages.info(request, f'Mesa {mesa_pedido}, Pedido #{numero_pedido}, actualizado exitosamente.')
            mesa.save()
            return redirect('index')

    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})

    # Cargar datos actuales del pedido
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
    try:
        pedido = get_object_or_404(Pedido, numero_pedido=numero_pedido)
        pedido.delete()
        messages.success(request, f'Pedido #{numero_pedido} eliminado exitosamente')
    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    return redirect('gestionar_pedidos')


#CIERRES DE CAJA
@login_required
def gestionar_cierres(request):
    try:
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')
        cierres = Cierre.objects.all().order_by('-creado_en')
        if fecha_inicio and fecha_fin:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            cierres = cierres.filter(creado_en__range=[fecha_inicio_dt, fecha_fin_dt])

    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})
    
    return render(request, 'cierres/gestionar_cierres.html', {
        'cierres': cierres,
    })

@login_required
def agregar_cierre(request):
    try:
        #Asignar fecha actual en la zona horaria local
        hoy = localtime(now()).date()  
        fecha_actual = hoy.strftime("%Y-%m-%d")
        # Crear rangos para filtrar valores
        fecha_inicio = make_aware(datetime.strptime(fecha_actual, "%Y-%m-%d"))
        fecha_fin = make_aware(datetime.strptime(fecha_actual, "%Y-%m-%d")).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        #Sumatoria de valores por fecha actual 
        total_base = Base.objects.filter(
            creado_en__range=(fecha_inicio, fecha_fin)
        ).aggregate(total=Sum('base_dia'))['total'] or 0
        total_retiros = Retiro.objects.filter(
            creado_en__range=(fecha_inicio, fecha_fin)
        ).aggregate(total=Sum('retiro_monto'))['total'] or 0 
        total_efectivo = Pedido.objects.filter(
            creado_en__range=(fecha_inicio, fecha_fin), estado_pedido=2
        ).aggregate(total=Sum('total_pedido'))['total'] or 0 
        total_nequi = Pedido.objects.filter(
            creado_en__range=(fecha_inicio, fecha_fin), estado_pedido=3
        ).aggregate(total=Sum('total_pedido'))['total'] or 0 
        total_davip = Pedido.objects.filter(
            creado_en__range=(fecha_inicio, fecha_fin), estado_pedido=4
        ).aggregate(total=Sum('total_pedido'))['total'] or 0
        total_ventas = total_efectivo + total_nequi + total_davip 
        total_caja = (total_base + total_efectivo) - total_retiros
        # Crear cierre
        if request.method == 'POST':
            us_caja = request.POST.get('us_caja')
            obs_cierre = request.POST.get('obs_cierre')
            try:
                if not us_caja:
                    raise ValueError('El valor de "Validar Caja" es requerido')
                us_caja = int(us_caja)
                if us_caja < 0:
                    raise ValueError(f'${us_caja} no es un valor valido')
            except (ValueError, TypeError,) as e:
                messages.error(request, f'Error: {str(e)}')
                return redirect('agregar_cierre')
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
            messages.success(request, f'El cierre fue grabado en ${us_caja}')
            return redirect('gestionar_cierres')
            
    except Exception as e:
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
    try:
        cierre = get_object_or_404(Cierre, id=cierre_id)
        if request.method == 'POST':
            us_caja = request.POST.get('us_caja')
            obs_cierre = request.POST.get('obs_cierre')
            usuario = request.user
            try:
                if not us_caja:
                    raise ValueError('El valor de "Validar Caja" es requerido')
                us_caja = int(us_caja)
                if us_caja < 0:
                    raise ValueError(f'${us_caja} no es un valor valido')
            except (ValueError, TypeError,) as e:
                messages.error(request, f'Error: {str(e)}')
                return redirect('editar_cierre', cierre_id=cierre_id)
            now = timezone.now()
            cierre.us_caja = us_caja
            cierre.obs_cierre = obs_cierre
            cierre.usuario = usuario
            cierre.actualizado_en = now
            cierre.save()
            messages.success(request, f'El cierre fue actualizado en ${us_caja}')
            return redirect('gestionar_cierres')
                
    except Exception as e:
        return render(request, 'errores/error_general.html', {'error_message': str(e)})

    return render(request, 'cierres/editar_cierre.html', {'cierre': cierre})