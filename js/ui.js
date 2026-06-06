// ===== ui.js =====
// Funciones relacionadas con la UI y formateo (sin lógica de negocio pesada).

/**
 * Formatea un número a formato de moneda con dos decimales (estilo español).
 * @param {number} value
 * @returns {string}
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('es-ES', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

/**
 * Muestra los resultados de la cotización en la interfaz.
 * @param {object} data Objeto con los resultados del cálculo.
 */
function updateUI(data) {
    document.getElementById('dataDe1').innerText = `$${formatCurrency(data.amount)}`;
    document.getElementById('dataDe2').innerText = `${data.interest}%`;
    document.getElementById('dataDe3').innerText = data.creditType;
    document.getElementById('dataDe4').innerText = "Fija";

    const years = Math.floor(data.term / 12);
    const months = data.term % 12;
    const plazoText = months > 0
        ? `${data.term} meses (${years} año${years > 1 ? 's' : ''} y ${months} mes${months > 1 ? 'es' : ''})`
        : `${data.term} meses (${years} año${years > 1 ? 's' : ''})`;
    document.getElementById('dataDe5').innerText = plazoText;

    document.getElementById('dataDe6').innerText = `${data.encajeRate}%`;
    document.getElementById('dataCuota').innerText = `$${formatCurrency(data.monthlyPayment)}`;
    document.getElementById('EncajeText').innerText = `$${formatCurrency(data.encajeAmount)}`;
    document.getElementById('seguro-desgravamen-amount').innerText = `$${formatCurrency(data.desgravamenAmount)}`;
    document.getElementById('solca-amount').innerText = `$${formatCurrency(data.solcaAmount)}`;
    document.getElementById('total-discounts').innerText = `$${formatCurrency(data.totalDiscounts)}`;
    document.getElementById('net-amount').innerText = `$${formatCurrency(data.netAmount)}`;
}

/**
 * Configura dinámicamente las opciones del select de plazos
 * según el tipo de crédito elegido.
 * @param {HTMLElement} creditTypeSelect Select del tipo de crédito.
 * @param {HTMLElement} termSelect Select del plazo.
 */
function setupTermSelect(creditTypeSelect, termSelect) {
    termSelect.innerHTML = '<option value="">Seleccione el plazo</option>';
    let minMonths, maxMonths;

    if (creditTypeSelect.value === "Consumo") {
        minMonths = 36;
        maxMonths = 96;
    } else if (creditTypeSelect.value === "Hipotecario") {
        minMonths = 36;
        maxMonths = 180;
    } else return;

    for (let i = minMonths; i <= maxMonths; i += 12) {
        const option = document.createElement("option");
        option.value = i;
        const years = i / 12;
        option.textContent = `${i} meses (${years} año${years > 1 ? "s" : ""})`;
        termSelect.appendChild(option);
    }
}

// Exponer funciones globalmente
window.updateUI = updateUI;
window.setupTermSelect = setupTermSelect;
