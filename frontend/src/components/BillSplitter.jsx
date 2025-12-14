import React, { useState, useEffect } from "react";
import { Receipt, Plus, ArrowLeft } from "lucide-react";
import BillCard from "./BillCard";
import BillModal from "./BillModal";
import PaymentPlansView from "./PaymentPlansView";
import EmptyState from "./EmptyState";
import { uploadReceipt, calculateSplit } from "../utils/api";

const BillSplitter = () => {
  const [bills, setBills] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editingBillId, setEditingBillId] = useState(null);
  const [paymentPlans, setPaymentPlans] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [paidBy, setPaidBy] = useState("");
  const [taxRate, setTaxRate] = useState("5");
  const [serviceCharge, setServiceCharge] = useState("0");
  const [items, setItems] = useState([{ name: "", price: 0, quantity: 1, consumed_by: [] }]);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const resetForm = () => {
    setPaidBy("");
    setTaxRate("5");
    setServiceCharge("0");
    setItems([{ name: "", price: 0, quantity: 1, consumed_by: [] }]);
    setEditingBillId(null);
  };

  const handleAddBill = () => {
    setShowModal(true);
    setShowResults(false);
    setPaymentPlans([]);
    resetForm();
  };

  const handleEditBill = (bill) => {
    setEditingBillId(bill.id);
    setPaidBy(bill.paid_by);
    setTaxRate((bill.tax_rate * 100).toString());
    setServiceCharge((bill.service_charge * 100).toString());
    setItems(bill.items);
    setShowModal(true);
    setShowResults(false);
    setPaymentPlans([]);
  };

  const handleDeleteBill = (id) => {
    setBills(bills.filter((b) => b.id !== id));
  };

  const handleSaveBill = () => {
    if (!paidBy.trim()) {
      alert("Please enter who paid the bill");
      return;
    }

    const validItems = items.filter(
      (item) => item.name.trim() && item.price > 0 && item.quantity > 0 && item.consumed_by.length > 0,
    );

    if (validItems.length === 0) {
      alert("Please add at least one valid item with consumers");
      return;
    }

    const bill = {
      id: editingBillId || Date.now().toString(),
      paid_by: paidBy.trim(),
      tax_rate: parseFloat(taxRate) / 100,
      service_charge: parseFloat(serviceCharge) / 100,
      items: validItems,
    };

    if (editingBillId) {
      setBills(bills.map((b) => (b.id === editingBillId ? bill : b)));
    } else {
      setBills([...bills, bill]);
    }

    setShowModal(false);
    resetForm();
  };

  const handleAddItem = () => {
    setItems([...items, { name: "", price: 0, quantity: 1, consumed_by: [] }]);
  };

  const handleDeleteItem = (index) => {
    if (items.length > 1) {
      setItems(items.filter((_, i) => i !== index));
    }
  };

  const handleItemChange = (index, field, value) => {
    const newItems = [...items];
    newItems[index][field] = value;
    setItems(newItems);
  };

  const handleConsumerKeyDown = (index, e) => {
    if (e.key === "Enter" && e.target.value.trim()) {
      e.preventDefault();
      const newItems = [...items];
      const currentConsumers = newItems[index].consumed_by || [];
      const newConsumer = e.target.value.trim();

      if (!currentConsumers.includes(newConsumer)) {
        newItems[index].consumed_by = [...currentConsumers, newConsumer];
        setItems(newItems);
      }
      e.target.value = "";
    }
  };

  const removeConsumer = (itemIndex, consumerName) => {
    const newItems = [...items];
    newItems[itemIndex].consumed_by = newItems[itemIndex].consumed_by.filter((c) => c !== consumerName);
    setItems(newItems);
  };

  const handleUploadReceipt = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);

    try {
      const ocrData = await uploadReceipt(file);

      setTaxRate((ocrData.tax_rate * 100).toString());
      setServiceCharge((ocrData.service_charge * 100).toString());
      setItems(
        ocrData.items.map((item) => ({
          ...item,
          consumed_by: [],
        })),
      );

      alert("Receipt scanned! Please add who consumed each item.");
    } catch (error) {
      console.error("OCR error:", error);
      alert("Failed to scan receipt. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleCalculateSplit = async () => {
    if (bills.length === 0) {
      alert("Please add at least one bill");
      return;
    }

    try {
      const result = await calculateSplit(bills);
      setPaymentPlans(result.payment_plans);
      setShowResults(true);
    } catch (error) {
      console.error("Split calculation error:", error);
      alert("Failed to calculate split. Please try again.");
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    resetForm();
  };

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
                  setPaidBy={setPaidBy}
                  taxRate={taxRate}
                  setTaxRate={setTaxRate}
                  serviceCharge={serviceCharge}
                  setServiceCharge={setServiceCharge}
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
                  setPaidBy={setPaidBy}
                  taxRate={taxRate}
                  setTaxRate={setTaxRate}
                  serviceCharge={serviceCharge}
                  setServiceCharge={setServiceCharge}
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
                  onClick={() => setShowResults(false)}
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
