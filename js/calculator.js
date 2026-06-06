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
 * Lógica de desgravamen:
 *   - Si activo: financedAmount = amount + (amount * 2.5%)
 *   - El cliente recibe exactamente financedAmount
 *   - Encaje y cuota se calculan sobre financedAmount
 */
function calculateLoan(creditType, amount, term, selectedInterest, encajeRate, desgravamenActivo) {
    amount     = Number(amount)     || 0;
    term       = Number(term)       || 1;
    encajeRate = Number(encajeRate) || 8;

    let interest = (typeof selectedInterest === 'number' && !isNaN(selectedInterest) && selectedInterest > 0)
        ? selectedInterest
        : getInteres(creditType);
    if (typeof interest === 'string') interest = parseFloat(interest);

    // Desgravamen se SUMA al monto solicitado
    const desgravamenAmount = desgravamenActivo ? amount * 0.025 : 0;
    const financedAmount    = amount + desgravamenAmount;

    // Cuota y encaje sobre el monto financiado total
    const monthlyPayment = calculateMonthlyPayment(financedAmount, interest, term);
    const encajeAmount   = financedAmount * (encajeRate / 100);
    const netAmount      = financedAmount;

    return {
        creditType,
        amount,
        financedAmount,
        term,
        interest,
        encajeRate,
        encajeAmount,
        desgravamenActivo: !!desgravamenActivo,
        desgravamenAmount,
        netAmount,
        monthlyPayment,
    };
}

window.getInteres              = getInteres;
window.calculateMonthlyPayment = calculateMonthlyPayment;
window.calculateLoan           = calculateLoan;