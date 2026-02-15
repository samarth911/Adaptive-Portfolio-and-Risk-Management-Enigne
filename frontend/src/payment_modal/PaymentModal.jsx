import { useState } from "react";
import { addFunds, withdraw as withdrawApi } from "../api";

export default function PaymentModal({ onClose, onSuccess, mode = "add" }) {
  const [amount, setAmount] = useState("");
  const [card, setCard] = useState("");
  const [expiry, setExpiry] = useState("");
  const [cvv, setCvv] = useState("");
  const [processing, setProcessing] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const num = parseFloat(amount);
    if (isNaN(num) || num <= 0) return;
    setError("");
    setProcessing(true);
    try {
      await new Promise((r) => setTimeout(r, 2000));
      if (mode === "add") {
        await addFunds({ amount: num, card_number: card, expiry, cvv });
      } else {
        await withdrawApi({ amount: num });
      }
      setDone(true);
      onSuccess && onSuccess(mode === "add" ? num : -num);
      setTimeout(() => { onClose(); setDone(false); setAmount(""); setCard(""); setExpiry(""); setCvv(""); }, 1200);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Request failed");
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>{mode === "add" ? "Add funds" : "Withdraw funds"}</h3>
        {!done ? (
          <form onSubmit={handleSubmit}>
            <input
              type="number"
              placeholder="Amount (USD)"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              min="1"
              step="0.01"
              required
            />
            {mode === "add" && (
              <>
                <input
                  type="text"
                  placeholder="Card number (e.g. 4242 4242 4242 4242)"
                  value={card}
                  onChange={(e) => setCard(e.target.value)}
                />
                <input type="text" placeholder="MM/YY" value={expiry} onChange={(e) => setExpiry(e.target.value)} />
                <input type="text" placeholder="CVV" value={cvv} onChange={(e) => setCvv(e.target.value)} />
              </>
            )}
            {error && <p style={{ color: "var(--red)", fontSize: "0.9375rem", marginBottom: "0.5rem" }}>{error}</p>}
            <div className="modal-actions">
              <button type="button" className="btn" onClick={onClose} style={{ background: "rgba(0,0,0,0.06)", color: "#1d1d1f" }}>
                Cancel
              </button>
              <button type="submit" className="btn primary" disabled={processing}>
                {processing ? "Processing…" : mode === "add" ? "Add funds" : "Withdraw"}
              </button>
            </div>
          </form>
        ) : (
          <p style={{ color: "var(--green)", fontWeight: 600 }}>Success. Balance updated.</p>
        )}
      </div>
    </div>
  );
}
