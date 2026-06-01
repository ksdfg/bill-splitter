import { useEffect, useState } from "react";
import { Receipt, Plus, ArrowLeft } from "lucide-react";
import BillCard from "./BillCard";
import BillModal from "./BillModal";
import PaymentPlansView from "./PaymentPlansView";
import EmptyState from "./EmptyState";
import { useBillStore } from "../stores/useBillStore";

const BillSplitter = () => {
  const [isMobile, setIsMobile] = useState(() => window.innerWidth < 768);
  const {
    bills,
    draft,
    paymentPlans,
    showModal,
    showResults,
    isUploading,
    setPaidBy,
    setTaxRate,
    setServiceCharge,
    setAmountPaid,
    handleAddBill,
    handleEditBill,
    handleDeleteBill,
    handleSaveBill,
    handleAddItem,
    handleDeleteItem,
    handleItemChange,
    handleConsumerKeyDown,
    removeConsumer,
    handleUploadReceipt,
    handleCalculateSplit,
    handleCloseModal,
    handleBackToBills,
  } = useBillStore();
  const { editingBillId, paidBy, taxRate, serviceCharge, amountPaid, items } = draft;

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return (
    <div className="min-h-screen bg-white dark:bg-stone-900 p-6 lg:p-8 transition-colors">
      <div className="max-w-7xl mx-auto mb-12">
        <div className="flex items-center gap-3 mb-2">
          <Receipt size={24} className="text-gray-900 dark:text-gray-100" strokeWidth={2} />
          <h1 className="text-2xl font-mono text-gray-900 dark:text-gray-100">bill splitter</h1>
        </div>
        <p className="text-sm font-mono text-gray-700 dark:text-gray-400">split bills fairly among friends</p>
      </div>

      <div className="max-w-7xl mx-auto">
        {!isMobile && (
          <div className="grid grid-cols-2 gap-8" style={{ height: "calc(100vh - 200px)" }}>
            <div className="border-2 border-gray-900 dark:border-gray-200 p-6 overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-mono text-gray-900 dark:text-gray-100">bills</h2>
                <span className="text-xs text-gray-700 dark:text-gray-400 font-mono">{bills.length}</span>
              </div>

              <button
                onClick={handleAddBill}
                className="w-full py-3 mb-6 border-2 border-dashed border-gray-400 dark:border-gray-600 text-gray-800 dark:text-gray-300 hover:border-gray-900 dark:hover:border-gray-300 hover:text-gray-900 dark:hover:text-gray-100 transition-colors flex items-center justify-center gap-2 text-sm font-mono"
              >
                <Plus size={16} strokeWidth={2} />
                add new bill
              </button>

              {bills.length === 0 ? (
                <EmptyState message="no bills yet" />
              ) : (
                bills.map((bill) => (
                  <BillCard key={bill.id} bill={bill} onEdit={handleEditBill} onDelete={handleDeleteBill} />
                ))
              )}

              <button
                onClick={handleCalculateSplit}
                className="w-full mt-6 py-3 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 hover:bg-gray-800 dark:hover:bg-gray-200 transition-colors disabled:opacity-30 disabled:cursor-not-allowed font-mono"
                disabled={bills.length === 0}
              >
                calculate split
              </button>
            </div>

            <div>
              {showModal && (
                <BillModal
                  show={showModal}
                  editingBillId={editingBillId}
                  paidBy={paidBy}
                  onPaidByChange={setPaidBy}
                  taxRate={taxRate}
                  onTaxRateChange={setTaxRate}
                  serviceCharge={serviceCharge}
                  onServiceChargeChange={setServiceCharge}
                  amountPaid={amountPaid}
                  onAmountPaidChange={setAmountPaid}
                  items={items}
                  isUploading={isUploading}
                  onClose={handleCloseModal}
                  onSave={handleSaveBill}
                  onUploadReceipt={handleUploadReceipt}
                  onAddItem={handleAddItem}
                  onItemChange={handleItemChange}
                  onDeleteItem={handleDeleteItem}
                  onConsumerKeyDown={handleConsumerKeyDown}
                  onRemoveConsumer={removeConsumer}
                />
              )}
              {showResults && <PaymentPlansView paymentPlans={paymentPlans} />}
              {!showModal && !showResults && (
                <div className="border-2 border-dashed border-gray-400 dark:border-gray-600 h-full flex flex-col items-center justify-center p-12">
                  <div className="text-center">
                    <div className="w-16 h-16 mx-auto mb-4 border-2 border-gray-300 dark:border-gray-700 flex items-center justify-center">
                      <Receipt size={24} className="text-gray-400 dark:text-gray-600" strokeWidth={2} />
                    </div>
                    <p className="text-gray-600 dark:text-gray-500 text-sm font-mono">add bills or calculate split</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
        {isMobile && (
          <div>
            {!showModal && !showResults && (
              <div className="border-2 border-gray-900 dark:border-gray-200 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-lg font-normal text-gray-900 dark:text-gray-100">bills</h2>
                  <span className="text-xs text-gray-700 dark:text-gray-400 font-mono">{bills.length}</span>
                </div>

                <button
                  onClick={handleAddBill}
                  className="w-full py-3 mb-6 border-2 border-dashed border-gray-400 dark:border-gray-600 text-gray-800 dark:text-gray-300 hover:border-gray-900 dark:hover:border-gray-300 hover:text-gray-900 dark:hover:text-gray-100 transition-colors flex items-center justify-center gap-2 text-sm"
                >
                  <Plus size={16} strokeWidth={2} />
                  add new bill
                </button>

                {bills.length === 0 ? (
                  <EmptyState message="no bills yet" />
                ) : (
                  bills.map((bill) => (
                    <BillCard key={bill.id} bill={bill} onEdit={handleEditBill} onDelete={handleDeleteBill} />
                  ))
                )}

                <button
                  onClick={handleCalculateSplit}
                  className="w-full mt-6 py-3 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 hover:bg-gray-800 dark:hover:bg-gray-200 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                  disabled={bills.length === 0}
                >
                  calculate split
                </button>
              </div>
            )}

            {showModal && (
              <div className="fixed inset-0 bg-white dark:bg-stone-900 z-50 overflow-y-auto">
                <BillModal
                  show={showModal}
                  editingBillId={editingBillId}
                  paidBy={paidBy}
                  onPaidByChange={setPaidBy}
                  taxRate={taxRate}
                  onTaxRateChange={setTaxRate}
                  serviceCharge={serviceCharge}
                  onServiceChargeChange={setServiceCharge}
                  amountPaid={amountPaid}
                  onAmountPaidChange={setAmountPaid}
                  items={items}
                  isUploading={isUploading}
                  onClose={handleCloseModal}
                  onSave={handleSaveBill}
                  onUploadReceipt={handleUploadReceipt}
                  onAddItem={handleAddItem}
                  onItemChange={handleItemChange}
                  onDeleteItem={handleDeleteItem}
                  onConsumerKeyDown={handleConsumerKeyDown}
                  onRemoveConsumer={removeConsumer}
                />
              </div>
            )}

            {showResults && (
              <div className="space-y-6">
                <button
                  onClick={handleBackToBills}
                  className="w-full py-3 border-2 border-gray-400 dark:border-gray-600 text-gray-800 dark:text-gray-300 hover:border-gray-900 dark:hover:border-gray-300 hover:text-gray-900 dark:hover:text-gray-100 transition-colors flex items-center justify-center gap-2"
                >
                  <ArrowLeft size={16} strokeWidth={2} />
                  back to bills
                </button>
                <PaymentPlansView paymentPlans={paymentPlans} />
                <button
                  onClick={handleAddBill}
                  className="w-full py-3 border-2 border-dashed border-gray-400 dark:border-gray-600 text-gray-800 dark:text-gray-300 hover:border-gray-900 dark:hover:border-gray-300 hover:text-gray-900 dark:hover:text-gray-100 transition-colors flex items-center justify-center gap-2 text-sm"
                >
                  <Plus size={16} strokeWidth={2} />
                  add new bill
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default BillSplitter;
