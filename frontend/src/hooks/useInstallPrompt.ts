import { useEffect, useState } from "react";

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

const INSTALL_PROMPT_DISMISS_KEY = "bill-splitter-install-prompt-dismissed";

const getInitialDismissedState = () => {
  if (typeof window === "undefined") {
    return false;
  }

  return window.localStorage.getItem(INSTALL_PROMPT_DISMISS_KEY) === "true";
};

const isStandalone = () =>
  window.matchMedia("(display-mode: standalone)").matches ||
  ((window.navigator as Navigator & { standalone?: boolean }).standalone ?? false);

const isIosBrowser = () => {
  const userAgent = window.navigator.userAgent;
  const isTouchMac = window.navigator.platform === "MacIntel" && window.navigator.maxTouchPoints > 1;

  return /iPad|iPhone|iPod/.test(userAgent) || isTouchMac;
};

export const useInstallPrompt = () => {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [dismissed, setDismissed] = useState(getInitialDismissedState);
  const [showIosInstructions, setShowIosInstructions] = useState(false);

  useEffect(() => {
    if (isStandalone()) {
      return undefined;
    }

    setShowIosInstructions(isIosBrowser());

    const handleBeforeInstallPrompt = (event: Event) => {
      event.preventDefault();
      setDeferredPrompt(event as BeforeInstallPromptEvent);
    };

    const handleAppInstalled = () => {
      setDeferredPrompt(null);
      setShowIosInstructions(false);
      setDismissed(true);
      window.localStorage.setItem(INSTALL_PROMPT_DISMISS_KEY, "true");
    };

    window.addEventListener("beforeinstallprompt", handleBeforeInstallPrompt);
    window.addEventListener("appinstalled", handleAppInstalled);

    return () => {
      window.removeEventListener("beforeinstallprompt", handleBeforeInstallPrompt);
      window.removeEventListener("appinstalled", handleAppInstalled);
    };
  }, []);

  const dismissPrompt = () => {
    setDismissed(true);
    window.localStorage.setItem(INSTALL_PROMPT_DISMISS_KEY, "true");
  };

  const promptInstall = async () => {
    if (!deferredPrompt) {
      return null;
    }

    await deferredPrompt.prompt();
    const result = await deferredPrompt.userChoice;
    setDeferredPrompt(null);

    if (result.outcome === "accepted") {
      dismissPrompt();
    }

    return result.outcome;
  };

  return {
    canInstall: deferredPrompt !== null && !dismissed,
    showIosInstructions: showIosInstructions && !dismissed,
    promptInstall,
    dismissPrompt,
  };
};
