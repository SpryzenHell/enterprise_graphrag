from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    server_version = "GraphRAG-CI-Mock/1.0"

    def _send(self, status: int, payload: dict) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        if self.path.rstrip("/") in {"/health", "/v1/models"}:
            self._send(200, {
                "object": "list",
                "data": [{"id": "ci-mock", "object": "model", "owned_by": "local-test"}],
            })
            return
        self._send(404, {"error": {"message": "not found"}})

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            self._send(400, {"error": {"message": "invalid JSON"}})
            return

        if self.path.rstrip("/") == "/v1/completions":
            prompt = str(body.get("prompt") or "")
            tokens = prompt.split()
            token_ids = list(range(len(tokens)))
            entries = [None]
            for token_id in token_ids[1:]:
                entries.append({str(token_id): {"logprob": -0.1}})
            token_logprobs = [None] + [-0.1 for _ in token_ids[1:]]
            self._send(200, {
                "id": "cmpl-ci-mock",
                "object": "text_completion",
                "model": str(body.get("model") or "ci-mock"),
                "choices": [{
                    "index": 0,
                    "text": prompt,
                    "finish_reason": "length",
                    "prompt_token_ids": token_ids,
                    "prompt_logprobs": entries,
                    "logprobs": {"tokens": tokens, "token_logprobs": token_logprobs, "top_logprobs": [{} for _ in tokens]},
                }],
                "usage": {"prompt_tokens": len(tokens), "completion_tokens": 0, "total_tokens": len(tokens)},
            })
            return

        if self.path.rstrip("/") == "/v1/chat/completions":
            self._send(200, {
                "id": "chatcmpl-ci-mock",
                "object": "chat.completion",
                "model": str(body.get("model") or "ci-mock"),
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "The available evidence identifies the authorized retention policy. Use the cited passage as the source of truth.",
                    },
                    "finish_reason": "stop",
                }],
                "usage": {"prompt_tokens": 1, "completion_tokens": 12, "total_tokens": 13},
            })
            return

        self._send(404, {"error": {"message": "not found"}})

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Local OpenAI-compatible mock for container smoke tests only.")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"CI-only mock model endpoint listening on {args.host}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
