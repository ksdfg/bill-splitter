import React, { useState, useEffect, ChangeEvent } from "react";
import { Item, ItemUIState } from "../types/schema";

interface ItemFormProps {
  initialItem: ItemUIState;
  index: number;
  onChange: (index: number, uiState: ItemUIState, apiState: Item) => void;
  onDelete?: (index: number) => void;
}

const stringToArray = (str: string): string[] =>
  str
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s.length > 0);

const DEFAULT_ITEM_STATE: ItemUIState = {
  name: "",
  price: "",
  quantity: 1,
  consumed_by_string: "",
};

export default function ItemForm({ initialItem, index, onChange, onDelete }: ItemFormProps) {
  const [item, setItem] = useState<ItemUIState>(() => ({
    ...DEFAULT_ITEM_STATE,
    ...initialItem,
  }));

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;

    setItem((prev) => {
      const updatedItem = { ...prev, [name]: value };

      // Prepare Item schema for parent component (conversion logic)
      const itemForCallback: Item = {
        name: updatedItem.name,
        price: parseFloat((updatedItem.price as string) || "0"),
        quantity: parseInt((updatedItem.quantity as string) || "1"),
        consumed_by: stringToArray(updatedItem.consumed_by_string),
      };

      onChange(index, updatedItem, itemForCallback);
      return updatedItem;
    });
  };

  return (
    <div style={{ border: "1px dashed #ccc", padding: "10px", marginBottom: "10px", position: "relative" }}>
      {onDelete && (
        <button
          type="button"
          className="btn btn-red"
          onClick={() => onDelete(index)}
          style={{ position: "absolute", top: 5, right: 5, width: "25px", height: "25px", fontSize: "0.8rem" }}
        >
          X
        </button>
      )}
      <div className="form-group">
        <label>Name:</label>
        <input name="name" value={item.name} onChange={handleChange} placeholder="e.g. Pizza Margherita" />
      </div>
      <div style={{ display: "flex", gap: "10px" }}>
        <div className="form-group" style={{ flex: 1 }}>
          <label>Price:</label>
          <input
            name="price"
            type="number"
            step="0.01"
            value={item.price}
            onChange={handleChange}
            placeholder="24.00"
          />
        </div>
        <div className="form-group" style={{ flex: 1 }}>
          <label>Qty:</label>
          <input name="quantity" type="number" min="1" value={item.quantity} onChange={handleChange} placeholder="2" />
        </div>
      </div>
      <div className="form-group">
        <label>Consumed By:</label>
        <input
          name="consumed_by_string"
          value={item.consumed_by_string}
          onChange={handleChange}
          placeholder="Alice, Bob (comma-separated)"
        />
      </div>
    </div>
  );
}
