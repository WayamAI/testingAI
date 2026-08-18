import { describe, it, expect, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { useExecutionSocket } from "./useExecutionSocket";

class MockWebSocket {
  static instances: MockWebSocket[] = [];
  url: string;
  onmessage: ((ev: { data: string }) => void) | null = null;
  onclose: (() => void) | null = null;
  constructor(url: string) {
    this.url = url;
    MockWebSocket.instances.push(this);
  }
  send() {}
  close() {
    this.onclose?.();
  }
}

beforeEach(() => {
  MockWebSocket.instances = [];
  // @ts-expect-error test override
  global.WebSocket = MockWebSocket;
});

describe("useExecutionSocket", () => {
  it("accumulates events received over the socket", async () => {
    const { result } = renderHook(() => useExecutionSocket("run-1"));
    const socket = MockWebSocket.instances[0];

    socket.onmessage?.({ data: JSON.stringify({ type: "status", status: "running" }) });
    socket.onmessage?.({ data: JSON.stringify({ type: "result", test_case_id: "c1", status: "passed" }) });

    await waitFor(() => expect(result.current.events.length).toBe(2));
    expect(result.current.status).toBe("running");
  });
});
