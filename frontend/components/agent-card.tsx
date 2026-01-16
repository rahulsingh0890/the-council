"use client";

import { useState, useMemo } from "react";
import type { SwarmResponse, SwarmSource } from "@/lib/api";

/**
 * Render basic markdown to HTML
 */
function renderMarkdown(text: string): string {
  return text
    // Bold: **text** or __text__
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/__(.+?)__/g, '<strong>$1</strong>')
    // Italic: *text* or _text_
    .replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>')
    .replace(/(?<!_)_(?!_)(.+?)(?<!_)_(?!_)/g, '<em>$1</em>')
    // Line breaks
    .replace(/\n/g, '<br />')
    // Bullet points: - item
    .replace(/^-\s+(.+)$/gm, '<div class="ml-4">• $1</div>');
}

interface AgentCardProps {
  name: string;
  focus: string;
  color?: string;
  response: SwarmResponse | null;
  isLoading: boolean;
}

/**
 * Diversify sources to show variety of speakers.
 * Takes one source from each unique speaker first, then fills remaining slots.
 */
function diversifySources(sources: SwarmSource[], maxSources: number = 4): SwarmSource[] {
  if (!sources || sources.length === 0) return [];

  const speakerMap = new Map<string, SwarmSource[]>();

  // Group sources by speaker
  for (const source of sources) {
    const speaker = source.speaker || "Unknown";
    if (!speakerMap.has(speaker)) {
      speakerMap.set(speaker, []);
    }
    speakerMap.get(speaker)!.push(source);
  }

  const diversified: SwarmSource[] = [];
  const speakers = Array.from(speakerMap.keys());

  // Round-robin: take one from each speaker until we hit maxSources
  let round = 0;
  while (diversified.length < maxSources) {
    let addedThisRound = false;
    for (const speaker of speakers) {
      if (diversified.length >= maxSources) break;
      const speakerSources = speakerMap.get(speaker)!;
      if (round < speakerSources.length) {
        diversified.push(speakerSources[round]);
        addedThisRound = true;
      }
    }
    if (!addedThisRound) break; // No more sources to add
    round++;
  }

  return diversified;
}

export function AgentCard({ name, focus, color, response, isLoading }: AgentCardProps) {
  const [expandedSource, setExpandedSource] = useState<number | null>(null);

  // Diversify sources to show variety of speakers
  const displaySources = useMemo(() => {
    if (!response?.sources) return [];
    return diversifySources(response.sources, 4);
  }, [response?.sources]);

  return (
    <div
      className="agent-card flex flex-col h-full"
      style={{ '--agent-color': color } as React.CSSProperties}
    >
      {/* Header with color accent */}
      <div className="p-6 pb-4 border-b border-border">
        <div className="flex items-center gap-2">
          {color && (
            <div
              className="w-2.5 h-2.5 rounded-full"
              style={{ backgroundColor: color }}
            />
          )}
          <h3 className="agent-name">{name}</h3>
        </div>
        <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mt-1">{focus}</p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6 pt-4">
        {isLoading ? (
          <div className="space-y-3">
            <div className="skeleton h-4 w-full rounded" />
            <div className="skeleton h-4 w-5/6 rounded" />
            <div className="skeleton h-4 w-4/6 rounded" />
            <div className="skeleton h-4 w-full rounded" />
            <div className="skeleton h-4 w-3/4 rounded" />
          </div>
        ) : response ? (
          <div className="fade-in">
            <div
              className="text-[15px] leading-7 text-gray-600"
              dangerouslySetInnerHTML={{ __html: renderMarkdown(response.response) }}
            />

            {/* Sources with speaker attribution - diversified to show variety */}
            {displaySources.length > 0 && (
              <div className="mt-4 pt-4 border-t border-border">
                <p className="text-xs font-medium text-muted mb-2">
                  Referenced insights
                </p>
                <div className="space-y-2">
                  {displaySources.map((source, idx) => (
                    <div
                      key={idx}
                      className="text-xs bg-background rounded-lg p-2 cursor-pointer hover:bg-gray-100 transition-colors"
                      onClick={() => setExpandedSource(expandedSource === idx ? null : idx)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="text-muted">
                          <span className="font-medium text-foreground">{source.speaker}</span>
                          <span className="mx-1">·</span>
                          <span className="truncate">{source.episode}</span>
                          <span className="mx-1">·</span>
                          <span>{source.timestamp}</span>
                        </div>
                        <span className="text-muted ml-2 flex-shrink-0">
                          {expandedSource === idx ? "▼" : "▶"}
                        </span>
                      </div>
                      {expandedSource === idx && source.text && (
                        <p className="mt-2 text-muted italic border-l-2 pl-2" style={{ borderColor: color || '#e5e7eb' }}>
                          &ldquo;{source.text}&rdquo;
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <p className="text-muted text-sm italic">
            Awaiting your question...
          </p>
        )}
      </div>
    </div>
  );
}
