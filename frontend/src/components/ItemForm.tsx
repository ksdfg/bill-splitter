import type { KeyboardEvent } from "react";
import { Trash2, X } from "lucide-react";
import type { BillItem, BillItemField, BillItemFieldValue } from "../types";

interface ItemFormProps {
  item: BillItem;
  index: number;
  onItemChange: (index: number, field: BillItemField, value: BillItemFieldValue) => void;
  onDelete: (index: number) => void;
  canDelete: boolean;
  onConsumerKeyDown: (index: number, event: KeyboardEvent<HTMLInputElement>) => void;
  onRemoveConsumer: (itemIndex: number, consumerName: string) => void;
}

const ItemForm = ({
  item,
  index,
  onItemChange,
  onDelete,
  canDelete,
  onConsumerKeyDown,
  onRemoveConsumer,
}: ItemFormProps) => {
  return (
    <div className="border-2 border-gray-300 dark:border-gray-700 p-4 relative">
      <button
        onClick={() => onDelete(index)}
        disabled={!canDelete}
        className="absolute top-3 right-3 text-gray-600 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
      >
        <Trash2 size={14} strokeWidth={2} />
      </button>

      <div className="space-y-4 pr-8">
        <input
          type="text"
          value={item.name}
          onChange={(event) => onItemChange(index, "name", event.target.value)}
          placeholder="item name"
          className="w-full px-0 py-2 bg-transparent border-b-2 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-500 focus:outline-none focus:border-gray-900 dark:focus:border-gray-300 transition-colors"
        />

        <div className="grid grid-cols-2 gap-4">
          <input
            type="text"
            inputMode="decimal"
            value={item.price || ""}
            onChange={(event) => onItemChange(index, "price", parseFloat(event.target.value) || 0)}
            placeholder="price"
            className="w-full px-0 py-2 bg-transparent border-b-2 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-500 focus:outline-none focus:border-gray-900 dark:focus:border-gray-300 transition-colors font-mono"
            min="0"
            step="0.01"
          />
          <input
            type="text"
            inputMode="numeric"
            value={item.quantity || ""}
            onChange={(event) => onItemChange(index, "quantity", parseInt(event.target.value, 10) || 1)}
            placeholder="qty"
            className="w-full px-0 py-2 bg-transparent border-b-2 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-500 focus:outline-none focus:border-gray-900 dark:focus:border-gray-300 transition-colors font-mono"
            min="1"
          />
        </div>

        <div>
          <label className="block text-xs text-gray-700 dark:text-gray-400 mb-2 font-mono tracking-wider">
            CONSUMED BY
          </label>
          <div className="flex flex-wrap gap-2 mb-2">
            {item.consumed_by.map((consumer, consumerIndex) => (
              <span
                key={consumerIndex}
                className="inline-flex items-center gap-1.5 px-3 py-1 bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm border border-gray-300 dark:border-gray-700"
              >
                {consumer}
                <button
                  onClick={() => onRemoveConsumer(index, consumer)}
                  className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
                >
                  <X size={14} strokeWidth={2} />
                </button>
              </span>
            ))}
          </div>
          <input
            type="text"
            onKeyDown={(event) => onConsumerKeyDown(index, event)}
            placeholder="add name, press enter"
            className="w-full px-0 py-2 bg-transparent border-b-2 border-gray-300 dark:border-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-500 focus:outline-none focus:border-gray-900 dark:focus:border-gray-300 transition-colors"
          />
        </div>
      </div>
    </div>
  );
};

export default ItemForm;
