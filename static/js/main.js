document.addEventListener('DOMContentLoaded', function () {
    /*Asignacion de datasets*/
        const messages = document.body.dataset.messages;
        const page = document.body.dataset.page;
        let url =  document.body.dataset.url;
        
    
    /*Debbuggin*/
        console.log("Ejecutando script en:", page);


    /*base.html*/
        // Inicializar tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.forEach(function (tooltipTriggerEl) {
            new bootstrap.Tooltip(tooltipTriggerEl);
        });
        //Personalizacion datatables por defecto
        $(document).ready(function () {
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
        //Funcionalidad para control de alertas y mensajes
        if (messages) {
            try {
                const parsedMessages = JSON.parse(messages);
                //Personalizacion de Alertas y menajes por defecto
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
            //Asignacion de icono por tipo de mensaje
            function getIconType(type) {
                switch (type) {
                    case "error": return "error";
                    case "success": return "success";
                    case "warning": return "warning";
                    case "info": return "info";
                    default: return "info";
                }
            }
            //Asignacion de background por tipo de mensaje
            function getBackgroundColor(type) {
                switch (type) {
                    case "error": return "#ff4d4d";
                    case "success": return "#28a745";
                    case "warning": return "#ffb109";
                    case "info": return "#17a2b8";
                    default: return "#333";
                }
            }
            //Asignacion color de texto por tipo de mensaje
            function getTextColor(type) {
                return type === "warning" ? "#000" : "#fff";
            }


    /*login.html*/
        if (page === "login") {
            initLoginScripts();
        }
            //Funcionalidad boton ver contraseña
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
        if (page === "index" && url) {
            actualizarMesas();
            mesaInterval = setInterval(actualizarMesas, 5000);
        }
            //Funcionalidad actualizar estado de mesas
            function actualizarMesas() {
                $.getJSON(url, function (data) {
                    data.mesas.forEach(function (mesa) {
                        let mesaElement = $(".mesa-" + mesa.numero_mesa);
                        let cardElement = mesaElement.find(".card");

                        if (mesa.estado_mesa == 1) {
                            cardElement.removeClass("bg-navbar text-light").addClass("text-bg-danger");
                            mesaElement.attr("title", mesa.responsable + " - $" + mesa.total_pedido);
                            mesaElement.find("p").text("Ocupada");
                        } else {
                            cardElement.removeClass("text-bg-danger").addClass("bg-navbar text-light");
                            mesaElement.attr("title", "Seleccionar");
                            mesaElement.find("p").text("Disponible");
                        }
                    });
                }).fail(function () {
                    console.error("Error al obtener los datos de las mesas");
                });
            }
            //Funcionalidad detener intervalo actualizacion de mesas si se cambia de página
            window.addEventListener("beforeunload", function () {
                if (mesaInterval) {
                    clearInterval(mesaInterval);
                }
            });


    /*gestionar_mesas.html*/
            
});
