import React from "react";
import BillList from "./BillList";
import BillForm from "./BillForm";
import PaymentPlans from "./PaymentPlans";
import { Bill, OutingSplit, UI_STATE } from "../types/schema";

interface AppState {
  bills: Bill[];
  splitResults: OutingSplit | null;
  currentView: UI_STATE;
  editingBill: Bill | null;
  isCalculating: boolean;
}

interface AppHandlers {
  startAddBill: () => void;
  startEditBill: (bill: Bill) => void;
  deleteBill: (id: number) => void;
  handleCalculateSplit: () => Promise<void>;
  saveBill: (billData: Bill) => void;
  cancelForm: () => void;
  setCurrentView: React.Dispatch<React.SetStateAction<UI_STATE>>;
}

interface LayoutProps {
  state: AppState;
  handlers: AppHandlers;
}

// --- Desktop Layout (768px+) ---
export function DesktopLayout({ state, handlers }: LayoutProps) {
  const { bills, splitResults, currentView, editingBill, isCalculating } = state;
  const { startAddBill, startEditBill, deleteBill, handleCalculateSplit, saveBill, cancelForm } = handlers;

  let RightPanelContent: React.ReactNode;

  if (currentView === UI_STATE.FORM) {
    RightPanelContent = (
      <div className="card desktop-main-panel">
        <BillForm initialData={editingBill} onSave={saveBill} onCancel={cancelForm} />
      </div>
    );
  } else if (currentView === UI_STATE.RESULTS) {
    RightPanelContent = (
      <div className="card desktop-main-panel">
        <PaymentPlans splitResults={splitResults} isMobile={false} />
      </div>
    );
  } else {
    RightPanelContent = (
      <div
        className="card desktop-main-panel"
        style={{
          border: "2px dashed #ccc",
          height: "400px",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          color: "#777",
        }}
      >
        Click "+ Add New Bill" or "Calculate Split" to see content here
      </div>
    );
  }

  return (
    <div className="desktop-layout">
      <div className="desktop-panel">
        <BillList
          bills={bills}
          onAdd={startAddBill}
          onEdit={startEditBill}
          onDelete={deleteBill}
          onCalculate={handleCalculateSplit}
          isCalculating={isCalculating}
        />
      </div>
      {RightPanelContent}
    </div>
  );
}

// --- Mobile Layout (below 768px) ---
export function MobileLayout({ state, handlers }: LayoutProps) {
  const { bills, splitResults, currentView, editingBill, isCalculating } = state;
  const { startAddBill, deleteBill, handleCalculateSplit, saveBill, cancelForm, setCurrentView } = handlers;

  if (currentView === UI_STATE.FORM) {
    return (
      <div className="mobile-fullscreen-modal">
        <div className="mobile-header">
          <button type="button" onClick={cancelForm}>
            &larr; Back to Bills
          </button>
          <h3>{editingBill ? "Edit Bill" : "Add New Bill"}</h3>
          <button type="button" onClick={cancelForm}>
            &times;
          </button>
        </div>
        <BillForm initialData={editingBill} onSave={saveBill} onCancel={cancelForm} />
      </div>
    );
  }

  if (currentView === UI_STATE.RESULTS) {
    return (
      <div className="mobile-fullscreen-modal">
        <div className="mobile-header">
          <button type="button" onClick={() => setCurrentView(UI_STATE.LIST)}>
            &larr; Back to Bills
          </button>
          <h3>Bill Splitter</h3>
          <div></div>
        </div>
        <PaymentPlans splitResults={splitResults} isMobile={true} onBackToBills={startAddBill} />
      </div>
    );
  }

  return (
    <div className="mobile-view">
      <BillList
        bills={bills}
        onAdd={startAddBill}
        onEdit={handlers.startEditBill}
        onDelete={deleteBill}
        onCalculate={handleCalculateSplit}
        isCalculating={isCalculating}
      />
    </div>
  );
}
