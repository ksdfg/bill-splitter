import React, { useState, useEffect } from "react";
import { useAppState } from "./hooks/useAppState";
import { DesktopLayout, MobileLayout } from "./components/Layouts";
import "./styles/App.css";

const useIsMobile = (breakpoint: number = 768): boolean => {
  const [width, setWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => setWidth(window.innerWidth);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return width < breakpoint;
};

export default function App() {
  const state = useAppState();
  const isMobile = useIsMobile();

  const handlers = {
    startAddBill: state.startAddBill,
    startEditBill: state.startEditBill,
    deleteBill: state.deleteBill,
    handleCalculateSplit: state.handleCalculateSplit,
    saveBill: state.saveBill,
    cancelForm: state.cancelForm,
    setCurrentView: state.setCurrentView,
  };

  return (
    <div className="app">
      <header className="header">Bill Splitter</header>
      <main className="app-container">
        {isMobile ? (
          <MobileLayout state={state} handlers={handlers} />
        ) : (
          <DesktopLayout state={state} handlers={handlers} />
        )}
      </main>
    </div>
  );
}
