const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface SwarmSource {
  text: string;
  speaker: string;
  episode: string;
  timestamp: string;
}

export interface SwarmResponse {
  response: string;
  sources: SwarmSource[];
  agent: string;
}

export interface CouncilResponse {
  problem: string;
  founder_swarm: SwarmResponse | null;
  product_swarm: SwarmResponse | null;
  growth_swarm: SwarmResponse | null;
  engineering_swarm: SwarmResponse | null;
  synthesis: string | null;
}

export interface StreamEvent {
  event: string;
  data: {
    swarm?: string;
    display_name?: string;
    response?: SwarmResponse;
    synthesis?: string;
    error?: string;
  };
}

export async function conveneCouncil(problem: string): Promise<CouncilResponse> {
  const response = await fetch(`${API_BASE}/api/council`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ problem }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

export async function* streamCouncil(problem: string): AsyncGenerator<StreamEvent> {
  const response = await fetch(`${API_BASE}/api/council/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ problem }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("No response body");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();

    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    let currentEvent = "";
    let currentData = "";

    for (const line of lines) {
      if (line.startsWith("event: ")) {
        currentEvent = line.slice(7);
      } else if (line.startsWith("data: ")) {
        currentData = line.slice(6);
        if (currentEvent && currentData) {
          try {
            yield {
              event: currentEvent,
              data: JSON.parse(currentData),
            };
          } catch {
            // Skip malformed JSON
          }
          currentEvent = "";
          currentData = "";
        }
      }
    }
  }
}
