import { useSearchParams } from "react-router-dom";
import { useCallback, useMemo } from "react";

/**
 * Read/write a set of string filters in the URL query string so views are
 * shareable and back/forward works. Empty values are dropped from the URL.
 */
export function useUrlState<T extends Record<string, string>>(defaults: T) {
  const [params, setParams] = useSearchParams();

  const state = useMemo(() => {
    const out = { ...defaults };
    for (const key of Object.keys(defaults) as (keyof T)[]) {
      const v = params.get(key as string);
      if (v !== null) out[key] = v as T[keyof T];
    }
    return out;
  }, [params, defaults]);

  const set = useCallback(
    (patch: Partial<T>) => {
      const next = new URLSearchParams(params);
      for (const [k, v] of Object.entries(patch)) {
        if (v === "" || v === undefined || v === defaults[k]) next.delete(k);
        else next.set(k, String(v));
      }
      setParams(next, { replace: true });
    },
    [params, setParams, defaults],
  );

  const reset = useCallback(() => setParams({}, { replace: true }), [setParams]);

  return { state, set, reset };
}
