export interface BillItem {
  name: string;
  price: number;
  quantity: number;
  consumed_by: string[];
}

export type BillItemField = "name" | "price" | "quantity" | "consumed_by";
export type BillItemFieldValue = string | number | string[];

export interface Bill {
  id: string;
  paid_by: string;
  tax_rate: number;
  service_charge: number;
  items: BillItem[];
  amount_paid: number;
}

export interface Payment {
  to: string;
  amount: number;
}

export interface PaymentPlan {
  name: string;
  payments: Payment[];
}

export interface OCRResponse {
  tax_rate: number;
  service_charge: number;
  amount_paid: number;
  items: Array<Omit<BillItem, "consumed_by">>;
}

export interface SplitResponse {
  payment_plans: PaymentPlan[];
}

export interface BillDraft {
  editingBillId: string | null;
  paidBy: string;
  taxRate: string;
  serviceCharge: string;
  amountPaid: string;
  items: BillItem[];
}
