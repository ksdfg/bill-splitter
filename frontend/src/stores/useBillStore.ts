import type { KeyboardEvent } from "react";
import { create } from "zustand";
import { calculateSplit, uploadReceipt } from "../services/billService";
import type {
  Bill,
  BillDraft,
  BillItem,
  BillItemField,
  BillItemFieldValue,
  OCRResponse,
  PaymentPlan,
} from "../types";

interface BillStoreState {
  bills: Bill[];
  draft: BillDraft;
  paymentPlans: PaymentPlan[];
  showModal: boolean;
  showResults: boolean;
  isUploading: boolean;
}

interface BillStoreActions {
  setPaidBy: (value: string) => void;
  setTaxRate: (value: string) => void;
  setServiceCharge: (value: string) => void;
  setAmountPaid: (value: string) => void;
  handleAddBill: () => void;
  handleEditBill: (bill: Bill) => void;
  handleDeleteBill: (id: string) => void;
  handleSaveBill: () => void;
  handleAddItem: () => void;
  handleDeleteItem: (index: number) => void;
  handleItemChange: (index: number, field: BillItemField, value: BillItemFieldValue) => void;
  handleConsumerKeyDown: (index: number, event: KeyboardEvent<HTMLInputElement>) => void;
  removeConsumer: (itemIndex: number, consumerName: string) => void;
  handleUploadReceipt: (file: File) => Promise<void>;
  handleCalculateSplit: () => Promise<void>;
  handleCloseModal: () => void;
  handleBackToBills: () => void;
}

type BillStore = BillStoreState & BillStoreActions;

const createEmptyItem = (): BillItem => ({
  name: "",
  price: 0,
  quantity: 1,
  consumed_by: [],
});

const createEmptyDraft = (): BillDraft => ({
  editingBillId: null,
  paidBy: "",
  taxRate: "5",
  serviceCharge: "0",
  amountPaid: "",
  items: [createEmptyItem()],
});

const updateDraftItem = (
  items: BillItem[],
  index: number,
  field: BillItemField,
  value: BillItemFieldValue,
): BillItem[] =>
  items.map((item, itemIndex) => {
    if (itemIndex !== index) {
      return item;
    }

    switch (field) {
      case "name":
        return typeof value === "string" ? { ...item, name: value } : item;
      case "price":
        return typeof value === "number" ? { ...item, price: value } : item;
      case "quantity":
        return typeof value === "number" ? { ...item, quantity: value } : item;
      case "consumed_by":
        return Array.isArray(value) ? { ...item, consumed_by: value } : item;
      default:
        return item;
    }
  });

const applyDraftField = (
  draft: BillDraft,
  field: keyof Omit<BillDraft, "editingBillId" | "items">,
  value: string,
): BillDraft => ({
  ...draft,
  [field]: value,
});

