import React from "react";
import { Trash2 } from "lucide-react";

const BillCard = ({ bill, onEdit, onDelete }) => {
  const totalItems = bill.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const totalWithFees = totalItems * (1 + bill.tax_rate + bill.service_charge);

  return (
    <div className="group border-2 border-gray-900 dark:border-gray-200 p-6 mb-4 hover:border-gray-700 dark:hover:border-gray-400 transition-all duration-200">
      <div className="flex justify-between items-start mb-4">
        <div>
          <div className="text-xs text-gray-700 dark:text-gray-400 mb-1 font-mono tracking-wider">PAID BY</div>
          <h3 className="text-lg font-normal text-gray-900 dark:text-gray-100">{bill.paid_by}</h3>
          <p className="text-base text-gray-900 dark:text-gray-100 font-mono mt-1">₹{totalWithFees.toFixed(2)}</p>
        </div>
        <div className="flex gap-2 opacity-60 group-hover:opacity-100 transition-opacity duration-200">
          <button
            onClick={() => onEdit(bill)}
            className="text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 transition-colors p-2"
            title="Edit"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
              />
            </svg>
          </button>
          <button
            onClick={() => onDelete(bill.id)}
            className="text-gray-700 dark:text-gray-300 hover:text-red-600 dark:hover:text-red-400 transition-colors p-2"
            title="Delete"
          >
            <Trash2 size={16} strokeWidth={2} />
          </button>
        </div>
      </div>

      <div className="space-y-1.5 mb-4 text-sm">
        {bill.items.map((item, idx) => (
          <div key={idx} className="flex justify-between text-gray-800 dark:text-gray-200">
            <span>
              {item.quantity} × {item.name}
            </span>
            <span className="font-mono">₹{(item.price * item.quantity).toFixed(2)}</span>
          </div>
        ))}
      </div>

      {(bill.tax_rate > 0 || bill.service_charge > 0) && (
        <div className="pt-3 border-t-2 border-gray-300 dark:border-gray-700 text-xs text-gray-700 dark:text-gray-400 font-mono space-x-4 tracking-wider">
          {bill.tax_rate > 0 && <span>tax: {(bill.tax_rate * 100).toFixed(0)}%</span>}
          {bill.service_charge > 0 && <span>service: {(bill.service_charge * 100).toFixed(0)}%</span>}
        </div>
      )}
    </div>
  );
};

export default BillCard;
