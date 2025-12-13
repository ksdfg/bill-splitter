import React, { createContext, useContext, ReactNode } from "react";

export type Theme = "light" | "dark" | "auto";

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  isDark: boolean;
  isAuto: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = React.useState<Theme>(() => {
    // Only load from localStorage if explicitly set by user
    const saved = localStorage.getItem("theme") as Theme | null;
    // Default to 'auto' to follow system preferences
    return saved || "auto";
  });

  const [isDark, setIsDark] = React.useState(false);

  React.useEffect(() => {
    const updateDarkMode = () => {
      let darkMode = false;

      if (theme === "auto") {
        darkMode = window.matchMedia("(prefers-color-scheme: dark)").matches;
      } else {
        darkMode = theme === "dark";
      }

      setIsDark(darkMode);
      const root = document.documentElement;
      root.setAttribute("data-theme", darkMode ? "dark" : "light");
    };

    updateDarkMode();

    // Always listen to system changes when in auto mode
    if (theme === "auto") {
      const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
      mediaQuery.addEventListener("change", updateDarkMode);
      return () => mediaQuery.removeEventListener("change", updateDarkMode);
    }
  }, [theme]);

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    // Only save to localStorage if not 'auto' (to keep system defaults as default)
    if (newTheme === "auto") {
      localStorage.removeItem("theme");
    } else {
      localStorage.setItem("theme", newTheme);
    }
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme, isDark, isAuto: theme === "auto" }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};
