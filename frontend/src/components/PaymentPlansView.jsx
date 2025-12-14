import React from "react";
import PaymentPlanCard from "./PaymentPlanCard";

const PaymentPlansView = ({ paymentPlans }) => {
  const plansWithPayments = paymentPlans.filter((plan) => plan.payments.length > 0);

  return (
    <div className="bg-white dark:bg-stone-900 border-2 border-gray-900 dark:border-gray-200 h-full overflow-y-auto">
      <div className="border-b-2 border-gray-900 dark:border-gray-200 p-6">
        <h2 className="text-lg font-mono text-gray-900 dark:text-gray-100">payment plans</h2>
      </div>

      <div className="p-6 space-y-6">
        {plansWithPayments.map((plan, index) => (
          <PaymentPlanCard key={index} plan={plan} />
        ))}

        <p className="text-xs text-gray-600 dark:text-gray-500 text-center pt-4 font-mono">
          modify bills to recalculate
        </p>
      </div>
    </div>
  );
};

export default PaymentPlansView;
