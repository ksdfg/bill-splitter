import React from "react";
import { Bill, Item } from "../types/schema";

interface BillListProps {
  bills: Bill[];
  onAdd: () => void;
  onEdit: (bill: Bill) => void;
  onDelete: (id: number) => void;
  onCalculate: () => void;
  isCalculating: boolean;
}

const formatItemSummary = (items: Item[]): string => {
  if (!items || items.length === 0) return "No items listed";
  return items.map((item) => `${item.name} (₹${item.price.toFixed(2)} x ${item.quantity})`).join(", ");
};

const formatConsumers = (items: Item[]): string => {
  const allConsumers = new Set<string>();
  items.forEach((item) => {
    item.consumed_by.forEach((c) => allConsumers.add(c));
  });
  return Array.from(allConsumers).join(", ");
};

export default function BillList({ bills, onAdd, onEdit, onDelete, onCalculate, isCalculating }: BillListProps) {
  return (
    <div className="card">
      <h3 className="panel-header">Bills</h3>
      <button type="button" className="btn btn-green" style={{ width: "100%" }} onClick={onAdd}>
        + Add New Bill
      </button>

      <div style={{ marginTop: "15px" }}>
        {bills.length === 0 ? (
          <p style={{ textAlign: "center", color: "#777" }}>No bills added yet.</p>
        ) : (
          bills.map((bill, index) => (
            <div key={bill.id} className="bill-item">
              <div className="bill-item-details">
                <strong>
                  Bill #{index + 1} - Paid by {bill.paid_by}
                </strong>
                <p style={{ fontSize: "0.9rem", margin: "3px 0" }}>Items: {formatItemSummary(bill.items)}</p>
                <p style={{ fontSize: "0.9rem", margin: "3px 0" }}>
                  Tax: {(bill.tax_rate * 100).toFixed(0)}% | Service: {(bill.service_charge * 100).toFixed(0)}% |
                  Shared: {formatConsumers(bill.items)}
                </p>
              </div>
              <div className="bill-item-actions">
                <button type="button" className="btn btn-red" onClick={() => bill.id && onDelete(bill.id)}>
                  <span role="img" aria-label="Delete">
                    🗑️
                  </span>
                </button>
                <button type="button" className="btn btn-blue" onClick={() => onEdit(bill)}>
                  Edit
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      <button
        type="button"
        className="btn btn-orange"
        onClick={onCalculate}
        disabled={bills.length === 0 || isCalculating}
      >
        {isCalculating ? "Calculating..." : "Calculate Split"}
      </button>
    </div>
  );
}
