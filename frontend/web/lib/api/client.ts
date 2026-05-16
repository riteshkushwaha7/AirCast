// Proxy all frontend requests through the Next/Vercel server using the
// `/api` prefix. This avoids mixed-content issues in production (HTTPS frontend
// calling HTTP backend). Keep paths relative in client code (e.g. '/v1/foo').
const API_PREFIX = '/api';

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

interface RequestOptions extends RequestInit {
  headers?: HeadersInit;
  token?: string;
  timeout?: number;
}

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { token: providedToken, headers, ...rest } = options;

  let token = providedToken;
  if (!token) {
    if (typeof window === "undefined") {
      const { cookies } = await import("next/headers");
      const cookieStore = await cookies();
      token = cookieStore.get("airwise-token")?.value;
    } else {
      token = document.cookie
        .split("; ")
        .find((row) => row.startsWith("airwise-token="))
        ?.split("=")[1];
      if (!token) {
        token = localStorage.getItem("airwise-token") ?? undefined;
      }
    }
  }
  // Normalize incoming path and ensure it maps under /api so Vercel rewrites
  // proxy to the backend host.
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;

  // On the client, use relative /api so the browser talks to Vercel (HTTPS).
  // On the server (Node), build an absolute URL to our own deployment so
  // fetch() can resolve it and Next/Vercel will still apply rewrites.
  let url: string;
  if (typeof window === 'undefined') {
    const vercelUrl = process.env.VERCEL_URL;
    if (vercelUrl) {
      // Vercel provides VERCEL_URL at runtime (e.g. my-app.vercel.app)
      url = `https://${vercelUrl}${API_PREFIX}${normalizedPath}`;
    } else {
      // Local development fallback
      const host = process.env.HOST || 'localhost';
      const port = process.env.PORT || '3000';
      url = `http://${host}:${port}${API_PREFIX}${normalizedPath}`;
    }
  } else {
    url = `${API_PREFIX}${normalizedPath}`;
  }

  // Timeout support using AbortController
  const controller = new AbortController();
  const timeout = (rest as any)?.timeout ?? 10000; // default 10s
  const timer = setTimeout(() => controller.abort(), timeout);

  const response = await fetch(url, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(headers ?? {}),
    },
    cache: "no-store",
    signal: controller.signal,
  });

  clearTimeout(timer);

  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const contentType = response.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        const payload = (await response.json()) as { error?: { message?: string }; message?: string };
        message = payload?.error?.message ?? payload?.message ?? message;
      } else {
        const text = await response.text().catch(() => '');
        if (text) message = `${message} | ${text}`;
      }
    } catch (err) {
      // keep original message
    }
    throw new ApiError(message, response.status);
  }

  // Try to parse JSON, fall back to text for non-JSON responses
  const ct = response.headers.get('content-type') ?? '';
  if (ct.includes('application/json')) return (await response.json()) as T;
  return (await response.text()) as unknown as T;
}

