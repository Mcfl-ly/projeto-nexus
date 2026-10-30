import { useEffect, useState } from "react";
import { Navigate, Outlet } from "react-router-dom";

export default function ProtectedRoute() {
    const [user, setUser] = useState(null);
    const [status, setStatus] = useState("loading");

    useEffect(() => {
        const controller = new AbortController();

        async function checkSession() {
            try {
                const response = await fetch("http://localhost:8000/users/me", {

                    credentials: "include",
                    signal: controller.signal,
                });

                if (!response.ok) {
                    const details = await response.text();

                    console.error("Falha em /users/me:", response.status, details);
                }

                if (response.ok) {
                    const data = await response.json();

                    setUser(data);
                    setStatus("authenticated");
                } else if (response.status === 401) {
                    setStatus("unauthenticated");
                } else {
                    setStatus("error");
                }
            } catch (error) {
                if (error.name !== "AbortError") {
                    setStatus("error");
                }
            }
        }

        checkSession();

        return () => controller.abort();
    }, []);

    if (status === "loading") {
        return <p>Verificando sua sessão...</p>;
    }

    if (status === "error") {
        return <p>Não foi possível verificar sua sessão. Recarregue a página.</p>;
    }

    if (status === "unauthenticated") {
        return <Navigate to="/login" replace />;
    }

    return <Outlet context={{ user }}/>;
}