"use client";

import { useState } from "react";

interface ProblemInputProps {
  onSubmit: (problem: string) => void;
  isLoading: boolean;
}

export function ProblemInput({ onSubmit, isLoading }: ProblemInputProps) {
  const [problem, setProblem] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (problem.trim() && !isLoading) {
      onSubmit(problem.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card">
      <label htmlFor="problem" className="block mb-4">
        <span className="text-xs font-bold uppercase tracking-wider text-gray-400">
          The Situation
        </span>
        <span className="block text-sm text-gray-500 mt-1">
          Brief the Council on what you&apos;re facing.
        </span>
      </label>

      <textarea
        id="problem"
        value={problem}
        onChange={(e) => setProblem(e.target.value)}
        placeholder="Be specific about constraints and leverage. e.g., 'Our PM is blocking every initiative. I have exec support but don't want to burn bridges...'"
        className="input-field min-h-[120px] mb-4"
        disabled={isLoading}
      />

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={!problem.trim() || isLoading}
          className="btn-primary flex items-center gap-2"
        >
          {isLoading ? (
            <>
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Deploying...
            </>
          ) : (
            "Run Simulation"
          )}
        </button>
      </div>
    </form>
  );
}
