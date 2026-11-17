import { useCallback, useEffect, useState } from "react";
import { apiUrl } from "../api.js";
import { LibraryContext } from "../hooks/libraryContext.js";

export default function LibraryProvider({ children }) {
    const [revision, setRevision] = useState(0);
    const [state, setState] = useState({ library: [], fullContent: [], libraryError: "", loadingLibrary: true });
    const reloadLibrary = useCallback(() => setRevision((value) => value + 1), []);
    const updateItem = useCallback((id, changes) => {
        const columns = { status: 4, rating: 5, favorite: 9 };
        setState((current) => ({ ...current, library: current.library.map((row) => {
            if (row[0] !== id) return row;
            const updated = [...row];
            for (const [field, value] of Object.entries(changes)) {
                if (columns[field] !== undefined) updated[columns[field]] = value;
            }
            return updated;
        }) }));
    }, []);
    const removeItem = useCallback((id) => setState((current) => ({ ...current, library: current.library.filter((row) => row[0] !== id) })), []);

    useEffect(() => {
        const controller = new AbortController();
        fetch(apiUrl("/library/full"), { credentials: "include", signal: controller.signal })
            .then(async (response) => {
                if (!response.ok) throw new Error(response.status === 401 ? "Sua sessão expirou. Entre novamente." : "Não foi possível carregar a biblioteca. Tente novamente.");
                return response.json();
            })
            .then((data) => {
                if (!controller.signal.aborted) setState({ library: data.library, fullContent: data.contents.filter(Boolean), libraryError: "", loadingLibrary: false });
            })
            .catch((error) => {
                if (!controller.signal.aborted) setState((current) => ({ ...current, libraryError: error.message, loadingLibrary: false }));
            });
        return () => controller.abort();
    }, [revision]);

    return <LibraryContext.Provider value={{ ...state, reloadLibrary, updateItem, removeItem }}>{children}</LibraryContext.Provider>;
}
