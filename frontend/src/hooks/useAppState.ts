// src/hooks/useAppState.ts
import { useState } from "react";
import { calculateSplit } from "../api/api";
import { Bill, OutingSplit, UI_STATE } from "../types/schema";

const initialBills: Bill[] = [];

interface AppStateHook {
  bills: Bill[];
  splitResults: OutingSplit | null;
  currentView: UI_STATE;
  editingBill: Bill | null;
  isCalculating: boolean;

  saveBill: (billData: Bill) => void;
  deleteBill: (id: number) => void;
  startAddBill: () => void;
  startEditBill: (bill: Bill) => void;
  cancelForm: () => void;
  handleCalculateSplit: () => Promise<void>;
  setCurrentView: React.Dispatch<React.SetStateAction<UI_STATE>>;
}

let nextId = initialBills.length > 0 ? Math.max(...initialBills.map((b) => b.id!)) + 1 : 1;

export function useAppState(): AppStateHook {
  const [bills, setBills] = useState<Bill[]>(initialBills);
  const [splitResults, setSplitResults] = useState<OutingSplit | null>(null);
  const [currentView, setCurrentView] = useState<UI_STATE>(UI_STATE.LIST);
  const [editingBill, setEditingBill] = useState<Bill | null>(null);

  const [isCalculating, setIsCalculating] = useState(false);

  const saveBill = (billData: Bill) => {
    setSplitResults(null);

    if (billData.id) {
      setBills((prev) => prev.map((b) => (b.id === billData.id ? billData : b)));
    } else {
      setBills((prev) => [...prev, { ...billData, id: nextId++ }]);
    }
    setEditingBill(null);
    setCurrentView(UI_STATE.LIST);
  };

  const deleteBill = (id: number) => {
    setSplitResults(null);
    setBills((prev) => prev.filter((b) => b.id !== id));
  };

  const startAddBill = () => {
    setEditingBill(null);
    setCurrentView(UI_STATE.FORM);
  };

  const startEditBill = (bill: Bill) => {
    setEditingBill(bill);
    setCurrentView(UI_STATE.FORM);
  };

  const cancelForm = () => {
    setEditingBill(null);
    if (splitResults) {
      setCurrentView(UI_STATE.RESULTS);
    } else {
      setCurrentView(UI_STATE.LIST);
    }
  };

  const handleCalculateSplit = async () => {
    if (bills.length === 0) return;
    setIsCalculating(true);
    try {
      const results = await calculateSplit(bills);
      setSplitResults(results);
      setCurrentView(UI_STATE.RESULTS);
    } catch (error) {
      console.error("Error calculating split:", error);
      alert("Failed to calculate split.");
    } finally {
      setIsCalculating(false);
    }
  };

  return {
    bills,
    splitResults,
    currentView,
    editingBill,
    isCalculating,
    saveBill,
    deleteBill,
    startAddBill,
    startEditBill,
    cancelForm,
    handleCalculateSplit,
    setCurrentView,
  };
}
