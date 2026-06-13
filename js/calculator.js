// ===== calculator.js =====
// Funciones de cálculo puro — Humancred

function getInteres(type) {
    if (type === 'Microcredito') return 22;
    if (type === 'Consumo')      return 11.95;
    if (type === 'Hipotecario')  return 4.95;
    return 0;
}

function calculateMonthlyPayment(amount, annualInterest, termInMonths) {
    // Tasa efectiva anual -> tasa efectiva mensual (NO BORRAR, referencia):
    // const monthlyRate = Math.pow(1 + annualInterest / 100, 1 / 12) - 1;

    // Tasa nominal anual -> tasa nominal mensual (división simple entre 12):
    const monthlyRate = annualInterest / 100 / 12;

    if (!monthlyRate || monthlyRate === 0) return amount / termInMonths;
    const num = monthlyRate * Math.pow(1 + monthlyRate, termInMonths);
    const den = Math.pow(1 + monthlyRate, termInMonths) - 1;
    return amount * (num / den);
}

/**
 * El seguro de desgravamen (2.5%) siempre se incluye. El cliente solo elige
 * la modalidad:
 *   'descuento' - 2.5% se DESCUENTA del desembolso; el préstamo y la cuota no cambian
 *   'cuotas'    - 2.5% se reparte entre los meses del plazo y ese valor se SUMA a cada cuota
 */
function calculateLoan(creditType, amount, term, selectedInterest, encajeRate, desgravamenMode) {
    amount     = Number(amount)     || 0;
    term       = Number(term)       || 1;
    encajeRate = Number(encajeRate) || 8;

    let interest = (typeof selectedInterest === 'number' && !isNaN(selectedInterest) && selectedInterest > 0)
        ? selectedInterest
        : getInteres(creditType);
    if (typeof interest === 'string') interest = parseFloat(interest);

    const mode              = desgravamenMode === 'cuotas' ? 'cuotas' : 'descuento';
    const desgravamenAmount = amount * 0.025;

    // El préstamo (capital a amortizar) siempre es el monto solicitado
    const financedAmount    = amount;
    const baseMonthlyPayment = calculateMonthlyPayment(financedAmount, interest, term);

    let desgravamenMonthly = 0;
    let monthlyPayment     = baseMonthlyPayment;
    let netAmount          = amount;

    if (mode === 'cuotas') {
        // El seguro se reparte entre los meses del plazo y se suma a la cuota
        desgravamenMonthly = desgravamenAmount / term;
        monthlyPayment      = baseMonthlyPayment + desgravamenMonthly;
    } else {
        // 'descuento': se descuenta del desembolso, la cuota no cambia
        netAmount = amount - desgravamenAmount;
    }

    const encajeAmount = financedAmount * (encajeRate / 100);

    return {
        creditType,
        amount,
        financedAmount,
        term,
        interest,
        encajeRate,
        encajeAmount,
        desgravamenMode: mode,
        desgravamenAmount,
        desgravamenMonthly,
        baseMonthlyPayment,
        netAmount,
        monthlyPayment,
    };
}

window.getInteres              = getInteres;
window.calculateMonthlyPayment = calculateMonthlyPayment;
window.calculateLoan           = calculateLoan;
