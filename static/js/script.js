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


/*.addEventListener("DOMContentLoaded", function () {
    const campoData = document.querySelector('input[type="date"]');

    const hoje = new Date();
    const ano = hoje.getFullYear();
    const mes = String(hoje.getMonth() + 1).padStart(2, '0');
    const dia = String(hoje.getDate()).padStart(2, '0');

    const dataMinima = `${ano}-${mes}-${dia}`;

   
    campoData.min = dataMinima;

    
    campoData.addEventListener("change", function () {
        if (campoData.value < dataMinima) {
            alert("Essa data já passou");
            campoData.value = "";
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const campoTelefone = document.querySelector('input[name="telefone"]');

    campoTelefone.addEventListener("input", function () {
        let valor = campoTelefone.value.replace(/\D/g, ""); 

        if (valor.length > 11) {
            valor = valor.slice(0, 11);
        }

        if (valor.length > 10) {
            campoTelefone.value = `(${valor.slice(0, 2)}) ${valor.slice(2, 7)}-${valor.slice(7)}`;
        } else if (valor.length > 6) {
            campoTelefone.value = `(${valor.slice(0, 2)}) ${valor.slice(2, 6)}-${valor.slice(6)}`;
        } else if (valor.length > 2) {
            campoTelefone.value = `(${valor.slice(0, 2)}) ${valor.slice(2)}`;
        } else {
            campoTelefone.value = valor;
        }
    });
});
*/
