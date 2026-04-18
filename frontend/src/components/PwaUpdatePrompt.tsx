import { CheckCircle2, RefreshCcw, WifiOff, X } from "lucide-react";
import { useRegisterSW } from "virtual:pwa-register/react";

const PwaUpdatePrompt = () => {
  const {
    offlineReady: [offlineReady, setOfflineReady],
    needRefresh: [needRefresh, setNeedRefresh],
    updateServiceWorker,
  } = useRegisterSW();

  if (!offlineReady && !needRefresh) {
    return null;
  }

  return (
    <div className="fixed inset-x-4 top-4 z-50 rounded-2xl border-2 border-gray-900 bg-white p-4 shadow-[8px_8px_0_0_rgba(17,17,17,0.12)] dark:border-gray-200 dark:bg-stone-900 lg:inset-x-auto lg:left-6 lg:w-[22rem]">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-mono uppercase tracking-[0.2em] text-gray-500 dark:text-gray-400">App Status</p>
          <h2 className="mt-2 flex items-center gap-2 text-base font-mono text-gray-900 dark:text-gray-100">
            {needRefresh ? <RefreshCcw size={16} strokeWidth={2} /> : <CheckCircle2 size={16} strokeWidth={2} />}
            {needRefresh ? "Update available" : "Offline ready"}
          </h2>
          <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
            {needRefresh
              ? "A fresh version is available. Reload when you're ready."
              : "The app shell is cached and can launch with limited connectivity."}
          </p>
        </div>
        <button
          type="button"
          onClick={() => {
            setOfflineReady(false);
            setNeedRefresh(false);
          }}
          className="text-gray-500 transition-colors hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100"
          aria-label="Dismiss app status"
        >
          <X size={18} strokeWidth={2} />
        </button>
      </div>

      <div className="mt-4 flex gap-3">
        {needRefresh ? (
          <button
            type="button"
            onClick={() => void updateServiceWorker(true)}
            className="flex flex-1 items-center justify-center gap-2 bg-gray-900 px-4 py-3 text-sm font-mono text-white transition-colors hover:bg-gray-800 dark:bg-gray-100 dark:text-gray-900 dark:hover:bg-gray-200"
          >
            <RefreshCcw size={16} strokeWidth={2} />
            update app
          </button>
        ) : (
          <div className="flex flex-1 items-center gap-2 border-2 border-dashed border-gray-300 px-4 py-3 text-sm font-mono text-gray-700 dark:border-gray-700 dark:text-gray-300">
            <WifiOff size={16} strokeWidth={2} />
            cached for offline use
          </div>
        )}
      </div>
    </div>
  );
};

export default PwaUpdatePrompt;
