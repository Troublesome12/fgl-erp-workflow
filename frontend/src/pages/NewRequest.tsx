import { useMutation, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createRequest } from "../api";
import { Layout } from "../components/Layout";

/**
 * The NewRequest component provides a form for sales users to create new billing requests.
 * It captures client details, amount, billing period, and description.
 * Upon submission, it uses React Query's `useMutation` to send the data to the API and handles navigation.
 */
export function NewRequest() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [clientName, setClientName] = useState("");
  const [amount, setAmount] = useState("");
  const [billingPeriod, setBillingPeriod] = useState("June 2026");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");

  const mutation = useMutation({
    mutationFn: createRequest,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["my-requests"] });
      navigate(`/requests/${data.id}`);
    },
    onError: () => setError("Failed to create request. Please check your inputs."),
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    mutation.mutate({
      client_name: clientName,
      amount,
      billing_period: billingPeriod,
      description,
    });
  }

  const nav = (
    <nav className="flex gap-4 text-sm">
      <Link to="/sales" className="text-slate-600 hover:text-brand-600">
        My Requests
      </Link>
      <Link to="/sales/new" className="font-medium text-brand-600">
        New Request
      </Link>
    </nav>
  );

  return (
    <Layout title="New Billing Request" nav={nav}>
      <form onSubmit={handleSubmit} className="max-w-xl space-y-4 rounded-lg border border-slate-200 bg-white p-6">
        <div>
          <label htmlFor="client" className="block text-sm font-medium text-slate-700">
            Client Name
          </label>
          <input
            id="client"
            value={clientName}
            onChange={(e) => setClientName(e.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            required
          />
        </div>
        <div>
          <label htmlFor="amount" className="block text-sm font-medium text-slate-700">
            Amount (BDT)
          </label>
          <input
            id="amount"
            type="number"
            step="0.01"
            min="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            required
          />
        </div>
        <div>
          <label htmlFor="period" className="block text-sm font-medium text-slate-700">
            Billing Period
          </label>
          <input
            id="period"
            value={billingPeriod}
            onChange={(e) => setBillingPeriod(e.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            required
          />
        </div>
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-slate-700">
            Description
          </label>
          <textarea
            id="description"
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            required
          />
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <div className="flex gap-3">
          <button
            type="submit"
            disabled={mutation.isPending}
            className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
          >
            {mutation.isPending ? "Submitting..." : "Submit Request"}
          </button>
          <Link
            to="/sales"
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium hover:bg-slate-50"
          >
            Cancel
          </Link>
        </div>
      </form>
    </Layout>
  );
}
