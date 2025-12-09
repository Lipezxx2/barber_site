function selecionarHorario(horario, botao) {
    document.getElementById("hora").value = horario;

    document.querySelectorAll(".horario-btn").forEach(btn => {
        btn.classList.remove("selecionado");
    });

    botao.classList.add("selecionado");
}

function abrirFormulario() {
        let form = document.getElementById("form-upload");

        if (form.style.display === "none") {
            form.style.display = "block";
        } else {
            form.style.display = "none";
        }
    }


