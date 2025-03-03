document.addEventListener('DOMContentLoaded', function () {
    /*Asignacion de datasets*/
        const page = document.body.dataset.page;
        const messages = document.body.dataset.messages;
        const info = document.body.dataset.info;
        const url =  document.body.dataset.url;
        const key_create = document.body.dataset.key_create;
        const key_delete = document.body.dataset.key_delete;
        
    
    /*Debbuggin*/
        console.info("DEBUGGIN: ", page);
        //console.log("key_create:", key_create)
        //console.log("key_delete:", key_delete);


    /*General*/
        //Inicializar tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.forEach(function (tooltipTriggerEl) {
            new bootstrap.Tooltip(tooltipTriggerEl);
            console.info("--Tooltips inicializados"); //debuggin
        });

        //Inicializar datatables por defecto (bases, grupos, mesas, productos, retiros)
        $(document).ready(function () {
            console.info("--Datatable por defecto inicializada"); //Debuggin

            $('#mi-tabla').DataTable({
                responsive: true,
                paging: true,        
                searching: false,    
                ordering: false,      
                info: true,           
                select: true,
                language: {
                    select: {
                        rows: {
                            1: "1 fila seleccionada"
                        }
                    },
                    processing: "Procesando...",
                    search: "Buscar:",
                    lengthMenu: "Mostrar _MENU_ elementos",
                    info: "Mostrando _START_ a _END_ de _TOTAL_ elementos",
                    infoEmpty: "Mostrando 0 a 0 de 0 elementos",
                    infoFiltered: "(filtrado de _MAX_ elementos en total)",
                    loadingRecords: "Cargando...",
                    zeroRecords: "No se encontraron resultados",
                    emptyTable: "No hay datos disponibles en la tabla",
                },
            });
        });

        //Inicializar control de alertas y mensajes
        if (messages) {
            try {
                //Personalizacion de Alertas y menajes por defecto
                console.info("--Alertas y mensajes funcionando"); //Debuggin
                const parsedMessages = JSON.parse(messages);
                parsedMessages.forEach(message => {
                    Swal.fire({
                        text: message.text,
                        icon: getIconType(message.type),
                        toast: true,
                        position: "bottom-end",
                        showConfirmButton: false,
                        timer: 4000,
                        timerProgressBar: true,
                        didOpen: (toast) => {
                            toast.onmouseenter = Swal.stopTimer;
                            toast.onmouseleave = Swal.resumeTimer;
                        },
                        background: getBackgroundColor(message.type),
                        color: getTextColor(message.type)
                    });
                });
    
            } catch (error) {
                console.error("Error al parsear los mensajes:", error);
            }
        }
            //Personalizacion de icono por tipo de mensaje
            function getIconType(type) {
                switch (type) {
                    case "error": return "error";
                    case "success": return "success";
                    case "warning": return "warning";
                    case "info": return "info";
                    default: return "info";
                }
            }
            //Personalizacion de background por tipo de mensaje
            function getBackgroundColor(type) {
                switch (type) {
                    case "error": return "#ff4d4d";
                    case "success": return "#28a745";
                    case "warning": return "#ffb109";
                    case "info": return "#17a2b8";
                    default: return "#333";
                }
            }
            //Personalizacion de color de texto por tipo de mensaje
            function getTextColor(type) {
                return type === "warning" ? "#000" : "#fff";
            }
            
        //Inicializar datatables para arqueos (arqueos, cierres)
        if (page === "arqueos"){
            $(document).ready(function () {
                console.info("--Datatable 'Arqueos' inicializada"); //debuggin
                $('#tabla-arqueo').DataTable({
                    responsive: true,
                    paging: false,        
                    searching: false,    
                    ordering: false,      
                    info: true,           
                    select: true,
                    language: {
                        select: {
                            rows: {
                                1: "1 fila seleccionada"
                            }
                        },
                        processing: "Procesando...",
                        search: "Buscar:",
                        info: `${info}`,
                    },
                });
            });
        }

        // Inicializar Toast creacion/edicion de registros
        if (page && key_create) {
            create_elements();
        }
            // Función confirmar/cancelar creacion/edicion de registros
            function create_elements() {
                const saveButton = document.querySelector(".save-btn");
                const form = saveButton.closest("form"); // Obtiene el formulario más cercano

                // Función para mostrar el toast de confirmación
                function showConfirmationToast(e) {
                    e.preventDefault();

                    let confirmMessage = saveButton.dataset.msj_create || "¿Estás seguro de grabar este elemento?";
                    let valor = document.querySelector(".valor");
                    let valueConfirm = valor.value || " ";

                    Swal.fire({
                        text: `¿${confirmMessage} ${valueConfirm}?`,
                        icon: "warning",
                        showCancelButton: true,
                        confirmButtonText: '<i class="bi bi-check-circle"></i> Confirmar',
                        cancelButtonText: '<i class="bi bi-x-circle"></i> Cancelar',
                        background: "#1e272e",
                        color: "#f8f9fa",
                        width: "300px"
                    }).then((result) => {
                        if (result.isConfirmed) {
                            form.submit(); // Envía el formulario si el usuario confirma
                        }
                    });
                }

                // Evento click al botón de guardar
                saveButton.addEventListener("click", showConfirmationToast);

                // Evento oprimir tecla Enter/Intro
                form.addEventListener("keydown", function (e) {
                    if (e.key === "Enter") {
                        showConfirmationToast(e);
                    }
                });
            }

        //Inicializar Toast eliminacion de registros
        if (page && key_delete) {
            delete_elements()    
        }
            //Funcion confirmar/cancelar eliminacion de registros
            function delete_elements() {
                document.querySelectorAll(".delete-btn").forEach(button => {
                    button.addEventListener("click", function (e) {
                        e.preventDefault();
            
                        let deleteUrl = this.dataset.delete_url;
                        let confirmMessage = this.dataset.msj_delete || "¿Estás seguro de eliminar este elemento?";
            
                        const Toast = Swal.mixin({
                            toast: false,
                            position: "center",
                            showConfirmButton: true,
                            showCancelButton: true,
                            confirmButtonText: '<i class="bi bi-trash"></i> Eliminar',
                            cancelButtonText: '<i class="bi bi-x-circle"></i> Cancelar',
                            customClass: {
                                confirmButton: "swal2-confirm",
                                cancelButton: "swal2-cancel"
                            },
                            timer: 10000,
                            timerProgressBar: true,
                            icon: "warning",
                            background: "#1e272e",
                            color: "#f8f9fa",
                            width: "300px"
                        });
            
                        Toast.fire({
                            text: confirmMessage,
                        }).then((result) => {
                            if (result.isConfirmed) {
                                window.location.href = deleteUrl;
                            }
                        });
                    });
                });
            }


    /*login.html*/
        //Inicializar Scripts en login
        if (page === "login") {
            initLoginScripts();
        }
            //Funcion boton "ver contraseña"
            function initLoginScripts() {
            
                const togglePassword = document.getElementById("togglePassword");
                const passwordInput = document.querySelector("input[type='password']");
            
                if (togglePassword && passwordInput) {
                    togglePassword.addEventListener("click", function () {
                        const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
                        passwordInput.setAttribute("type", type);
                
                        this.innerHTML = type === "password" 
                            ? '<i class="bi bi-eye"></i>' 
                            : '<i class="bi bi-eye-slash"></i>';
                    });
                }
            }


    /*index.html*/
        let mesaInterval = null;
        let intentosFallidos = 0;
        const MAX_INTENTOS = 3;
        const INACTIVIDAD_MAXIMA = 10000;
        let ultimaActividad = Date.now();
        let ajaxActivo = false;
        
        /*Gestion Ajax Actualizar mesas*/
        if (page === "index" && url) {
            // Inicializar AJAX al cargar la página
            iniciarActualizacion();
        
            // Evento actividad del usuario (mouse, scroll, teclado o clics)
            $(document).on("mousemove scroll keydown click", function () {
                ultimaActividad = Date.now();
                if (!ajaxActivo) {
                    iniciarActualizacion();
                }
            });
        
            // Evento clic en cualquier mesa para reiniciar AJAX si estaba inactivo
            $("a").on("click", function () {
                ultimaActividad = Date.now();
                if (!ajaxActivo) {
                    iniciarActualizacion();
                }
            });
        
            // Comprobacion inactividad cada 5 segundos
            setInterval(() => {
                if (ajaxActivo && Date.now() - ultimaActividad > INACTIVIDAD_MAXIMA) {
                    detenerActualizacion();
                }
            }, 5000);
        }
        
            // Función iniciar la actualización periódica
            function iniciarActualizacion() {
                if (!ajaxActivo) {
                    ajaxActivo = true;
                    actualizarMesas();
                    mesaInterval = setInterval(actualizarMesas, 1000);
                }
            }
            
            // Función detener la actualización periódica
            function detenerActualizacion() {
                if (ajaxActivo) {
                    ajaxActivo = false;
                    clearInterval(mesaInterval);
                }
            }
            
            // Función AJAX actualizar mesas
            function actualizarMesas() {
                $.getJSON(url, function (data) {
                    intentosFallidos = 0; // Reiniciar contador si la petición es exitosa
            
                    data.mesas.forEach(function (mesa) {
                        let mesaElement = $(".mesa-" + mesa.numero_mesa);
                        let cardElement = mesaElement.find(".card");
                        let spanInfo = mesaElement.find(".badge");
                        let linkElement = mesaElement;
            
                        if (mesa.estado_mesa == 1) {
                            cardElement.removeClass("bg-navbar text-light").addClass("text-bg-danger");
                            spanInfo.removeClass("d-none");
                            mesaElement.attr("title", "Tomó: " + mesa.responsable);
                            mesaElement.find("p").text("Ocupada");  
                            mesaElement.find("small").text(mesa.total_pedido);
                            linkElement.attr("href", `pedidos/editar/${mesa.pedido_asociado}/`);
                        } else {
                            cardElement.removeClass("text-bg-danger").addClass("bg-navbar text-light");
                            spanInfo.addClass("d-none");
                            mesaElement.attr("title", "Seleccionar");
                            mesaElement.find("p").text("Disponible");
                            mesaElement.find("small").text(" ");
                            linkElement.attr("href", `pedidos/agregar/${mesa.numero_mesa}/`);
                        }
                    });
                }).fail(function () {
                    intentosFallidos++;
                    console.error(`Error al obtener los datos de las mesas (Intento ${intentosFallidos} de ${MAX_INTENTOS})`);
            
                    if (intentosFallidos >= MAX_INTENTOS) {
                        console.error("Se alcanzó el límite de intentos fallidos. Deteniendo actualización de mesas.");
                        detenerActualizacion();
                    }
                });
            }
            
            // Evento AJAX abandono de página
            window.addEventListener("beforeunload", function () {
                detenerActualizacion();
            });


    /*gestionar_mesas.html*/  
    
    
});
