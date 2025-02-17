document.addEventListener('DOMContentLoaded', function () {
    /*INICIO base.html*/
        // Inicializar todos los tooltips en la página
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.forEach(function (tooltipTriggerEl) {
            new bootstrap.Tooltip(tooltipTriggerEl);
        });
        //Personalizacion por defecto en datatables
        $(document).ready(function () {
            // Inicializar DataTables
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
        //Control de mensajes y alertas
        const messagesElement = document.getElementById("django_messages");
    
        if (messagesElement) {
            const djangoMessages = JSON.parse(messagesElement.textContent);
            
            djangoMessages.forEach((message) => {
                Swal.fire({
                    text: message.message,
                    icon: message.tags,
                    toast: true,
                    position: "bottom-end",
                    showConfirmButton: false,
                    timer: 4000,
                    timerProgressBar: true,
                    didOpen: (toast) => {
                        toast.onmouseenter = Swal.stopTimer;
                        toast.onmouseleave = Swal.resumeTimer;
                    },
                    background: getMessageBackground(message.tags),
                    color: getMessageTextColor(message.tags),
                });
            });
        }
        function getMessageBackground(type) {
            const colors = {
                error: "#ff4d4d",
                success: "#28a745",
                warning: "#ffb109",
                info: "#17a2b8",
            };
            return colors[type] || "#ffffff";
        }
        function getMessageTextColor(type) {
            return type === "warning" ? "#000" : "#fff";
        }
    

    /*INICIO login.html*/
        //Identidicar pagina login
        const page = document.body.dataset.page; 
        if (page === "login") {
            initLoginScripts();
        }

        function initLoginScripts() {
            console.log("Ejecutando scripts de Login");
        
            // Funcionalidad para mostrar/ocultar contraseña
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
    
    /*INICIO index.html*/

});