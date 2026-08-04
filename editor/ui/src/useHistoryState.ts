import { useCallback, useState } from "react";

interface HistoryValue<T> {
  past: T[];
  present: T;
  future: T[];
}

export function useHistoryState<T>(initial: T) {
  const [history, setHistory] = useState<HistoryValue<T>>({ past: [], present: initial, future: [] });

  const set = useCallback((next: T | ((current: T) => T), record = true) => {
    setHistory((current) => {
      const value = typeof next === "function" ? (next as (current: T) => T)(current.present) : next;
      if (!record) return { ...current, present: value };
      return { past: [...current.past.slice(-49), current.present], present: value, future: [] };
    });
  }, []);

  const reset = useCallback((value: T) => {
    setHistory({ past: [], present: value, future: [] });
  }, []);

  const undo = useCallback(() => {
    setHistory((current) => {
      if (!current.past.length) return current;
      const previous = current.past[current.past.length - 1];
      return { past: current.past.slice(0, -1), present: previous, future: [current.present, ...current.future] };
    });
  }, []);

  const redo = useCallback(() => {
    setHistory((current) => {
      if (!current.future.length) return current;
      const next = current.future[0];
      return { past: [...current.past, current.present], present: next, future: current.future.slice(1) };
    });
  }, []);

  return {
    value: history.present,
    set,
    reset,
    undo,
    redo,
    canUndo: history.past.length > 0,
    canRedo: history.future.length > 0,
  };
}
