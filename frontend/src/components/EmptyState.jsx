import React from "react";
import { Receipt } from "lucide-react";

const EmptyState = ({ message }) => {
  return (
    <div className="text-center py-16">
      <Receipt size={32} className="mx-auto mb-4 text-gray-400 dark:text-gray-600" strokeWidth={2} />
      <p className="text-gray-600 dark:text-gray-500 text-sm font-mono">{message}</p>
    </div>
  );
};

export default EmptyState;
