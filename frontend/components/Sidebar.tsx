"use client";

import { useState } from "react";

interface SwarmMember {
  name: string;
}

interface SwarmData {
  id: string;
  name: string;
  color: string;
  members: SwarmMember[];
  skills: string;
}

const SWARMS: SwarmData[] = [
  {
    id: "founder",
    name: "The Visionary",
    color: "#FF6B35",
    members: [
      { name: "Brian Chesky" },
      { name: "Marc Benioff" },
      { name: "Tobi Lutke" },
    ],
    skills: "Vision, Storytelling, Culture",
  },
  {
    id: "product",
    name: "The Scaler",
    color: "#4ECDC4",
    members: [
      { name: "Marty Cagan" },
      { name: "Shreyas Doshi" },
      { name: "Julie Zhuo" },
    ],
    skills: "Strategy, Discovery, Empathy",
  },
  {
    id: "growth",
    name: "The Scientist",
    color: "#95E1D3",
    members: [
      { name: "Elena Verna" },
      { name: "Brian Balfour" },
      { name: "Casey Winters" },
    ],
    skills: "Loops, PLG, Distribution",
  },
  {
    id: "engineering",
    name: "The Architect",
    color: "#6C5CE7",
    members: [
      { name: "Will Larson" },
      { name: "Camille Fournier" },
    ],
    skills: "Systems, Scale, Trade-offs",
  },
];

export function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [expandedSwarm, setExpandedSwarm] = useState<string | null>(null);

  const toggleSwarm = (id: string) => {
    if (isCollapsed) {
      setIsCollapsed(false);
      setExpandedSwarm(id);
    } else {
      setExpandedSwarm(expandedSwarm === id ? null : id);
    }
  };

  return (
    <aside
      className={`flex-shrink-0 flex flex-col bg-white border-r border-gray-200 h-screen sticky top-0 transition-all duration-300 ${
        isCollapsed ? "w-16" : "w-64"
      }`}
    >
      {/* Logo Header */}
      <div className={`border-b border-gray-100 ${isCollapsed ? "p-3" : "p-5"}`}>
        <div className="flex items-center justify-between">
          {/* Four Dots Logo + Text */}
          <div className="flex items-center gap-3">
            {/* 2x2 Dot Grid */}
            <div className="grid grid-cols-2 gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#8B5CF6]"></span>
              <span className="w-2.5 h-2.5 rounded-full bg-[#3B82F6]"></span>
              <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]"></span>
              <span className="w-2.5 h-2.5 rounded-full bg-[#F97316]"></span>
            </div>

            {/* Brand Text */}
            {!isCollapsed && (
              <div className="flex flex-col -space-y-1">
                <span className="text-[10px] font-medium text-gray-400 tracking-widest">
                  THE
                </span>
                <span className="text-xl font-black text-gray-900 tracking-tighter">
                  COUNCIL
                </span>
              </div>
            )}
          </div>

          {/* Collapse Toggle Button */}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-md hover:bg-gray-100 transition-colors"
            title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            <svg
              className={`w-4 h-4 text-gray-400 transition-transform duration-300 ${
                isCollapsed ? "rotate-180" : ""
              }`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M11 19l-7-7 7-7m8 14l-7-7 7-7"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Interactive Swarm List */}
      <nav className="flex-1 overflow-y-auto py-4">
        {!isCollapsed && (
          <div className="px-4 mb-2">
            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">
              The Swarms
            </h4>
          </div>
        )}

        <div className={`space-y-1 ${isCollapsed ? "px-1" : "px-2"}`}>
          {SWARMS.map((swarm) => {
            const isExpanded = expandedSwarm === swarm.id && !isCollapsed;

            return (
              <div key={swarm.id}>
                {/* Swarm Header - Clickable */}
                <button
                  onClick={() => toggleSwarm(swarm.id)}
                  className={`w-full flex items-center rounded-lg hover:bg-gray-50 transition-colors text-left group ${
                    isCollapsed ? "justify-center p-3" : "justify-between px-3 py-2.5"
                  }`}
                  title={isCollapsed ? swarm.name : undefined}
                >
                  <div className={`flex items-center ${isCollapsed ? "" : "gap-3"}`}>
                    <span
                      className={`rounded-full flex-shrink-0 ${isCollapsed ? "w-3 h-3" : "w-2.5 h-2.5"}`}
                      style={{ backgroundColor: swarm.color }}
                    />
                    {!isCollapsed && (
                      <span className="text-sm font-bold text-gray-700">
                        {swarm.name}
                      </span>
                    )}
                  </div>

                  {/* Chevron - Only show when not collapsed */}
                  {!isCollapsed && (
                    <svg
                      className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${
                        isExpanded ? "rotate-90" : ""
                      }`}
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  )}
                </button>

                {/* Expanded Content - Only show when not collapsed */}
                {isExpanded && (
                  <div className="ml-8 mr-3 mt-1 mb-2 pl-3 border-l-2 border-gray-100">
                    {/* Members */}
                    <div className="space-y-0.5">
                      {swarm.members.map((member) => (
                        <p
                          key={member.name}
                          className="text-xs leading-normal text-gray-500"
                        >
                          {member.name}
                        </p>
                      ))}
                    </div>

                    {/* Skills */}
                    <p className="text-xs leading-normal text-gray-400 mt-2 italic">
                      {swarm.skills}
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </nav>

      {/* Footer - Only show when not collapsed */}
      {!isCollapsed && (
        <div className="p-4 border-t border-gray-100">
          <p className="text-xs text-center text-gray-400">
            Powered by Interview Transcripts from{" "}
            <a
              href="https://www.lennysnewsletter.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-500 hover:text-gray-700 hover:underline"
            >
              Lenny&apos;s Podcast
            </a>
          </p>
        </div>
      )}
    </aside>
  );
}
