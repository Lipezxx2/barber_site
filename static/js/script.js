   function selecionarHorario(horario) {
            document.getElementById("hora").value = horario;

            document.querySelectorAll(".horario-btn").forEach(btn => {
                btn.classList.remove("selecionado");
            });

            event.target.classList.add("selecionado");
        }