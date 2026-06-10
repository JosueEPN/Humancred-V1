// ===== calculator.js =====
// Funciones de cálculo puro — Humancred

function getInteres(type) {
    if (type === 'Microcredito') return 22;
    if (type === 'Consumo')      return 11.95;
    if (type === 'Hipotecario')  return 4.95;
    return 0;
}

function calculateMonthlyPayment(amount, annualInterest, termInMonths) {
    const monthlyRate = Math.pow(1 + annualInterest / 100, 1 / 12) - 1;
    if (!monthlyRate || monthlyRate === 0) return amount / termInMonths;
    const num = monthlyRate * Math.pow(1 + monthlyRate, termInMonths);
    const den = Math.pow(1 + monthlyRate, termInMonths) - 1;
    return amount * (num / den);
}

/**
 * Dos modalidades de desgravamen:
 *   'cuotas'   — 2.5% se SUMA al monto financiado; cuota sube; cliente recibe el monto completo
 *   'descuento'— 2.5% se DESCUENTA del desembolso; préstamo queda en el monto original; cliente recibe menos
 */
function calculateLoan(creditType, amount, term, selectedInterest, encajeRate, desgravamenActivo, desgravamenMode) {
    amount     = Number(amount)     || 0;
    term       = Number(term)       || 1;
    encajeRate = Number(encajeRate) || 8;

    let interest = (typeof selectedInterest === 'number' && !isNaN(selectedInterest) && selectedInterest > 0)
        ? selectedInterest
        : getInteres(creditType);
    if (typeof interest === 'string') interest = parseFloat(interest);

    const mode            = desgravamenActivo ? (desgravamenMode || 'cuotas') : 'cuotas';
    const desgravamenAmount = desgravamenActivo ? amount * 0.025 : 0;

    let financedAmount, netAmount;
    if (desgravamenActivo && mode === 'descuento') {
        financedAmount = amount;                      // préstamo = monto original
        netAmount      = amount - desgravamenAmount;  // cliente recibe menos
    } else {
        financedAmount = amount + desgravamenAmount;  // préstamo sube
        netAmount      = financedAmount;              // cliente recibe el total
    }

    const monthlyPayment = calculateMonthlyPayment(financedAmount, interest, term);
    const encajeAmount   = financedAmount * (encajeRate / 100);

    return {
        creditType,
        amount,
        financedAmount,
        term,
        interest,
        encajeRate,
        encajeAmount,
        desgravamenActivo: !!desgravamenActivo,
        desgravamenMode:   mode,
        desgravamenAmount,
        netAmount,
        monthlyPayment,
    };
}

window.getInteres              = getInteres;
window.calculateMonthlyPayment = calculateMonthlyPayment;
window.calculateLoan           = calculateLoan;