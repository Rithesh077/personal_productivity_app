import { useState, useEffect, useCallback } from 'react';

/**
 * Generic data fetching hook.
 *
 * @param {Function} fetchFn — async function that returns data
 * @param {Array} deps — dependency array for re-fetching
 * @returns {{ data, loading, error, refresh }}
 */
export function useApi(fetchFn, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchFn();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [fetchFn]);

  useEffect(() => {
    refresh();
  }, deps);

  return { data, loading, error, refresh, setData };
}

/**
 * Mutation hook — wraps an API call with loading/error state.
 *
 * @param {Function} mutationFn — async function to call
 * @returns {{ mutate, loading, error }}
 */
export function useMutation(mutationFn) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const mutate = useCallback(async (...args) => {
    setLoading(true);
    setError(null);
    try {
      const result = await mutationFn(...args);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [mutationFn]);

  return { mutate, loading, error };
}
