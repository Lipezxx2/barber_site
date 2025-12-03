function selecionarHorario(horario, botao) {
    document.getElementById("hora").value = horario;

    document.querySelectorAll(".horario-btn").forEach(btn => {
        btn.classList.remove("selecionado");
    });

    botao.classList.add("selecionado");
}
