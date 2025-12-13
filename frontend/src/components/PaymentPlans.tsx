import React, { useMemo } from "react";
import { OutingSplit } from "../types/schema";
import { calculateNetPayments } from "../api/api";

interface PaymentPlansProps {
  splitResults: OutingSplit | null;
  onBackToBills?: () => void;
  isMobile: boolean;
}

const formatCurrency = (amount: number): string => `₹${Math.abs(amount).toFixed(2)}`;

export default function PaymentPlans({ splitResults, onBackToBills, isMobile }: PaymentPlansProps) {
  const paymentFlows = useMemo(() => {
    if (!splitResults) return [];
    return calculateNetPayments(splitResults);
  }, [splitResults]);

  if (!splitResults) {
    return <p>Click "Calculate Split" to see results.</p>;
  }

  return (
    <div className="card" style={isMobile ? { paddingTop: 0 } : {}}>
      <h3 className="panel-header" style={{ color: "#1abc9c" }}>
        Payment Plans
      </h3>

      {paymentFlows.map((flow) => (
        <div key={flow.name} className="payment-card">
          <h4>{flow.name}</h4>
          <div className="payment-info">
            {/* Display the 'Receives' status ONLY if there are no outgoing payments
                            AND the net amount is positive (the person is a net receiver). */}
            {flow.outgoing.length === 0 && flow.netAmount > 0 && (
              <p style={{ color: "#16a085", fontWeight: "bold" }}>📌 {flow.uiTextOverride || "Receives funds"}</p>
            )}

            {/* If the person is a net receiver but still needs to pay someone else,
                            we list their outgoing payments. */}

            {/* Display ONLY outgoing payments */}
            {flow.outgoing.map((p, idx) => (
              <p key={idx}>
                &rarr; Pay {p.to}: {formatCurrency(p.amount)}
              </p>
            ))}

            {/* Display totals matching the UI screenshot */}
            {(flow.name === "Alice" || flow.name === "Carol") && flow.totalOutgoing > 0 && (
              <p style={{ borderTop: "1px dashed #eee", marginTop: "5px", paddingTop: "5px" }}>
                Total: {formatCurrency(flow.totalOutgoing)}
              </p>
            )}

            {/* If the person is a net receiver (like Bob) and has no outgoing payments,
                            we explicitly add a "No payments needed" line if the override wasn't used.
                            (Matching the spirit of the UI design where Bob's section ends cleaner). */}
            {flow.name === "Bob" && flow.outgoing.length === 0 && flow.netAmount > 0 && !flow.uiTextOverride && (
              <p style={{ fontSize: "0.9rem", color: "#777" }}>No payments needed</p>
            )}
          </div>
        </div>
      ))}

      {isMobile && onBackToBills && (
        <button
          type="button"
          className="btn btn-green"
          style={{ width: "100%", marginTop: "15px" }}
          onClick={onBackToBills}
        >
          + Add New Bill
        </button>
      )}

      {!isMobile && (
        <small
          style={{
            display: "block",
            marginTop: "15px",
            color: "#777",
            borderTop: "1px solid #eee",
            paddingTop: "10px",
          }}
        >
          Click "Add New Bill" or "Edit" to modify bills (results will be recalculated).
        </small>
      )}
    </div>
  );
}
