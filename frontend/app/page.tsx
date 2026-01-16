"use client";

import { useState } from "react";
import { ProblemInput } from "@/components/problem-input";
import { AgentCard } from "@/components/agent-card";
import { SynthesisBlock } from "@/components/synthesis-block";
import { conveneCouncil, type SwarmResponse } from "@/lib/api";

const SWARMS = [
  { key: "founder_swarm", name: "The Visionary", focus: "Vision, Intuition, Culture, Founder Mode", color: "#FF6B35" },
  { key: "product_swarm", name: "The Scaler", focus: "Strategy, Empowered Teams, Product Discovery", color: "#4ECDC4" },
  { key: "growth_swarm", name: "The Scientist", focus: "Loops, Acquisition, Pricing, Retention", color: "#95E1D3" },
  { key: "engineering_swarm", name: "The Architect", focus: "Systems, Technical Debt, Feasibility", color: "#6C5CE7" },
] as const;

type SwarmKey = (typeof SWARMS)[number]["key"];

interface CouncilState {
  founder_swarm: SwarmResponse | null;
  product_swarm: SwarmResponse | null;
  growth_swarm: SwarmResponse | null;
  engineering_swarm: SwarmResponse | null;
  synthesis: string | null;
}

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [loadingSwarms, setLoadingSwarms] = useState<Set<SwarmKey>>(new Set());
  const [loadingSynthesis, setLoadingSynthesis] = useState(false);
  const [council, setCouncil] = useState<CouncilState>({
    founder_swarm: null,
    product_swarm: null,
    growth_swarm: null,
    engineering_swarm: null,
    synthesis: null,
  });
  const [hasResults, setHasResults] = useState(false);

  const handleSubmit = async (problem: string) => {
    // Reset state
    setIsLoading(true);
    setHasResults(true);
    setCouncil({ founder_swarm: null, product_swarm: null, growth_swarm: null, engineering_swarm: null, synthesis: null });
    setLoadingSwarms(new Set(["founder_swarm", "product_swarm", "growth_swarm", "engineering_swarm"]));
    setLoadingSynthesis(true);

    try {
      const result = await conveneCouncil(problem);
      setCouncil({
        founder_swarm: result.founder_swarm,
        product_swarm: result.product_swarm,
        growth_swarm: result.growth_swarm,
        engineering_swarm: result.engineering_swarm,
        synthesis: result.synthesis,
      });
    } catch (error) {
      console.error("Failed to convene council:", error);
    } finally {
      setIsLoading(false);
      setLoadingSwarms(new Set());
      setLoadingSynthesis(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Page Header - Left Aligned */}
      <header className="border-b border-gray-200 bg-white">
        <div className="px-8 py-6">
          <h1 className="text-2xl font-black tracking-tighter text-gray-900">
            Run Simulation
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Describe your challenge. The Council will analyze it, cut through the noise, and give you a clean path forward.
          </p>
        </div>
      </header>

      {/* Content - Wide Dashboard Layout */}
      <div className="px-8 py-6 space-y-6">
        {/* Input Section */}
        <section>
          <ProblemInput onSubmit={handleSubmit} isLoading={isLoading} />
        </section>

        {/* Results Section */}
        {hasResults && (
          <section className="space-y-6 fade-in">
            {/* Swarm Cards - 2x2 Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 fade-in-stagger">
              {SWARMS.map((swarm) => (
                <AgentCard
                  key={swarm.key}
                  name={swarm.name}
                  focus={swarm.focus}
                  color={swarm.color}
                  response={council[swarm.key]}
                  isLoading={loadingSwarms.has(swarm.key)}
                />
              ))}
            </div>

            {/* Synthesis */}
            <SynthesisBlock
              synthesis={council.synthesis}
              isLoading={loadingSynthesis}
            />
          </section>
        )}
      </div>
    </div>
  );
}
