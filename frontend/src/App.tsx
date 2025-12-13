import React, { useState, useEffect } from "react";
import { useAppState } from "./hooks/useAppState";
import { ThemeProvider, useTheme } from "./context/ThemeContext";
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

function AppContent() {
  const state = useAppState();
  const isMobile = useIsMobile();

  // eslint-disable-next-line
  const { theme, setTheme, isDark, isAuto } = useTheme();

  const handlers = {
    startAddBill: state.startAddBill,
    startEditBill: state.startEditBill,
    deleteBill: state.deleteBill,
    handleCalculateSplit: state.handleCalculateSplit,
    saveBill: state.saveBill,
    cancelForm: state.cancelForm,
    setCurrentView: state.setCurrentView,
  };

  const toggleTheme = () => {
    if (isAuto) {
      // If in auto mode, switch to opposite of current dark mode
      setTheme(isDark ? "light" : "dark");
    } else {
      // If in manual mode, switch back to auto (system default)
      setTheme("auto");
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1 className="header-title">Bill Splitter</h1>
          <button
            className="theme-toggle-btn"
            onClick={toggleTheme}
            aria-label={isAuto ? "Switch to manual theme mode" : "Switch to system default theme"}
            title={isAuto ? `Switch to ${isDark ? "light" : "dark"} mode` : "Switch to system default"}
          >
            {isAuto ? (isDark ? "🌙" : "☀️") : isDark ? "🌙 📌" : "☀️ 📌"}
          </button>
        </div>
      </header>
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

export default function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}
