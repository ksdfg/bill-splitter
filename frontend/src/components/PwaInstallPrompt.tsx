import { Download, Share2, X } from "lucide-react";
import { useInstallPrompt } from "../hooks/useInstallPrompt";

const PwaInstallPrompt = () => {
  const { canInstall, showIosInstructions, promptInstall, dismissPrompt } = useInstallPrompt();

  if (!canInstall && !showIosInstructions) {
    return null;
  }

  const description = canInstall
    ? "Install bill splitter for a faster, app-like experience on your phone."
    : "On iPhone or iPad, tap Share and then Add to Home Screen to install bill splitter.";

  return (
    <div className="fixed inset-x-4 bottom-4 z-50 rounded-2xl border-2 border-gray-900 bg-white p-4 shadow-[8px_8px_0_0_rgba(17,17,17,0.15)] dark:border-gray-200 dark:bg-stone-900 lg:inset-x-auto lg:right-6 lg:w-[22rem]">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-mono uppercase tracking-[0.2em] text-gray-500 dark:text-gray-400">Install App</p>
          <h2 className="mt-2 text-base font-mono text-gray-900 dark:text-gray-100">Keep bill splitter handy</h2>
          <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">{description}</p>
        </div>
        <button
          type="button"
          onClick={dismissPrompt}
          className="text-gray-500 transition-colors hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100"
          aria-label="Dismiss install prompt"
        >
          <X size={18} strokeWidth={2} />
        </button>
      </div>

      <div className="mt-4 flex gap-3">
        {canInstall ? (
          <button
            type="button"
            onClick={() => void promptInstall()}
            className="flex flex-1 items-center justify-center gap-2 bg-gray-900 px-4 py-3 text-sm font-mono text-white transition-colors hover:bg-gray-800 dark:bg-gray-100 dark:text-gray-900 dark:hover:bg-gray-200"
          >
            <Download size={16} strokeWidth={2} />
            install now
          </button>
        ) : (
          <div className="flex flex-1 items-center gap-2 border-2 border-dashed border-gray-300 px-4 py-3 text-sm font-mono text-gray-700 dark:border-gray-700 dark:text-gray-300">
            <Share2 size={16} strokeWidth={2} />
            use safari share menu
          </div>
        )}
      </div>
    </div>
  );
};

export default PwaInstallPrompt;
