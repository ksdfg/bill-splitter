// src/api/api.ts
import { Bill, OutingSplit, OCRBill, NetPaymentFlow, PaymentPlan } from "../types/schema";

// --- Configuration ---
// Read API Base URL from environment variables, defaulting to a common local host if not set.
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

// Helper function to format currency
const formatCurrency = (amount: number): string => parseFloat(amount.toFixed(2)).toString();

// --- Core API Functions (Real Implementation) ---

/**
 * Calls the /api/v1/bills/ocr endpoint.
 * Sends the image file as multipart/form-data.
 */
export const extractBillDetailsFromImage = async (file: File): Promise<OCRBill> => {
  const url = `${API_BASE_URL}/api/v1/bills/ocr`;
  console.log(`[API CALL] POST ${url} for OCR`);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(url, {
      method: "POST",
      body: formData, // Automatically sets Content-Type: multipart/form-data
    });

    if (!response.ok) {
      let errorBody = await response.json().catch(() => ({ detail: "Unknown error during OCR" }));
      console.error("OCR API Error:", response.status, errorBody);
      throw new Error(`OCR extraction failed: ${response.statusText} (${response.status})`);
    }

    return response.json() as Promise<OCRBill>;
  } catch (error) {
    console.error("Network or Fetch Error during OCR:", error);
    throw new Error(`Failed to connect to OCR service: ${error instanceof Error ? error.message : String(error)}`);
  }
};

/**
 * Calls the /api/v1/bills/split endpoint.
 * Sends the array of Bills (wrapped in Outing schema) as application/json.
 */
export const calculateSplit = async (bills: Bill[]): Promise<OutingSplit> => {
  const url = `${API_BASE_URL}/api/v1/bills/split`;
  console.log(`[API CALL] POST ${url} for Split`);

  // The API expects the Bills array nested under the 'bills' key (Outing schema)
  const outingPayload = { bills: bills };

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(outingPayload),
    });

    if (!response.ok) {
      let errorBody = await response.json().catch(() => ({ detail: "Unknown error during split calculation" }));
      console.error("Split API Error:", response.status, errorBody);
      throw new Error(`Split calculation failed: ${response.statusText} (${response.status})`);
    }

    return response.json() as Promise<OutingSplit>;
  } catch (error) {
    console.error("Network or Fetch Error during Split:", error);
    throw new Error(`Failed to connect to Split service: ${error instanceof Error ? error.message : String(error)}`);
  }
};

// --- Client-Side Helper Function (Unchanged, necessary for PaymentPlans.tsx) ---

/**
 * Calculates net flow based on the results from the API for UI presentation.
 * We calculate totalIncoming purely to determine the 'net amount received' for people
 * who have no outgoing payments, but we do NOT expose the 'incoming' list to the component.
 */
export const calculateNetPayments = (splitResult: OutingSplit): NetPaymentFlow[] => {
  if (!splitResult || !splitResult.payment_plans) return [];

  const netFlows: { [key: string]: Omit<NetPaymentFlow, "incoming" | "uiTextOverride"> & { totalIncoming: number } } =
    {};

  // 1. Initialize and calculate outgoing totals
  splitResult.payment_plans.forEach((plan) => {
    netFlows[plan.name] = {
      totalOutgoing: 0,
      totalIncoming: 0,
      outgoing: plan.payments,
      name: plan.name,
      netAmount: 0,
    };
    plan.payments.forEach((p) => {
      netFlows[plan.name].totalOutgoing += p.amount;
    });
  });

  // 2. Calculate incoming totals (needed only for net calculation)
  splitResult.payment_plans.forEach((payerPlan) => {
    payerPlan.payments.forEach((payment) => {
      const recipientName = payment.to;
      const amount = payment.amount;

      if (netFlows[recipientName]) {
        netFlows[recipientName].totalIncoming += amount;
      }
    });
  });

  // 3. Finalize results, calculate net, and apply UI formatting
  return Object.values(netFlows).map((flow) => {
    const net = flow.totalIncoming - flow.totalOutgoing;

    let uiTextOverride: string | null = null;

    // Match Bob's display text if he is a net receiver
    if (flow.name === "Bob" && net > 0) {
      uiTextOverride = `Receives: $${formatCurrency(net)} total`;
    }

    return {
      name: flow.name,
      totalOutgoing: flow.totalOutgoing,
      totalIncoming: flow.totalIncoming, // Keep here for clarity, though not used by UI
      outgoing: flow.outgoing,
      netAmount: net,
      uiTextOverride: uiTextOverride,
      incoming: [], // Explicitly empty, as we don't display individual incoming payments
    } as NetPaymentFlow;
  });
};
