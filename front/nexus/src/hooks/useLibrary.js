import { apiUrl } from "../api.js";
import { useCallback, useEffect, useState } from "react";

export default function useLibrary(userId) {
    const [revision, setRevision] = useState(0);
    const reloadLibrary = useCallback(() => setRevision((value) => value + 1), []);
    const [library, setLibrary] = useState([]);
    const [fullContent, setFullContent] = useState([]);
    const [libraryError, setLibraryError] = useState("");
    const [loadingLibrary, setLoadingLibrary] = useState(true);

    useEffect(() => {
        const controller = new AbortController();
        const { signal } = controller;

        setLibrary([]);
        setFullContent([]);
        setLibraryError("");

        if (userId == null) {
            setLoadingLibrary(false);
            return () => controller.abort();
        }

        async function carregarBiblioteca() {
            setLoadingLibrary(true);

            try {
                const response = await fetch(apiUrl("/library"), {
                    method: "GET",
                    credentials: "include",
                    signal,
                });

                if (!response.ok) {
                    throw new Error(
                        `Não foi possível buscar a biblioteca (${response.status}).`
                    );
                }

                const libraryData = await response.json();
                const ids = libraryData.map((item) => item[2]);

                let contentData = [];

                // Uma biblioteca vazia não precisa da segunda requisição.
                if (ids.length > 0) {
                    const mongoResponse = await fetch(
                        apiUrl("/get_mongo"),
                        {
                            method: "POST",
                            credentials: "include",
                            headers: {
                                "Content-Type": "application/json",
                            },
                            body: JSON.stringify({ ids }),
                            signal,
                        }
                    );

                    if (!mongoResponse.ok) {
                        throw new Error(
                            `Não foi possível buscar os conteúdos (${mongoResponse.status}).`
                        );
                    }

                    contentData = await mongoResponse.json();
                }

                if (!signal.aborted) {
                    setLibrary(libraryData);
                    setFullContent(contentData.filter(Boolean));
                }
            } catch (error) {
                if (!signal.aborted) {
                    setLibraryError(error.message);
                }
            } finally {
                if (!signal.aborted) {
                    setLoadingLibrary(false);
                }
            }
        }

        carregarBiblioteca();

        return () => controller.abort();
    }, [userId, revision]);

    return {
        reloadLibrary,
        library,
        fullContent,
        libraryError,
        loadingLibrary,
    };
}