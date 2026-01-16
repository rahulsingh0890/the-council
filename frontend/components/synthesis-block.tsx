"use client";

import { cn } from "@/lib/utils";

interface SynthesisBlockProps {
  synthesis: string | null;
  isLoading: boolean;
}

function renderMarkdown(text: string): string {
  return text
    // Bold: **text** or __text__
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/__(.+?)__/g, '<strong>$1</strong>')
    // Italic: *text* or _text_
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/_(.+?)_/g, '<em>$1</em>')
    // Line breaks
    .replace(/\n/g, '<br />')
    // Numbered lists: 1. item
    .replace(/^(\d+)\.\s+(.+)$/gm, '<div class="ml-4">$1. $2</div>')
    // Bullet points: - item
    .replace(/^-\s+(.+)$/gm, '<div class="ml-4">• $1</div>');
}

export function SynthesisBlock({ synthesis, isLoading }: SynthesisBlockProps) {
  if (!synthesis && !isLoading) {
    return null;
  }

  return (
    <div className="verdict-card fade-in">
      {/* Header */}
      <div className="mb-6 pb-4 border-b border-border">
        <h3 className="text-2xl font-black tracking-tighter text-gray-900">The Verdict</h3>
        <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mt-1">
          Your strategic options, distilled
        </p>
      </div>

      {/* Content */}
      <div>
        {isLoading ? (
          <div className="space-y-3">
            <div className="skeleton h-4 w-full rounded" />
            <div className="skeleton h-4 w-5/6 rounded" />
            <div className="skeleton h-4 w-full rounded" />
            <div className="skeleton h-4 w-4/5 rounded" />
            <div className="skeleton h-4 w-3/4 rounded" />
            <div className="skeleton h-4 w-full rounded" />
          </div>
        ) : (
          <div
            className="fade-in text-sm leading-relaxed text-gray-600 [&_strong]:text-base [&_strong]:font-bold [&_strong]:text-gray-900"
            dangerouslySetInnerHTML={{ __html: renderMarkdown(synthesis || '') }}
          />
        )}
      </div>
    </div>
  );
}
