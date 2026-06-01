import { useEffect, type ChangeEvent, type KeyboardEvent } from "react";
import { X, Upload, Plus } from "lucide-react";
import ItemForm from "./ItemForm";
import type { BillItem, BillItemField, BillItemFieldValue } from "../types";

interface BillModalProps {
  show: boolean;
  editingBillId: string | null;
  paidBy: string;
  onPaidByChange: (value: string) => void;
  taxRate: string;
  onTaxRateChange: (value: string) => void;
  serviceCharge: string;
  onServiceChargeChange: (value: string) => void;
  amountPaid: string;
  onAmountPaidChange: (value: string) => void;
  items: BillItem[];
  isUploading: boolean;
  onClose: () => void;
  onSave: () => void;
  onUploadReceipt: (file: File) => void | Promise<void>;
  onAddItem: () => void;
  onItemChange: (index: number, field: BillItemField, value: BillItemFieldValue) => void;
  onDeleteItem: (index: number) => void;
  onConsumerKeyDown: (index: number, event: KeyboardEvent<HTMLInputElement>) => void;
  onRemoveConsumer: (itemIndex: number, consumerName: string) => void;
}

const BillModal = ({
  show,
  editingBillId,
  paidBy,
  onPaidByChange,
  taxRate,
  onTaxRateChange,
  serviceCharge,
  onServiceChargeChange,
  amountPaid,
  onAmountPaidChange,
  items,
  isUploading,
  onClose,
  onSave,
  onUploadReceipt,
  onAddItem,
  onItemChange,
  onDeleteItem,
  onConsumerKeyDown,
  onRemoveConsumer,
}: BillModalProps) => {
  useEffect(() => {
    if (!show || isUploading) return;

    const handlePaste = (event: ClipboardEvent) => {
      const clipboardItems = event.clipboardData?.items;
      if (!clipboardItems) return;

      for (let index = 0; index < clipboardItems.length; index += 1) {
        if (clipboardItems[index].type.includes("image")) {
          const file = clipboardItems[index].getAsFile();
          if (file) {
            event.preventDefault();
            void onUploadReceipt(file);
            break;
          }
        }
      }
    };

    document.addEventListener("paste", handlePaste);
    return () => document.removeEventListener("paste", handlePaste);
  }, [show, isUploading, onUploadReceipt]);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      void onUploadReceipt(file);
    }
  };

  return (
    <div
      className={`${show ? "block" : "hidden"} lg:block bg-white dark:bg-stone-900 border-2 border-gray-900 dark:border-gray-200 lg:h-full overflow-y-auto`}
    >
      <div className="border-b-2 border-gray-900 dark:border-gray-200 p-6 flex justify-between items-center">
        <h2 className="text-lg font-mono text-gray-900 dark:text-gray-100">
          {editingBillId ? "edit bill" : "new bill"}
        </h2>
        <button
          onClick={onClose}
          className="text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
        >
          <X size={20} strokeWidth={2} />
        </button>
      </div>

      <div className="p-6 space-y-6">
        <div className="border-2 border-dashed border-gray-400 dark:border-gray-600 p-4 hover:border-gray-900 dark:hover:border-gray-300 transition-colors">
          <label className="flex items-center gap-3 cursor-pointer">
            <Upload size={18} className="text-gray-700 dark:text-gray-300" strokeWidth={2} />
            <div className="flex-1">
              <p className="text-sm text-gray-900 dark:text-gray-100">
                {isUploading ? "scanning receipt..." : "upload or paste receipt"}
              </p>
              <p className="text-xs text-gray-700 dark:text-gray-400 mt-0.5">auto-fill using OCR (ctrl+v)</p>
            </div>
            <input
              type="file"
              accept="image/jpeg,image/png"
              onChange={handleFileChange}
              className="hidden"
              disabled={isUploading}
            />
          </label>
        </div>

        <div>
          <label className="block text-xs text-gray-700 dark:text-gray-400 mb-2 font-mono tracking-wider">
            PAID BY
          </label>
          <input
            type="text"
            value={paidBy}
            onChange={(event) => onPaidByChange(event.target.value)}
            placeholder="enter name"
            className="w-full px-0 py-2 bg-transparent border-b-2 border-gray-400 dark:border-gray-600 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-500 focus:outline-none focus:border-gray-900 dark:focus:border-gray-300 transition-colors"
          />
        </div>

        <div>
          <label className="block text-xs text-gray-700 dark:text-gray-400 mb-2 font-mono tracking-wider">
            AMOUNT PAID
          </label>
          <input
            type="text"
            inputMode="decimal"
            value={amountPaid}
            onChange={(event) => onAmountPaidChange(event.target.value)}
            placeholder="0.00"
            className="w-full px-0 py-2 bg-transparent border-b-2 border-gray-400 dark:border-gray-600 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-500 focus:outline-none focus:border-gray-900 dark:focus:border-gray-300 transition-colors font-mono"
            min="0"
            step="0.01"
          />
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block text-xs text-gray-700 dark:text-gray-400 mb-2 font-mono tracking-wider">
              TAX (%)
            </label>
            <input
              type="text"
              inputMode="decimal"
              value={taxRate}
              onChange={(event) => onTaxRateChange(event.target.value)}
              placeholder="5.0"
              className="w-full px-0 py-2 bg-transparent border-b-2 border-gray-400 dark:border-gray-600 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-500 focus:outline-none focus:border-gray-900 dark:focus:border-gray-300 transition-colors font-mono"
              min="0"
              max="100"
              step="0.1"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-700 dark:text-gray-400 mb-2 font-mono tracking-wider">
              SERVICE (%)
            </label>
            <input
              type="text"
              inputMode="decimal"
              value={serviceCharge}
              onChange={(event) => onServiceChargeChange(event.target.value)}
              placeholder="10.0"
              className="w-full px-0 py-2 bg-transparent border-b-2 border-gray-400 dark:border-gray-600 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-500 focus:outline-none focus:border-gray-900 dark:focus:border-gray-300 transition-colors font-mono"
              min="0"
              max="100"
              step="0.1"
            />
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xs text-gray-700 dark:text-gray-400 font-mono tracking-wider">ITEMS</h3>
          </div>

          <div className="space-y-4">
            {items.map((item, index) => (
              <ItemForm
                key={index}
                item={item}
                index={index}
                onItemChange={onItemChange}
                onDelete={onDeleteItem}
                canDelete={items.length > 1}
                onConsumerKeyDown={onConsumerKeyDown}
                onRemoveConsumer={onRemoveConsumer}
              />
            ))}
          </div>

          <button
            onClick={onAddItem}
            className="w-full mt-4 py-3 border-2 border-dashed border-gray-400 dark:border-gray-600 text-gray-800 dark:text-gray-300 hover:border-gray-900 dark:hover:border-gray-300 hover:text-gray-900 dark:hover:text-gray-100 transition-colors flex items-center justify-center gap-2 text-sm"
          >
            <Plus size={16} strokeWidth={2} />
            add item
          </button>
        </div>

        <div className="flex gap-4 pt-4">
          <button
            onClick={onSave}
            className="flex-1 py-3 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 hover:bg-gray-800 dark:hover:bg-gray-200 transition-colors"
          >
            save bill
          </button>
          <button
            onClick={onClose}
            className="px-6 py-3 border-2 border-gray-400 dark:border-gray-600 text-gray-800 dark:text-gray-300 hover:border-gray-900 dark:hover:border-gray-300 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
          ></button>
        </div>
      </div>
    </div>
  );
};

export default BillModal;
