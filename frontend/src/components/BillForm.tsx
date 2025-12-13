import React, { useState, useEffect, ChangeEvent, FormEvent } from "react";
import ItemForm from "./ItemForm";
import { extractBillDetailsFromImage } from "../api/api";
import { Bill, Item, ItemUIState, OCRBillItem } from "../types/schema";

interface BillFormProps {
  initialData: Bill | null;
  onSave: (billData: Bill) => void;
  onCancel: () => void;
}

interface BillUIState extends Omit<Bill, "items"> {
  items: ItemUIState[];
  apiItems: Item[];
}

const mapBillToUIState = (bill: Bill | null): BillUIState => {
  if (!bill) {
    return { id: undefined, paid_by: "", tax_rate: 0.05, service_charge: 0.0, items: [], apiItems: [] };
  }

  const itemsUI: ItemUIState[] = bill.items.map((item) => ({
    ...item,
    price: item.price.toFixed(2),
    quantity: item.quantity.toString(),
    consumed_by_string: item.consumed_by.join(", "),
  }));

  return { ...bill, items: itemsUI, apiItems: bill.items };
};

export default function BillForm({ initialData, onSave, onCancel }: BillFormProps) {
  const [bill, setBill] = useState<BillUIState>(mapBillToUIState(initialData));
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    setBill(mapBillToUIState(initialData));
  }, [initialData]);

  const handleTextChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setBill((prev) => ({ ...prev, [name as "paid_by"]: value }));
  };

  const handleRateChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    const numericValue = parseFloat(value) || 0;
    const rate = numericValue / 100;
    setBill((prev) => ({ ...prev, [name as "tax_rate" | "service_charge"]: rate }));
  };

  const addItem = () => {
    const newItemUI: ItemUIState = { name: "", price: "", quantity: 1, consumed_by_string: "" };
    const newItemAPI: Item = { name: "", price: 0, quantity: 1, consumed_by: [] };

    setBill((prev) => ({
      ...prev,
      items: [...prev.items, newItemUI],
      apiItems: [...prev.apiItems, newItemAPI],
    }));
  };

  const handleItemChange = (index: number, itemUIState: ItemUIState, itemApiState: Item) => {
    setBill((prev) => {
      const newItems = [...prev.items];
      newItems[index] = itemUIState;
      const newApiItems = [...prev.apiItems];
      newApiItems[index] = itemApiState;
      return { ...prev, items: newItems, apiItems: newApiItems };
    });
  };

  const deleteItem = (index: number) => {
    setBill((prev) => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index),
      apiItems: prev.apiItems.filter((_, i) => i !== index),
    }));
  };

  const handleOcrUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      const ocrResult = await extractBillDetailsFromImage(file);

      const newItemsUI: ItemUIState[] = ocrResult.items.map((item: OCRBillItem) => ({
        name: item.name,
        price: item.price.toFixed(2),
        quantity: item.quantity.toString(),
        consumed_by_string: "",
      }));

      const newItemsAPI: Item[] = ocrResult.items.map(
        (item: OCRBillItem): Item => ({
          ...item,
          consumed_by: [], // User must add this
        }),
      );

      setBill((prev) => ({
        ...prev,
        tax_rate: ocrResult.tax_rate,
        service_charge: ocrResult.service_charge,
        items: newItemsUI,
        apiItems: newItemsAPI,
      }));
    } catch (error) {
      console.error("OCR failed:", error);
      alert("Failed to process receipt via OCR.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    if (!bill.paid_by || bill.apiItems.length === 0 || bill.apiItems.some((item) => item.consumed_by.length === 0)) {
      alert("Please ensure all items have a name, price, quantity, and assigned consumers.");
      return;
    }

    const billToSave: Bill = {
      id: bill.id,
      paid_by: bill.paid_by,
      tax_rate: bill.tax_rate,
      service_charge: bill.service_charge,
      items: bill.apiItems,
    };
    onSave(billToSave);
  };

  const title = bill.id ? "Edit Bill" : "Add New Bill";
  const taxRateDisplay = (bill.tax_rate * 100).toFixed(2);
  const serviceChargeDisplay = (bill.service_charge * 100).toFixed(2);

  return (
    <form onSubmit={handleSubmit} className="form-card">
      <h3 className="panel-header">{title}</h3>

      {/* OCR Uploader */}
      <div className="form-group">
        <label htmlFor="ocr-upload" className="btn btn-blue" style={{ textAlign: "center" }}>
          {isUploading ? "Processing..." : "Auto-fill from bill image using OCR"}
        </label>
        <input
          id="ocr-upload"
          type="file"
          accept="image/jpeg, image/png"
          onChange={handleOcrUpload}
          style={{ display: "none" }}
          disabled={isUploading}
        />
      </div>

      <div className="form-group">
        <label>Paid By:</label>
        <input name="paid_by" value={bill.paid_by} onChange={handleTextChange} placeholder="Enter name..." />
      </div>

      <div style={{ display: "flex", gap: "10px" }}>
        <div className="form-group" style={{ flex: 1 }}>
          <label>Tax Rate (% of subtotal):</label>
          <input
            name="tax_rate"
            type="number"
            step="0.1"
            value={taxRateDisplay}
            onChange={handleRateChange}
            placeholder="e.g. 5.0"
          />
        </div>
        <div className="form-group" style={{ flex: 1 }}>
          <label>Service Charge (%):</label>
          <input
            name="service_charge"
            type="number"
            step="0.1"
            value={serviceChargeDisplay}
            onChange={handleRateChange}
            placeholder="e.g. 10.0"
          />
        </div>
      </div>

      <h4 style={{ marginTop: "20px" }}>Items</h4>
      {bill.items.map((item, index) => (
        <ItemForm key={index} index={index} initialItem={item} onChange={handleItemChange} onDelete={deleteItem} />
      ))}

      <button type="button" className="btn btn-green" style={{ width: "100%" }} onClick={addItem}>
        + Add Item
      </button>

      <div style={{ display: "flex", justifyContent: "space-between", marginTop: "20px" }}>
        <button type="submit" className="btn btn-blue" style={{ flex: 1, marginRight: "10px" }}>
          Save Bill
        </button>
        <button type="button" className="btn btn-gray" style={{ flex: 1, marginLeft: "10px" }} onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  );
}
