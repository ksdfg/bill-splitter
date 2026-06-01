import type { Bill, OCRResponse, SplitResponse } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API === "true";

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const buildMockSplit = (bills: Bill[]): SplitResponse => {
  const balances = new Map<string, number>();

  bills.forEach((bill) => {
    const billTotal =
      bill.items.reduce((sum, item) => sum + item.price * item.quantity, 0) *
      (1 + (bill.tax_rate || 0) + (bill.service_charge || 0));

    const consumers = bill.items.flatMap((item) => item.consumed_by);
    const uniqueConsumers = [...new Set(consumers)];

    if (!bill.paid_by || uniqueConsumers.length === 0) {
      return;
    }

    const splitPerPerson = billTotal / uniqueConsumers.length;
    balances.set(bill.paid_by, (balances.get(bill.paid_by) || 0) + billTotal);

    uniqueConsumers.forEach((consumer) => {
      balances.set(consumer, (balances.get(consumer) || 0) - splitPerPerson);
    });
  });

  const creditors: Array<{ name: string; amount: number }> = [];
  const debtors: Array<{ name: string; amount: number }> = [];

  balances.forEach((balance, name) => {
    if (balance > 0.01) {
      creditors.push({ name, amount: balance });
    } else if (balance < -0.01) {
      debtors.push({ name, amount: Math.abs(balance) });
    }
  });

  const paymentMap = new Map<string, Array<{ to: string; amount: number }>>();
  creditors.sort((a, b) => b.amount - a.amount);
  debtors.sort((a, b) => b.amount - a.amount);

  let creditorIndex = 0;
  let debtorIndex = 0;

  while (creditorIndex < creditors.length && debtorIndex < debtors.length) {
    const creditor = creditors[creditorIndex];
    const debtor = debtors[debtorIndex];
    const amount = Math.min(creditor.amount, debtor.amount);

    if (amount > 0.01) {
      const existing = paymentMap.get(debtor.name) || [];
      existing.push({ to: creditor.name, amount: Number(amount.toFixed(2)) });
      paymentMap.set(debtor.name, existing);
    }

    creditor.amount -= amount;
    debtor.amount -= amount;

    if (creditor.amount <= 0.01) creditorIndex += 1;
    if (debtor.amount <= 0.01) debtorIndex += 1;
  }

  return {
    payment_plans: [...paymentMap.entries()].map(([name, payments]) => ({
      name,
      payments,
    })),
  };
};

const getApiBaseUrl = (): string => {
  if (!API_BASE_URL) {
    throw new Error("API_BASE_URL is not defined");
  }

  return API_BASE_URL;
};

export const uploadReceipt = async (file: File): Promise<OCRResponse> => {
  if (USE_MOCK_API) {
    await delay(300);
    return {
      tax_rate: 0.05,
      service_charge: 0.1,
      amount_paid: 878,
      items: [
        { name: "Margherita Pizza", price: 320, quantity: 1 },
        { name: "Pasta Alfredo", price: 280, quantity: 1 },
        { name: "Cold Coffee", price: 139, quantity: 2 },
      ],
    };
  }

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${getApiBaseUrl()}/api/v1/bills/ocr`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("OCR request failed");
  }

  return (await response.json()) as OCRResponse;
};

export const calculateSplit = async (bills: Bill[]): Promise<SplitResponse> => {
  if (USE_MOCK_API) {
    await delay(300);
    return buildMockSplit(bills);
  }

  const response = await fetch(`${getApiBaseUrl()}/api/v1/bills/split`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ bills }),
  });

  if (!response.ok) {
    throw new Error("Split calculation failed");
  }

  return (await response.json()) as SplitResponse;
};
