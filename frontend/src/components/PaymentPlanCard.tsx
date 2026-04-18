import type { PaymentPlan } from "../types";

interface PaymentPlanCardProps {
  plan: PaymentPlan;
}

const PaymentPlanCard = ({ plan }: PaymentPlanCardProps) => {
  const totalToPay = plan.payments.reduce((sum, payment) => sum + payment.amount, 0);

  return (
    <div className="border-2 border-gray-300 dark:border-gray-700 p-6">
      <div className="mb-4">
        <h3 className="text-lg font-normal text-gray-900 dark:text-gray-100">{plan.name}</h3>
        <p className="text-sm text-gray-900 dark:text-gray-100 font-mono mt-1">owes ₹{totalToPay.toFixed(2)}</p>
      </div>

      <div className="space-y-2">
        {plan.payments.map((payment, index) => (
          <div
            key={index}
            className="flex items-center justify-between py-2 border-t-2 border-gray-300 dark:border-gray-700"
          >
            <span className="text-gray-800 dark:text-gray-200">→ {payment.to}</span>
            <span className="text-gray-900 dark:text-gray-100 font-mono">₹{payment.amount.toFixed(2)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PaymentPlanCard;
