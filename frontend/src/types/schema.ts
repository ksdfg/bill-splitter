// src/types/schema.ts

// --- OpenAPI Schemas ---

export interface Item {
  name: string;
  price: number;
  quantity: number;
  consumed_by: string[]; // List of names
}

export interface Bill {
  id?: number; // Frontend specific ID for mapping
  items: Item[];
  paid_by: string;
  tax_rate: number; // Stored as fraction (0.0 to 1.0)
  service_charge: number; // Stored as fraction (0.0 to 1.0)
}

export interface OutingSplit {
  payment_plans: PaymentPlan[];
}

export interface Payment {
  to: string;
  amount: number; // Amount > 0
}

export interface PaymentPlan {
  name: string;
  payments: Payment[]; // Outgoing payments
}

export interface OCRBillItem {
  name: string;
  price: number;
  quantity: number;
}

export interface OCRBill {
  items: OCRBillItem[];
  tax_rate: number;
  service_charge: number;
}

// --- Frontend Helper Types ---

// The structure used internally by ItemForm
export interface ItemUIState {
  name: string;
  price: number | string; // Allow string temporarily for input fields
  quantity: number | string;
  consumed_by_string: string; // Comma-separated string for input field
}

// Result structure used by PaymentPlans.tsx after processing OutingSplit
export interface NetPaymentFlow {
  name: string;
  totalOutgoing: number;
  totalIncoming: number; // Still calculated, but not displayed as list
  outgoing: Payment[];
  incoming: { from: string; amount: number }[]; // Included for schema completeness, but will be empty array for UI display logic
  netAmount: number;
  uiTextOverride: string | null;
}

export enum UI_STATE {
  LIST = "LIST",
  FORM = "FORM",
  RESULTS = "RESULTS",
}