export const useBillStore = create<BillStore>((set, get) => ({
  bills: [],
  draft: createEmptyDraft(),
  paymentPlans: [],
  showModal: false,
  showResults: false,
  isUploading: false,

  setPaidBy: (value) =>
    set((state) => ({
      draft: applyDraftField(state.draft, "paidBy", value),
    })),
  setTaxRate: (value) =>
    set((state) => ({
      draft: applyDraftField(state.draft, "taxRate", value),
    })),
  setServiceCharge: (value) =>
    set((state) => ({
      draft: applyDraftField(state.draft, "serviceCharge", value),
    })),
  setAmountPaid: (value) =>
    set((state) => ({
      draft: applyDraftField(state.draft, "amountPaid", value),
    })),

  handleAddBill: () =>
    set({
      draft: createEmptyDraft(),
      paymentPlans: [],
      showModal: true,
      showResults: false,
    }),

  handleEditBill: (bill) =>
    set({
      draft: {
        editingBillId: bill.id,
        paidBy: bill.paid_by,
        taxRate: (bill.tax_rate * 100).toString(),
        serviceCharge: (bill.service_charge * 100).toString(),
        amountPaid: bill.amount_paid != null ? String(bill.amount_paid) : "",
        items: bill.items,
      },
      paymentPlans: [],
      showModal: true,
      showResults: false,
    }),

  handleDeleteBill: (id) =>
    set((state) => ({
      bills: state.bills.filter((bill) => bill.id !== id),
    })),

  handleSaveBill: () => {
    const { bills, draft } = get();

    if (!draft.paidBy.trim()) {
      alert("Please enter who paid the bill");
      return;
    }

    const validItems = draft.items.filter(
      (item) => item.name.trim() && item.price > 0 && item.quantity > 0 && item.consumed_by.length > 0,
    );

    if (validItems.length === 0) {
      alert("Please add at least one valid item with consumers");
      return;
    }

    const bill: Bill = {
      id: draft.editingBillId || Date.now().toString(),
      paid_by: draft.paidBy.trim(),
      tax_rate: parseFloat(draft.taxRate) / 100,
      service_charge: parseFloat(draft.serviceCharge) / 100,
      items: validItems,
      amount_paid: draft.amountPaid ? parseFloat(draft.amountPaid) : 0,
    };

    const nextBills = draft.editingBillId
      ? bills.map((currentBill) => (currentBill.id === draft.editingBillId ? bill : currentBill))
      : [...bills, bill];

    set({
      bills: nextBills,
      draft: createEmptyDraft(),
      showModal: false,
    });
  },

  handleAddItem: () =>
    set((state) => ({
      draft: {
        ...state.draft,
        items: [...state.draft.items, createEmptyItem()],
      },
    })),

  handleDeleteItem: (index) =>
    set((state) => ({
      draft: {
        ...state.draft,
        items:
          state.draft.items.length > 1
            ? state.draft.items.filter((_, itemIndex) => itemIndex !== index)
            : state.draft.items,
      },
    })),

  handleItemChange: (index, field, value) =>
    set((state) => ({
      draft: {
        ...state.draft,
        items: updateDraftItem(state.draft.items, index, field, value),
      },
    })),

  handleConsumerKeyDown: (index, event) => {
    const input = event.currentTarget;
    const consumerName = input.value.trim();

    if (event.key !== "Enter" || !consumerName) {
      return;
    }

    event.preventDefault();
    set((state) => ({
      draft: {
        ...state.draft,
        items: state.draft.items.map((item, itemIndex) => {
          if (itemIndex !== index || item.consumed_by.includes(consumerName)) {
            return item;
          }

          return {
            ...item,
            consumed_by: [...item.consumed_by, consumerName],
          };
        }),
      },
    }));
    input.value = "";
  },

  removeConsumer: (itemIndex, consumerName) =>
    set((state) => ({
      draft: {
        ...state.draft,
        items: state.draft.items.map((item, index) => {
          if (index !== itemIndex) {
            return item;
          }

          return {
            ...item,
            consumed_by: item.consumed_by.filter((consumer) => consumer !== consumerName),
          };
        }),
      },
    })),

  handleUploadReceipt: async (file) => {
    set({ isUploading: true });

    try {
      const ocrData: OCRResponse = await uploadReceipt(file);
      set((state) => ({
        draft: {
          ...state.draft,
          taxRate: (ocrData.tax_rate * 100).toString(),
          serviceCharge: (ocrData.service_charge * 100).toString(),
          amountPaid: ocrData.amount_paid.toString(),
          items: ocrData.items.map((item) => ({
            ...item,
            consumed_by: [],
          })),
        },
      }));
      alert("Receipt scanned! Please add who consumed each item.");
    } catch (error) {
      console.error("OCR error:", error);
      alert("Failed to scan receipt. Please try again.");
    } finally {
      set({ isUploading: false });
    }
  },

  handleCalculateSplit: async () => {
    const { bills } = get();

    if (bills.length === 0) {
      alert("Please add at least one bill");
      return;
    }

    try {
      const result = await calculateSplit(bills);
      set({
        paymentPlans: result.payment_plans,
        showResults: true,
      });
    } catch (error) {
      console.error("Split calculation error:", error);
      alert("Failed to calculate split. Please try again.");
    }
  },

  handleCloseModal: () =>
    set({
      draft: createEmptyDraft(),
      showModal: false,
    }),

  handleBackToBills: () =>
    set({
      showResults: false,
    }),
}));
