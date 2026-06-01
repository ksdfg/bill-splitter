import BillSplitter from "./components/BillSplitter";
import PwaInstallPrompt from "./components/PwaInstallPrompt";
import PwaUpdatePrompt from "./components/PwaUpdatePrompt";

function App() {
  return (
    <div className="lg:max-h-screen">
      <PwaInstallPrompt />
      <PwaUpdatePrompt />
      <BillSplitter />
    </div>
  );
}

export default App;
