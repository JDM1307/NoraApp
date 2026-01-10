document.addEventListener('DOMContentLoaded', function () {

    /*GENERAL*/
        /*Asignacion de datasets*/
        const page = document.getElementById('page')?.dataset.page;
        const messages = document.getElementById('data-messages')?.dataset.messages;
        const dataTable = document.getElementById('page')?.dataset.tables;
        const info = document.getElementById('data-info')?.dataset.info;
        const url =  document.getElementById('data-url')?.dataset.url;
        const key_create = document.getElementById('page')?.dataset.key_create;
        const key_delete = document.getElementById('page')?.dataset.key_delete;
        
        console.log("Plantilla: ", page); //Debbuggin

        // Iconos Sidebar
        const icons = [
            { id: "home-icon" },
            { id: "user-icon" },
            { id: "ventas-icon" },
            { id: "productos-icon" },
            { id: "bases-icon" },
            { id: "grupos-icon" },
            { id: "arqueos-icon" },
            { id: "cierres-icon" },
            { id: "retiros-icon" },
            { id: "mesas-icon" }
        ];

            // Inicializar iconos Lottie
            function initializeLottieIcon({ id }) {
                const element = document.getElementById(id);
                if (!element) return;

                const path = element.dataset.path;

                const animation = lottie.loadAnimation({
                    container: element,
                    renderer: 'svg',
                    loop: false,
                    autoplay: false,
                    path: path
                });

                element.addEventListener('mouseenter', () => animation.play());
                element.addEventListener('mouseleave', () => animation.stop());
            }

            // Inicializar iconos
            icons.forEach(initializeLottieIcon);

        // Toooltips
        try {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.forEach(function (tooltipTriggerEl) {
                console.log("--Tooltips: enable"); //Debbuggin
                new bootstrap.Tooltip(tooltipTriggerEl);
            });
        } catch (error) {  
            console.error("--Tooltips, Error:", error); //Debbuggin
        }
        
        // Datatable por defecto
        if (dataTable === "enable") {
            try {
                $(document).ready(function () {
                    console.info("--Datatable por defecto: enable"); //Debuggin
    
                    $('#mi-tabla').DataTable({
                        responsive: true,
                        paging: true,        
                        searching: false,    
                        ordering: false,      
                        info: true,           
                        select: false,
                        language: {
                            select: {
                                rows: {
                                    1: "1 fila seleccionada"
                                }
                            },
                            processing: "Procesando...",
                            search: "Buscar:",
                            lengthMenu: "Mostrar _MENU_ registros",
                            info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
                            infoEmpty: "Mostrando 0 a 0 de 0 registros",
                            infoFiltered: "(filtrado de _MAX_ registros en total)",
                            loadingRecords: "Cargando...",
                            zeroRecords: "No se encontraron resultados",
                            emptyTable: "No hay datos disponibles en la tabla",
                        },
                    });
                });
            } catch (error) {
                console.error("--Datatable por defecto, Error:", error); //Debbuggin
            }
        }
       
        // Alertas y mensajes
        if (messages) {
            try {
                //Personalizacion de Alertas y menajes por defecto
                console.info("--Alertas y mensajes: enable"); //Debuggin
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
                        color: getTextColor(message.type),
                        customClass: {
                            popup: "custom-swal"
                        }
                    });
                });
    
            } catch (error) {
                console.error("--Alertas y mensajes, Error:", error); //Debbuggin
            }
        }
            // Personalizacion Iconos
            function getIconType(type) {
                switch (type) {
                    case "error": return "error";
                    case "success": return "success";
                    case "warning": return "warning";
                    case "info": return "info";
                    default: return "info";
                }
            }
            // Personalizacion Background
            function getBackgroundColor(type) {
                switch (type) {
                    case "error": return "#ff4d4d";
                    case "success": return "#28a745";
                    case "warning": return "#ffb109";
                    case "info": return "#17a2b8";
                    default: return "#333";
                }
            }
            // Personalizacion Texto
            function getTextColor(type) {
                return type === "warning" ? "#000" : "#fff";
            }
            
        // Datatable arqueos
        if (page === "arqueos"){
            try {
                $(document).ready(function () {
                    console.info("--Datatable 'Arqueos': enable"); //Debbuggin
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
            } catch (error) {
                console.error("--Datatable arqueos, Error:", error); //Debbuggin
            }
        }

        // Boton volver
        let backBtn;
        backBtn = document.getElementById("backButton");
        if (backBtn) {
            console.log("--Botón volver: enable"); //Debbuggin
            backBtn.addEventListener("click", function () {
                window.history.back();
            });
        }

        // Cerrar sesión
        if (document.getElementById("logout-btn") && page !== "Login") {
            console.log("--Cerrar sesión: enable"); //Debbuggin
            initializeConfirmation("#logout-btn", {
                dataAttr: "msj_logout",
                onConfirmAction: "submit",
                enableEnterKey: true
            });
        }
    
        // Creación/Edición de registros
        if (page && key_create === "enable") {
            console.log("--Creación/Edición de registros: enable"); //Debbuggin
            initializeConfirmation(".save-btn", {
                dataAttr: "msj_create",
                onConfirmAction: "submit",
                enableEnterKey: true,
                extraSelector: ".valor"
            });
        }
    
        // Eliminación de registros
        if (page && key_delete === "enable") {
            console.log("--Eliminación de registros: enable"); //Debbuggin
            initializeConfirmation(".delete-btn", {
                dataAttr: "msj_delete",
                onConfirmAction: "redirect"
            });
        }
        
            // Inicializar confirmación
            function initializeConfirmation(selector, options) {
                document.querySelectorAll(selector).forEach(button => {
                    button.addEventListener("click", function (e) {
                        e.preventDefault();
        
                        let form = button.closest("form");
                        let customMessage = button.dataset[options.dataAttr];
                        let extraValue = options.extraSelector ? document.querySelector(options.extraSelector)?.value || "" : "";
        
                        showConfirmationDialog({
                            message: `¿${customMessage} ${extraValue}?`,
                            onConfirm: () => {
                                if (options.onConfirmAction === "submit" && form) {
                                    form.submit();
                                } else if (options.onConfirmAction === "redirect") {
                                    window.location.href = button.dataset.delete_url;
                                }
                            }
                        });
                    });
        
                    // Habilitar la tecla Enter para confirmar
                    if (options.enableEnterKey && button.closest("form")) {
                        button.closest("form").addEventListener("keydown", function (e) {
                            if (e.key === "Enter") {
                                e.preventDefault();
                                button.click();
                            }
                        });
                    }
                });
            }

            // SweetAlert confirmación/cancelación
            function showConfirmationDialog({ message, onConfirm }) {
                try {
                    Swal.fire({
                        text: message,
                        icon: "warning",
                        showCancelButton: true,
                        confirmButtonText: '<i class="bi bi-check-circle"></i> Confirmar',
                        cancelButtonText: '<i class="bi bi-x-circle"></i> Cancelar',
                        background: "#1e272e",
                        color: "#f8f9fa",
                        width: "300px",
                        customClass: {
                            popup: "custom-swal"
                        }
                    }).then((result) => {
                        if (result.isConfirmed && typeof onConfirm === "function") {
                            onConfirm();
                        }
                    });
                } catch (error) {
                    console.error("--SweetAlert confirmación/cancelación, Error:", error); //Debbuggin
                }
            }

        //Milesimas en numeros
        document.querySelectorAll(".format-numbers").forEach(element => {
            try {
                console.log("--Milesimas en numeros: enable"); //Debbuggin
                let value = element.innerText || element.value;
                let number = parseFloat(value.replace(/\D/g, "")) || 0;
                let formatted = new Intl.NumberFormat("es-ES").format(number);

                if (element.tagName === "INPUT") {
                    element.value = formatted;
                } else {
                    element.innerText = formatted;
                }
            } catch (error) { 
                console.error("--Milesimas en numeros, Error:", error); //Debbuggin
            }
            
        });


    /*Login*/
        // Scripts login
        if (page === "Login") {
            initLoginScripts();
        }
            
        // Inicializar scripts de login
            function initLoginScripts() {
                console.log("--Scripts login:"); //debuggin
                try {
                    //Botón 'ver contraseña'
                    function togglePassword() {
                        const passwordInput = document.querySelector("input[type='password']");
                        const togglePassword = document.getElementById("togglePassword");
                    
                        if (togglePassword && passwordInput) {
                            console.log("\t*Botón 'ver contraseña': enable");
                            togglePassword.addEventListener("click", function () {
                                const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
                                passwordInput.setAttribute("type", type);
                        
                                this.innerHTML = type === "password" 
                                    ? '<i class="bi bi-eye"></i>' 
                                    : '<i class="bi bi-eye-slash"></i>';
                            });
                        }
                    }
                togglePassword();
                } catch (error) {
                    console.error("--Login, Error:", error);
                }
            }


    /*Index*/
        // Variables
        let mesaInterval = null;
        let intentosFallidos = 0;
        const MAX_INTENTOS = 3;
        const INACTIVIDAD_MAXIMA = 10000;
        let ultimaActividad = Date.now();
        let ajaxActivo = false;

        /*Gestion Ajax Actualizar mesas*/
        if (page === "Barra" && url) {
            try {

                console.log("--Gestión Ajax Actualizar mesas: enable"); //Debbuggin
                // Inicializar AJAX
                iniciarActualizacion();
            
                // Evento accion usuario (mouse, scroll, teclado o clics)
                $(document).on("mousemove scroll keydown click", function () {
                    ultimaActividad = Date.now();
                    if (!ajaxActivo) {
                        iniciarActualizacion();
                    }
                });
            
                // Evento clic reiniciar AJAX inactivo
                $("a").on("click", function () {
                    ultimaActividad = Date.now();
                    if (!ajaxActivo) {
                        iniciarActualizacion();
                    }
                });
            
                // Comprobar inactividad
                setInterval(() => {
                    if (ajaxActivo && Date.now() - ultimaActividad > INACTIVIDAD_MAXIMA) {
                        detenerActualizacion();
                    }
                }, 5000);

            } catch (error) {
                console.error("--Gestión Ajax Actualizar mesas, Error:", error); //Debbuggin
            }
        }
        
            // Iniciar actualización periódica
            function iniciarActualizacion() {
                if (!ajaxActivo) {
                    ajaxActivo = true;
                    actualizarMesas();
                    mesaInterval = setInterval(actualizarMesas, 1000);
                }
            }
            
            // Detener actualización periódica
            function detenerActualizacion() {
                if (ajaxActivo) {
                    ajaxActivo = false;
                    clearInterval(mesaInterval);
                }
            }
            
            // AJAX actualizar mesas
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


    /**/  
    
    
});
